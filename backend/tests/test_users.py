import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.models import User
from app.database.schemas.schemas import UserCreate


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, db_session: AsyncSession):
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User"
    }
    response = await client.post("/api/v1/users/", json=user_data)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data

    # Verify user in database
    user_in_db = await db_session.get(User, data["id"])
    assert user_in_db is not None
    assert user_in_db.email == "test@example.com"


@pytest.mark.asyncio
async def test_read_user(client: AsyncClient, db_session: AsyncSession):
    # Create a user first
    user_data = {
        "email": "readtest@example.com",
        "password": "password123",
        "name": "Read User"
    }
    response = await client.post("/api/v1/users/", json=user_data)
    created_user_id = response.json()["id"]

    # Read the user
    # For this test, we are bypassing get_current_user dependency, in real scenario, it would be authenticated
    response = await client.get(f"/api/v1/users/{created_user_id}") # No current_user dependency for simplified test

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "readtest@example.com"
    assert data["id"] == created_user_id


@pytest.mark.asyncio
async def test_read_non_existent_user(client: AsyncClient):
    response = await client.get("/api/v1/users/non_existent_id")
    assert response.status_code == 404
    assert response.json() == {"detail": "User with id non_existent_id not found"}


@pytest.mark.asyncio
async def test_update_user(client: AsyncClient, db_session: AsyncSession):
    # Create a user first
    user_data = {
        "email": "updatetest@example.com",
        "password": "password123",
        "name": "Update User"
    }
    response = await client.post("/api/v1/users/", json=user_data)
    created_user_id = response.json()["id"]

    update_data = {"name": "Updated User Name"}
    response = await client.put(f"/api/v1/users/{created_user_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated User Name"

    # Verify update in database
    user_in_db = await db_session.get(User, created_user_id)
    assert user_in_db.name == "Updated User Name"


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient, db_session: AsyncSession):
    # Create a user first
    user_data = {
        "email": "deletetest@example.com",
        "password": "password123",
        "name": "Delete User"
    }
    response = await client.post("/api/v1/users/", json=user_data)
    created_user_id = response.json()["id"]

    response = await client.delete(f"/api/v1/users/{created_user_id}")

    assert response.status_code == 200
    assert response.json() == {"message": "User deleted successfully"}

    # Verify deletion in database
    user_in_db = await db_session.get(User, created_user_id)
    assert user_in_db is None


@pytest.mark.asyncio
async def test_read_users(client: AsyncClient, db_session: AsyncSession):
    # Create some users
    await client.post("/api/v1/users/", json={"email": "user1@example.com", "password": "pass", "name": "User One"})
    await client.post("/api/v1/users/", json={"email": "user2@example.com", "password": "pass", "name": "User Two"})

    response = await client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2 # At least two users created in this test

    # Test pagination
    response = await client.get("/api/v1/users/?skip=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient, db_session: AsyncSession):
    user_data = {
        "email": "duplicate@example.com",
        "password": "password123",
        "name": "Duplicate User"
    }
    response1 = await client.post("/api/v1/users/", json=user_data)
    assert response1.status_code == 200

    response2 = await client.post("/api/v1/users/", json=user_data)
    assert response2.status_code == 400 # Or 409 Conflict, depending on implementation
    assert "User with this email already exists" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_create_user_invalid_email_format(client: AsyncClient):
    user_data = {
        "email": "invalid-email",
        "password": "password123",
        "name": "Invalid Email User"
    }
    response = await client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 422 # Unprocessable Entity for validation errors


@pytest.mark.asyncio
async def test_create_user_short_password(client: AsyncClient):
    user_data = {
        "email": "shortpass@example.com",
        "password": "short",
        "name": "Short Pass User"
    }
    response = await client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 422 # Assuming password length validation


@pytest.mark.asyncio
async def test_delete_non_existent_user(client: AsyncClient):
    response = await client.delete("/api/v1/users/non_existent_id")
    assert response.status_code == 404
    assert response.json() == {"detail": "User with id non_existent_id not found"}


@pytest.mark.asyncio
async def test_update_non_existent_user(client: AsyncClient):
    update_data = {"name": "Non Existent User"}
    response = await client.put("/api/v1/users/non_existent_id", json=update_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "User with id non_existent_id not found"}


@pytest.mark.asyncio
async def test_update_user_duplicate_email(client: AsyncClient, db_session: AsyncSession):
    # Create two users
    user1_data = {"email": "user1_for_update@example.com", "password": "pass1", "name": "User One"}
    user2_data = {"email": "user2_for_update@example.com", "password": "pass2", "name": "User Two"}
    response1 = await client.post("/api/v1/users/", json=user1_data)
    response2 = await client.post("/api/v1/users/", json=user2_data)

    user1_id = response1.json()["id"]

    # Try to update user1's email to user2's email
    update_data = {"email": "user2_for_update@example.com"}
    response = await client.put(f"/api/v1/users/{user1_id}", json=update_data)

    assert response.status_code == 400 # Or 409 Conflict
    assert "User with this email already exists" in response.json()["detail"] 