import enum


class CardTransactionDirection(str, enum.Enum):
    TRANSFER_IN  = "transfer-in"
    TRANSFER_OUT = "transfer-out"


class CardTransactionType(str, enum.Enum):
    CARD_RECHARGE = "card-recharge"
    CARD_REFUND = "card-refund"
    CARD_TO_WALLET = "card-to-wallet"
    WALLET_TO_CARD = "wallet-to-card"
    CARD_TO_CARD = "card-to-card"


class CardUsagePolicy(str, enum.Enum):
    STANDARD = "card-standard-policy"
    AMOUNT_LIMITED = "card-amount-limited-policy"
