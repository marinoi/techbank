from __future__ import annotations

import uuid
from sqlalchemy import String, ForeignKey, select, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, Mapped, mapped_column, selectinload

from ..common.db.models import BaseExt


class UserRef(BaseExt):
    __tablename__ = "users_ref"
    name: Mapped[str] = mapped_column(String)
    surname: Mapped[str] = mapped_column(String)
    notifications: Mapped[list[Notification]] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=True)


class Notification(BaseExt):
    __tablename__ = "notifications"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users_ref.id"), nullable=False)
    user: Mapped[UserRef] = relationship(back_populates="notifications")

    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    source_event_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), unique=True, nullable=True)
    emitter: Mapped[str] = mapped_column(String)
    reason: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(String)

    @classmethod
    async def get_by_id(cls,
                        session: AsyncSession,
                        notification_id: uuid.UUID,
                        for_update: bool = False) -> Notification | None:
        loading_options = [selectinload(cls.user)]

        stmt = select(cls).options(*loading_options).where(cls.id == notification_id)

        if for_update:
            stmt = stmt.with_for_update()

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_all_by_user_id(cls, session: AsyncSession, user_id: uuid.UUID):
        result = await session.execute(select(cls).where(cls.user_id == user_id).order_by(cls.created_at.desc()))
        notifications = result.scalars().all()
        return notifications
