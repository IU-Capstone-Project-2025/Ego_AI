from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse


class EgoAIException(Exception):
    """Base exception for the application."""
    def __init__(self, detail: str):
        self.detail = detail

class BadRequestError(EgoAIException):
    """(400) Bad Request."""
    pass

class ForbiddenError(EgoAIException):
    """(403) Forbidden."""
    pass

class NotFoundError(EgoAIException):
    """(404) Not Found."""
    pass

class DatabaseError(EgoAIException):
    """(500) Database Error."""
    pass


async def bad_request_error_handler(request: Request, exc: BadRequestError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc.detail})

async def forbidden_error_handler(request: Request, exc: ForbiddenError):
    return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": exc.detail})

async def not_found_error_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.detail})

async def database_error_handler(request: Request, exc: DatabaseError):
    # In production, you might want to log the full error but return a generic message
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal database error occurred."},
    )

def add_exception_handlers(app):
    app.add_exception_handler(BadRequestError, bad_request_error_handler)
    app.add_exception_handler(ForbiddenError, forbidden_error_handler)
    app.add_exception_handler(NotFoundError, not_found_error_handler)
    app.add_exception_handler(DatabaseError, database_error_handler) 
