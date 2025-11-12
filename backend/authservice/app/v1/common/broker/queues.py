import enum

from faststream.rabbit import RabbitQueue


class WalletQueues(enum.Enum):
    CARD_RECHARGE = RabbitQueue("wallet-card-recharge", durable=True)
    CARD_REFUND = RabbitQueue("wallet-card-refund", durable=True)

    CARD_TO_WALLET_PAYMENT = RabbitQueue("card-to-wallet-payment", durable=True)
    WALLET_TO_CARD_PAYMENT_RESPONSE = RabbitQueue("wallet-to-card-payment-response", durable=True)


class CardQueues(enum.Enum):
    CARD_RECHARGE_RESPONSE = RabbitQueue("card-wallet-recharge-response", durable=True)
    CARD_REFUND_RESPONSE = RabbitQueue("card-wallet-refund-response", durable=True)

    CARD_TO_WALLET_PAYMENT_RESPONSE = RabbitQueue("card-to-wallet-payment-response", durable=True)
    WALLET_TO_CARD_PAYMENT = RabbitQueue("wallet-to-card-payment", durable=True)


class NotificationQueues(enum.Enum):
    NOTIFY = RabbitQueue("notification-notify", durable=True)
