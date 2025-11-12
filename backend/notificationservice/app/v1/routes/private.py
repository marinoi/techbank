import uuid

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request

from .utils import user_exists_or_404, notification_exists_or_404, notification_ownership_or_404
from ..common.db.orm import get_async_session
from ..common.schemas.token import JWTPayload
from ..common.security.router import RuledAPIRouter
from ..common.security.roles import Role

from .routes import PrivateRoutes, PRIVATE_ROUTER_PREFIX
from ..models.models import UserRef, Notification
from ..schemas.schemas import NotificationOut, NotificationDetailsOut

private_api = RuledAPIRouter(prefix=PRIVATE_ROUTER_PREFIX,
                             tags=["private"],
                             allowed_roles=[Role.USER])


@private_api.get(PrivateRoutes.NOTIFICATIONS.value, response_model=list[NotificationOut], status_code=status.HTTP_200_OK)
async def get_notifications(request: Request, session: AsyncSession = Depends(get_async_session)):
    jwt: JWTPayload = request.state.jwt

    notifications = await Notification.get_all_by_user_id(session, jwt.sub)

    return notifications


@private_api.get(PrivateRoutes.NOTIFICATION.value, response_model=NotificationDetailsOut, status_code=status.HTTP_200_OK)
async def get_notification_detail(notification_id: uuid.UUID, request: Request, session: AsyncSession = Depends(get_async_session)):
    jwt: JWTPayload = request.state.jwt

    notification = await Notification.get_by_id(session, notification_id)
    notification_exists_or_404(notification)
    notification_ownership_or_404(notification, jwt.sub)

    return notification
