import os
import uuid

from sqlalchemy.exc import SQLAlchemyError

from ..common.broker.queues import WalletQueues, CardQueues, NotificationQueues
from ..common.broker.rabbitmq import rabbitmq
from ..common.db.models import OutBoxEvent
from ..common.db.orm import async_session
from ..common.inbox.utils import inbox_based_idempotency
from ..common.schemas.enums import WalletToCardPaymentFailedReason
from ..common.schemas.events import (CardRechargeResponseEvent,
                                     NotificationEvent,
                                     CardToWalletPaymentResponseEvent,
                                     WalletToCardPaymentResponseEvent,
                                     WalletRefundResponseEvent,
                                     WalletToCardPaymentEvent,
                                     CardToWalletPaymentEvent)
from ..models.enums import CardUsagePolicy
from ..models.models import Card


@rabbitmq.subscriber(CardQueues.CARD_REFUND_RESPONSE.value)
@inbox_based_idempotency(CardQueues.CARD_REFUND_RESPONSE.value.name)
async def card_refund_response(data: WalletRefundResponseEvent):
    try:
        async with async_session() as session:
            async with session.begin():
                card = await Card.get_by_id(session, data.card_id, load_user=True, for_update=True)

                if data.failed:
                    event = NotificationEvent(event_id=uuid.uuid4(),
                                              source_event_id=data.event_id,
                                              user_id=data.user_id,
                                              emitter=os.environ["SERVICE_NAME"],
                                              reason=data.failed_reason,
                                              message=f"Refund error, the card can't refund on the wallet.")

                    outbox_event = OutBoxEvent(payload=event.model_dump_json(),
                                               event_id=event.event_id,
                                               queue=NotificationQueues.NOTIFY.value.name)

                    card.is_active = True
                    await outbox_event.save(session, commit=False)

                else:
                    transaction = card.card_refund(wallet_id=data.wallet_id,
                                                   amount=data.amount,
                                                   reason=data.reason)
                    await transaction.save(session, commit=False)

    except SQLAlchemyError:
        # todo: database error handling
        raise


@rabbitmq.subscriber(CardQueues.CARD_RECHARGE_RESPONSE.value)
@inbox_based_idempotency(CardQueues.CARD_RECHARGE_RESPONSE.value.name)
async def card_recharge_response(data: CardRechargeResponseEvent):
    try:
        async with async_session() as session:
            async with session.begin():
                card = await Card.get_by_id(session, data.card_id, load_user=True, for_update=True)

                if data.failed:
                    event = NotificationEvent(event_id=uuid.uuid4(),
                                              source_event_id=data.event_id,
                                              user_id=data.user_id,
                                              emitter=os.environ["SERVICE_NAME"],
                                              reason=data.failed_reason,
                                              message=f"Recharge error, the card can't be recharged from the wallet.")

                    outbox_event = OutBoxEvent(payload=event.model_dump_json(),
                                               event_id=event.event_id,
                                               queue=NotificationQueues.NOTIFY.value.name)

                    await outbox_event.save(session, commit=False)

                else:
                    transaction = card.card_recharge(wallet_id=data.wallet_id,
                                                     amount=data.amount)
                    await transaction.save(session, commit=False)

    except SQLAlchemyError:
        # todo: database error handling
        raise


@rabbitmq.subscriber(CardQueues.CARD_TO_WALLET_PAYMENT_RESPONSE.value)
@inbox_based_idempotency(CardQueues.CARD_TO_WALLET_PAYMENT_RESPONSE.value.name)
async def card_to_wallet_payment_response(data: CardToWalletPaymentResponseEvent):
    try:
        async with async_session() as session:
            async with session.begin():
                if data.failed:
                    event = NotificationEvent(event_id=uuid.uuid4(),
                                              source_event_id=data.event_id,
                                              user_id=data.source_user_id,
                                              emitter=os.environ["SERVICE_NAME"],
                                              reason=data.failed_reason,
                                              message=f"Payment error from card {data.source_card_id} to wallet {data.destination_wallet_id}")

                    outbox_event = OutBoxEvent(payload=event.model_dump_json(),
                                               event_id=event.event_id,
                                               queue=NotificationQueues.NOTIFY.value.name)

                    await outbox_event.save(session, commit=False)

                else:

                    card = await Card.get_by_id(session, data.source_card_id, load_user=True, for_update=True)
                    transaction = card.payment_to_wallet(counterparty_user_name=data.counterparty_user_name,
                                                         counterparty_user_surname=data.counterparty_user_surname,
                                                         counterparty_wallet_id=data.destination_wallet_id,
                                                         amount=data.amount,
                                                         description=data.description)

                    await transaction.save(session, commit=False)

    except SQLAlchemyError:
        # todo: database error handling
        raise


@rabbitmq.subscriber(CardQueues.WALLET_TO_CARD_PAYMENT.value)
@inbox_based_idempotency(CardQueues.WALLET_TO_CARD_PAYMENT.value.name)
async def wallet_to_card_payment(data: WalletToCardPaymentEvent):
    try:
        async with async_session() as session:
            async with session.begin():
                card = await Card.get_by_id(session, data.destination_card_id, load_user=True, for_update=True)

                event = None

                if card is None:
                    event = WalletToCardPaymentResponseEvent(event_id=data.event_id,
                                                             source_user_id=data.source_user_id,
                                                             source_wallet_id=data.source_wallet_id,
                                                             source_user_name=data.source_user_name,
                                                             source_user_surname=data.source_user_surname,
                                                             destination_card_id=data.destination_card_id,
                                                             amount=data.amount,
                                                             failed=True,
                                                             failed_reason=WalletToCardPaymentFailedReason.CARD_NOT_FOUND)

                elif not card.is_active:
                    event = WalletToCardPaymentResponseEvent(event_id=data.event_id,
                                                             source_user_id=data.source_user_id,
                                                             source_wallet_id=data.source_wallet_id,
                                                             source_user_name=data.source_user_name,
                                                             source_user_surname=data.source_user_surname,
                                                             destination_card_id=data.destination_card_id,
                                                             amount=data.amount,
                                                             failed=True,
                                                             failed_reason=WalletToCardPaymentFailedReason.CARD_IS_BLOCKED)

                elif CardUsagePolicy.AMOUNT_LIMITED in card.policy and card.amount + data.amount > card.amount_limit:
                    event = WalletToCardPaymentResponseEvent(event_id=data.event_id,
                                                             source_user_id=data.source_user_id,
                                                             source_wallet_id=data.source_wallet_id,
                                                             source_user_name=data.source_user_name,
                                                             source_user_surname=data.source_user_surname,
                                                             destination_card_id=data.destination_card_id,
                                                             amount=data.amount,
                                                             failed=True,
                                                             failed_reason=WalletToCardPaymentFailedReason.CARD_POLICY_VIOLATED)

                if event is not None:
                    outbox_event = OutBoxEvent(event_id=event.event_id,
                                               payload=event.model_dump_json(),
                                               queue=WalletQueues.WALLET_TO_CARD_PAYMENT_RESPONSE.value.name)

                    await outbox_event.save(session, commit=False)
                else:
                    transaction = card.payment_from_wallet(source_user_name=data.source_user_name,
                                                           source_user_surname=data.source_user_surname,
                                                           source_wallet_id=data.source_wallet_id,
                                                           amount=data.amount,
                                                           description=data.description)

                    event = WalletToCardPaymentResponseEvent(event_id=data.event_id,
                                                             source_user_id=data.source_user_id,
                                                             source_wallet_id=data.source_wallet_id,
                                                             source_user_name=data.source_user_name,
                                                             source_user_surname=data.source_user_surname,
                                                             destination_card_id=data.destination_card_id,
                                                             counterparty_user_id=card.user.id,
                                                             counterparty_user_name=card.user.name,
                                                             counterparty_user_surname=card.user.surname,
                                                             amount=data.amount,
                                                             failed=False)

                    outbox_event = OutBoxEvent(event_id=event.event_id,
                                               payload=event.model_dump_json(),
                                               queue=WalletQueues.WALLET_TO_CARD_PAYMENT_RESPONSE.value.name)

                    await outbox_event.save(session, commit=False)
                    await transaction.save(session, commit=False)

    except SQLAlchemyError:
        # todo: database error handling
        raise
