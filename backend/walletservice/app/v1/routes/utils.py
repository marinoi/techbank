import uuid
from decimal import Decimal

from starlette import status
from starlette.exceptions import HTTPException

from ..models.models import Wallet, WalletTransaction


def wallet_exists_or_404(wallet: Wallet | None, detail: str ="wallet-not-found"):
    if wallet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=detail)


def wallet_is_active_or_403(wallet: Wallet, detail: str = "wallet-is-blocked"):
    if not wallet.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=detail)


def wallet_has_enough_funds_or_409(wallet: Wallet, amount: Decimal, detail: str = "no-enough-funds"):
    if wallet.amount < amount:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=detail)


def transaction_exists_or_404(transaction: WalletTransaction | None, detail: str = "transaction-not-found"):
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=detail)


def transaction_ownership_or_404(transaction: WalletTransaction, user_id: uuid.UUID, detail: str = "transaction-not-found"):
    if transaction.wallet.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=detail)


def transaction_wallet_ownership_or_404(transaction: WalletTransaction, wallet: Wallet, detail: str = "transaction-not-found"):
    if transaction.wallet.id != wallet.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=detail)

