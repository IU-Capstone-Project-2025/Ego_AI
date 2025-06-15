from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from ..models.models import Event
from ..schemas.schemas import EventCreate, EventUpdate

def get_event(db: Session, event_id: str) -> Optional[Event]:
    return db.query(Event).filter(Event.id == event_id).first()

def get_events_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Event]:
    return db.query(Event).filter(Event.user_id == user_id).offset(skip).limit(limit).all()

def get_events_by_date_range(
    db: Session, 
    user_id: str, 
    start_date: datetime, 
    end_date: datetime
) -> List[Event]:
    return db.query(Event).filter(
        Event.user_id == user_id,
        Event.start_time >= start_date,
        Event.end_time <= end_date
    ).all()

def create_event(db: Session, event: EventCreate, user_id: str) -> Event:
    db_event = Event(
        **event.dict(),
        user_id=user_id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def update_event(db: Session, event_id: str, event: EventUpdate) -> Optional[Event]:
    db_event = get_event(db, event_id)
    if not db_event:
        return None
    
    update_data = event.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_event, key, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event

def delete_event(db: Session, event_id: str) -> bool:
    db_event = get_event(db, event_id)
    if not db_event:
        return False
    
    db.delete(db_event)
    db.commit()
    return True 