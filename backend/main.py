from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import logging
import json

from app.core import settings
from app.core.logging import logger
from app.api import api_router
from app.core.exception_handlers import add_exception_handlers
from app.core.cors_middleware import CustomCORSMiddleware

# Alembic теперь управляет созданием таблиц, поэтому эта строка не нужна
# from app.database import Base, engine 
# Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")
logger.info("[APP] FastAPI app is starting up...")

app = FastAPI(
    title=settings.PROJECT_NAME
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
)

add_exception_handlers(app)

cors_origins = [
    "http://egoai.duckdns.org",
    "https://egoai.duckdns.org",
    "http://egoai-api.duckdns.org",
    "https://egoai-api.duckdns.org", 
    "http://localhost:3000",
    "https://localhost:3000"
]

logger.info(f"CORS origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def on_startup():
    logger.info(f"Starting {settings.PROJECT_NAME}")

