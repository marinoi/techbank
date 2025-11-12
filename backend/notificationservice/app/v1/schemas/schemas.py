from pydantic import ConfigDict
from pydantic import UUID4

from app.v1.common.schemas.dbentity import HasID, HasCreatedAt


class NotificationOut(HasID, HasCreatedAt):
    emitter: str
    reason: str

    model_config = ConfigDict(from_attributes=True)


class NotificationDetailsOut(HasID, HasCreatedAt):
    user_id: UUID4
    source_event_id: UUID4 | None
    emitter: str
    reason: str
    message: str

    model_config = ConfigDict(from_attributes=True)
