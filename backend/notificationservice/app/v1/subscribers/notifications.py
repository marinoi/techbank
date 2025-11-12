from ..common.broker.queues import NotificationQueues
from ..common.broker.rabbitmq import rabbitmq
from ..common.db.orm import async_session
from ..common.inbox.utils import inbox_based_idempotency
from ..common.schemas.events import NotificationEvent
from ..models.models import Notification, UserRef


@rabbitmq.subscriber(queue=NotificationQueues.NOTIFY.value)
@inbox_based_idempotency(queue=NotificationQueues.NOTIFY.value.name)
async def register_notification(data: NotificationEvent):
    async with async_session() as session:
        user = await UserRef.get_by_id(session, data.user_id)

        if not user:
            raise ValueError("user-not-found")

        notification = Notification(event_id=data.event_id,
                                    source_event_id=data.source_event_id,
                                    user=user,
                                    emitter=data.emitter,
                                    reason=data.reason,
                                    message=data.message)

        await notification.save(session)
