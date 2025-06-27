from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
import os 

from app.database import schemas

router = APIRouter()

MONGO_URI = os.getenv("MONGO_URL")

client = AsyncIOMotorClient(MONGO_URI)
db = client["ego_ai_db"]
collection = db["chat_history"]

@router.post("/add_message")
async def add_message(data: schemas.AddMessageRequest):
    chat = await collection.find_one({"user_id": data.user_id})
    message = {
        "role": data.role, 
        "content": data.content
    }
    if chat:
        await collection.update_one(
            {"user_id": data.user_id},
            {"$push": {"message": message}}
        )
    else:
        await collection.insert_one({
            "user_id": data.user_id,
            "messages": [message]
        })
    return {"success": True}

@router.get("/get_messages")
async def get_message(user_id: str= Query(...)):
    chat = await collection.find_one({"user_id": user_id})
    return chat["messages"] if chat else []

@router.delete("/delete_messages")
async def delete_messages(user_id: str = Query(...)):
    await collection.delete_one({"user_id": user_id})
    return {"success": True}