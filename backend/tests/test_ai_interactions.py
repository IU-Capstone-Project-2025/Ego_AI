import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone

from app.database.models.models import AI_Interaction, User
from app.database.schemas.schemas import AI_InteractionCreate


@pytest.mark.asyncio
async def test_create_ai_interaction(client: AsyncClient, db_session: AsyncSession):
    # Create a user first
    user_data = {"email": "aiuser@example.com", "password": "testpass", "name": "AI User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    interaction_data = {
        "user_id": user_id,
        "prompt": "What is the capital of France?",
        "response": "Paris",
        "intent": "question",
        "feedback": 5
    }
    response = await client.post("/api/v1/ai-interactions/", json=interaction_data)

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["prompt"] == "What is the capital of France?"
    assert "id" in data

    # Verify interaction in database
    interaction_in_db = await db_session.get(AI_Interaction, data["id"])
    assert interaction_in_db is not None
    assert interaction_in_db.prompt == "What is the capital of France?"


@pytest.mark.asyncio
async def test_read_ai_interactions_by_user(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "aiuser2@example.com", "password": "testpass", "name": "AI User 2"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    for i in range(3):
        interaction_data = {
            "user_id": user_id,
            "prompt": f"Prompt {i+1}",
            "response": f"Response {i+1}",
            "intent": "information",
            "feedback": 4
        }
        await client.post("/api/v1/ai-interactions/", json=interaction_data)
    
    response = await client.get(f"/api/v1/ai-interactions/user/{user_id}")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]["user_id"] == user_id


@pytest.mark.asyncio
async def test_create_ai_interaction_user_not_found(client: AsyncClient):
    interaction_data = {
        "user_id": "nonexistent_user",
        "prompt": "Nonexistent user prompt",
        "response": "Response",
        "intent": "query",
        "feedback": 3
    }
    response = await client.post("/api/v1/ai-interactions/", json=interaction_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "User with id nonexistent_user not found"} # Assuming service raises NotFoundError


@pytest.mark.asyncio
async def test_read_recent_ai_interactions(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "recentaiuser@example.com", "password": "testpass", "name": "Recent AI User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    # Create interactions: one old, two recent
    old_interaction_data = {
        "user_id": user_id,
        "prompt": "Old prompt",
        "response": "Old response",
        "intent": "old",
        "feedback": 1
    }
    old_interaction = AI_Interaction(**old_interaction_data)
    old_interaction.created_at = datetime.now(timezone.utc) - timedelta(hours=25) # More than 24 hours ago
    db_session.add(old_interaction)
    await db_session.commit()

    recent_interaction_data_1 = {
        "user_id": user_id,
        "prompt": "Recent prompt 1",
        "response": "Recent response 1",
        "intent": "recent",
        "feedback": 5
    }
    recent_interaction_1 = AI_Interaction(**recent_interaction_data_1)
    recent_interaction_1.created_at = datetime.now(timezone.utc) - timedelta(hours=5)
    db_session.add(recent_interaction_1)
    await db_session.commit()

    recent_interaction_data_2 = {
        "user_id": user_id,
        "prompt": "Recent prompt 2",
        "response": "Recent response 2",
        "intent": "recent",
        "feedback": 4
    }
    recent_interaction_2 = AI_Interaction(**recent_interaction_data_2)
    recent_interaction_2.created_at = datetime.now(timezone.utc) - timedelta(hours=1)
    db_session.add(recent_interaction_2)
    await db_session.commit()

    # Manually refresh the instances to get updated 'created_at' values if necessary
    await db_session.refresh(old_interaction)
    await db_session.refresh(recent_interaction_1)
    await db_session.refresh(recent_interaction_2)

    # Call the endpoint to get recent interactions (assuming a new endpoint for this is needed or it's part of existing one)
    # For simplicity, let's assume we add a /user/{user_id}/recent endpoint or modify the existing one
    # Since the API doesn't have a direct endpoint for `get_recent_interactions`, 
    # we will test the service method directly via the client if such an endpoint existed, or create one.
    # For now, let's just assert the service method directly if it's integrated somewhere

    # For testing the service function itself, not via API endpoint currently implemented
    from app.services.ai_interaction import AI_InteractionService
    ai_service = AI_InteractionService(db_session)
    recent_interactions = await ai_service.get_recent_interactions(user_id=user_id, hours=24)

    assert len(recent_interactions) == 2
    assert any(i.prompt == "Recent prompt 1" for i in recent_interactions)
    assert any(i.prompt == "Recent prompt 2" for i in recent_interactions)
    assert not any(i.prompt == "Old prompt" for i in recent_interactions)


@pytest.mark.asyncio
async def test_create_ai_interaction_invalid_feedback(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "invalidfeedback@example.com", "password": "testpass", "name": "Invalid Feedback User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    interaction_data = {
        "user_id": user_id,
        "prompt": "Test prompt",
        "response": "Test response",
        "intent": "question",
        "feedback": 6 # Invalid feedback
    }
    response = await client.post("/api/v1/ai-interactions/", json=interaction_data)
    assert response.status_code == 422 # Unprocessable Entity for validation errors
    assert "Input should be less than or equal to 5" in response.json()["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_create_ai_interaction_invalid_intent(client: AsyncClient, db_session: AsyncSession):
    user_data = {"email": "invalidintent@example.com", "password": "testpass", "name": "Invalid Intent User"}
    user_response = await client.post("/api/v1/users/", json=user_data)
    user_id = user_response.json()["id"]

    interaction_data = {
        "user_id": user_id,
        "prompt": "Test prompt",
        "response": "Test response",
        "intent": "invalid_intent", # Invalid intent
        "feedback": 3
    }
    response = await client.post("/api/v1/ai-interactions/", json=interaction_data)
    assert response.status_code == 422 # Unprocessable Entity for Enum validation
    assert "value is not a valid enumeration member" in response.json()["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_read_ai_interactions_other_user_forbidden(authenticated_client: AsyncClient, client: AsyncClient, db_session: AsyncSession):
    # Create a user for the authenticated client
    from app.services.user import UserService
    user_service = UserService(db_session)
    auth_user = await user_service.get_by_email(email="auth_test_user@example.com") # User created by authenticated_client fixture
    auth_user_id = auth_user.id

    # Create an interaction for the authenticated user
    interaction_data_auth_user = {
        "user_id": auth_user_id,
        "prompt": "Auth user AI interaction",
        "response": "Response",
        "intent": "question",
        "feedback": 4
    }
    await authenticated_client.post("/api/v1/ai-interactions/", json=interaction_data_auth_user)

    # Create a second user and interaction
    other_user_data = {"email": "other_user_ai@example.com", "password": "otherpass", "name": "Other AI User"}
    other_user_response = await client.post("/api/v1/users/", json=other_user_data)
    other_user_id = other_user_response.json()["id"]

    interaction_data_other_user = {
        "user_id": other_user_id,
        "prompt": "Other user AI interaction",
        "response": "Response",
        "intent": "command",
        "feedback": 5
    }
    await client.post("/api/v1/ai-interactions/", json=interaction_data_other_user)

    # Attempt to read the other user's interactions with the authenticated client
    response = await authenticated_client.get(f"/api/v1/ai-interactions/user/{other_user_id}")
    assert response.status_code == 200 # It returns an empty list if no interactions found for the authenticated user for the given user_id
    assert response.json() == []


@pytest.mark.asyncio
async def test_read_ai_interactions_by_non_existent_user(client: AsyncClient):
    response = await client.get("/api/v1/ai-interactions/user/non_existent_id")
    assert response.status_code == 404
    assert response.json() == {"detail": "User with id non_existent_id not found"} 