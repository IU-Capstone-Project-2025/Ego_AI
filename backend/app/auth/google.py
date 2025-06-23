from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from typing import Dict
import httpx

from ..database import get_db
from ..database.schemas import UserCreate, UserUpdate
from app.services.user import UserService
from .jwt import create_access_token
from ..core import settings

router = APIRouter()


oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile https://www.googleapis.com/auth/calendar.events'}
)

@router.get("/google-login")
async def google_login(request: Request):
    """
    Генерирует редирект на страницу аутентификации Google.
    """
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    if settings.ENVIRONMENT == "production":
        try:
            token = await oauth.google.authorize_access_token(request)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not authorize access token: {e}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_info = token.get('userinfo')
        access_token = token.get('access_token')
        refresh_token = token.get('refresh_token')

    else:
        code = request.query_params.get('code')
        if not code:
            raise HTTPException(status_code=400, detail="Dev mode: Authorization code not found.")

        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_json = token_response.json()

        access_token = token_json.get('access_token')
        refresh_token = token_json.get('refresh_token')

        userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        async with httpx.AsyncClient() as client:
            userinfo_response = await client.get(userinfo_url, headers=headers)
            user_info = userinfo_response.json()

    if not user_info or not user_info.get('email'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not retrieve user information from Google."
        )

    user_email = user_info['email']
    user_name = user_info.get('name', user_email)
    
    user_service = UserService(db)
    user = await user_service.get_by_email(email=user_email)

    if not user:
        google_user_id = user_info.get('sub') or user_info.get('id')
        if not google_user_id:
            raise HTTPException(status_code=400, detail="Could not retrieve a unique user identifier from Google.")
        
        user_create = UserCreate(email=user_email, name=user_name, password=google_user_id)
        user = await user_service.create(user_in=user_create)

    # Update user with new tokens
    user_update_data = {
        "google_access_token": access_token,
    }
    if refresh_token:
        user_update_data["google_refresh_token"] = refresh_token

    user_update = UserUpdate(**user_update_data)
    await user_service._update(user=user, user_in=user_update)

    jwt_token = create_access_token(data={"sub": str(user.id)})

    redirect_url = f"{settings.FRONTEND_URL}/login/callback?token={jwt_token}"
    return RedirectResponse(url=redirect_url) 
