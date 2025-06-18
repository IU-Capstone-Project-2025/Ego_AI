from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.exception_handlers import NotFoundError, DatabaseError, ForbiddenError, BadRequestError
from app.database import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[models.User]:
        """Получить пользователя по ID"""
        result = await self.db.execute(select(models.User).filter(models.User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[models.User]:
        """Получить пользователя по email"""
        result = await self.db.execute(select(models.User).filter(models.User.email == email))
        return result.scalar_one_or_none()

    async def create(self, user_in: schemas.UserCreate) -> models.User:
        """Создать нового пользователя с проверкой на дубликат email."""
        existing_user = await self.get_by_email(email=user_in.email)
        if existing_user:
            raise BadRequestError(f"User with email {user_in.email} already exists.")
        
        hashed_password = self._hash_password(user_in.password)
        user_data = user_in.model_dump()
        user_data['pass_hash'] = hashed_password
        del user_data['password'] # Удаляем пароль в открытом виде

        try:
            user = models.User(**user_data)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Error creating user: {str(e)}")

    async def update(self, user_id: uuid.UUID, user_in: schemas.UserUpdate, current_user: models.User) -> models.User:
        """Обновить пользователя с проверкой прав."""
        if current_user.id != user_id:
            raise ForbiddenError("You are not authorized to update this user.")

        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")
            
        try:
            update_data = user_in.model_dump(exclude_unset=True)
            if 'password' in update_data:
                update_data['pass_hash'] = self._hash_password(update_data['password'])
                del update_data['password']

            for field, value in update_data.items():
                setattr(user, field, value)
            
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Error updating user: {str(e)}")

    async def delete(self, user_id: uuid.UUID, current_user: models.User) -> None:
        """Удалить пользователя с проверкой прав."""
        if current_user.id != user_id:
            raise ForbiddenError("You are not authorized to delete this user.")

        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")

        try:
            await self.db.delete(user)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Error deleting user: {str(e)}")

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[models.User]:
        """Получить список пользователей (может требовать прав администратора)."""
        result = await self.db.execute(select(models.User).offset(skip).limit(limit))
        return list(result.scalars().all())
