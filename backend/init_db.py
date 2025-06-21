import asyncio
import logging

from app.database.session import engine
from app.database.base import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db.init")

async def init_db():
    logger.info("[DB] Connecting to database and creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("[DB] Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())