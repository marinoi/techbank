from __future__ import annotations

import datetime
from typing import Optional

from pydantic import EmailStr
from sqlalchemy import String, Date, Boolean, Enum, DateTime, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from ..common.db.models import BaseExt
from ..common.security.roles import Role
from ..password.hasher import PasswordHasher
from ..schemas.schemas import UserDataIn


class User(BaseExt):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(254), unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    surname: Mapped[str] = mapped_column(String, nullable=False)
    date_of_birth: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role, name="role"), nullable=False)
    last_login: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    def verify_password(self, password: str) -> bool:
        return PasswordHasher().verify(password, self.password_hash)

    @classmethod
    async def signup(cls, session: AsyncSession, payload: UserDataIn, commit: bool = False) -> User:
        new_user = cls(name=payload.name,
                       surname=payload.surname,
                       email=payload.email,
                       date_of_birth=payload.date_of_birth,
                       password_hash=PasswordHasher().hash(payload.password),
                       role=payload.role)

        session.add(new_user)
        await session.flush()

        if commit:
            await session.commit()

        return new_user

    @classmethod
    async def from_email(cls, session: AsyncSession, email: str | EmailStr) -> Optional[User]:
        stmt = select(cls).where(cls.email == email)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
