import logging
import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

logger = logging.getLogger("fastapi.app")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/orders",
)

logger.debug("Using database URL: %s", DATABASE_URL)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    logger.debug("Opening DB session")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
            logger.debug("DB session closed")


async def create_tables_if_not_exist():
    logger.info("Running create_all on DB metadata")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("DB metadata create_all completed")


async def drop_tables():
    logger.warning("Dropping all tables")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.warning("All tables dropped")
