from __future__ import annotations

import uuid
from decimal import Decimal
from sqlalchemy import String, ForeignKey, Boolean, Enum, select, UUID, Numeric
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, selectinload, Mapped, mapped_column

from .enums import WalletTransactionType, WalletTransactionDirection
from ..common.db.models import BaseExt
from ..common.schemas.enums import WalletRefundReason


class UserRef(BaseExt):
    __tablename__ = "users_ref"
    name: Mapped[str] = mapped_column(String)
    surname: Mapped[str] = mapped_column(String)
    wallet: Mapped[Wallet] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False)


class Wallet(BaseExt):
    __tablename__ = "wallets"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users_ref.id"), nullable=False, unique=True)
    user: Mapped[UserRef] = relationship(back_populates="wallet")

    amount: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    transactions: Mapped[list[WalletTransaction]] = relationship(back_populates="wallet", cascade="all, delete-orphan")

    @classmethod
    async def get_by_user_id(cls,
                             session: AsyncSession,
                             user_id: uuid.UUID,
                             load_transactions: bool = False,
                             load_user: bool = False,
                             for_update: bool = False) -> Wallet | None:
        loading_options = []
        if load_transactions:
            loading_options.append(selectinload(cls.transactions))
        if load_user:
            loading_options.append(selectinload(cls.user))

        stmt = select(cls).options(*loading_options).where(cls.user_id == user_id)

        if for_update:
            stmt = stmt.with_for_update()

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_id(cls,
                        session: AsyncSession,
                        wallet_id: uuid.UUID,
                        load_transactions: bool = False,
                        load_user: bool = False,
                        for_update: bool = False) -> Wallet | None:
        loading_options = []
        if load_transactions:
            loading_options.append(selectinload(cls.transactions))
        if load_user:
            loading_options.append(selectinload(cls.user))

        stmt = select(cls).options(*loading_options).where(cls.id == wallet_id)

        if for_update:
            stmt = stmt.with_for_update()

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    def deposit(self, amount: Decimal) -> WalletTransaction:
        self.amount += amount
        return WalletTransaction(wallet=self,
                                 counterparty_instrument_id=self.id,
                                 counterparty_name=self.user.name,
                                 counterparty_surname=self.user.surname,
                                 amount=amount,
                                 type=WalletTransactionType.DEPOSIT,
                                 direction=WalletTransactionDirection.TRANSFER_IN)

    def make_payment_to_wallet(self,
                               counterparty_wallet: Wallet,
                               amount: Decimal,
                               description: str | None) -> tuple[WalletTransaction, WalletTransaction]:
        self.amount -= amount
        counterparty_wallet.amount += amount

        user_tx = WalletTransaction(wallet=self,
                                    counterparty_instrument_id=counterparty_wallet.id,
                                    counterparty_name=counterparty_wallet.user.name,
                                    counterparty_surname=counterparty_wallet.user.surname,
                                    amount=amount,
                                    type=WalletTransactionType.WALLET_TO_WALLET,
                                    direction=WalletTransactionDirection.TRANSFER_OUT,
                                    description=description)

        counterparty_tx = WalletTransaction(wallet=counterparty_wallet,
                                            counterparty_instrument_id=self.id,
                                            counterparty_name=self.user.name,
                                            counterparty_surname=self.user.surname,
                                            amount=amount,
                                            type=WalletTransactionType.WALLET_TO_WALLET,
                                            direction=WalletTransactionDirection.TRANSFER_IN,
                                            description=description)

        return user_tx, counterparty_tx

    def card_refund(self,
                    card_id: uuid.UUID,
                    amount: Decimal,
                    reason: WalletRefundReason) -> WalletTransaction:
        self.amount += amount
        return WalletTransaction(wallet=self,
                                 counterparty_instrument_id=card_id,
                                 counterparty_name=self.user.name,
                                 counterparty_surname=self.user.surname,
                                 amount=amount,
                                 type=WalletTransactionType.CARD_REFUND,
                                 direction=WalletTransactionDirection.TRANSFER_IN,
                                 description=reason)

    def card_recharge(self,
                      card_id: uuid.UUID,
                      amount: Decimal) -> WalletTransaction:
        self.amount -= amount
        return WalletTransaction(wallet=self,
                                 counterparty_instrument_id=card_id,
                                 counterparty_name=self.user.name,
                                 counterparty_surname=self.user.surname,
                                 amount=amount,
                                 type=WalletTransactionType.CARD_RECHARGE,
                                 direction=WalletTransactionDirection.TRANSFER_OUT)

    def payment_from_card(self,
                          source_user_name: str,
                          source_user_surname: str,
                          source_card_id: uuid.UUID,
                          amount: Decimal,
                          description: str | None) -> WalletTransaction:
        self.amount += amount
        return WalletTransaction(wallet=self,
                                 counterparty_instrument_id=source_card_id,
                                 counterparty_name=source_user_name,
                                 counterparty_surname=source_user_surname,
                                 amount=amount,
                                 type=WalletTransactionType.CARD_TO_WALLET,
                                 direction=WalletTransactionDirection.TRANSFER_IN,
                                 description=description)

    def payment_to_card(self,
                        counterparty_user_name: str,
                        counterparty_user_surname: str,
                        counterparty_card_id: uuid.UUID,
                        amount: Decimal,
                        description: str | None) -> WalletTransaction:
        # The balance was already debited when the payment was requested.
        return WalletTransaction(wallet=self,
                                 counterparty_instrument_id=counterparty_card_id,
                                 counterparty_name=counterparty_user_name,
                                 counterparty_surname=counterparty_user_surname,
                                 amount=amount,
                                 type=WalletTransactionType.WALLET_TO_CARD,
                                 direction=WalletTransactionDirection.TRANSFER_OUT,
                                 description=description)


class WalletTransaction(BaseExt):
    __tablename__ = "wallet_transactions"
    wallet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wallets.id"), nullable=False)
    wallet: Mapped[Wallet] = relationship(back_populates="transactions")

    counterparty_instrument_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    counterparty_name: Mapped[str] = mapped_column(String, nullable=False)
    counterparty_surname: Mapped[str] = mapped_column(String, nullable=False)

    amount: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False)
    type: Mapped[WalletTransactionType] = mapped_column(Enum(WalletTransactionType, name="wallet_transaction_type"), nullable=False)
    direction: Mapped[WalletTransactionDirection] = mapped_column(Enum(WalletTransactionDirection, name="wallet_transaction_direction"), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    @classmethod
    async def get_by_id(cls,
                        session: AsyncSession,
                        transaction_id: uuid.UUID,
                        load_wallet: bool = False,
                        for_update: bool = False) -> Wallet | None:
        loading_options = []
        if load_wallet:
            loading_options.append(selectinload(cls.wallet))


        stmt = select(cls).options(*loading_options).where(cls.id == transaction_id)

        if for_update:
            stmt = stmt.with_for_update()

        result = await session.execute(stmt)
        return result.scalar_one_or_none()
