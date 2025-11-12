import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response

from .routes import PRIVATE_ROUTER_PREFIX
from ..common.broker.exchanges import BrokerExchanges
from ..common.db.models import TokenBlacklist, OutBoxEvent
from ..common.db.orm import get_async_session
from ..common.misc.cookies import Cookies, COOKIES_CONFIG
from ..common.schemas.events import TokenRevokedEvent
from ..common.schemas.token import JWTPayload
from ..common.security.roles import Role
from ..common.security.router import RuledAPIRouter
from ..models.models import User
from ..routes.routes import PrivateRoutes
from ..schemas.schemas import UserOut


private_api = RuledAPIRouter(prefix=PRIVATE_ROUTER_PREFIX,
                             tags=["private"],
                             allowed_roles=[Role.ADMIN, Role.USER])


@private_api.get(PrivateRoutes.LOGOUT.value, status_code=status.HTTP_200_OK)
async def logout(request: Request, response: Response, session: AsyncSession = Depends(get_async_session)):
    jwt: JWTPayload = request.state.jwt
    event = TokenRevokedEvent(event_id=str(uuid.uuid4()), jti=jwt.jti)

    async with session.begin():

        outbox_event = OutBoxEvent(payload=event.model_dump_json(),
                                   event_id=event.event_id,
                                   exchange=BrokerExchanges.TOKEN_REVOKED.value.name)

        await outbox_event.save(session, commit=False)
        await TokenBlacklist.revoke(session, jwt.jti, commit=False)

    response.delete_cookie(key=Cookies.JWT_TOKEN.value, **COOKIES_CONFIG)

    return {"response": "logout"}


@private_api.get(PrivateRoutes.ME.value, response_model=UserOut, status_code=status.HTTP_200_OK)
async def me(request: Request, session: AsyncSession = Depends(get_async_session)):
    jwt: JWTPayload = request.state.jwt

    user = await User.get_by_id(session, jwt.sub)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="user-not-found")

    return user


