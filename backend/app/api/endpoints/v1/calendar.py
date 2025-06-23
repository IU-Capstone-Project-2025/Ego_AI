import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import httpx
import os
from datetime import datetime, timedelta

from app.database.session import get_db
from app.database import models, schemas
from app.utils.deps import get_current_user
from app.services.event import EventService

router = APIRouter()

ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8001/chat")

class CalendarInterpretRequest(BaseModel):
    text: str

def parse_event(text):
    for line in text.splitlines():
        match = re.match(r"-\s*(.+?)\s+from\s+(.+?)\s+to\s+(.+?)\s+at\s+(.+)", line)
        if match:
            title = match.group(1).strip()
            start_str = match.group(2).strip()
            end_str = match.group(3).strip()
            location = match.group(4).strip()
            try:
                start_time = datetime.strptime(start_str, "%B %d, %Y %I:%M %p")
                end_time = datetime.strptime(end_str, "%I:%M %p").replace(
                    year=start_time.year, month=start_time.month, day=start_time.day
                )
                if end_time < start_time:
                    end_time += timedelta(days=1)
            except Exception:
                start_time = datetime.now()
                end_time = start_time + timedelta(hours=1)
            return title, "", start_time, end_time, location
    now = datetime.now()
    return text.strip().splitlines()[0], "", now, now + timedelta(hours=1), ""

@router.post("/interpret", response_model=schemas.Event)
async def interpret_and_create_event(
    request: CalendarInterpretRequest,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                ML_SERVICE_URL,
                json={"message": request.text},
                timeout=30.0
            )
            response.raise_for_status()
            ml_response_data = response.json()
            ai_text = ml_response_data.get("response", "")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to the ML service: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting response from ML service: {e}")

    title, description, start_dt, end_dt, location = parse_event(ai_text)

    event_service = EventService(db)
    event_create = schemas.EventCreate(
        title=title,
        description=description,
        start_time=start_dt,
        end_time=end_dt,
        location=location
    )
    db_event = await event_service.create(event_in=event_create, user_id=current_user.id)
    return db_event