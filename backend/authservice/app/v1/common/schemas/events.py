from decimal import Decimal

from pydantic import UUID4, BaseModel

from .dbentity import HasEventID
from .enums import (CardRechargeFailedReason,
                    WalletRefundReason,
                    WalletRefundFailedReason,
                    WalletToCardPaymentFailedReason,
                    CardToWalletPaymentFailedReason)

# SYSTEM CONSISTENCY EVENTS
class UserCreatedEvent(HasEventID):
    user_id: UUID4
    name: str
    surname: str

class TokenRevokedEvent(HasEventID):
    jti: UUID4

class UserDeletedEvent(HasEventID):
    user_id: UUID4


# REFUND
class WalletRefundEvent(HasEventID):
    card_id: UUID4
    user_id: UUID4
    amount: Decimal
    reason: WalletRefundReason

class WalletRefundResponseEvent(WalletRefundEvent):
    wallet_id: UUID4 | None = None
    failed: bool
    failed_reason: WalletRefundFailedReason | None = None


# RECHARGE
class CardRechargeEvent(HasEventID):
    card_id: UUID4
    user_id: UUID4
    amount: Decimal

class CardRechargeResponseEvent(CardRechargeEvent):
    wallet_id: UUID4 | None = None
    failed: bool
    failed_reason: CardRechargeFailedReason | None = None


# MIXIN FOR THE PAYMENT REQUEST/RESPONSE BETWEEN WALLET AND CARD EVENTS
class _PaymentMixinResponse(BaseModel):
    counterparty_user_id: UUID4 | None = None
    counterparty_user_name: str | None = None
    counterparty_user_surname: str | None = None
    failed: bool

class _PaymentMixinSourceUser(BaseModel):
    source_user_id: UUID4
    source_user_name: str
    source_user_surname: str


# WALLET TO CARD PAYMENT EVENTS
class WalletToCardPaymentEvent(HasEventID, _PaymentMixinSourceUser):
    source_wallet_id: UUID4
    destination_card_id: UUID4
    amount: Decimal
    description: str | None = None

class WalletToCardPaymentResponseEvent(WalletToCardPaymentEvent, _PaymentMixinResponse):
    failed_reason: WalletToCardPaymentFailedReason | None = None


# CARD TO WALLET PAYMENT EVENTS
class CardToWalletPaymentEvent(HasEventID, _PaymentMixinSourceUser):
    source_card_id: UUID4
    destination_wallet_id: UUID4
    amount: Decimal
    description: str | None = None

class CardToWalletPaymentResponseEvent(CardToWalletPaymentEvent, _PaymentMixinResponse):
    failed_reason: CardToWalletPaymentFailedReason | None = None


# NOTIFICATION
class NotificationEvent(HasEventID):
    user_id: UUID4
    source_event_id: UUID4 | None
    emitter: str
    reason: str
    message: str