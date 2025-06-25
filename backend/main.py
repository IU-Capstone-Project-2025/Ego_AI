from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import logging

from app.core import settings
from app.core.logging import logger
from app.api import api_router
from app.core.exception_handlers import add_exception_handlers

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def on_startup():
    logger.info(f"Starting {settings.PROJECT_NAME}")
