from datetime import datetime, date
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

from ..common.schemas.dbentity import HasID, HasCreatedAt
from ..common.security.roles import Role


class UserDataIn(BaseModel):
    email: EmailStr
    name: str
    surname: str
    date_of_birth: date
    password: Annotated[str, Field(min_length=8)]
    role: Role = Role.USER

    @field_validator("date_of_birth")
    @classmethod
    def signup_age_check(cls, v: date) -> date:
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("user-too-young")
        return v


class AdminUserDataIn(BaseModel):
    email: EmailStr
    name: str
    surname: str
    date_of_birth: date


class LoginDataIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    name: str
    surname: str
    email: EmailStr
    role: Role

    model_config = ConfigDict(from_attributes=True)


class UserOutAdmin(UserOut, HasID, HasCreatedAt):
    date_of_birth: date
    is_banned: bool
    last_login: datetime | None

    model_config = ConfigDict(from_attributes=True)
