from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime
from ..models.models import Event
from ..schemas.schemas import EventCreate, EventUpdate

async def get_event(db: AsyncSession, event_id: str) -> Optional[Event]:
    result = await db.execute(select(Event).where(Event.id == event_id))
    return result.scalar_one_or_none()

async def get_events_by_user(db: AsyncSession, user_id: str, skip: int = 0, limit: int = 100) -> List[Event]:
    result = await db.execute(select(Event).where(Event.user_id == user_id).offset(skip).limit(limit))
    return list(result.scalars().all())

async def get_events_by_date_range(
    db: AsyncSession, 
    user_id: str, 
    start_date: datetime, 
    end_date: datetime
) -> List[Event]:
    result = await db.execute(select(Event).where(
        Event.user_id == user_id,
        Event.start_time >= start_date,
        Event.end_time <= end_date
    ))
    return list(result.scalars().all())

async def create_event(db: AsyncSession, event: EventCreate, user_id: str) -> Event:
    db_event = Event(
        **event.dict(),
        user_id=user_id
    )
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event

async def update_event(db: AsyncSession, event_id: str, event: EventUpdate) -> Optional[Event]:
    db_event = await get_event(db, event_id)
    if not db_event:
        return None
    
    update_data = event.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_event, key, value)
    
    await db.commit()
    await db.refresh(db_event)
    return db_event

async def delete_event(db: AsyncSession, event_id: str) -> bool:
    db_event = await get_event(db, event_id)
    if not db_event:
        return False
    
    await db.delete(db_event)
    await db.commit()
    return True 
