import enum

from faststream.rabbit import RabbitExchange, ExchangeType


class BrokerExchanges(enum.Enum):
    TOKEN_REVOKED = RabbitExchange("token.revoked", type=ExchangeType.FANOUT, durable=True)
    USER_CREATED = RabbitExchange("user.created", type=ExchangeType.FANOUT, durable=True)
    USER_DELETED = RabbitExchange("user.deleted", type=ExchangeType.FANOUT, durable=True)