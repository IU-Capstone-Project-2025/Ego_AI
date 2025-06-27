from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
import os 
import logging

from app.database import schemas
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Use the MongoDB URL from settings, with fallback to environment variable
MONGO_URI = settings.MONGO_URL or os.getenv("MONGO_URL")

if not MONGO_URI:
    logger.error("MONGO_URL not configured")
    raise ValueError("MONGO_URL must be configured in environment variables")

logger.info(f"Connecting to MongoDB at: {MONGO_URI}")
client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["ego_ai_db"]
collection = db["chat_history"]

async def test_connection():
    """Test MongoDB connection"""
    try:
        await client.server_info()
        logger.info("MongoDB connection successful")
        return True
    except Exception as e:
        logger.error(f"MongoDB connection failed: {str(e)}")
        return False

@router.post("/add_message")
async def add_message(data: schemas.AddMessageRequest):
    try:
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
    except Exception as e:
        print(f"Error adding message for user {data.user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add message: {str(e)}")

@router.get("/get_messages")
async def get_message(user_id: str= Query(...)):
    try:
        print(f"Getting messages for user {user_id}")
        
        # Test connection first
        if not await test_connection():
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        chat = await collection.find_one({"user_id": user_id})
        if chat:
            messages = chat.get("messages", [])
            print(f"Found {len(messages)} messages for user {user_id}")
            return messages
        else:
            print(f"No chat found for user {user_id}")
            return []
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting messages for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")

@router.delete("/delete_messages")
async def delete_messages(user_id: str = Query(...)):
    try:
        print(f"Deleting messages for user {user_id}")
        result = await collection.delete_one({"user_id": user_id})
        print(f"Deleted {result.deleted_count} chat records for user {user_id}")
        return {"success": True, "deleted_count": result.deleted_count}
    except Exception as e:
        print(f"Error deleting messages for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete messages: {str(e)}")