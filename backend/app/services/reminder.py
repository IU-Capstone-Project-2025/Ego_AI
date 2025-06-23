from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exception_handlers import NotFoundError, DatabaseError
from app.database.models.models import Reminder
from app.database.schemas.schemas import ReminderCreate, ReminderUpdate


class ReminderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, reminder_id: str) -> Optional[Reminder]:
        """Получить напоминание по ID"""
        result = await self.db.execute(select(Reminder).filter(Reminder.id == reminder_id))
        reminder = result.scalar_one_or_none()
        if not reminder:
            raise NotFoundError(f"Reminder with id {reminder_id} not found")
        return reminder

    async def get_reminders_by_event(self, event_id: str) -> List[Reminder]:
        """Получить список напоминаний по ID события"""
        result = await self.db.execute(select(Reminder).filter(Reminder.event_id == event_id))
        return list(result.scalars().all())

    async def get_upcoming_reminders(
        self, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[Reminder]:
        """Получить предстоящие напоминания в заданном диапазоне времени"""
        result = await self.db.execute(select(Reminder).filter(
            Reminder.remind_at >= start_time,
            Reminder.remind_at <= end_time
        ))
        return list(result.scalars().all())

    async def create(self, reminder_in: ReminderCreate) -> Reminder:
        """Создать новое напоминание"""
        try:
            reminder = Reminder(**reminder_in.model_dump())
            self.db.add(reminder)
            await self.db.commit()
            await self.db.refresh(reminder)
            return reminder
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Error creating reminder: {str(e)}")

    async def update(self, reminder_id: str, reminder_in: ReminderUpdate) -> Reminder:
        """Обновить напоминание"""
        reminder = await self.get_by_id(reminder_id)
        try:
            update_data = reminder_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(reminder, field, value)
            await self.db.commit()
            await self.db.refresh(reminder)
            return reminder
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Error updating reminder: {str(e)}")

    async def delete(self, reminder_id: str) -> None:
        """Удалить напоминание"""
        reminder = await self.get_by_id(reminder_id)
        try:
            await self.db.delete(reminder)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Error deleting reminder: {str(e)}")

    async def delete_reminders_by_event(self, event_id: str) -> None:
        """Удалить все напоминания, связанные с событием"""
        result = await self.db.execute(select(Reminder).where(Reminder.event_id == event_id))
        reminders = result.scalars().all()
        for reminder in reminders:
            await self.db.delete(reminder)
        await self.db.commit() 
