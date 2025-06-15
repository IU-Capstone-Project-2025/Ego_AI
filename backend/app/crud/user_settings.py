from sqlalchemy.orm import Session
from typing import Optional
from ..models.models import User_Settings
from ..schemas.schemas import User_SettingsCreate, User_SettingsUpdate

def get_user_settings(db: Session, user_id: str) -> Optional[User_Settings]:
    return db.query(User_Settings).filter(User_Settings.user_id == user_id).first()

def create_user_settings(db: Session, settings: User_SettingsCreate) -> User_Settings:
    db_settings = User_Settings(**settings.dict())
    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    return db_settings

def update_user_settings(
    db: Session, 
    user_id: str, 
    settings: User_SettingsUpdate
) -> Optional[User_Settings]:
    db_settings = get_user_settings(db, user_id)
    if not db_settings:
        return None
    
    update_data = settings.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_settings, key, value)
    
    db.commit()
    db.refresh(db_settings)
    return db_settings

def delete_user_settings(db: Session, user_id: str) -> bool:
    db_settings = get_user_settings(db, user_id)
    if not db_settings:
        return False
    
    db.delete(db_settings)
    db.commit()
    return True 