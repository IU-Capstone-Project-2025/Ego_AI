from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import httpx
import os
from typing import Optional

from app.database.session import get_db
from app.database import models
from app.utils.deps import get_current_user

router = APIRouter()

ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8001/chat")

class CalendarInterpretRequest(BaseModel):
    text: str

class ChatRequest(BaseModel):
    message: str
    calendar: Optional[list] = None

def serialize_event(event):
    return {
        "summary": event.title,
        "start": event.start_time.isoformat() if event.start_time else "",
        "end": event.end_time.isoformat() if event.end_time else "",
        "location": event.location or ""
    }

@router.post("/interpret")
async def interpret_and_create_event(
    request: CalendarInterpretRequest,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Получаем все события пользователя из базы
    result = await db.execute(
        models.Event.__table__.select().where(models.Event.user_id == current_user.id)
    )
    events = result.fetchall()
    calendar = [serialize_event(e) for e in [row for row in events]]
    print("calendar to send:", calendar)
    # Отправляем календарь и текст пользователя в chat.py
    payload = {
        "message": request.text,
        "calendar": calendar
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                ML_SERVICE_URL,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            ml_response_data = response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to the ML service: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting response from ML service: {e}")

    return ml_response_data
