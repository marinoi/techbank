from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import String, Float, ForeignKey, Boolean, Enum, select, ARRAY, Numeric, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, selectinload, Mapped, mapped_column

from .enums import CardTransactionType, CardTransactionDirection, CardUsagePolicy
from ..common.db.models import BaseExt
from ..common.schemas.enums import WalletRefundReason


class UserRef(BaseExt):
    __tablename__ = "users_ref"
    name: Mapped[str] = mapped_column(String)
    surname: Mapped[str] = mapped_column(String)

    cards: Mapped[list[Card]] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=True)


class Card(BaseExt):
    __tablename__ = "cards"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users_ref.id"), nullable=False)
    user: Mapped[UserRef] = relationship(back_populates="cards")

    amount: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False, default=0)
    policy: Mapped[list[CardUsagePolicy]] = mapped_column(ARRAY(Enum(CardUsagePolicy, name="card_usage_policy")), nullable=False, default=[CardUsagePolicy.STANDARD])
    amount_limit: Mapped[Decimal | None] = mapped_column(Numeric(precision=12, scale=2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    transactions: Mapped[list[CardTransaction]] = relationship(back_populates="card", cascade="all, delete-orphan")

    @classmethod
    async def get_by_user_id(cls,
                             session: AsyncSession,
                             user_id: uuid.UUID,
                             load_transactions: bool = False,
                             load_user: bool = False,
                             only_active: bool = False,
                             for_update: bool = False) -> list[Card]:
        loading_options = []
        if load_transactions:
            loading_options.append(selectinload(cls.transactions))
        if load_user:
            loading_options.append(selectinload(cls.user))

        stmt = select(cls).options(*loading_options).where(cls.user_id == user_id)

        if only_active:
            stmt = stmt.where(cls.is_active == True)

        if for_update:
            stmt = stmt.with_for_update()

        result = await session.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def get_by_id(cls,
                        session: AsyncSession,
                        card_id: uuid.UUID,
                        load_transactions: bool = False,
                        load_user: bool = False,
                        for_update: bool = False) -> Card | None:
        loading_options = []
        if load_transactions:
            loading_options.append(selectinload(cls.transactions))
        if load_user:
            loading_options.append(selectinload(cls.user))

        stmt = select(cls).options(*loading_options).where(cls.id == card_id)

        if for_update:
            stmt = stmt.with_for_update()

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    def make_payment_to_card(self,
                             counterparty_card: Card,
                             amount: Decimal,
                             description: str | None) -> tuple[CardTransaction, CardTransaction]:
        self.amount -= amount
        counterparty_card.amount += amount

        user_tx = CardTransaction(card=self,
                                  counterparty_instrument_id=counterparty_card.id,
                                  counterparty_name=counterparty_card.user.name,
                                  counterparty_surname=counterparty_card.user.surname,
                                  amount=amount,
                                  type=CardTransactionType.CARD_TO_CARD,
                                  direction=CardTransactionDirection.TRANSFER_OUT,
                                  description=description)

        counterparty_tx = CardTransaction(card=counterparty_card,
                                          counterparty_instrument_id=self.id,
                                          counterparty_name=self.user.name,
                                          counterparty_surname=self.user.surname,
                                          amount=amount,
                                          type=CardTransactionType.CARD_TO_CARD,
                                          direction=CardTransactionDirection.TRANSFER_IN,
                                          description=description)

        return user_tx, counterparty_tx

    def card_refund(self,
                    wallet_id: uuid.UUID,
                    amount: Decimal,
                    reason: WalletRefundReason) -> CardTransaction:
        self.amount -= amount
        return CardTransaction(card=self,
                               counterparty_instrument_id=wallet_id,
                               counterparty_name=self.user.name,
                               counterparty_surname=self.user.surname,
                               amount=amount,
                               type=CardTransactionType.CARD_REFUND,
                               direction=CardTransactionDirection.TRANSFER_OUT,
                               description=reason)
    def card_recharge(self,
                      wallet_id: uuid.UUID,
                      amount: Decimal) -> CardTransaction:
        self.amount += amount
        return CardTransaction(card=self,
                               counterparty_instrument_id=wallet_id,
                               counterparty_name=self.user.name,
                               counterparty_surname=self.user.surname,
                               amount=amount,
                               type=CardTransactionType.CARD_RECHARGE,
                               direction=CardTransactionDirection.TRANSFER_IN)

    def payment_from_wallet(self,
                            source_user_name: str,
                            source_user_surname: str,
                            source_wallet_id: uuid.UUID,
                            amount: Decimal,
                            description: str | None) -> CardTransaction:
        self.amount += amount
        return CardTransaction(card=self,
                               counterparty_instrument_id=source_wallet_id,
                               counterparty_name=source_user_name,
                               counterparty_surname=source_user_surname,
                               amount=amount,
                               type=CardTransactionType.WALLET_TO_CARD,
                               direction=CardTransactionDirection.TRANSFER_IN,
                               description=description)

    def payment_to_wallet(self,
                          counterparty_user_name: str,
                          counterparty_user_surname: str,
                          counterparty_wallet_id: uuid.UUID,
                          amount: Decimal,
                          description: str | None) -> CardTransaction:
        self.amount -= amount
        return CardTransaction(card=self,
                               counterparty_instrument_id=counterparty_wallet_id,
                               counterparty_name=counterparty_user_name,
                               counterparty_surname=counterparty_user_surname,
                               amount=amount,
                               type=CardTransactionType.CARD_TO_WALLET,
                               direction=CardTransactionDirection.TRANSFER_OUT,
                               description=description)


class CardTransaction(BaseExt):
    __tablename__ = "card_transactions"
    card_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cards.id"), nullable=False)
    card: Mapped[Card] = relationship(back_populates="transactions")

    counterparty_instrument_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    counterparty_name: Mapped[str] = mapped_column(String, nullable=False)
    counterparty_surname: Mapped[str] = mapped_column(String, nullable=False)

    amount: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False)
    type: Mapped[CardTransactionType] = mapped_column(Enum(CardTransactionType, name="card_transaction_type"), nullable=False)
    direction: Mapped[CardTransactionDirection] = mapped_column(Enum(CardTransactionDirection, name="card_transaction_direction"), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
