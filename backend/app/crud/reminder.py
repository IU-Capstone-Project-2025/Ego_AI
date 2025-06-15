from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from ..models.models import Reminder
from ..schemas.schemas import ReminderCreate, ReminderUpdate

def get_reminder(db: Session, reminder_id: str) -> Optional[Reminder]:
    return db.query(Reminder).filter(Reminder.id == reminder_id).first()

def get_reminders_by_event(db: Session, event_id: str) -> List[Reminder]:
    return db.query(Reminder).filter(Reminder.event_id == event_id).all()

def get_upcoming_reminders(
    db: Session, 
    start_time: datetime, 
    end_time: datetime
) -> List[Reminder]:
    return db.query(Reminder).filter(
        Reminder.remind_at >= start_time,
        Reminder.remind_at <= end_time
    ).all()

def create_reminder(db: Session, reminder: ReminderCreate) -> Reminder:
    db_reminder = Reminder(**reminder.dict())
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

def update_reminder(db: Session, reminder_id: str, reminder: ReminderUpdate) -> Optional[Reminder]:
    db_reminder = get_reminder(db, reminder_id)
    if not db_reminder:
        return None
    
    update_data = reminder.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_reminder, key, value)
    
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

def delete_reminder(db: Session, reminder_id: str) -> bool:
    db_reminder = get_reminder(db, reminder_id)
    if not db_reminder:
        return False
    
    db.delete(db_reminder)
    db.commit()
    return True

def delete_reminders_by_event(db: Session, event_id: str) -> bool:
    db.query(Reminder).filter(Reminder.event_id == event_id).delete()
    db.commit()
    return True 