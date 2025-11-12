import enum


# RECHARGE
class CardRechargeFailedReason(str, enum.Enum):
    NO_ENOUGH_FUNDS = "no-enough-funds"
    WALLET_NOT_FOUND = "wallet-not-found"
    WALLET_IS_BLOCKED = "wallet-is-blocked"


# REFUND
class WalletRefundReason(str, enum.Enum):
    CARD_DISMISSED = "card-dismissed"

class WalletRefundFailedReason(str, enum.Enum):
    WALLET_NOT_FOUND = "wallet-not-found"
    WALLET_IS_BLOCKED = "wallet-is-blocked"


# WALLET TO CARD PAYMENT ENUMS
class WalletToCardPaymentFailedReason(str, enum.Enum):
    CARD_NOT_FOUND = "card-not-found"
    CARD_IS_BLOCKED = "card-is-blocked"
    CARD_POLICY_VIOLATED = "card-policy-violated"


# CARD TO WALLET PAYMENT ENUMS
class CardToWalletPaymentFailedReason(str, enum.Enum):
    WALLET_NOT_FOUND = "wallet-not-found"
    WALLET_IS_BLOCKED = "wallet-is-blocked"

