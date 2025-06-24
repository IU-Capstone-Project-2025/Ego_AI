from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.database.schemas.schemas import User_SettingsCreate, User_Settings, User_SettingsUpdate, User # Import User schema for current_user type hint
from app.utils.deps import get_current_user
from app.services.user_settings import User_SettingsService # Import User_SettingsService

user_settings_router = APIRouter()

@user_settings_router.post("/user-settings/", response_model=User_Settings)
async def create_user_settings_endpoint(settings: User_SettingsCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_settings_service = User_SettingsService(db)
    return await user_settings_service.create(settings_in=settings)

@user_settings_router.get("/user-settings/{user_id}", response_model=User_Settings)
async def read_user_settings(user_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_settings_service = User_SettingsService(db)
    db_settings = await user_settings_service.get_by_user_id(user_id=user_id)
    return db_settings

@user_settings_router.put("/user-settings/{user_id}", response_model=User_Settings)
async def update_user_settings_endpoint(user_id: str, settings: User_SettingsUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_settings_service = User_SettingsService(db)
    db_settings = await user_settings_service.update(user_id=user_id, settings_in=settings)
    return db_settings

@user_settings_router.delete("/user-settings/{user_id}")
async def delete_user_settings_endpoint(user_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_settings_service = User_SettingsService(db)
    await user_settings_service.delete(user_id=user_id)
    return {"message": "User settings deleted successfully"} 
