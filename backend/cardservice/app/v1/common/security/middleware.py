from typing import overload

from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


from .jwt import JWTValidator


class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, whitelist_paths: set | None = None):
        self._whitelist_path = whitelist_paths or set()

        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self._whitelist_path:
            return await call_next(request)

        try:
            token = await JWTValidator.from_request(request)
            request.state.jwt = token
            return await call_next(request)

        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code,
                                content={"detail": exc.detail})
