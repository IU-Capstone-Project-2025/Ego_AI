from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.session import get_db
from app.database.schemas.schemas import AI_InteractionCreate, AI_Interaction, User
from app.utils.deps import get_current_user
from app.services.ai_interaction import AI_InteractionService

ai_interaction_router = APIRouter()

@ai_interaction_router.post("/ai-interactions/", response_model=AI_Interaction)
async def create_ai_interaction_endpoint(interaction: AI_InteractionCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    ai_interaction_service = AI_InteractionService(db)
    return await ai_interaction_service.create(interaction_in=interaction)

@ai_interaction_router.get("/ai-interactions/user/{user_id}", response_model=List[AI_Interaction])
async def read_ai_interactions_by_user(user_id: str, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    ai_interaction_service = AI_InteractionService(db)
    interactions = await ai_interaction_service.get_ai_interactions_by_user(user_id=user_id, skip=skip, limit=limit)
    return interactions 
