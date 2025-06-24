from fastapi import APIRouter
from fastapi.responses import JSONResponse

health_router = APIRouter()

@health_router.get("", tags=["health"])
def health_check():
    return JSONResponse(content={"status": "ok"})
