from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.services.event import EventService
from app.database.session import get_db
from app.database import schemas, models
from app.utils import deps

router = APIRouter()

@router.post("/", response_model=schemas.Event, status_code=status.HTTP_201_CREATED)
async def create_event(
    event: schemas.EventCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(deps.get_current_user)
):
    """Create an event for the current user."""
    event_service = EventService(db)
    return await event_service.create(event_in=event, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Event])
async def read_events_for_user(
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(deps.get_current_user),
    skip: int = 0, 
    limit: int = 100
):
    """Get all events for the current user."""
    event_service = EventService(db)
    return await event_service.get_events_by_user(user_id=current_user.id, skip=skip, limit=limit)

@router.get("/{event_id}", response_model=schemas.Event)
async def read_event(
    event_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(deps.get_current_user)
):
    """Get a specific event by its ID."""
    event_service = EventService(db)
    return await event_service.get_by_id(event_id=event_id, current_user=current_user)

@router.put("/{event_id}", response_model=schemas.Event)
async def update_event(
    event_id: uuid.UUID, 
    event: schemas.EventUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(deps.get_current_user)
):
    """Update an event."""
    event_service = EventService(db)
    return await event_service.update(event_id=event_id, event_in=event, current_user=current_user)

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(deps.get_current_user)
):
    """Delete an event."""
    event_service = EventService(db)
    await event_service.delete(event_id=event_id, current_user=current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT) 
