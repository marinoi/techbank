import jose.jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request

from .keys import KeysLoader
from ..db.models import TokenBlacklist
from ..db.orm import async_session
from ..misc.cookies import Cookies
from ..schemas.token import JWTPayload

JWT_SECURITY_ALGORITHM = "RS256"


class JWTValidator:
    @staticmethod
    async def from_request(request: Request,
                           allow_expired: bool = False,
                           raise_on_none: bool = True,
                           check_blacklist: bool = True,
                           session: AsyncSession | None = None) -> JWTPayload | None:

        jwt = request.cookies.get(Cookies.JWT_TOKEN.value)

        if not jwt:
            if raise_on_none:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing-token")
            return None

        options = {"verify_exp": not allow_expired,
                   "require_sub": True,
                   "require_jti": True}

        try:
            try:
                decoded_jwt = jose.jwt.decode(jwt,
                                              KeysLoader().public_key,
                                              algorithms=JWT_SECURITY_ALGORITHM,
                                              options=options)

            except jose.ExpiredSignatureError:
                if allow_expired:
                    decoded_jwt = jose.jwt.get_unverified_claims(jwt)
                else:
                    raise

            payload = JWTPayload(**decoded_jwt)

            if check_blacklist:
                if session is None:
                    async with async_session() as session:
                        is_revoked = await TokenBlacklist.is_revoked(session, payload.jti)
                else:
                    is_revoked =  await TokenBlacklist.is_revoked(session, payload.jti)

                if is_revoked:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token-is-revoked")

            return payload

        except ValidationError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid-jwt-schema")

        except jose.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token-expired")

        except jose.JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid-token")
