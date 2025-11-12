import uuid
from datetime import datetime, timezone, timedelta

from jose import jwt
from pydantic.v1 import UUID4

from .config import JWTConfig, JWTField
from ..common.misc.singleton import SingletonMeta
from ..common.security.jwt import JWT_SECURITY_ALGORITHM
from ..common.security.keys import KeysLoader


class JWTManager(metaclass=SingletonMeta):
    def __init__(self):
        self._private_key = KeysLoader().private_key
        self._public_key = KeysLoader().public_key

    def create_access_token(self,
                            sub: uuid.UUID,
                            role: str,
                            refresh_count: int,
                            expires_in: int = JWTConfig.JWT_TOKEN_EXP_TIME) -> str:

        now = datetime.now(timezone.utc)

        payload = {JWTField.SUB.value: str(sub),
                   JWTField.ROLE.value: role,
                   JWTField.IAT.value: int(now.timestamp()),
                   JWTField.EXP.value: int((now + timedelta(seconds=expires_in)).timestamp()),
                   JWTField.REFRESH_COUNTER.value: refresh_count,
                   JWTField.JTI.value: str(uuid.uuid4())}

        token = jwt.encode(payload, self._private_key, algorithm=JWT_SECURITY_ALGORITHM)
        return token
