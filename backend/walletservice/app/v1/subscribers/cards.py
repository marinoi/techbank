import os
import uuid

from sqlalchemy.exc import SQLAlchemyError

from ..common.broker.queues import WalletQueues, CardQueues, NotificationQueues
from ..common.broker.rabbitmq import rabbitmq
from ..common.db.models import OutBoxEvent
from ..common.db.orm import async_session
from ..common.inbox.utils import inbox_based_idempotency
from ..common.schemas.enums import CardRechargeFailedReason, WalletRefundFailedReason, CardToWalletPaymentFailedReason
from ..common.schemas.events import (WalletRefundEvent,
                                     CardRechargeEvent,
                                     CardRechargeResponseEvent,
                                     WalletRefundResponseEvent,
                                     NotificationEvent,
                                     CardToWalletPaymentEvent,
                                     CardToWalletPaymentResponseEvent,
                                     WalletToCardPaymentResponseEvent)
from ..models.models import Wallet


def crate_wallet_refund_response_event(data: WalletRefundEvent,
                                       wallet: Wallet | None = None,
                                       failed_reason: WalletRefundFailedReason | None = None) -> WalletRefundResponseEvent:
    return WalletRefundResponseEvent(event_id=data.event_id,
                                     card_id=data.card_id,
                                     user_id=data.user_id,
                                     wallet_id=wallet.id if wallet else None,
                                     amount=data.amount,
                                     reason=data.reason,
                                     failed=bool(failed_reason),
                                     failed_reason=failed_reason)


def create_card_recharge_response_event(data: CardRechargeEvent,
                                        wallet: Wallet | None = None,
                                        failed_reason: CardRechargeFailedReason | None = None) -> CardRechargeResponseEvent:
    return CardRechargeResponseEvent(event_id=data.event_id,
                                     card_id=data.card_id,
                                     user_id=data.user_id,
                                     wallet_id=wallet.id if wallet else None,
                                     amount=data.amount,
                                     failed=bool(failed_reason),
                                     failed_reason=failed_reason)


def create_card_to_wallet_payment_response_event(data: CardToWalletPaymentEvent,
                                                 wallet: Wallet | None = None,
                                                 failed_reason: CardToWalletPaymentFailedReason | None = None) -> CardToWalletPaymentResponseEvent:
    return CardToWalletPaymentResponseEvent(event_id=data.event_id,
                                            source_user_id=data.source_user_id,
                                            source_card_id=data.source_card_id,
                                            source_user_name=data.source_user_name,
                                            source_user_surname=data.source_user_surname,
                                            destination_wallet_id=data.destination_wallet_id,
                                            counterparty_user_id=wallet.user_id if wallet else None,
                                            counterparty_user_name=wallet.user.name if wallet else None,
                                            counterparty_user_surname=wallet.user.surname if wallet else None,
                                            amount=data.amount,
                                            description=data.description,
                                            failed=bool(failed_reason),
                                            failed_reason=failed_reason)


@rabbitmq.subscriber(queue=WalletQueues.CARD_REFUND.value)
@inbox_based_idempotency(queue=WalletQueues.CARD_REFUND.value.name)
async def wallet_refund(data: WalletRefundEvent):
    try:
        async with async_session() as session:
            async with session.begin():
                wallet = await Wallet.get_by_user_id(session, data.user_id, load_user=True, for_update=True)

                event = None

                if not wallet:
                    event = crate_wallet_refund_response_event(data, failed_reason=WalletRefundFailedReason.WALLET_NOT_FOUND)

                elif not wallet.is_active:
                    event = crate_wallet_refund_response_event(data, failed_reason=WalletRefundFailedReason.WALLET_IS_BLOCKED)

                if event is not None:
                    outbox_event = OutBoxEvent(payload=event.model_dump_json(),
                                               event_id=event.event_id,
                                               queue=CardQueues.CARD_REFUND_RESPONSE.value.name)

                    await outbox_event.save(session, commit=False)

                else:
                    transaction = wallet.card_refund(card_id=data.card_id, amount=data.amount, reason=data.reason)

                    event = crate_wallet_refund_response_event(data, wallet)
                    outbox_event = OutBoxEvent(payload=event.model_dump_json(),
                                               event_id=event.event_id,
                                               queue=CardQueues.CARD_REFUND_RESPONSE.value.name)

                    await transaction.save(session, commit=False)
                    await outbox_event.save(session, commit=False)

    except SQLAlchemyError:
        #todo: database error handling
        raise


@rabbitmq.subscriber(queue=WalletQueues.CARD_RECHARGE.value)
@inbox_based_idempotency(queue=WalletQueues.CARD_RECHARGE.value.name)
async def wallet_card_recharge(data: CardRechargeEvent):
    try:
        async with async_session() as session:
            async with session.begin():
                wallet = await Wallet.get_by_user_id(session, data.user_id, load_user=True, for_update=True)

                event = None

                if not wallet:
                    event = create_card_recharge_response_event(data, failed_reason=CardRechargeFailedReason.WALLET_NOT_FOUND)

                elif not wallet.is_active:
                    event = create_card_recharge_response_event(data, failed_reason=CardRechargeFailedReason.WALLET_IS_BLOCKED)

                elif wallet.amount - data.amount < 0:
                    event = create_card_recharge_response_event(data, failed_reason=CardRechargeFailedReason.NO_ENOUGH_FUNDS)


                if event is not None:
                    outbox_event = OutBoxEvent(payload=event.model_dump_json(),
                                               event_id=event.event_id,
                                               queue=CardQueues.CARD_RECHARGE_RESPONSE.value.name)

                    await outbox_event.save(session, commit=False)

                else:
                    transaction = wallet.card_recharge(card_id=data.card_id, amount=data.amount)

                    event = create_card_recharge_response_event(data, wallet)
                    outbox_event = OutBoxEvent(event_id=data.event_id,
                                               payload=event.model_dump_json(),
                                               queue=CardQueues.CARD_RECHARGE_RESPONSE.value.name)

                    await transaction.save(session, commit=False)
                    await outbox_event.save(session, commit=False)

    except SQLAlchemyError:
        #todo: database error handling
        raise


@rabbitmq.subscriber(queue=WalletQueues.CARD_TO_WALLET_PAYMENT.value)
@inbox_based_idempotency(queue=WalletQueues.CARD_TO_WALLET_PAYMENT.value.name)
async def card_to_wallet_payment(data: CardToWalletPaymentEvent):
    try:
        async with async_session() as session:
            async with session.begin():
                wallet = await Wallet.get_by_id(session, data.destination_wallet_id, load_user=True, for_update=True)

                event = None

                if not wallet:
                    event = create_card_to_wallet_payment_response_event(data,
                                                                         failed_reason=CardToWalletPaymentFailedReason.WALLET_NOT_FOUND)
                elif not wallet.is_active:
                    event = create_card_to_wallet_payment_response_event(data,
                                                                         failed_reason=CardToWalletPaymentFailedReason.WALLET_IS_BLOCKED)

                if event is not None:
                    outbox_event = OutBoxEvent(payload=event.model_dump_json(),
                                               event_id=event.event_id,
                                               queue=CardQueues.CARD_TO_WALLET_PAYMENT_RESPONSE.value.name)

                    await outbox_event.save(session, commit=False)

                else:
                    transaction = wallet.payment_from_card(source_user_name=data.source_user_name,
                                                           source_user_surname=data.source_user_surname,
                                                           source_card_id=data.source_card_id,
                                                           amount=data.amount,
                                                           description=data.description)

                    event = create_card_to_wallet_payment_response_event(data, wallet)
                    outbox_event = OutBoxEvent(payload=event.model_dump_json(),
                                               event_id=event.event_id,
                                               queue=CardQueues.CARD_TO_WALLET_PAYMENT_RESPONSE.value.name)

                    await transaction.save(session, commit=False)
                    await outbox_event.save(session, commit=False)

    except SQLAlchemyError:
        #todo: database error handling
        raise


@rabbitmq.subscriber(queue=WalletQueues.WALLET_TO_CARD_PAYMENT_RESPONSE.value)
@inbox_based_idempotency(queue=WalletQueues.WALLET_TO_CARD_PAYMENT_RESPONSE.value.name)
async def wallet_to_card_payment_response(data: WalletToCardPaymentResponseEvent):
    try:
        async with async_session() as session:
            async with session.begin():
                wallet = await Wallet.get_by_id(session, data.source_wallet_id, load_user=True, for_update=True)

                if data.failed:
                    event = NotificationEvent(event_id=uuid.uuid4(),
                                              source_event_id=data.event_id,
                                              user_id=data.source_user_id,
                                              emitter=os.environ["SERVICE_NAME"],
                                              reason=data.failed_reason,
                                              message=f"Payment error from wallet {data.source_wallet_id} to card {data.destination_card_id}.")

                    outbox_event = OutBoxEvent(payload=event.model_dump_json(),
                                               event_id=event.event_id,
                                               queue=NotificationQueues.NOTIFY.value.name)

                    await outbox_event.save(session, commit=False)

                else:
                    transaction = wallet.payment_to_card(counterparty_user_name=data.counterparty_user_name,
                                                         counterparty_user_surname=data.counterparty_user_surname,
                                                         counterparty_card_id=data.destination_card_id,
                                                         amount=data.amount,
                                                         description=data.description)

                    await transaction.save(session, commit=False)

    except SQLAlchemyError:
        #todo: database error handling
        raise
