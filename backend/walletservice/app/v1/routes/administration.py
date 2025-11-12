import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from .utils import wallet_exists_or_404, transaction_exists_or_404, transaction_wallet_ownership_or_404
from ..common.db.orm import get_async_session
from ..common.security.router import RuledAPIRouter
from ..common.security.roles import Role

from .routes import AdminRoutes, ADMIN_ROUTER_PREFIX
from ..models.models import Wallet, WalletTransaction
from ..schemas.schemas import WalletOut, WalletDetailsOut, TransactionOut, TransactionDetailsOut

administration_api = RuledAPIRouter(prefix=ADMIN_ROUTER_PREFIX,
                                    tags=["administration"],
                                    allowed_roles=[Role.ADMIN])


@administration_api.get(AdminRoutes.WALLETS.value, response_model=list[WalletOut], status_code=status.HTTP_200_OK)
async def get_wallets(session: AsyncSession = Depends(get_async_session)):
    wallets = await Wallet.get_all(session)
    return wallets


@administration_api.get(AdminRoutes.WALLET.value, response_model=WalletOut, status_code=status.HTTP_200_OK)
async def get_wallet(user_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    wallet = await Wallet.get_by_user_id(session, user_id)
    wallet_exists_or_404(wallet)

    return wallet


@administration_api.get(AdminRoutes.WALLET_DETAILS.value, response_model=WalletDetailsOut, status_code=status.HTTP_200_OK)
async def get_wallet_details(wallet_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    wallet = await Wallet.get_by_id(session, wallet_id)
    wallet_exists_or_404(wallet)

    return wallet


@administration_api.get(AdminRoutes.WALLET_TRANSACTIONS.value, response_model=list[TransactionOut], status_code=status.HTTP_200_OK)
async def get_transactions(wallet_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    wallet = await Wallet.get_by_id(session, wallet_id, load_transactions=True)
    wallet_exists_or_404(wallet)

    return wallet.transactions


@administration_api.get(AdminRoutes.TRANSACTION_DETAILS.value, response_model=TransactionDetailsOut, status_code=status.HTTP_200_OK)
async def get_transaction_details(wallet_id: uuid.UUID, transaction_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    wallet = await Wallet.get_by_id(session, wallet_id)
    wallet_exists_or_404(wallet)

    transaction =  await WalletTransaction.get_by_id(session, transaction_id)
    transaction_exists_or_404(transaction)
    transaction_wallet_ownership_or_404(transaction, wallet)

    return transaction


@administration_api.patch(AdminRoutes.BLOCK_WALLET.value, status_code=status.HTTP_200_OK)
async def patch_block_wallet(wallet_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    async with session.begin():
        wallet = await Wallet.get_by_id(session, wallet_id, for_update=True)
        wallet_exists_or_404(wallet)

        wallet.is_active = False

    return {"detail": "wallet-blocked-successfully"}


@administration_api.patch(AdminRoutes.UNBLOCK_WALLET.value, status_code=status.HTTP_200_OK)
async def patch_unblock_wallet(wallet_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    async with session.begin():
        wallet = await Wallet.get_by_id(session, wallet_id, for_update=True)
        wallet_exists_or_404(wallet)

        wallet.is_active = True

    return {"detail": "wallet-unblocked-successfully"}

