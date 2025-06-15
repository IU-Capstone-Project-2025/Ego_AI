from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database.database import get_db
from app.crud import (
    create_user, get_user, get_users, update_user, delete_user,
    create_event, get_event, get_events_by_user, update_event, delete_event,
    create_reminder, get_reminder, get_reminders_by_event, update_reminder, delete_reminder,
    create_ai_interaction, get_ai_interaction, get_ai_interactions_by_user,
    create_user_settings, get_user_settings, update_user_settings, delete_user_settings
)
from app.schemas.schemas import (
    UserCreate, User, UserUpdate,
    EventCreate, Event, EventUpdate,
    ReminderCreate, Reminder, ReminderUpdate,
    AI_InteractionCreate, AI_Interaction,
    User_SettingsCreate, User_Settings, User_SettingsUpdate
)

router = APIRouter()

# User endpoints
@router.post("/users/", response_model=User)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db=db, user=user)

@router.get("/users/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=User)
def read_user(user_id: str, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/users/{user_id}", response_model=User)
def update_user_endpoint(user_id: str, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = update_user(db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/users/{user_id}")
def delete_user_endpoint(user_id: str, db: Session = Depends(get_db)):
    success = delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# Event endpoints
@router.post("/events/", response_model=Event)
def create_event_endpoint(event: EventCreate, user_id: str, db: Session = Depends(get_db)):
    return create_event(db=db, event=event, user_id=user_id)

@router.get("/events/user/{user_id}", response_model=List[Event])
def read_events_by_user(user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = get_events_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return events

@router.get("/events/{event_id}", response_model=Event)
def read_event(event_id: str, db: Session = Depends(get_db)):
    db_event = get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event

@router.put("/events/{event_id}", response_model=Event)
def update_event_endpoint(event_id: str, event: EventUpdate, db: Session = Depends(get_db)):
    db_event = update_event(db, event_id=event_id, event=event)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event

@router.delete("/events/{event_id}")
def delete_event_endpoint(event_id: str, db: Session = Depends(get_db)):
    success = delete_event(db, event_id=event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully"}

# Reminder endpoints
@router.post("/reminders/", response_model=Reminder)
def create_reminder_endpoint(reminder: ReminderCreate, db: Session = Depends(get_db)):
    return create_reminder(db=db, reminder=reminder)

@router.get("/reminders/event/{event_id}", response_model=List[Reminder])
def read_reminders_by_event(event_id: str, db: Session = Depends(get_db)):
    reminders = get_reminders_by_event(db, event_id=event_id)
    return reminders

@router.get("/reminders/{reminder_id}", response_model=Reminder)
def read_reminder(reminder_id: str, db: Session = Depends(get_db)):
    db_reminder = get_reminder(db, reminder_id=reminder_id)
    if db_reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return db_reminder

@router.put("/reminders/{reminder_id}", response_model=Reminder)
def update_reminder_endpoint(reminder_id: str, reminder: ReminderUpdate, db: Session = Depends(get_db)):
    db_reminder = update_reminder(db, reminder_id=reminder_id, reminder=reminder)
    if db_reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return db_reminder

@router.delete("/reminders/{reminder_id}")
def delete_reminder_endpoint(reminder_id: str, db: Session = Depends(get_db)):
    success = delete_reminder(db, reminder_id=reminder_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Reminder deleted successfully"}

# AI Interaction endpoints
@router.post("/ai-interactions/", response_model=AI_Interaction)
def create_ai_interaction_endpoint(interaction: AI_InteractionCreate, db: Session = Depends(get_db)):
    return create_ai_interaction(db=db, interaction=interaction)

@router.get("/ai-interactions/user/{user_id}", response_model=List[AI_Interaction])
def read_ai_interactions_by_user(user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    interactions = get_ai_interactions_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return interactions

# User Settings endpoints
@router.post("/user-settings/", response_model=User_Settings)
def create_user_settings_endpoint(settings: User_SettingsCreate, db: Session = Depends(get_db)):
    return create_user_settings(db=db, settings=settings)

@router.get("/user-settings/{user_id}", response_model=User_Settings)
def read_user_settings(user_id: str, db: Session = Depends(get_db)):
    db_settings = get_user_settings(db, user_id=user_id)
    if db_settings is None:
        raise HTTPException(status_code=404, detail="User settings not found")
    return db_settings

@router.put("/user-settings/{user_id}", response_model=User_Settings)
def update_user_settings_endpoint(user_id: str, settings: User_SettingsUpdate, db: Session = Depends(get_db)):
    db_settings = update_user_settings(db, user_id=user_id, settings=settings)
    if db_settings is None:
        raise HTTPException(status_code=404, detail="User settings not found")
    return db_settings

@router.delete("/user-settings/{user_id}")
def delete_user_settings_endpoint(user_id: str, db: Session = Depends(get_db)):
    success = delete_user_settings(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User settings not found")
    return {"message": "User settings deleted successfully"} 