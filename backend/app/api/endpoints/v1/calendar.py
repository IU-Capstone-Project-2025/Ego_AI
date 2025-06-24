from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import httpx
import os
from typing import Optional, List
from datetime import datetime
import uuid
from fastapi.encoders import jsonable_encoder

from app.database.session import get_db
from app.database import models, schemas
from app.utils.deps import get_current_user
from app.services.event import EventService

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

    result = await db.execute(
        models.Event.__table__.select().where(models.Event.user_id == current_user.id)
    )
    events = result.fetchall()
    calendar = [serialize_event(e) for e in [row for row in events]]
    print("calendar to send:", calendar)
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

@router.get("/get_tasks", response_model=List[schemas.Event])
async def get_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    event_service = EventService(db)
    events = await event_service.get_events_by_user(uuid.UUID(str(current_user.id)))
    return events

@router.post("/set_task", response_model=schemas.Event)
async def set_task(
    event_in: schemas.EventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    event_service = EventService(db)
    created_event = await event_service.create(event_in, uuid.UUID(str(current_user.id)))
    return created_event

@router.delete("/delete_task", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    event_id: uuid.UUID,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event_service = EventService(db)
    await event_service.delete(event_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

class GetTasksByTimeRequest(BaseModel):
    start_time: datetime
    end_time: datetime

@router.post("/get_tasks_by_time", response_model=List[schemas.Event])
async def get_tasks_by_time(
    time_range: GetTasksByTimeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    event_service = EventService(db)
    events = await event_service.get_events_by_date_range(uuid.UUID(str(current_user.id)), time_range.start_time, time_range.end_time)
    return events


@router.put("/update_task/{event_id}", response_model=schemas.Event)
async def update_task(
    event_id: uuid.UUID,
    event_in: schemas.EventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    event_service = EventService(db)
    updated_event = await event_service.update(event_id, event_in, current_user)
    return updated_event
