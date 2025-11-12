from sqlalchemy.exc import IntegrityError

from .queues import CardFanoutQueues
from ..common.broker.exchanges import BrokerExchanges
from ..common.broker.rabbitmq import rabbitmq
from ..common.db.orm import async_session
from ..common.schemas.events import UserCreatedEvent, UserDeletedEvent
from ..models.models import UserRef


@rabbitmq.subscriber(CardFanoutQueues.CARD_USER_CREATED.value, exchange=BrokerExchanges.USER_CREATED.value)
async def user_created_subscriber(data: UserCreatedEvent):
    try:
        new_user = UserRef(id=data.user_id, name=data.name, surname=data.surname)

        async with async_session() as session:
            await new_user.save(session)

    except IntegrityError:
        pass


@rabbitmq.subscriber(CardFanoutQueues.CARD_USER_DELETED.value, exchange=BrokerExchanges.USER_DELETED.value)
async def user_deleted_subscriber(data: UserDeletedEvent):
    async with async_session() as session:
        user = await UserRef.get_by_id(session, data.user_id)
        await user.delete(session)

