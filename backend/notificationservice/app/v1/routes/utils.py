import uuid

from starlette import status
from starlette.exceptions import HTTPException

from ..models.models import Notification, UserRef


def user_exists_or_404(user: UserRef | None, detail: str = "user-not-found"):
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=detail)


def notification_exists_or_404(notification: Notification | None, detail: str = "notification-not-found"):
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=detail)



def notification_ownership_or_404(notification: Notification, user_id: uuid.UUID, detail="notification-not-found"):
    if notification.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=detail)