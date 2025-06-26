from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from typing import Dict
import httpx
from datetime import timedelta, datetime, timezone
import json

from ..database import get_db
from ..database.schemas import UserCreate
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
    client_kwargs={'scope': 'openid email profile'}
)

@router.get("/google")
async def google_login(request: Request):
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    redirect_to_frontend = request.query_params.get('redirect_to')

    state_data = {
        "redirect_to": redirect_to_frontend
    }
    state_param = json.dumps(state_data)

    return await oauth.google.authorize_redirect(request, redirect_uri, state=state_param)


@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    user_info = None
    redirect_to_frontend = None

    state_param = request.query_params.get('state')
    if state_param:
        try:
            state_data = json.loads(state_param)
            redirect_to_frontend = state_data.get('redirect_to')
        except json.JSONDecodeError:
            pass

    if settings.ENVIRONMENT == "production":
        try:
            token = await oauth.google.authorize_access_token(request)
            user_info = await oauth.google.parse_id_token(token)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not authorize access token: {e}",
                headers={"WWW-Authenticate": "Bearer"},
            )
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
        id_token_raw = token_json.get('id_token')

        if not access_token or not id_token_raw:
            raise HTTPException(status_code=400, detail=f"Dev mode: Failed to retrieve access_token or id_token: {token_json}")

        import jwt as pyjwt
        try:
            user_info = pyjwt.decode(id_token_raw, options={"verify_signature": False})
        except pyjwt.PyJWTError as e:
            raise HTTPException(status_code=400, detail=f"Dev mode: Failed to decode id_token: {e}")

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
    
    jwt_token = create_access_token(data={"sub": str(user.id)})
    
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expires = datetime.now(timezone.utc) + expires_delta

    if redirect_to_frontend:
        # Add token as query parameter for frontend
        separator = "&" if "?" in redirect_to_frontend else "?"
        final_redirect_url = f"{settings.FRONTEND_URL}{redirect_to_frontend}{separator}token={jwt_token}"
    else:
        final_redirect_url = f"{settings.FRONTEND_URL}/auth/callback?token={jwt_token}" # Fallback to the correct frontend callback route

    response = RedirectResponse(url=final_redirect_url, status_code=status.HTTP_302_FOUND)
    
    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,
        secure=True if settings.ENVIRONMENT == "production" else False,
        samesite="none" if settings.ENVIRONMENT == "production" else "lax",
        max_age=int(expires_delta.total_seconds()),
        path="/",
        domain=".duckdns.org" if settings.ENVIRONMENT == "production" else None
    )
    
    return response

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    
    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        secure=True if settings.ENVIRONMENT == "production" else False,
        samesite="none" if settings.ENVIRONMENT == "production" else "lax",
        max_age=0,
        path="/",
        domain=".duckdns.org" if settings.ENVIRONMENT == "production" else None
    )
    return {"message": "Successfully logged out"}
