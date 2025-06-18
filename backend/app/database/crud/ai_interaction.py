from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime, timedelta
from ..models.models import AI_Interaction
from ..schemas.schemas import AI_InteractionCreate

async def get_ai_interaction(db: AsyncSession, interaction_id: str) -> Optional[AI_Interaction]:
    result = await db.execute(select(AI_Interaction).where(AI_Interaction.id == interaction_id))
    return result.scalar_one_or_none()

async def get_ai_interactions_by_user(
    db: AsyncSession, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 100
) -> List[AI_Interaction]:
    result = await db.execute(select(AI_Interaction).where(
        AI_Interaction.user_id == user_id
    ).offset(skip).limit(limit))
    return list(result.scalars().all())

async def get_ai_interactions_by_intent(
    db: AsyncSession, 
    intent: str, 
    skip: int = 0, 
    limit: int = 100
) -> List[AI_Interaction]:
    result = await db.execute(select(AI_Interaction).where(
        AI_Interaction.intent == intent
    ).offset(skip).limit(limit))
    return list(result.scalars().all())

async def create_ai_interaction(db: AsyncSession, interaction: AI_InteractionCreate) -> AI_Interaction:
    db_interaction = AI_Interaction(**interaction.dict())
    db.add(db_interaction)
    await db.commit()
    await db.refresh(db_interaction)
    return db_interaction

async def get_recent_interactions(
    db: AsyncSession,
    user_id: str,
    hours: int = 24
) -> List[AI_Interaction]:
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    result = await db.execute(select(AI_Interaction).where(
        AI_Interaction.user_id == user_id,
        AI_Interaction.created_at >= cutoff_time
    ).order_by(AI_Interaction.created_at.desc()))
    return list(result.scalars().all()) 
