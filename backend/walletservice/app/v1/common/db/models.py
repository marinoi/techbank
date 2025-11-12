from __future__ import annotations

import json
import uuid

from datetime import datetime, timezone
from functools import partial
from typing import Sequence

from sqlalchemy import DateTime, UUID, select, exists, inspect, Enum, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from .enums import OutBoxEventStatus
from .orm import Base


class BaseExt(Base):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=partial(datetime.now, tz=timezone.utc),
                                                 nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=partial(datetime.now, tz=timezone.utc),
                                                 onupdate=partial(datetime.now, tz=timezone.utc),
                                                 nullable=False)

    @classmethod
    async def get_by_id(cls, session: AsyncSession, _uuid: uuid.UUID) -> BaseExt | None:
        stmt = select(cls).where(cls.id == _uuid)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, session: AsyncSession) -> Sequence[BaseExt]:
        stmt = select(cls)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def save(self, session: AsyncSession, commit: bool = True) -> BaseExt:
        session.add(self)
        if commit:
            await session.commit()
            await session.refresh(self)
        return self

    async def delete(self, session: AsyncSession, commit: bool = True) -> None:
        await session.delete(self)
        if commit:
            await session.commit()

    async def update_from_dict(self, session: AsyncSession, data: dict, commit: bool = True) -> BaseExt:
        mapper = inspect(self.__class__)
        columns = set(attr.key for attr in mapper.attrs)
        excluded_fields = {"id", "created_at", "updated_at"}

        for k, v in data.items():
            if k in columns and k not in excluded_fields:
                setattr(self, k, v)

        session.add(self)
        if commit:
            await session.commit()
            await session.refresh(self)
        return self


class TokenBlacklist(BaseExt):
    __tablename__ = "tokens_blacklist"

    jti: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)

    @classmethod
    async def is_revoked(cls, session: AsyncSession, _jti: uuid.UUID) -> bool:
        stmt = select(exists().where(cls.jti == _jti))
        result = await session.execute(stmt)
        return result.scalar()

    @classmethod
    async def revoke(cls, session: AsyncSession, _jti: uuid.UUID, commit: bool = False) -> None:
        record = cls(jti=_jti)
        session.add(record)

        if commit:
            await session.commit()


class OutBoxEvent(BaseExt):
    __tablename__ = "outbox_events"

    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, unique=True, default=uuid.uuid4)
    exchange: Mapped[str] = mapped_column(String, nullable=True)
    queue: Mapped[str] = mapped_column(String, nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[OutBoxEventStatus] = mapped_column(Enum(OutBoxEventStatus, name="outbox_event_status"),
                                                      default=OutBoxEventStatus.PENDING,
                                                      nullable=False)

    async def save(self, session: AsyncSession, commit: bool = True) -> OutBoxEvent:
        self.payload = json.loads(self.payload)
        session.add(self)
        if commit:
            await session.commit()
            await session.refresh(self)
        return self

    @classmethod
    async def get_pending_events(cls, session: AsyncSession, limit: int = 10):
        stmt = (select(cls)
                .where(cls.status == OutBoxEventStatus.PENDING)
                .order_by(cls.created_at)
                .limit(limit)
                .with_for_update(skip_locked=True))

        result = await session.execute(stmt)
        events = result.scalars().all()

        return events

    @classmethod
    async def register_new_event(cls,
                                 session: AsyncSession,
                                 payload: str | dict,
                                 event_id: uuid.UUID = None,
                                 exchange: str = None,
                                 queue: str = None,
                                 commit: bool = True):

        event = cls(event_id=event_id or uuid.uuid4(),
                    exchange=exchange,
                    queue=queue,
                    payload=payload)

        session.add(event)

        if commit:
            await session.commit()

    def mark_sent(self):
        self.status = OutBoxEventStatus.SENT

    def mark_failed(self):
        self.status = OutBoxEventStatus.FAILED


class InBoxEvents(BaseExt):
    __tablename__ = "inbox_events"

    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, unique=True, default=uuid.uuid4)
    exchange: Mapped[str] = mapped_column(String, nullable=True)
    queue: Mapped[str] = mapped_column(String, nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    @classmethod
    async def is_already_processed(cls, session: AsyncSession, event_id: uuid.UUID):
        stmt = select(exists().where(cls.event_id == event_id))
        result = await session.execute(stmt)
        return result.scalar()

    @classmethod
    async def register_processed_event(cls,
                                       session: AsyncSession,
                                       event_id: uuid.UUID,
                                       payload: BaseModel,
                                       exchange: str | None = None,
                                       queue: str | None = None,
                                       commit: bool = True):

        event = cls(event_id=event_id,
                    exchange=exchange,
                    queue=queue,
                    payload=json.loads(payload.model_dump_json()))

        session.add(event)

        if commit:
            await session.commit()

        return event