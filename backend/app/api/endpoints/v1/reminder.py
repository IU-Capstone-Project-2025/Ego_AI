from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.session import get_db
from app.database.schemas.schemas import ReminderCreate, Reminder, ReminderUpdate, User # Import User schema for current_user type hint
from app.utils.deps import get_current_user
from app.services.reminder import ReminderService # Import ReminderService

reminder_router = APIRouter()

@reminder_router.post("/reminders/", response_model=Reminder)
async def create_reminder_endpoint(reminder: ReminderCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    reminder_service = ReminderService(db)
    return await reminder_service.create(reminder_in=reminder)

@reminder_router.get("/reminders/event/{event_id}", response_model=List[Reminder])
async def read_reminders_by_event(event_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    reminder_service = ReminderService(db)
    reminders = await reminder_service.get_reminders_by_event(event_id=event_id)
    return reminders

@reminder_router.get("/reminders/{reminder_id}", response_model=Reminder)
async def read_reminder(reminder_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    reminder_service = ReminderService(db)
    db_reminder = await reminder_service.get_by_id(reminder_id=reminder_id)
    return db_reminder

@reminder_router.put("/reminders/{reminder_id}", response_model=Reminder)
async def update_reminder_endpoint(reminder_id: str, reminder: ReminderUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    reminder_service = ReminderService(db)
    db_reminder = await reminder_service.update(reminder_id=reminder_id, reminder_in=reminder)
    return db_reminder

@reminder_router.delete("/reminders/{reminder_id}")
async def delete_reminder_endpoint(reminder_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    reminder_service = ReminderService(db)
    await reminder_service.delete(reminder_id=reminder_id)
    return {"message": "Reminder deleted successfully"} 
