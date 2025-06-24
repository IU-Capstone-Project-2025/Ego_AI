from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from fastapi.encoders import jsonable_encoder
import httpx
import os
from typing import Optional, List

from app.database import schemas

router = APIRouter()

ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8001/chat")

@router.post("/chat")
async def chat_with_llm(
    req: schemas.LLM_ChatRequest,
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

            llm_chat_response = schemas.LLM_ChatResponse(**ml_response_data)

            return Response(
                content=jsonable_encoder(llm_chat_response.model_dump()),
                media_type="application/json"
            )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to the ML service: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting response from ML service or processing event: {e}") 