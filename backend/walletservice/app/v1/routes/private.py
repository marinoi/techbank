import uuid

from fastapi.params import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request

from .utils import (wallet_exists_or_404,
                    transaction_exists_or_404,
                    transaction_ownership_or_404,
                    wallet_has_enough_funds_or_409,
                    wallet_is_active_or_403)
from ..common.broker.queues import CardQueues
from ..common.db.models import OutBoxEvent
from ..common.db.orm import get_async_session
from ..common.schemas.events import WalletToCardPaymentEvent
from ..common.schemas.token import JWTPayload
from ..common.security.router import RuledAPIRouter
from ..common.security.roles import Role

from .routes import PrivateRoutes, PRIVATE_ROUTER_PREFIX
from ..models.enums import WalletTransactionType
from ..models.models import Wallet, WalletTransaction
from ..schemas.schemas import WalletOut, TransactionOut, TransactionDetailsOut, DepositIn, PaymentRequestIn


private_api = RuledAPIRouter(prefix=PRIVATE_ROUTER_PREFIX,
                             tags=["private"],
                             allowed_roles=[Role.USER])


@private_api.get(PrivateRoutes.WALLET.value, response_model=WalletOut, status_code=status.HTTP_200_OK)
async def get_wallet(request: Request, session: AsyncSession = Depends(get_async_session)):
    jwt: JWTPayload = request.state.jwt

    wallet = await Wallet.get_by_user_id(session, jwt.sub)
    wallet_exists_or_404(wallet)

    return wallet


@private_api.get(PrivateRoutes.TRANSACTIONS.value, response_model=list[TransactionOut], status_code=status.HTTP_200_OK)
async def get_wallet_transactions(request: Request, session: AsyncSession = Depends(get_async_session)):
    jwt: JWTPayload = request.state.jwt

    wallet = await Wallet.get_by_user_id(session, jwt.sub, load_transactions=True)
    wallet_exists_or_404(wallet)

    return wallet.transactions


@private_api.get(PrivateRoutes.TRANSACTION.value, response_model=TransactionDetailsOut, status_code=status.HTTP_200_OK)
async def get_transaction_details(transaction_id: uuid.UUID, request: Request, session: AsyncSession = Depends(get_async_session)):
    jwt: JWTPayload = request.state.jwt

    transaction = await WalletTransaction.get_by_id(session, transaction_id, load_wallet=True)
    transaction_exists_or_404(transaction)
    transaction_ownership_or_404(transaction, jwt.sub)

    return transaction


@private_api.post(PrivateRoutes.DEPOSIT.value, status_code=status.HTTP_200_OK)
async def post_deposit_to_wallet(deposit: DepositIn, request: Request, session: AsyncSession = Depends(get_async_session)):
    jwt: JWTPayload = request.state.jwt

    async with session.begin():
        wallet = await Wallet.get_by_user_id(session, jwt.sub, load_user=True, for_update=True)
        wallet_exists_or_404(wallet)
        wallet_is_active_or_403(wallet)

        try:
            new_transaction = wallet.deposit(deposit.amount)
            await new_transaction.save(session, commit=False)

        except SQLAlchemyError as e:
            # todo: remove print
            print(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="db-deposit-exception")


@private_api.post(PrivateRoutes.PAYMENT.value, status_code=status.HTTP_200_OK)
async def post_wallet_payment(payment: PaymentRequestIn, request: Request, session: AsyncSession = Depends(get_async_session)):
    jwt: JWTPayload = request.state.jwt

    async with session.begin():
        user_wallet = await Wallet.get_by_user_id(session, jwt.sub, load_user=True, for_update=True)
        wallet_exists_or_404(user_wallet)
        wallet_is_active_or_403(user_wallet)
        wallet_has_enough_funds_or_409(user_wallet, payment.amount)

        if payment.transaction_type == WalletTransactionType.WALLET_TO_WALLET:
            counterparty_wallet = await Wallet.get_by_id(session, payment.counterparty_instrument_id, load_user=True, for_update=True)
            wallet_exists_or_404(counterparty_wallet, detail="counterparty-wallet-not-found")
            wallet_is_active_or_403(counterparty_wallet, detail="counterparty-wallet-cannot-accept-payments")

            try:
                user_transaction, counterparty_transaction = user_wallet.make_payment_to_wallet(counterparty_wallet=counterparty_wallet,
                                                                                                amount=payment.amount,
                                                                                                description=payment.description)
                await user_transaction.save(session, commit=False)
                await counterparty_transaction.save(session, commit=False)

                return {"response": "transfer-completed"}

            except SQLAlchemyError:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail="db-wallet-to-wallet-exception")

        elif payment.transaction_type == WalletTransactionType.WALLET_TO_CARD:
            try:
                event = WalletToCardPaymentEvent(event_id=uuid.uuid4(),
                                                 source_wallet_id=user_wallet.id,
                                                 source_user_id=user_wallet.user_id,
                                                 source_user_name=user_wallet.user.name,
                                                 source_user_surname=user_wallet.user.surname,
                                                 destination_card_id=payment.counterparty_instrument_id,
                                                 amount=payment.amount,
                                                 description=payment.description)

                outbox_event = OutBoxEvent(event_id=event.event_id,
                                           queue=CardQueues.WALLET_TO_CARD_PAYMENT.value.name,
                                           payload=event.model_dump_json())

                await outbox_event.save(session, commit=False)

            except SQLAlchemyError:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail="db-wallet-to-wallet-exception")

            return {"response": "payment-sent-to-card"}

        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="transaction-type-not-supported")
