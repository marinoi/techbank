import enum

from faststream.rabbit import RabbitQueue


class WalletFanoutQueues(enum.Enum):
    WALLET_USER_CREATED = RabbitQueue("wallet-user-created", durable=True)
    WALLET_USER_DELETED = RabbitQueue("wallet-user-deleted", durable=True)
    WALLET_TOKEN_REVOKED = RabbitQueue("wallet-user-revoked", durable=True)
