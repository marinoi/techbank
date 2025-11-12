from sqlalchemy.exc import IntegrityError

from .queues import WalletFanoutQueues
from ..common.broker.exchanges import BrokerExchanges
from ..common.broker.rabbitmq import rabbitmq
from ..common.db.models import TokenBlacklist
from ..common.db.orm import async_session
from ..common.schemas.events import TokenRevokedEvent


@rabbitmq.subscriber(WalletFanoutQueues.WALLET_TOKEN_REVOKED.value, exchange=BrokerExchanges.TOKEN_REVOKED.value)
async def token_revoked_subscriber(data: TokenRevokedEvent):
    try:
        token = TokenBlacklist(jti=data.jti)

        async with async_session() as session:
            await token.save(session)

    except IntegrityError:
        pass
