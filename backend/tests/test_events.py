import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.services.user import UserService

from app.database.models.models import Event, User
from app.database.schemas.schemas import EventCreate, UserCreate


@pytest.mark.asyncio
async def test_create_event(client: AsyncClient, db_session: AsyncSession):
    # Create a user first, as events require a user_id
    user_data = {"email": "eventuser@example.com", "password": "testpass", "name": "Event User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    event_data = {
        "title": "Test Event",
        "description": "This is a test event.",
        "start_time": "2024-07-20T10:00:00",
        "end_time": "2024-07-20T11:00:00",
        "location": "Online",
        "all_day": False
    }
    response = await client.post(f"/api/v1/events/?user_id={user_id}", json=event_data)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Event"
    assert data["user_id"] == user_id
    assert "id" in data

    # Verify event in database
    event_in_db = await db_session.get(Event, data["id"])
    assert event_in_db is not None
    assert event_in_db.title == "Test Event"


@pytest.mark.asyncio
async def test_read_events_by_user(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "readuserforevents@example.com", "password": "testpass", "name": "Read User Events"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    # Create multiple events for this user
    for i in range(3):
        event_data = {
            "title": f"User Event {i+1}",
            "description": "Description",
            "start_time": f"2024-08-01T10:0{i}:00",
            "end_time": f"2024-08-01T11:0{i}:00",
            "location": "Location",
            "all_day": False
        }
        await client.post(f"/api/v1/events/?user_id={user_id}", json=event_data)

    response = await client.get(f"/api/v1/events/user/{user_id}")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]["user_id"] == user_id


@pytest.mark.asyncio
async def test_read_single_event(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "singleeventuser@example.com", "password": "testpass", "name": "Single Event User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    event_data = {
        "title": "Unique Event",
        "description": "Unique description",
        "start_time": "2024-09-01T12:00:00",
        "end_time": "2024-09-01T13:00:00",
        "location": "Venue",
        "all_day": False
    }
    create_response = await client.post(f"/api/v1/events/?user_id={user_id}", json=event_data)
    created_event_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/events/{created_event_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_event_id
    assert data["title"] == "Unique Event"


@pytest.mark.asyncio
async def test_update_event(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "updateeventuser@example.com", "password": "testpass", "name": "Update Event User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    event_data = {
        "title": "Event to Update",
        "description": "Old description",
        "start_time": "2024-10-01T09:00:00",
        "end_time": "2024-10-01T10:00:00",
        "location": "Old Place",
        "all_day": False
    }
    create_response = await client.post(f"/api/v1/events/?user_id={user_id}", json=event_data)
    created_event_id = create_response.json()["id"]

    update_data = {"title": "Updated Event Title", "location": "New Place"}
    response = await client.put(f"/api/v1/events/{created_event_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Event Title"
    assert data["location"] == "New Place"

    # Verify update in database
    event_in_db = await db_session.get(Event, created_event_id)
    assert event_in_db.title == "Updated Event Title"
    assert event_in_db.location == "New Place"


@pytest.mark.asyncio
async def test_delete_event(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "deleteeventuser@example.com", "password": "testpass", "name": "Delete Event User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    event_data = {
        "title": "Event to Delete",
        "description": "Description",
        "start_time": "2024-11-01T10:00:00",
        "end_time": "2024-11-01T11:00:00",
        "location": "Somewhere",
        "all_day": False
    }
    create_response = await client.post(f"/api/v1/events/?user_id={user_id}", json=event_data)
    created_event_id = create_response.json()["id"]

    response = await client.delete(f"/api/v1/events/{created_event_id}")

    assert response.status_code == 200
    assert response.json() == {"message": "Event deleted successfully"}

    # Verify deletion in database
    event_in_db = await db_session.get(Event, created_event_id)
    assert event_in_db is None


@pytest.mark.asyncio
async def test_create_event_user_not_found(client: AsyncClient):
    event_data = {
        "title": "Test Event",
        "description": "This is a test event.",
        "start_time": "2024-07-20T10:00:00",
        "end_time": "2024-07-20T11:00:00",
        "location": "Online",
        "all_day": False
    }
    response = await client.post("/api/v1/events/?user_id=nonexistent_user", json=event_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "User with id nonexistent_user not found"} # Assuming service raises NotFoundError 


@pytest.mark.asyncio
async def test_create_event_invalid_time_order(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "eventuser_time_order@example.com", "password": "testpass", "name": "Time Order User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    event_data = {
        "title": "Invalid Time Event",
        "description": "End time before start time.",
        "start_time": "2024-07-20T11:00:00",
        "end_time": "2024-07-20T10:00:00", # Invalid order
        "location": "Online",
        "all_day": False
    }
    response = await client.post(f"/api/v1/events/?user_id={user_id}", json=event_data)

    assert response.status_code == 422 # Unprocessable Entity due to validation
    assert "end_time must be after start_time" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_event_invalid_datetime_format(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "eventuser_bad_time@example.com", "password": "testpass", "name": "Bad Time User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    event_data = {
        "title": "Bad Format Event",
        "description": "Invalid datetime format.",
        "start_time": "2024/07/20 10:00:00", # Invalid format
        "end_time": "2024-07-20T11:00:00",
        "location": "Online",
        "all_day": False
    }
    response = await client.post(f"/api/v1/events/?user_id={user_id}", json=event_data)

    assert response.status_code == 422 # Unprocessable Entity due to validation
    assert "value is not a valid datetime" in response.json()["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_update_non_existent_event(client: AsyncClient):
    update_data = {"title": "Non Existent Event"}
    response = await client.put("/api/v1/events/non_existent_id", json=update_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Event with id non_existent_id not found"}


@pytest.mark.asyncio
async def test_delete_non_existent_event(client: AsyncClient):
    response = await client.delete("/api/v1/events/non_existent_id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Event with id non_existent_id not found"}


@pytest.mark.asyncio
async def test_update_event_invalid_time_order(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "eventuser_update_time_order@example.com", "password": "testpass", "name": "Update Time Order User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    event_data = {
        "title": "Event to Update Time",
        "description": "Description",
        "start_time": "2024-10-01T10:00:00",
        "end_time": "2024-10-01T11:00:00",
        "location": "Location",
        "all_day": False
    }
    create_response = await client.post(f"/api/v1/events/?user_id={user_id}", json=event_data)
    created_event_id = create_response.json()["id"]

    update_data = {"start_time": "2024-10-01T12:00:00", "end_time": "2024-10-01T11:00:00"} # Invalid order
    response = await client.put(f"/api/v1/events/{created_event_id}", json=update_data)

    assert response.status_code == 422 # Unprocessable Entity
    assert "end_time must be after start_time" in response.json()["detail"]


@pytest.mark.asyncio
async def test_read_event_other_user_forbidden(authenticated_client: AsyncClient, client: AsyncClient, db_session: AsyncSession):
    # Create a user for the authenticated client
    user_service = UserService(db_session)
    auth_user = await user_service.get_by_email(email="auth_test_user@example.com") # User created by authenticated_client fixture
    auth_user_id = auth_user.id

    # Create an event for the authenticated user
    event_data_auth_user = {
        "title": "Auth User Event",
        "description": "Description",
        "start_time": "2024-12-01T10:00:00",
        "end_time": "2024-12-01T11:00:00",
        "location": "Auth Location",
        "all_day": False
    }
    auth_event_response = await authenticated_client.post(f"/api/v1/events/?user_id={auth_user_id}", json=event_data_auth_user)
    auth_event_id = auth_event_response.json()["id"]

    # Create a second user and event
    other_user_data = {"email": "other_user_event@example.com", "password": "otherpass", "name": "Other Event User"}
    other_user_response = await client.post("/api/v1/users/", json=other_user_data)
    other_user_id = other_user_response.json()["id"]

    event_data_other_user = {
        "title": "Other User Event",
        "description": "Description",
        "start_time": "2024-12-02T10:00:00",
        "end_time": "2024-12-02T11:00:00",
        "location": "Other Location",
        "all_day": False
    }
    other_event_response = await client.post(f"/api/v1/events/?user_id={other_user_id}", json=event_data_other_user)
    other_event_id = other_event_response.json()["id"]

    # Attempt to read the other user's event with the authenticated client
    response = await authenticated_client.get(f"/api/v1/events/{other_event_id}")
    assert response.status_code == 404 # Should be 404 Not Found if not accessible or 403 Forbidden
    assert response.json() == {"detail": f"Event with id {other_event_id} not found"}


@pytest.mark.asyncio
async def test_update_event_other_user_forbidden(authenticated_client: AsyncClient, client: AsyncClient, db_session: AsyncSession):
    user_service = UserService(db_session)
    auth_user = await user_service.get_by_email(email="auth_test_user@example.com")
    auth_user_id = auth_user.id

    event_data_auth_user = {
        "title": "Auth User Event For Update",
        "description": "Description",
        "start_time": "2024-12-03T10:00:00",
        "end_time": "2024-12-03T11:00:00",
        "location": "Auth Location",
        "all_day": False
    }
    auth_event_response = await authenticated_client.post(f"/api/v1/events/?user_id={auth_user_id}", json=event_data_auth_user)
    auth_event_id = auth_event_response.json()["id"]

    other_user_data = {"email": "other_user_event_update@example.com", "password": "otherpass", "name": "Other Event User Update"}
    other_user_response = await client.post("/api/v1/users/", json=other_user_data)
    other_user_id = other_user_response.json()["id"]

    event_data_other_user = {
        "title": "Other User Event For Update",
        "description": "Description",
        "start_time": "2024-12-04T10:00:00",
        "end_time": "2024-12-04T11:00:00",
        "location": "Other Location",
        "all_day": False
    }
    other_event_response = await client.post(f"/api/v1/events/?user_id={other_user_id}", json=event_data_other_user)
    other_event_id = other_event_response.json()["id"]

    update_data = {"title": "Attempted Update"}
    response = await authenticated_client.put(f"/api/v1/events/{other_event_id}", json=update_data)
    assert response.status_code == 404 # Should be 404 Not Found or 403 Forbidden
    assert response.json() == {"detail": f"Event with id {other_event_id} not found"}


@pytest.mark.asyncio
async def test_delete_event_other_user_forbidden(authenticated_client: AsyncClient, client: AsyncClient, db_session: AsyncSession):
    user_service = UserService(db_session)
    auth_user = await user_service.get_by_email(email="auth_test_user@example.com")
    auth_user_id = auth_user.id

    event_data_auth_user = {
        "title": "Auth User Event For Delete",
        "description": "Description",
        "start_time": "2024-12-05T10:00:00",
        "end_time": "2024-12-05T11:00:00",
        "location": "Auth Location",
        "all_day": False
    }
    auth_event_response = await authenticated_client.post(f"/api/v1/events/?user_id={auth_user_id}", json=event_data_auth_user)
    auth_event_id = auth_event_response.json()["id"]

    other_user_data = {"email": "other_user_event_delete@example.com", "password": "otherpass", "name": "Other Event User Delete"}
    other_user_response = await client.post("/api/v1/users/", json=other_user_data)
    other_user_id = other_user_response.json()["id"]

    event_data_other_user = {
        "title": "Other User Event For Delete",
        "description": "Description",
        "start_time": "2024-12-06T10:00:00",
        "end_time": "2024-12-06T11:00:00",
        "location": "Other Location",
        "all_day": False
    }
    other_event_response = await client.post(f"/api/v1/events/?user_id={other_user_id}", json=event_data_other_user)
    other_event_id = other_event_response.json()["id"]

    response = await authenticated_client.delete(f"/api/v1/events/{other_event_id}")
    assert response.status_code == 404 # Should be 404 Not Found or 403 Forbidden
    assert response.json() == {"detail": f"Event with id {other_event_id} not found"} 