import enum

from faststream.rabbit import RabbitQueue


class CardFanoutQueues(enum.Enum):
    CARD_USER_CREATED = RabbitQueue("card-user-created", durable=True)
    CARD_USER_DELETED = RabbitQueue("card-user-deleted", durable=True)
    CARD_TOKEN_REVOKED = RabbitQueue("card-user-revoked", durable=True)
