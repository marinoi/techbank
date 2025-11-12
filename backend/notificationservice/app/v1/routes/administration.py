import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from .utils import notification_exists_or_404, notification_ownership_or_404
from ..common.db.orm import get_async_session
from ..common.security.router import RuledAPIRouter
from ..common.security.roles import Role

from .routes import AdminRoutes, ADMIN_ROUTER_PREFIX
from ..models.models import Notification
from ..schemas.schemas import NotificationOut, NotificationDetailsOut


administration_api = RuledAPIRouter(prefix=ADMIN_ROUTER_PREFIX,
                                    tags=["administration"],
                                    allowed_roles=[Role.ADMIN])


@administration_api.get(AdminRoutes.NOTIFICATIONS.value, response_model=list[NotificationOut], status_code=status.HTTP_200_OK)
async def get_notifications(user_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    notifications = await Notification.get_all_by_user_id(session, user_id)
    return notifications


@administration_api.get(AdminRoutes.NOTIFICATION.value, response_model=NotificationDetailsOut, status_code=status.HTTP_200_OK)
async def get_notification(user_id: uuid.UUID, notification_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    notification = await Notification.get_by_id(session, notification_id)
    notification_exists_or_404(notification)
    notification_ownership_or_404(notification, user_id)

    return notification

