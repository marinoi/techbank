import uuid

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request

from .routes import PrivateRoutes, PRIVATE_ROUTER_PREFIX
from .utils import card_exists_or_404, card_ownership_or_404, transaction_exists_or_404, transaction_ownership_or_404, \
    card_is_active_or_403, card_has_enough_funds_or_409
from ..common.broker.queues import WalletQueues
from ..common.db.models import OutBoxEvent
from ..common.db.orm import get_async_session
from ..common.schemas.enums import WalletRefundReason
from ..common.schemas.events import CardRechargeEvent, WalletRefundEvent, CardToWalletPaymentEvent
from ..common.schemas.token import JWTPayload
from ..common.security.roles import Role
from ..common.security.router import RuledAPIRouter
from ..models.enums import CardTransactionType, CardUsagePolicy
from ..models.models import Card, CardTransaction, UserRef
from ..schemas.schemas import (CardOut,
                               TransactionOut,
                               TransactionDetailsOut,
                               PaymentRequestIn,
                               CardDetailsOut,
                               NewCardIn,
                               CardRechargeIn)


private_api = RuledAPIRouter(prefix=PRIVATE_ROUTER_PREFIX,
                             tags=["private"],
                             allowed_roles=[Role.USER])


@private_api.get(PrivateRoutes.CARDS.value, response_model=list[CardOut], status_code=status.HTTP_200_OK)
async def get_cards(request: Request, session: AsyncSession = Depends(get_async_session)):
    jwt: JWTPayload = request.state.jwt

    cards = await Card.get_by_user_id(session, jwt.sub, only_active=True)

    return cards


@private_api.get(PrivateRoutes.CARD.value, response_model=CardDetailsOut, status_code=status.HTTP_200_OK)
async def get_card(card_id: uuid.UUID, request: Request, session: AsyncSession = Depends(get_async_session)):
    jwt: JWTPayload = request.state.jwt

    card = await Card.get_by_id(session, card_id)

    card_exists_or_404(card)
    card_ownership_or_404(card, jwt.sub)

    return card


@private_api.get(PrivateRoutes.TRANSACTIONS.value, response_model=list[TransactionOut], status_code=status.HTTP_200_OK)
async def get_card_transactions(card_id: uuid.UUID,
                                request: Request,
                                session: AsyncSession = Depends(get_async_session)):
    jwt: JWTPayload = request.state.jwt

    card = await Card.get_by_id(session, card_id, load_transactions=True)

    card_exists_or_404(card)
    card_ownership_or_404(card, jwt.sub)

    return card.transactions


@private_api.get(PrivateRoutes.TRANSACTION.value, response_model=TransactionDetailsOut, status_code=status.HTTP_200_OK)
async def get_transaction_details(card_id: uuid.UUID,
                                  transaction_id: uuid.UUID,
                                  request: Request,
                                  session: AsyncSession = Depends(get_async_session)):
    jwt: JWTPayload = request.state.jwt

    transaction = await CardTransaction.get_by_id(session, transaction_id)
    card = await Card.get_by_id(session, card_id)

    card_exists_or_404(card)
    card_ownership_or_404(card, jwt.sub)
    transaction_exists_or_404(transaction)
    transaction_ownership_or_404(transaction, card)

    return transaction


@private_api.post(PrivateRoutes.NEW_CARD.value, status_code=status.HTTP_201_CREATED)
async def post_new_card(payload: NewCardIn, request: Request, session: AsyncSession = Depends(get_async_session)):
    jwt: JWTPayload = request.state.jwt

    async with session.begin():
        user = await UserRef.get_by_id(session, jwt.sub)
        new_card = Card(id=uuid.uuid4(),
                        user=user,
                        policy=payload.policy,
                        amount_limit=payload.amount_limit)

        if payload.amount > 0:
            if CardUsagePolicy.AMOUNT_LIMITED in payload.policy and payload.amount > payload.amount_limit:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail="card-limit-future-overflow")

            event = CardRechargeEvent(event_id=uuid.uuid4(),
                                      card_id=new_card.id,
                                      user_id=user.id,
                                      amount=payload.amount)

            outbox_event = OutBoxEvent(event_id=event.event_id,
                                       queue=WalletQueues.CARD_RECHARGE.value.name,
                                       payload=event.model_dump_json())

            await outbox_event.save(session, commit=False)

        await new_card.save(session, commit=False)

    return {"detail": "new-card-request-created"}


@private_api.post(PrivateRoutes.CARD_RECHARGE.value, status_code=status.HTTP_201_CREATED)
async def post_card_recharge(card_id: uuid.UUID,
                             payload: CardRechargeIn,
                             request: Request,
                             session: AsyncSession = Depends(get_async_session)):
    jwt: JWTPayload = request.state.jwt

    async with session.begin():
        user = await UserRef.get_by_id(session, jwt.sub)
        card = await Card.get_by_id(session, card_id)

        card_exists_or_404(card)
        card_ownership_or_404(card, jwt.sub)
        card_is_active_or_403(card)

        if CardUsagePolicy.AMOUNT_LIMITED in card.policy:
            if payload.amount + card.amount > card.amount_limit:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail="card-limit-future-overflow")

        event = CardRechargeEvent(event_id=uuid.uuid4(),
                                  card_id=card.id,
                                  user_id=user.id,
                                  amount=payload.amount)

        outbox_event = OutBoxEvent(event_id=event.event_id,
                                   queue=WalletQueues.CARD_RECHARGE.value.name,
                                   payload=event.model_dump_json())

        await outbox_event.save(session, commit=False)

    return {"detail": "recharge-request-created"}


@private_api.patch(PrivateRoutes.DISMISS_CARD.value, status_code=status.HTTP_200_OK)
async def patch_dismiss_card(card_id: uuid.UUID, request: Request, session: AsyncSession = Depends(get_async_session)):
    jwt: JWTPayload = request.state.jwt

    async with session.begin():
        card = await Card.get_by_id(session, card_id, for_update=True)

        card_exists_or_404(card)
        card_ownership_or_404(card, jwt.sub)
        card_is_active_or_403(card)

        if card.amount > 0:
            event = WalletRefundEvent(event_id=uuid.uuid4(),
                                      card_id=card.id,
                                      user_id=jwt.sub,
                                      amount=card.amount,
                                      reason=WalletRefundReason.CARD_DISMISSED)

            outbox_event = OutBoxEvent(event_id=event.event_id,
                                       queue=WalletQueues.CARD_REFUND.value.name,
                                       payload=event.model_dump_json())

            await outbox_event.save(session, commit=False)

        card.is_active = False

    return {"detail": "card-dismissed"}


@private_api.post(PrivateRoutes.PAYMENT.value)
async def post_card_payment(card_id: uuid.UUID,
                            payload: PaymentRequestIn,
                            request: Request,
                            session: AsyncSession = Depends(get_async_session)):
    jwt: JWTPayload = request.state.jwt

    async with session.begin():
        user_card = await Card.get_by_id(session, card_id, load_user=True, for_update=True)

        card_exists_or_404(user_card)
        card_ownership_or_404(user_card, jwt.sub)
        card_is_active_or_403(user_card)
        card_has_enough_funds_or_409(user_card, payload.amount)

        if payload.transaction_type == CardTransactionType.CARD_TO_CARD:
            counterparty_card = await Card.get_by_id(session, payload.counterparty_instrument_id, load_user=True, for_update=True)

            card_exists_or_404(counterparty_card, detail="counterparty-card-not-found")

            if CardUsagePolicy.AMOUNT_LIMITED in counterparty_card.policy:
                if counterparty_card.amount + payload.amount > counterparty_card.amount_limit:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                        detail="counterparty-card-limit-overflow")

            user_transaction, counterparty_transaction = user_card.make_payment_to_card(counterparty_card=counterparty_card,
                                                                                        amount=payload.amount,
                                                                                        description=payload.description)

            await user_transaction.save(session, commit=False)
            await counterparty_transaction.save(session, commit=False)

            return {"detail": "payment-completed"}

        elif payload.transaction_type == CardTransactionType.CARD_TO_WALLET:
            event = CardToWalletPaymentEvent(event_id=uuid.uuid4(),
                                             source_card_id=user_card.id,
                                             source_user_id=user_card.user_id,
                                             source_user_name=user_card.user.name,
                                             source_user_surname=user_card.user.surname,
                                             destination_wallet_id=payload.counterparty_instrument_id,
                                             amount=payload.amount,
                                             description=payload.description)

            outbox_event = OutBoxEvent(event_id=event.event_id,
                                       queue=WalletQueues.CARD_TO_WALLET_PAYMENT.value.name,
                                       payload=event.model_dump_json())

            await outbox_event.save(session, commit=False)

            return {"detail": "payment-request-created"}

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="transaction-type-not-supported")
