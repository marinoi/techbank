from fastapi import APIRouter, Depends
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request

from .roles import Role
from ..schemas.token import JWTPayload


class RuledAPIRouter(APIRouter):
    def __init__(self, *args, allowed_roles: list[Role] = None, **kwargs):
        self._allowed_roles = allowed_roles or []

        if not self._allowed_roles:
            raise ValueError("RuledAPIRouter requires at least one allowed role")

        super().__init__(*args, **kwargs)

        self.dependencies.append(Depends(self.require_role(self._allowed_roles)))

    @property
    def roles_allowed(self):
        return self._allowed_roles

    @staticmethod
    def require_role(allowed_roles: list[Role]):
        def check_role(request: Request):
            jwt: JWTPayload = request.state.jwt

            if jwt.role not in allowed_roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="operation-not-permitted")

        return check_role
