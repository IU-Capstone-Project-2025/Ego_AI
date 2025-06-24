from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import os
from typing import Optional

from app.database import schemas
from app.utils.deps import get_db, get_current_user

router = APIRouter()

ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8001/chat")

@router.post("/chat", response_model=schemas.LLM_ChatResponse)
async def chat_with_llm(
    req: schemas.LLM_ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    payload = {
        "message": req.message,
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                ML_SERVICE_URL,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            ml_response_data = response.json()
            return schemas.LLM_ChatResponse(response=ml_response_data.get("response", ""))
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to the ML service: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting response from ML service: {e}") 