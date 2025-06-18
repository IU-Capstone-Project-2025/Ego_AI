from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
import uuid

from app.services.user import UserService
from app.database.session import get_db
from app.database import models
from app.auth.jwt import verify_token
from app.core import settings


oauth2_scheme = HTTPBearer()

async def get_current_user(
    db: AsyncSession = Depends(get_db), 
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
) -> models.User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id_str = verify_token(token=token, credentials_exception=credentials_exception)
    
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception
    
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    
    if user is None:
        raise credentials_exception
    return user 
