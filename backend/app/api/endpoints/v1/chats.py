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
    print(f"Adding message for user {data.user_id}: {data.role} - {data.content[:50]}...")
    chat = await collection.find_one({"user_id": data.user_id})
    message = {
        "role": data.role, 
        "content": data.content
    }
    if chat:
        print(f"Updating existing chat for user {data.user_id}")
        await collection.update_one(
            {"user_id": data.user_id},
            {"$push": {"messages": message}}
        )
    else:
        print(f"Creating new chat for user {data.user_id}")
        await collection.insert_one({
            "user_id": data.user_id,
            "messages": [message]
        })
    return {"success": True}

@router.get("/get_messages")
async def get_message(user_id: str= Query(...)):
    print(f"Getting messages for user {user_id}")
    chat = await collection.find_one({"user_id": user_id})
    if chat:
        messages = chat.get("messages", [])
        print(f"Found {len(messages)} messages for user {user_id}")
        return messages
    else:
        print(f"No chat found for user {user_id}")
        return []

@router.delete("/delete_messages")
async def delete_messages(user_id: str = Query(...)):
    await collection.delete_one({"user_id": user_id})
    return {"success": True}