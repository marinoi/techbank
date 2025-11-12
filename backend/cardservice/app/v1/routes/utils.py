import uuid
from decimal import Decimal

from starlette import status
from starlette.exceptions import HTTPException

from ..models.models import Card, CardTransaction


def card_exists_or_404(card: Card | None, detail: str = "card-not-found"):
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=detail)


def card_ownership_or_404(card: Card, user_id: uuid.UUID, detail: str = "card-not-found"):
    if card.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=detail)


def card_is_active_or_403(card: Card, detail: str ="card-is-blocked"):
    if not card.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=detail)


def card_has_enough_funds_or_409(card: Card, amount: Decimal, detail: str ="no-enough-funds"):
    if card.amount < amount:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=detail)


def transaction_exists_or_404(transaction: CardTransaction | None, detail: str = "transaction-not-found"):
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=detail)


def transaction_ownership_or_404(transaction: CardTransaction, card: Card, detail: str = "transaction-not-found"):
    if card.id != transaction.card_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=detail)
