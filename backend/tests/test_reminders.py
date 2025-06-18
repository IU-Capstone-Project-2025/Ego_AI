import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.database.models.models import Reminder, Event, User
from app.database.schemas.schemas import ReminderCreate, EventCreate


@pytest.mark.asyncio
async def test_create_reminder(client: AsyncClient, db_session: AsyncSession):
    # Create a user and an event first
    user_data = {"email": "reminderuser@example.com", "password": "testpass", "name": "Reminder User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    event_data = {
        "title": "Event for Reminder",
        "description": "Description",
        "start_time": "2024-07-25T10:00:00",
        "end_time": "2024-07-25T11:00:00",
        "location": "Location",
        "all_day": False
    }
    event_response = await client.post(f"/api/v1/events/?user_id={user_id}", json=event_data)
    event_id = event_response.json()["id"]

    reminder_data = {
        "event_id": event_id,
        "remind_at": "2024-07-25T09:45:00",
        "method": "email",
        "message": "Don't forget the event!"
    }
    response = await client.post("/api/v1/reminders/", json=reminder_data)

    assert response.status_code == 200
    data = response.json()
    assert data["event_id"] == event_id
    assert data["message"] == "Don't forget the event!"
    assert "id" in data

    # Verify reminder in database
    reminder_in_db = await db_session.get(Reminder, data["id"])
    assert reminder_in_db is not None
    assert reminder_in_db.event_id == event_id


@pytest.mark.asyncio
async def test_read_reminders_by_event(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "remindereventuser@example.com", "password": "testpass", "name": "Reminder Event User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    event_data = {
        "title": "Event for Multiple Reminders",
        "description": "Description",
        "start_time": "2024-08-01T10:00:00",
        "end_time": "2024-08-01T11:00:00",
        "location": "Location",
        "all_day": False
    }
    event_response = await client.post(f"/api/v1/events/?user_id={user_id}", json=event_data)
    event_id = event_response.json()["id"]

    # Create multiple reminders for this event
    for i in range(2):
        reminder_data = {
            "event_id": event_id,
            "remind_at": f"2024-08-01T09:5{i}:00",
            "method": "sms",
            "message": f"Reminder {i+1}"
        }
        await client.post("/api/v1/reminders/", json=reminder_data)
    
    response = await client.get(f"/api/v1/reminders/event/{event_id}")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["event_id"] == event_id


@pytest.mark.asyncio
async def test_read_single_reminder(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "singlereminderuser@example.com", "password": "testpass", "name": "Single Reminder User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    event_data = {
        "title": "Event for Single Reminder",
        "description": "Description",
        "start_time": "2024-09-01T10:00:00",
        "end_time": "2024-09-01T11:00:00",
        "location": "Location",
        "all_day": False
    }
    event_response = await client.post(f"/api/v1/events/?user_id={user_id}", json=event_data)
    event_id = event_response.json()["id"]

    reminder_data = {
        "event_id": event_id,
        "remind_at": "2024-09-01T09:30:00",
        "method": "app",
        "message": "Unique reminder message"
    }
    create_response = await client.post("/api/v1/reminders/", json=reminder_data)
    created_reminder_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/reminders/{created_reminder_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_reminder_id
    assert data["message"] == "Unique reminder message"


@pytest.mark.asyncio
async def test_update_reminder(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "updatereminderuser@example.com", "password": "testpass", "name": "Update Reminder User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    event_data = {
        "title": "Event to Update Reminder",
        "description": "Description",
        "start_time": "2024-10-01T10:00:00",
        "end_time": "2024-10-01T11:00:00",
        "location": "Location",
        "all_day": False
    }
    event_response = await client.post(f"/api/v1/events/?user_id={user_id}", json=event_data)
    event_id = event_response.json()["id"]

    reminder_data = {
        "event_id": event_id,
        "remind_at": "2024-10-01T09:00:00",
        "method": "email",
        "message": "Old message"
    }
    create_response = await client.post("/api/v1/reminders/", json=reminder_data)
    created_reminder_id = create_response.json()["id"]

    update_data = {"message": "New updated message", "method": "sms"}
    response = await client.put(f"/api/v1/reminders/{created_reminder_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "New updated message"
    assert data["method"] == "sms"

    # Verify update in database
    reminder_in_db = await db_session.get(Reminder, created_reminder_id)
    assert reminder_in_db.message == "New updated message"
    assert reminder_in_db.method == "sms"


@pytest.mark.asyncio
async def test_delete_reminder(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "deletereminderuser@example.com", "password": "testpass", "name": "Delete Reminder User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    event_data = {
        "title": "Event to Delete Reminder",
        "description": "Description",
        "start_time": "2024-11-01T10:00:00",
        "end_time": "2024-11-01T11:00:00",
        "location": "Location",
        "all_day": False
    }
    event_response = await client.post(f"/api/v1/events/?user_id={user_id}", json=event_data)
    event_id = event_response.json()["id"]

    reminder_data = {
        "event_id": event_id,
        "remind_at": "2024-11-01T09:00:00",
        "method": "email",
        "message": "Reminder to be deleted"
    }
    create_response = await client.post("/api/v1/reminders/", json=reminder_data)
    created_reminder_id = create_response.json()["id"]

    response = await client.delete(f"/api/v1/reminders/{created_reminder_id}")

    assert response.status_code == 200
    assert response.json() == {"message": "Reminder deleted successfully"}

    # Verify deletion in database
    reminder_in_db = await db_session.get(Reminder, created_reminder_id)
    assert reminder_in_db is None


@pytest.mark.asyncio
async def test_create_reminder_event_not_found(client: AsyncClient):
    reminder_data = {
        "event_id": "nonexistent_event",
        "remind_at": "2024-07-25T09:45:00",
        "method": "email",
        "message": "Don't forget the event!"
    }
    response = await client.post("/api/v1/reminders/", json=reminder_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Event with id nonexistent_event not found"} # Assuming service raises NotFoundError


@pytest.mark.asyncio
async def test_create_reminder_remind_at_in_past(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "pastreminduser@example.com", "password": "testpass", "name": "Past Remind User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    event_data = {
        "title": "Event for Past Reminder",
        "description": "Description",
        "start_time": "2024-07-25T10:00:00",
        "end_time": "2024-07-25T11:00:00",
        "location": "Location",
        "all_day": False
    }
    event_response = await client.post(f"/api/v1/events/?user_id={user_id}", json=event_data)
    event_id = event_response.json()["id"]

    reminder_data = {
        "event_id": event_id,
        "remind_at": "2023-01-01T09:00:00", # In the past
        "method": "email",
        "message": "Too late!"
    }
    response = await client.post("/api/v1/reminders/", json=reminder_data)
    assert response.status_code == 422 # Or another appropriate error for past date
    assert "remind_at cannot be in the past" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_reminder_remind_at_after_event_end(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "late_reminduser@example.com", "password": "testpass", "name": "Late Remind User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    event_data = {
        "title": "Event for Late Reminder",
        "description": "Description",
        "start_time": "2024-07-25T10:00:00",
        "end_time": "2024-07-25T11:00:00",
        "location": "Location",
        "all_day": False
    }
    event_response = await client.post(f"/api/v1/events/?user_id={user_id}", json=event_data)
    event_id = event_response.json()["id"]

    reminder_data = {
        "event_id": event_id,
        "remind_at": "2024-07-25T12:00:00", # After event end
        "method": "email",
        "message": "Too late!"
    }
    response = await client.post("/api/v1/reminders/", json=reminder_data)
    assert response.status_code == 422 # Or another appropriate error
    assert "remind_at cannot be after event end time" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_reminder_invalid_method(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "invalidmethoduser@example.com", "password": "testpass", "name": "Invalid Method User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    event_data = {
        "title": "Event for Invalid Method",
        "description": "Description",
        "start_time": "2024-07-25T10:00:00",
        "end_time": "2024-07-25T11:00:00",
        "location": "Location",
        "all_day": False
    }
    event_response = await client.post(f"/api/v1/events/?user_id={user_id}", json=event_data)
    event_id = event_response.json()["id"]

    reminder_data = {
        "event_id": event_id,
        "remind_at": "2024-07-25T09:00:00",
        "method": "invalid_method", # Invalid method
        "message": "Invalid method!"
    }
    response = await client.post("/api/v1/reminders/", json=reminder_data)
    assert response.status_code == 422 # Unprocessable Entity for Enum validation
    assert "value is not a valid enumeration member" in response.json()["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_update_non_existent_reminder(client: AsyncClient):
    update_data = {"message": "Non Existent Reminder"}
    response = await client.put("/api/v1/reminders/non_existent_id", json=update_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Reminder with id non_existent_id not found"}


@pytest.mark.asyncio
async def test_delete_non_existent_reminder(client: AsyncClient):
    response = await client.delete("/api/v1/reminders/non_existent_id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Reminder with id non_existent_id not found"}


@pytest.mark.asyncio
async def test_read_reminder_other_user_event_forbidden(authenticated_client: AsyncClient, client: AsyncClient, db_session: AsyncSession):
    # Create a user for the authenticated client
    from app.services.user import UserService
    user_service = UserService(db_session)
    auth_user = await user_service.get_by_email(email="auth_test_user@example.com") # User created by authenticated_client fixture
    auth_user_id = auth_user.id

    # Create an event for the authenticated user
    event_data_auth_user = {
        "title": "Auth User Event Reminder",
        "description": "Description",
        "start_time": "2024-12-01T10:00:00",
        "end_time": "2024-12-01T11:00:00",
        "location": "Auth Location",
        "all_day": False
    }
    auth_event_response = await authenticated_client.post(f"/api/v1/events/?user_id={auth_user_id}", json=event_data_auth_user)
    auth_event_id = auth_event_response.json()["id"]

    # Create a second user and event and reminder
    other_user_data = {"email": "other_user_reminder@example.com", "password": "otherpass", "name": "Other Reminder User"}
    other_user_response = await client.post("/api/v1/users/", json=other_user_data)
    other_user_id = other_user_response.json()["id"]

    event_data_other_user = {
        "title": "Other User Event Reminder",
        "description": "Description",
        "start_time": "2024-12-02T10:00:00",
        "end_time": "2024-12-02T11:00:00",
        "location": "Other Location",
        "all_day": False
    }
    other_event_response = await client.post(f"/api/v1/events/?user_id={other_user_id}", json=event_data_other_user)
    other_event_id = other_event_response.json()["id"]

    reminder_data_other_user = {
        "event_id": other_event_id,
        "remind_at": "2024-12-02T09:30:00",
        "method": "email",
        "message": "Other User Reminder"
    }
    other_reminder_response = await client.post("/api/v1/reminders/", json=reminder_data_other_user)
    other_reminder_id = other_reminder_response.json()["id"]

    # Attempt to read the other user's reminder with the authenticated client
    response = await authenticated_client.get(f"/api/v1/reminders/{other_reminder_id}")
    assert response.status_code == 404 # Should be 404 Not Found if not accessible or 403 Forbidden
    assert response.json() == {"detail": "Reminder with id \'{other_reminder_id}\' not found"}


@pytest.mark.asyncio
async def test_update_reminder_other_user_event_forbidden(authenticated_client: AsyncClient, client: AsyncClient, db_session: AsyncSession):
    from app.services.user import UserService
    user_service = UserService(db_session)
    auth_user = await user_service.get_by_email(email="auth_test_user@example.com")
    auth_user_id = auth_user.id

    event_data_auth_user = {
        "title": "Auth User Event Update Reminder",
        "description": "Description",
        "start_time": "2024-12-03T10:00:00",
        "end_time": "2024-12-03T11:00:00",
        "location": "Auth Location",
        "all_day": False
    }
    auth_event_response = await authenticated_client.post(f"/api/v1/events/?user_id={auth_user_id}", json=event_data_auth_user)
    auth_event_id = auth_event_response.json()["id"]

    other_user_data = {"email": "other_user_reminder_update@example.com", "password": "otherpass", "name": "Other Reminder User Update"}
    other_user_response = await client.post("/api/v1/users/", json=other_user_data)
    other_user_id = other_user_response.json()["id"]

    event_data_other_user = {
        "title": "Other User Event Update Reminder",
        "description": "Description",
        "start_time": "2024-12-04T10:00:00",
        "end_time": "2024-12-04T11:00:00",
        "location": "Other Location",
        "all_day": False
    }
    other_event_response = await client.post(f"/api/v1/events/?user_id={other_user_id}", json=event_data_other_user)
    other_event_id = other_event_response.json()["id"]

    reminder_data_other_user = {
        "event_id": other_event_id,
        "remind_at": "2024-12-04T09:30:00",
        "method": "email",
        "message": "Other User Reminder"
    }
    other_reminder_response = await client.post("/api/v1/reminders/", json=reminder_data_other_user)
    other_reminder_id = other_reminder_response.json()["id"]

    update_data = {"message": "Attempted Update"}
    response = await authenticated_client.put(f"/api/v1/reminders/{other_reminder_id}", json=update_data)
    assert response.status_code == 404 # Should be 404 Not Found or 403 Forbidden
    assert response.json() == {"detail": "Reminder with id \'{other_reminder_id}\' not found"}


@pytest.mark.asyncio
async def test_delete_reminder_other_user_event_forbidden(authenticated_client: AsyncClient, client: AsyncClient, db_session: AsyncSession):
    from app.services.user import UserService
    user_service = UserService(db_session)
    auth_user = await user_service.get_by_email(email="auth_test_user@example.com")
    auth_user_id = auth_user.id

    event_data_auth_user = {
        "title": "Auth User Event Delete Reminder",
        "description": "Description",
        "start_time": "2024-12-05T10:00:00",
        "end_time": "2024-12-05T11:00:00",
        "location": "Auth Location",
        "all_day": False
    }
    auth_event_response = await authenticated_client.post(f"/api/v1/events/?user_id={auth_user_id}", json=event_data_auth_user)
    auth_event_id = auth_event_response.json()["id"]

    other_user_data = {"email": "other_user_reminder_delete@example.com", "password": "otherpass", "name": "Other Reminder User Delete"}
    other_user_response = await client.post("/api/v1/users/", json=other_user_data)
    other_user_id = other_user_response.json()["id"]

    event_data_other_user = {
        "title": "Other User Event Delete Reminder",
        "description": "Description",
        "start_time": "2024-12-06T10:00:00",
        "end_time": "2024-12-06T11:00:00",
        "location": "Other Location",
        "all_day": False
    }
    other_event_response = await client.post(f"/api/v1/events/?user_id={other_user_id}", json=event_data_other_user)
    other_event_id = other_event_response.json()["id"]

    reminder_data_other_user = {
        "event_id": other_event_id,
        "remind_at": "2024-12-06T09:30:00",
        "method": "email",
        "message": "Other User Reminder"
    }
    other_reminder_response = await client.post("/api/v1/reminders/", json=reminder_data_other_user)
    other_reminder_id = other_reminder_response.json()["id"]

    response = await authenticated_client.delete(f"/api/v1/reminders/{other_reminder_id}")
    assert response.status_code == 404 # Should be 404 Not Found or 403 Forbidden
    assert response.json() == {"detail": "Reminder with id \'{other_reminder_id}\' not found"} 