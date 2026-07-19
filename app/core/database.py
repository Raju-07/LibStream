from app.models import Base
from app.db.session import engine
import logging

# declaring database log
logger = logging.getLogger("app.database")

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.critical(f"Database Connection failed.\n {str(e)}")


async def close_db():
    await engine.dispose()