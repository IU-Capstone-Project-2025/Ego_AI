from logging.config import fileConfig
import logging

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# add your model's MetaData object here
# for 'autogenerate' support
from app.database.base import Base
from app.database.models import models
from app.core.config import settings


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = logging.getLogger("db.alembic")

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Use the database URL from our application settings.
# This ensures that Alembic runs migrations on the same database.
# We assume the URL is already configured for async usage (e.g., with '...asyncpg').
db_url = str(settings.DATABASE_URL)
logger.info(f"[DB] Setting sqlalchemy.url to: {db_url}")
config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline() -> None:
    logger.info(f"[DB] Alembic running migrations OFFLINE with URL: {config.get_main_option('sqlalchemy.url')}")
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    logger.info("[DB] Alembic configured context for OFFLINE migrations")
    with context.begin_transaction():
        logger.info("[DB] Alembic starting OFFLINE migration transaction")
        context.run_migrations()
        logger.info("[DB] Alembic finished OFFLINE migration transaction")


def do_run_migrations(connection):
    logger.info("[DB] Alembic running migrations ONLINE (connection established)")
    context.configure(connection=connection, target_metadata=target_metadata)
    logger.info("[DB] Alembic configured context for ONLINE migrations")
    with context.begin_transaction():
        logger.info("[DB] Alembic starting ONLINE migration transaction")
        context.run_migrations()
        logger.info("[DB] Alembic finished ONLINE migration transaction")


async def run_migrations_online() -> None:
    logger.info(f"[DB] Alembic creating async engine with URL: {config.get_main_option('sqlalchemy.url')}")
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )
    logger.info("[DB] Alembic async engine created, connecting...")
    async with connectable.connect() as connection:
        logger.info("[DB] Alembic connected to database, running migrations...")
        await connection.run_sync(do_run_migrations)
        logger.info("[DB] Alembic migrations complete, disconnecting...")
    await connectable.dispose()
    logger.info("[DB] Alembic migrations complete, connection disposed.")


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio

    asyncio.run(run_migrations_online())
