import os
from typing import AsyncGenerator
from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base


db_uri = "{}+{}://{}:{}@{}:{}/{}".format(os.environ['DB_DIALECT'],
                                         os.environ['DB_DRIVER'],
                                         os.environ['DB_ADMIN_USERNAME'],
                                         quote_plus(os.environ['DB_ADMIN_PASSWORD']),
                                         os.environ['DB_HOST'],
                                         os.environ['DB_PORT'],
                                         os.environ['SERVICE_DB_NAME'])

engine = create_async_engine(db_uri)

Base = declarative_base()
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


# for FastAPI dependencies
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
