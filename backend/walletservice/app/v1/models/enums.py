import enum



class WalletTransactionDirection(str, enum.Enum):
    TRANSFER_IN  = "transfer-in"
    TRANSFER_OUT = "transfer-out"


class WalletTransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    CARD_RECHARGE = "card-recharge"
    CARD_REFUND = "card-refund"
    CARD_TO_WALLET = "card-to-wallet"
    WALLET_TO_CARD = "wallet-to-card"
    WALLET_TO_WALLET = "wallet-to-wallet"
