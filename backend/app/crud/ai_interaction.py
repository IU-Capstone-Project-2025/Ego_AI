from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from ..models.models import AI_Interaction
from ..schemas.schemas import AI_InteractionCreate

def get_ai_interaction(db: Session, interaction_id: str) -> Optional[AI_Interaction]:
    return db.query(AI_Interaction).filter(AI_Interaction.id == interaction_id).first()

def get_ai_interactions_by_user(
    db: Session, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 100
) -> List[AI_Interaction]:
    return db.query(AI_Interaction).filter(
        AI_Interaction.user_id == user_id
    ).offset(skip).limit(limit).all()

def get_ai_interactions_by_intent(
    db: Session, 
    intent: str, 
    skip: int = 0, 
    limit: int = 100
) -> List[AI_Interaction]:
    return db.query(AI_Interaction).filter(
        AI_Interaction.intent == intent
    ).offset(skip).limit(limit).all()

def create_ai_interaction(db: Session, interaction: AI_InteractionCreate) -> AI_Interaction:
    db_interaction = AI_Interaction(**interaction.dict())
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction

def get_recent_interactions(
    db: Session,
    user_id: str,
    hours: int = 24
) -> List[AI_Interaction]:
    cutoff_time = datetime.utcnow() - datetime.timedelta(hours=hours)
    return db.query(AI_Interaction).filter(
        AI_Interaction.user_id == user_id,
        AI_Interaction.created_at >= cutoff_time
    ).order_by(AI_Interaction.created_at.desc()).all() 