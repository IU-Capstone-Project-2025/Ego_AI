from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from ..models.models import User_Settings
from ..schemas.schemas import User_SettingsCreate, User_SettingsUpdate

async def get_user_settings(db: AsyncSession, user_id: str) -> Optional[User_Settings]:
    result = await db.execute(select(User_Settings).where(User_Settings.user_id == user_id))
    return result.scalar_one_or_none()

async def create_user_settings(db: AsyncSession, settings: User_SettingsCreate) -> User_Settings:
    db_settings = User_Settings(**settings.dict())
    db.add(db_settings)
    await db.commit()
    await db.refresh(db_settings)
    return db_settings

async def update_user_settings(
    db: AsyncSession, 
    user_id: str, 
    settings: User_SettingsUpdate
) -> Optional[User_Settings]:
    db_settings = await get_user_settings(db, user_id)
    if not db_settings:
        return None
    
    update_data = settings.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_settings, key, value)
    
    await db.commit()
    await db.refresh(db_settings)
    return db_settings

async def delete_user_settings(db: AsyncSession, user_id: str) -> bool:
    db_settings = await get_user_settings(db, user_id)
    if not db_settings:
        return False
    
    await db.delete(db_settings)
    await db.commit()
    return True 
