import asyncio
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import text

from main import app
from app.database.base import Base
from app.database.session import get_db
from app.core.config import settings
from app.auth.jwt import create_access_token
from app.database.models.models import User
from app.database.schemas.schemas import UserCreate
from app.services.user import UserService


DATABASE_URL_FROM_ENV = os.getenv("DATABASE_URL")

if DATABASE_URL_FROM_ENV:
    # Running in Docker
    TEST_DATABASE_URL = DATABASE_URL_FROM_ENV.replace("/egoai", "/egoai_test")
else:
    # Running locally
    TEST_DATABASE_URL = str(settings.DATABASE_URL).replace(settings.DATABASE_URL.path, "/egoai_test")


test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={"server_settings": {"jit": "off"}}
)
TestAsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession)

# Эта фикстура больше не нужна, pytest-asyncio управляет циклом событий автоматически
# @pytest.fixture(scope="session")
# def event_loop():
#     """Create a session-scoped event loop for async tests."""
#     policy = asyncio.get_event_loop_policy()
#     loop = policy.new_event_loop()
#     yield loop
#     loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture to provide a new database session for each test.
    Rolls back transaction after each test.
    """
    connection = await test_engine.connect()
    transaction = await connection.begin()
    session = TestAsyncSessionLocal(bind=connection)

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()

@pytest.fixture(scope="function")
async def client(db_session: AsyncSession):
    """
    Fixture for FastAPI test client that uses the test database session.
    """
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear() # Clear overrides after the test

@pytest.fixture(scope="function")
async def authenticated_client(client: AsyncClient, db_session: AsyncSession):
    """
    Fixture for an authenticated FastAPI test client.
    Creates a test user and provides a client with a valid JWT token.
    """
    user_service = UserService(db_session)
    user_data = {"email": "auth_test_user@example.com", "password": "secure_password", "name": "Auth Test User"}
    test_user = await user_service.create(user_in=UserCreate(**user_data))

    access_token = create_access_token(data={"sub": str(test_user.id)})

    client.headers.update({"Authorization": f"Bearer {access_token}"})
    yield client
    client.headers.pop("Authorization") # Clean up header after test 
