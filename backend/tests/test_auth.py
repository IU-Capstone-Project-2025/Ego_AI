import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.models import User
from app.database.schemas.schemas import UserCreate


@pytest.mark.asyncio
async def test_protected_endpoint_access_with_valid_token(authenticated_client: AsyncClient, db_session: AsyncSession):
    # Test access to a protected endpoint (e.g., read user by ID)
    # The authenticated_client already has a valid token attached.
    # We need to get the user ID of the authenticated user to query for it.
    # The authenticated_client fixture creates a user named 'Auth Test User'.
    # Let's retrieve that user's ID from the database.
    from app.services.user import UserService
    user_service = UserService(db_session)
    test_user = await user_service.get_by_email(email="auth_test_user@example.com")
    
    assert test_user is not None

    response = await authenticated_client.get(f"/api/v1/users/{test_user.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "auth_test_user@example.com"
    assert data["id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_protected_endpoint_access_without_token(client: AsyncClient):
    # Test access to a protected endpoint without any token
    # Use the unauthenticated 'client' fixture
    response = await client.get("/api/v1/users/some_id") # Any protected endpoint
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


@pytest.mark.asyncio
async def test_protected_endpoint_access_with_invalid_token(client: AsyncClient):
    # Test access to a protected endpoint with an invalid token
    client.headers.update({"Authorization": "Bearer invalid_token"})
    response = await client.get("/api/v1/users/some_id") # Any protected endpoint
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
    client.headers.pop("Authorization") # Clean up header


@pytest.mark.asyncio
async def test_protected_endpoint_access_with_malformed_token(client: AsyncClient):
    # Test access to a protected endpoint with a malformed token (e.g., missing Bearer)
    client.headers.update({"Authorization": "malformed_token"})
    response = await client.get("/api/v1/users/some_id") # Any protected endpoint
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    client.headers.pop("Authorization") # Clean up header

# You can add tests for your /auth/google-login endpoint here if it's considered public
# For example:
# @pytest.mark.asyncio
# async def test_google_login_redirect(client: AsyncClient):
#     response = await client.get("/api/v1/auth/google-login")
#     assert response.status_code == 307 # Temporary Redirect
#     assert "accounts.google.com" in response.headers["location"] 