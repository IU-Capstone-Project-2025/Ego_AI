import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exception_handlers import NotFoundError, DatabaseError, ForbiddenError
from app.database import models, schemas


class EventService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, event_id: uuid.UUID, current_user: models.User) -> Optional[models.Event]:
        """Получить событие по ID с проверкой прав."""
        result = await self.db.execute(select(models.Event).filter(models.Event.id == event_id))
        event = result.scalar_one_or_none()
        
        if not event:
            raise NotFoundError(f"Event with id {event_id} not found")
        if event.user_id != current_user.id:
            raise ForbiddenError("You are not authorized to access this event.")
            
        return event

    async def get_events_by_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[models.Event]:
        """Получить список событий пользователя"""
        result = await self.db.execute(select(models.Event).filter(models.Event.user_id == user_id).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_events_by_date_range(
        self, 
        user_id: uuid.UUID, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[models.Event]:
        """Получить события пользователя в заданном диапазоне дат"""
        result = await self.db.execute(select(models.Event).filter(
            models.Event.user_id == user_id,
            models.Event.start_time >= start_date,
            models.Event.end_time <= end_date
        ))
        return list(result.scalars().all())

    async def create(self, event_in: schemas.EventCreate, user_id: uuid.UUID) -> models.Event:
        """Создать новое событие"""
        try:
            event = models.Event(
                **event_in.model_dump(),
                user_id=user_id
            )
            self.db.add(event)
            await self.db.commit()
            await self.db.refresh(event)
            return event
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Error creating event: {str(e)}")

    async def update(self, event_id: uuid.UUID, event_in: schemas.EventUpdate, current_user: models.User) -> models.Event:
        """Обновить событие с проверкой прав."""
        event = await self.get_by_id(event_id, current_user) # The check is already here
        try:
            update_data = event_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(event, field, value)
            await self.db.commit()
            await self.db.refresh(event)
            return event
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Error updating event: {str(e)}")

    async def delete(self, event_id: uuid.UUID, current_user: models.User) -> None:
        """Удалить событие с проверкой прав."""
        event = await self.get_by_id(event_id, current_user)
        try:
            await self.db.delete(event)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Error deleting event: {str(e)}") 
