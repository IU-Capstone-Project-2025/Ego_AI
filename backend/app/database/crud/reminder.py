from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime
from ..models.models import Reminder
from ..schemas.schemas import ReminderCreate, ReminderUpdate

async def get_reminder(db: AsyncSession, reminder_id: str) -> Optional[Reminder]:
    result = await db.execute(select(Reminder).where(Reminder.id == reminder_id))
    return result.scalar_one_or_none()

async def get_reminders_by_event(db: AsyncSession, event_id: str) -> List[Reminder]:
    result = await db.execute(select(Reminder).where(Reminder.event_id == event_id))
    return list(result.scalars().all())

async def get_upcoming_reminders(
    db: AsyncSession,
    start_time: datetime, 
    end_time: datetime
) -> List[Reminder]:
    result = await db.execute(select(Reminder).where(
        Reminder.remind_at >= start_time,
        Reminder.remind_at <= end_time
    ))
    return list(result.scalars().all())

async def create_reminder(db: AsyncSession, reminder: ReminderCreate) -> Reminder:
    db_reminder = Reminder(**reminder.dict())
    db.add(db_reminder)
    await db.commit()
    await db.refresh(db_reminder)
    return db_reminder

async def update_reminder(db: AsyncSession, reminder_id: str, reminder: ReminderUpdate) -> Optional[Reminder]:
    db_reminder = await get_reminder(db, reminder_id)
    if not db_reminder:
        return None
    
    update_data = reminder.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_reminder, key, value)
    
    await db.commit()
    await db.refresh(db_reminder)
    return db_reminder

async def delete_reminder(db: AsyncSession, reminder_id: str) -> bool:
    db_reminder = await get_reminder(db, reminder_id)
    if not db_reminder:
        return False
    
    await db.delete(db_reminder)
    await db.commit()
    return True

async def delete_reminders_by_event(db: AsyncSession, event_id: str) -> bool:
    result = await db.execute(select(Reminder).where(Reminder.event_id == event_id))
    reminders = result.scalars().all()
    for reminder in reminders:
        await db.delete(reminder)
    await db.commit()
    return True 
