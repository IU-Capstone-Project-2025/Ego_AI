from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exception_handlers import NotFoundError, DatabaseError
from app.database.models.models import AI_Interaction
from app.database.schemas.schemas import AI_InteractionCreate


class AI_InteractionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, interaction_id: str) -> Optional[AI_Interaction]:
        """Получить взаимодействие с ИИ по ID"""
        result = await self.db.execute(select(AI_Interaction).filter(AI_Interaction.id == interaction_id))
        interaction = result.scalar_one_or_none()
        if not interaction:
            raise NotFoundError(f"AI Interaction with id {interaction_id} not found")
        return interaction

    async def get_ai_interactions_by_user(
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[AI_Interaction]:
        """Получить список взаимодействий с ИИ по ID пользователя"""
        result = await self.db.execute(select(AI_Interaction).filter(
            AI_Interaction.user_id == user_id
        ).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_ai_interactions_by_intent(
        self, 
        intent: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[AI_Interaction]:
        """Получить список взаимодействий с ИИ по намерению"""
        result = await self.db.execute(select(AI_Interaction).filter(
            AI_Interaction.intent == intent
        ).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, interaction_in: AI_InteractionCreate) -> AI_Interaction:
        """Создать новое взаимодействие с ИИ"""
        try:
            interaction = AI_Interaction(**interaction_in.model_dump())
            self.db.add(interaction)
            await self.db.commit()
            await self.db.refresh(interaction)
            return interaction
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Error creating AI Interaction: {str(e)}")

    async def get_recent_interactions(
        self,
        user_id: str,
        hours: int = 24
    ) -> List[AI_Interaction]:
        """Получить последние взаимодействия с ИИ для пользователя"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        result = await self.db.execute(select(AI_Interaction).filter(
            AI_Interaction.user_id == user_id,
            AI_Interaction.created_at >= cutoff_time
        ).order_by(AI_Interaction.created_at.desc()))
        return list(result.scalars().all()) 
