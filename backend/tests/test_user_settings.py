import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.models import User_Settings, User
from app.database.schemas.schemas import User_SettingsCreate, User_SettingsUpdate


@pytest.mark.asyncio
async def test_create_user_settings(client: AsyncClient, db_session: AsyncSession):
    # Create a user first
    user_data = {"email": "settingsuser@example.com", "password": "testpass", "name": "Settings User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    settings_data = {
        "user_id": user_id,
        "theme": "dark",
        "language": "en",
        "notifications_enabled": True
    }
    response = await client.post("/api/v1/user-settings/", json=settings_data)

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["theme"] == "dark"
    assert "id" in data

    # Verify settings in database
    settings_in_db = await db_session.get(User_Settings, data["id"])
    assert settings_in_db is not None
    assert settings_in_db.user_id == user_id


@pytest.mark.asyncio
async def test_read_user_settings(client: AsyncClient, db_session: AsyncSession):
    # Create a user and settings first
    user_data = {"email": "readsettingsuser@example.com", "password": "testpass", "name": "Read Settings User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    settings_data = {
        "user_id": user_id,
        "theme": "light",
        "language": "ru",
        "notifications_enabled": False
    }
    await client.post("/api/v1/user-settings/", json=settings_data)

    response = await client.get(f"/api/v1/user-settings/{user_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["theme"] == "light"


@pytest.mark.asyncio
async def test_read_non_existent_user_settings(client: AsyncClient):
    response = await client.get("/api/v1/user-settings/non_existent_user_id")
    assert response.status_code == 404
    assert response.json() == {"detail": "User settings for user_id non_existent_user_id not found"}


@pytest.mark.asyncio
async def test_update_user_settings(client: AsyncClient, db_session: AsyncSession):
    # Create a user and settings first
    user_data = {"email": "updatesettingsuser@example.com", "password": "testpass", "name": "Update Settings User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    settings_data = {
        "user_id": user_id,
        "theme": "dark",
        "language": "en",
        "notifications_enabled": True
    }
    await client.post("/api/v1/user-settings/", json=settings_data)

    update_data = {"theme": "blue", "notifications_enabled": False}
    response = await client.put(f"/api/v1/user-settings/{user_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["theme"] == "blue"
    assert data["notifications_enabled"] == False

    # Verify update in database
    settings_in_db = await db_session.get(User_Settings, data["id"])
    assert settings_in_db.theme == "blue"
    assert settings_in_db.notifications_enabled == False


@pytest.mark.asyncio
async def test_delete_user_settings(client: AsyncClient, db_session: AsyncSession):
    # Create a user and settings first
    user_data = {"email": "deletesettingsuser@example.com", "password": "testpass", "name": "Delete Settings User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    settings_data = {
        "user_id": user_id,
        "theme": "light",
        "language": "es",
        "notifications_enabled": True
    }
    create_response = await client.post("/api/v1/user-settings/", json=settings_data)
    created_settings_id = create_response.json()["id"]

    response = await client.delete(f"/api/v1/user-settings/{user_id}")

    assert response.status_code == 200
    assert response.json() == {"message": "User settings deleted successfully"}

    # Verify deletion in database
    settings_in_db = await db_session.get(User_Settings, created_settings_id)
    assert settings_in_db is None


@pytest.mark.asyncio
async def test_create_user_settings_user_not_found(client: AsyncClient):
    settings_data = {
        "user_id": "nonexistent_user",
        "theme": "dark",
        "language": "en",
        "notifications_enabled": True
    }
    response = await client.post("/api/v1/user-settings/", json=settings_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "User with id nonexistent_user not found"} # Assuming service raises NotFoundError


@pytest.mark.asyncio
async def test_create_user_settings_duplicate(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "dupesettings@example.com", "password": "testpass", "name": "Duplicate Settings User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    settings_data = {
        "user_id": user_id,
        "theme": "dark",
        "language": "en",
        "notifications_enabled": True
    }
    response1 = await client.post("/api/v1/user-settings/", json=settings_data)
    assert response1.status_code == 200

    response2 = await client.post("/api/v1/user-settings/", json=settings_data)
    assert response2.status_code == 400 # Or 409 Conflict
    assert "User settings for this user already exist" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_create_user_settings_invalid_theme(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "invalidtheme@example.com", "password": "testpass", "name": "Invalid Theme User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    settings_data = {
        "user_id": user_id,
        "theme": "purple", # Invalid theme
        "language": "en",
        "notifications_enabled": True
    }
    response = await client.post("/api/v1/user-settings/", json=settings_data)
    assert response.status_code == 422 # Unprocessable Entity for Enum validation
    assert "value is not a valid enumeration member" in response.json()["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_read_user_settings_other_user_forbidden(authenticated_client: AsyncClient, client: AsyncClient, db_session: AsyncSession):
    # Create a user for the authenticated client
    from app.services.user import UserService
    user_service = UserService(db_session)
    auth_user = await user_service.get_by_email(email="auth_test_user@example.com") # User created by authenticated_client fixture
    auth_user_id = auth_user.id

    # Create settings for the authenticated user
    settings_data_auth_user = {
        "user_id": auth_user_id,
        "theme": "dark",
        "language": "en",
        "notifications_enabled": True
    }
    await authenticated_client.post("/api/v1/user-settings/", json=settings_data_auth_user)

    # Create a second user and settings
    other_user_data = {"email": "other_user_settings@example.com", "password": "otherpass", "name": "Other Settings User"}
    other_user_response = await client.post("/api/v1/users/", json=other_user_data)
    other_user_id = other_user_response.json()["id"]

    settings_data_other_user = {
        "user_id": other_user_id,
        "theme": "light",
        "language": "fr",
        "notifications_enabled": False
    }
    await client.post("/api/v1/user-settings/", json=settings_data_other_user)

    # Attempt to read the other user's settings with the authenticated client
    response = await authenticated_client.get(f"/api/v1/user-settings/{other_user_id}")
    assert response.status_code == 404 # Should be 404 Not Found or 403 Forbidden
    assert response.json() == {"detail": f"User settings for user_id {other_user_id} not found"}


@pytest.mark.asyncio
async def test_update_user_settings_other_user_forbidden(authenticated_client: AsyncClient, client: AsyncClient, db_session: AsyncSession):
    from app.services.user import UserService
    user_service = UserService(db_session)
    auth_user = await user_service.get_by_email(email="auth_test_user@example.com")
    auth_user_id = auth_user.id

    settings_data_auth_user = {
        "user_id": auth_user_id,
        "theme": "dark",
        "language": "en",
        "notifications_enabled": True
    }
    await authenticated_client.post("/api/v1/user-settings/", json=settings_data_auth_user)

    other_user_data = {"email": "other_user_settings_update@example.com", "password": "otherpass", "name": "Other Settings User Update"}
    other_user_response = await client.post("/api/v1/users/", json=other_user_data)
    other_user_id = other_user_response.json()["id"]

    settings_data_other_user = {
        "user_id": other_user_id,
        "theme": "light",
        "language": "fr",
        "notifications_enabled": False
    }
    await client.post("/api/v1/user-settings/", json=settings_data_other_user)

    update_data = {"theme": "blue"}
    response = await authenticated_client.put(f"/api/v1/user-settings/{other_user_id}", json=update_data)
    assert response.status_code == 404 # Should be 404 Not Found or 403 Forbidden
    assert response.json() == {"detail": f"User settings for user_id {other_user_id} not found"}


@pytest.mark.asyncio
async def test_delete_user_settings_other_user_forbidden(authenticated_client: AsyncClient, client: AsyncClient, db_session: AsyncSession):
    from app.services.user import UserService
    user_service = UserService(db_session)
    auth_user = await user_service.get_by_email(email="auth_test_user@example.com")
    auth_user_id = auth_user.id

    settings_data_auth_user = {
        "user_id": auth_user_id,
        "theme": "dark",
        "language": "en",
        "notifications_enabled": True
    }
    await authenticated_client.post("/api/v1/user-settings/", json=settings_data_auth_user)

    other_user_data = {"email": "other_user_settings_delete@example.com", "password": "otherpass", "name": "Other Settings User Delete"}
    other_user_response = await client.post("/api/v1/users/", json=other_user_data)
    other_user_id = other_user_response.json()["id"]

    settings_data_other_user = {
        "user_id": other_user_id,
        "theme": "light",
        "language": "fr",
        "notifications_enabled": False
    }
    await client.post("/api/v1/user-settings/", json=settings_data_other_user)

    response = await authenticated_client.delete(f"/api/v1/user-settings/{other_user_id}")
    assert response.status_code == 404 # Should be 404 Not Found or 403 Forbidden
    assert response.json() == {"detail": f"User settings for user_id {other_user_id} not found"} 