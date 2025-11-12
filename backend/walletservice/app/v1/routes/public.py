from fastapi import APIRouter
from starlette import status

from .routes import PUBLIC_ROUTER_PREFIX, PublicRoutes


public_api = APIRouter(prefix=PUBLIC_ROUTER_PREFIX,
                       tags=["public"])


@public_api.get(PublicRoutes.HEALTH_CHECK.value, status_code=status.HTTP_200_OK)
async def health_check():
    return {"health-check": "ok"}

