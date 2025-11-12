import uuid
from typing import List

from fastapi.params import Depends
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from .routes import AdminRoutes, ADMIN_ROUTER_PREFIX
from ..common.broker.exchanges import BrokerExchanges
from ..common.db.models import OutBoxEvent
from ..common.db.orm import get_async_session
from ..common.schemas.events import UserDeletedEvent, UserCreatedEvent
from ..common.security.roles import Role
from ..common.security.router import RuledAPIRouter
from ..models.models import User
from ..schemas.schemas import UserOutAdmin, UserDataIn, AdminUserDataIn

administration_api = RuledAPIRouter(prefix=ADMIN_ROUTER_PREFIX,
                                    tags=["administration"],
                                     allowed_roles=[Role.ADMIN])


@administration_api.get(AdminRoutes.USERS.value, status_code=status.HTTP_200_OK, response_model=List[UserOutAdmin])
async def get_users(session: AsyncSession = Depends(get_async_session)):
    return await User.get_all(session)
 
@administration_api.get(AdminRoutes.USER.value, status_code=status.HTTP_200_OK, response_model=UserOutAdmin)
async def get_user(user_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    return await User.get_by_id(session, user_id)

@administration_api.post(AdminRoutes.NEW_USER.value, status_code=status.HTTP_201_CREATED)
async def new_user(payload: UserDataIn, session: AsyncSession = Depends(get_async_session)):
    try:
        async with session.begin():
            user = await User.signup(session, payload)

            if payload.role != Role.ADMIN:
                event = UserCreatedEvent(event_id=str(uuid.uuid4()), user_id=user.id, name=user.name, surname=user.surname)
                outbox_event = OutBoxEvent(payload=event.model_dump_json(),
                                           event_id=event.event_id,
                                           exchange=BrokerExchanges.USER_CREATED.value.name)

                await outbox_event.save(session, commit=False)

            return {"detail": "new-user-created"}

    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"user-already-exists")

@administration_api.put(AdminRoutes.UPDATE_USER.value, status_code=status.HTTP_200_OK)
async def update_user(user_id: uuid.UUID, payload: AdminUserDataIn, session: AsyncSession = Depends(get_async_session)):
    user = await User.get_by_id(session, user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="user-not-found")

    await user.update_from_dict(session, payload.model_dump(exclude_unset=True))

    return {"detail": "user-updated"}

@administration_api.patch(AdminRoutes.BAN_USER.value, status_code=status.HTTP_200_OK)
async def ban_user(user_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    user = await User.get_by_id(session, user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="user-not-found")

    user.is_banned = True
    await user.save(session)

    return {"detail": "user-banned"}

@administration_api.delete(AdminRoutes.DELETE_USER.value, status_code=status.HTTP_200_OK)
async def delete_user(user_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    try:
        async with session.begin():
            user = await User.get_by_id(session, user_id)

            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="user-not-found")


            await user.delete(session, commit=False)

            event = UserDeletedEvent(event_id=str(uuid.uuid4()), user_id=user.id)
            outbox_event = OutBoxEvent(payload=event.model_dump_json(),
                                       event_id=event.event_id,
                                       exchange=BrokerExchanges.USER_DELETED.value.name)

            await outbox_event.save(session, commit=False)

            return {"detail": "user-deleted"}

    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="db-error-deleting-user")
