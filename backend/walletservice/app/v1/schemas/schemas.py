from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, UUID4, ConfigDict, condecimal

from app.v1.common.schemas.dbentity import HasID, HasCreatedAt, HasUpdatedAt
from app.v1.models.enums import WalletTransactionType, WalletTransactionDirection


class WalletOut(HasID):
    user_id: UUID4
    amount: Decimal

    model_config = ConfigDict(from_attributes=True)


class TransactionOut(HasID, HasCreatedAt):
    counterparty_instrument_id: UUID4
    amount: Decimal
    direction: WalletTransactionDirection

    model_config = ConfigDict(from_attributes=True)


class TransactionDetailsOut(TransactionOut):
    wallet_id: UUID4
    counterparty_name: str
    counterparty_surname: str
    type: WalletTransactionType
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class DepositIn(BaseModel):
    amount: Annotated[Decimal, condecimal(gt=0, max_digits=12, decimal_places=2)]


class PaymentRequestIn(BaseModel):
    amount: Annotated[Decimal, condecimal(gt=0, max_digits=12, decimal_places=2)]
    counterparty_instrument_id: UUID4
    transaction_type: WalletTransactionType
    description: str


class WalletDetailsOut(WalletOut, HasCreatedAt, HasUpdatedAt):
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
