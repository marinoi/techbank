import uuid
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response

from .routes import PublicRoutes, PUBLIC_ROUTER_PREFIX
from ..common.broker.exchanges import BrokerExchanges
from ..common.db.models import OutBoxEvent
from ..common.db.orm import get_async_session
from ..common.misc.cookies import Cookies, COOKIES_CONFIG
from ..common.schemas.events import UserCreatedEvent
from ..common.security.jwt import JWTValidator
from ..common.security.keys import KeysLoader
from ..common.security.roles import Role
from ..models.models import User
from ..schemas.schemas import UserDataIn, LoginDataIn, UserOut
from ..token.config import JWTConfig
from ..token.manager import JWTManager


public_api = APIRouter(prefix=PUBLIC_ROUTER_PREFIX, tags=["public"])


@public_api.post(PublicRoutes.SIGNUP.value, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserDataIn, session: AsyncSession = Depends(get_async_session)):
    try:
        payload.role = Role.USER

        async with session.begin():
            user = await User.signup(session, payload)

            event = UserCreatedEvent(event_id=str(uuid.uuid4()), user_id=user.id, name=user.name, surname=user.surname)
            outbox_event = OutBoxEvent(payload=event.model_dump_json(),
                                       event_id=event.event_id,
                                       exchange=BrokerExchanges.USER_CREATED.value.name)

            await outbox_event.save(session, commit=False)

            return {"response": "signup"}

    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="user-already-exists")


@public_api.post(PublicRoutes.LOGIN.value, status_code=status.HTTP_200_OK, response_model=UserOut)
async def login(payload: LoginDataIn,
                request: Request,
                response: Response,
                session: AsyncSession = Depends(get_async_session)):

    jwt = await JWTValidator.from_request(request, allow_expired=True, raise_on_none=False, check_blacklist=False)

    if jwt and not jwt.is_expired():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="already-logged-in")

    user = await User.from_email(session, payload.email)

    if not user or not user.verify_password(payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="wrong-credentials")

    elif user.is_banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="user-is-banned")

    jwt_token = JWTManager().create_access_token(sub=user.id, role=user.role, refresh_count=0)

    response.set_cookie(key=Cookies.JWT_TOKEN.value, value=jwt_token, **COOKIES_CONFIG)

    user.last_login = datetime.now(tz=timezone.utc)
    await session.commit()

    return user


@public_api.get(PublicRoutes.REFRESH_TOKEN.value, status_code=status.HTTP_201_CREATED)
async def refresh_token(request: Request, response: Response, session: AsyncSession = Depends(get_async_session)):

    jwt = await JWTValidator.from_request(request, allow_expired=True, session=session)

    now = datetime.now(tz=timezone.utc)
    exp = datetime.fromtimestamp(jwt.exp, tz=timezone.utc)
    extended_exp = exp + timedelta(seconds=JWTConfig.JWT_REFRESH_BUFFER_TIME)

    if not jwt.is_expired():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="no-refresh-needed")

    elif extended_exp < now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="refresh-buffer-time-expired")

    user = await User.get_by_id(session, jwt.sub)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="user-not-found")

    elif user.is_banned:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="user-is-banned")

    elif jwt.refresh_counter >= JWTConfig.JWT_MAX_AUTO_REFRESH_ALLOWED:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="max-auto-refresh-exceed")

    new_token = JWTManager().create_access_token(sub=user.id,
                                                 role=user.role,
                                                 refresh_count=jwt.refresh_counter + 1)

    response.set_cookie(key=Cookies.JWT_TOKEN.value, value=new_token, **COOKIES_CONFIG)

    return {"response": "token-refreshed"}


@public_api.get(PublicRoutes.PUBLIC_KEY.value, status_code=status.HTTP_200_OK)
async def public_key():
    return {"public-key": KeysLoader().public_key}


@public_api.get(PublicRoutes.HEALTH_CHECK.value, status_code=status.HTTP_200_OK)
async def health_check():
    return {"health-check": "ok"}
