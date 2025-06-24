from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.services.user import UserService
from app.database.session import get_db
from app.database import schemas, models
from app.utils import deps

router = APIRouter()

@router.get("/me", response_model=schemas.UserMe)
async def read_users_me(current_user: models.User = Depends(deps.get_current_user)):
    """
    Get current user.
    """
    return current_user

@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user."""
    user_service = UserService(db)
    return await user_service.create(user_in=user)

@router.get("/", response_model=List[schemas.User], dependencies=[Depends(deps.get_current_user)])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get a list of users. (Protected)"""
    user_service = UserService(db)
    return await user_service.get_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=schemas.User, dependencies=[Depends(deps.get_current_user)])
async def read_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific user by ID. (Protected)"""
    user_service = UserService(db)
    db_user = await user_service.get_by_id(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: uuid.UUID, 
    user: schemas.UserUpdate, 
    current_user: models.User = Depends(deps.get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Update a user."""
    user_service = UserService(db)
    return await user_service.update(user_id=user_id, user_in=user, current_user=current_user)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID, 
    current_user: models.User = Depends(deps.get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Delete a user."""
    user_service = UserService(db)
    await user_service.delete(user_id=user_id, current_user=current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT) 
