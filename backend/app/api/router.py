from fastapi import APIRouter
from app.auth import google
from app.api.endpoints.v1 import (
    user,
    event,
    reminder,
    ai_interaction,
    user_settings,
    calendar,
    llm_chat,
)

api_router = APIRouter()

api_router.include_router(google.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(event.router, prefix="/events", tags=["events"])
api_router.include_router(reminder.reminder_router, prefix="/reminders", tags=["reminders"])
api_router.include_router(ai_interaction.ai_interaction_router, prefix="/ai", tags=["ai"])
api_router.include_router(user_settings.user_settings_router, prefix="/settings", tags=["settings"])
#api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
api_router.include_router(llm_chat.router, prefix="/llm_chat", tags=["llm_chat"])
