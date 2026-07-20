from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession, async_sessionmaker
from app.core.config import settings
import logging

#database logging logger
logger = logging.getLogger("app.database")


# Use async database URL
DB_URL = settings.db_url
# Example: "postgresql+asyncpg://user:password@localhost/dbname"

# Create async engine 
engine = create_async_engine(
    DB_URL,
    echo=settings.debug,  # "False" -> DB Logs will not show in console. For 'dev' env let it be 'True'
    future=True,
    pool_pre_ping=True
)


# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False
)

# Correct async generator with proper type hint
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    logger.info("Database session opened")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            logger.info("Database session closed")
            await session.close()
