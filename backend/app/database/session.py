from typing import AsyncGenerator
import logging

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

logger = logging.getLogger("db.session")

SQLALCHEMY_DATABASE_URL = str(settings.DATABASE_URL)

logger.info(f"[DB] Creating async engine with URL: {SQLALCHEMY_DATABASE_URL}")
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    logger.info("[DB] Opening new AsyncSession")
    async with AsyncSessionLocal() as session:
        yield session
    logger.info("[DB] Closed AsyncSession")
