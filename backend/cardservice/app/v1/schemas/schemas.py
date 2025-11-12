from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, UUID4, ConfigDict, model_validator, condecimal

from ..common.schemas.dbentity import HasID, HasCreatedAt, HasUpdatedAt
from ..models.enums import CardTransactionType, CardTransactionDirection, CardUsagePolicy


class CardOut(HasID):
    user_id: UUID4
    amount: Decimal
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class NewCardIn(BaseModel):
    amount: Annotated[Decimal, condecimal(gt=0, max_digits=12, decimal_places=2)] = Decimal("0")
    policy: list[CardUsagePolicy] = [CardUsagePolicy.STANDARD]
    amount_limit: Annotated[Decimal, condecimal(gt=0, max_digits=12, decimal_places=2)] | None = None

    @classmethod
    @model_validator(mode="after")
    def check_policy_rules(cls, model: "NewCardIn") -> "NewCardIn":
        print("Calling check policy_rules")
        if CardUsagePolicy.AMOUNT_LIMITED in model.policy:
            if model.amount_limit is None:
                raise ValueError("amount-limit-is-empty")
            if model.amount_limit < model.amount:
                raise ValueError("amount-limit-overflow")
        return model


class CardRechargeIn(BaseModel):
    amount: Annotated[Decimal, condecimal(gt=0, max_digits=12, decimal_places=2)]

class TransactionOut(HasID, HasCreatedAt):
    amount: Decimal
    direction: CardTransactionDirection

    model_config = ConfigDict(from_attributes=True)


class TransactionDetailsOut(TransactionOut):
    card_id: UUID4
    counterparty_instrument_id: UUID4
    counterparty_name: str
    counterparty_surname: str
    type: CardTransactionType
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PaymentRequestIn(BaseModel):
    amount: Annotated[Decimal, condecimal(gt=0, max_digits=12, decimal_places=2)]
    counterparty_instrument_id: UUID4
    transaction_type: CardTransactionType
    description: str


class CardDetailsOut(CardOut, HasCreatedAt, HasUpdatedAt):
    policy: list[CardUsagePolicy]
    amount_limit: Decimal | None = None
    model_config = ConfigDict(from_attributes=True)
