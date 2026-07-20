from app.models import Base
from app.db.session import engine
import logging

# declaring database log
logger = logging.getLogger("app.database")

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables initialized")
    except Exception as e:
        logger.critical("Database connection failed.",exc_info=True)


async def close_db():
    await engine.dispose()