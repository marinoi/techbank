import asyncio
import os
from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError
from starlette.middleware.cors import CORSMiddleware

from .common.broker.exchanges import BrokerExchanges
from .common.broker.rabbitmq import rabbitmq
from .common.db.commands import create_postgresql_db
from .common.db.orm import engine, Base, async_session, get_async_session
from .common.outbox.outboxloop import outbox_forwarding_loop
from .common.security.keys import KeysLoader
from .common.security.middleware import JWTAuthMiddleware
from .common.security.roles import Role
from .models.models import *
from .routes.administration import administration_api
from .routes.private import private_api
from .routes.public import public_api
from .routes.routes import PUBLIC_ROUTER_PREFIX


class AuthService:
    @staticmethod
    def factory() -> FastAPI:
        @asynccontextmanager
        async def lifespan(instance: FastAPI):
            await KeysLoader().load_keys()
            await rabbitmq.start()

            for exchange in BrokerExchanges:
                await rabbitmq.declare_exchange(exchange.value)

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            async with async_session() as session:
                try:
                    payload = UserDataIn(email="admin@example.com",
                                         name="Admin",
                                         surname="User",
                                         date_of_birth=date(1970, 1, 1),
                                         password="root1234",
                                         role=Role.ADMIN)

                    await User.signup(session, payload, commit=True)

                except IntegrityError:
                    print("User Admin Already Exists.")


            outbox_task = asyncio.create_task(outbox_forwarding_loop())

            yield

            outbox_task.cancel()
            await rabbitmq.close()

        create_postgresql_db(db_name=os.environ["SERVICE_DB_NAME"],
                             admin_username=os.environ["DB_ADMIN_USERNAME"],
                             admin_password=os.environ["DB_ADMIN_PASSWORD"],
                             admin_db=os.environ["ADMIN_DB"],
                             db_host=os.environ["DB_HOST"],
                             db_port=int(os.environ["DB_PORT"]))

        app = FastAPI(title=os.environ["FASTAPI_TITLE"], lifespan=lifespan)

        app.add_middleware(CORSMiddleware,
                           allow_origins=["*"],
                           allow_credentials=True,
                           allow_methods=["*"],
                           allow_headers=["*"])

        app.add_middleware(JWTAuthMiddleware,
                           whitelist_paths=set(route.path for route in public_api.routes) |
                                           {"/docs", "/redoc", "/openapi.json"})

        app.include_router(public_api)
        app.include_router(private_api)
        app.include_router(administration_api)

        return app
