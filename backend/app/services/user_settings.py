from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exception_handlers import NotFoundError, DatabaseError
from app.database.models.models import User_Settings
from app.database.schemas.schemas import User_SettingsCreate, User_SettingsUpdate


class User_SettingsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: str) -> Optional[User_Settings]:
        """Получить настройки пользователя по ID пользователя"""
        result = await self.db.execute(select(User_Settings).filter(User_Settings.user_id == user_id))
        settings = result.scalar_one_or_none()
        if not settings:
            raise NotFoundError(f"User settings for user_id {user_id} not found")
        return settings

    async def create(self, settings_in: User_SettingsCreate) -> User_Settings:
        """Создать новые настройки пользователя"""
        try:
            settings = User_Settings(**settings_in.model_dump())
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)
            return settings
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Error creating user settings: {str(e)}")

    async def update(self, user_id: str, settings_in: User_SettingsUpdate) -> User_Settings:
        """Обновить настройки пользователя"""
        settings = await self.get_by_user_id(user_id)
        try:
            update_data = settings_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(settings, field, value)
            await self.db.commit()
            await self.db.refresh(settings)
            return settings
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Error updating user settings: {str(e)}")

    async def delete(self, user_id: str) -> None:
        """Удалить настройки пользователя"""
        settings = await self.get_by_user_id(user_id)
        try:
            await self.db.delete(settings)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Error deleting user settings: {str(e)}") 
