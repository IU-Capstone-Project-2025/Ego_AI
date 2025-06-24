from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import crud, schemas
from app.utils.deps import get_db, get_current_user
from app.services.llm_chat import LLMChatService

router = APIRouter()

# Helper function for LLM prompt construction (can be moved to service later if more complex)
def build_system_prompt(user_id: str):
    # In a real application, calendar data would be fetched dynamically for the user
    # For this example, we'll use a placeholder or potentially fetch user-specific data
    # if it's integrated with a database for calendar events.
    calendar_context = "" # Placeholder for calendar events for the specific user
    # You would fetch calendar events for the given user_id from the database here
    # For now, let's just make a simple system prompt.

    # Example: Fetch user-specific settings or preferences from the DB if needed
    # user_settings = crud.user_settings.get_by_user_id(db, user_id)

    content = (
        "You are a helpful assistant who answers questions. "
        "Only respond based on the provided context and general knowledge. "
        f"User ID: {user_id}\n"
        f"Here is some context: {calendar_context}"
    )
    return {"role": "system", "content": content}

@router.post("/chat", response_model=schemas.LLM_ChatResponse)
def chat_with_llm(
    req: schemas.LLM_ChatRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    llm_service = LLMChatService()
    system_prompt = build_system_prompt(str(current_user.id)) # Pass user ID to system prompt
    messages = [system_prompt, {"role": "user", "content": req.message}]

    try:
        reply = llm_service.chat(messages)
        return schemas.LLM_ChatResponse(response=reply)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}") 