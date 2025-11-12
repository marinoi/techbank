from datetime import datetime, timezone

from pydantic import BaseModel
from pydantic import UUID4

from ..security.roles import Role


class JWTPayload(BaseModel):
    sub: UUID4
    role: Role
    refresh_counter: int
    iat: int
    exp: int
    jti: UUID4

    def is_expired(self) -> bool:
        now_ts = datetime.now(tz=timezone.utc).timestamp()
        return now_ts > self.exp