import asyncio
import logging
from sqlalchemy import text
from backend.infrastructure.db.session import engine
from backend.infrastructure.db.base import Base

import backend.infrastructure.db.user
import backend.infrastructure.db.pet
import backend.infrastructure.db.image
import backend.infrastructure.db.schedule
import backend.infrastructure.db.log
import backend.infrastructure.db.feeder_status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db():
    logger.info("Starting database initialization...")

    async with engine.begin() as conn:
        logger.info("Creating 'vector' extension if not exists...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

        logger.info("Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database initialization completed successfully.")


if __name__ == "__main__":
    asyncio.run(init_db())
