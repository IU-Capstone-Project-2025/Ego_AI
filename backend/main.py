from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import router

# Create Fast API app
app = FastAPI(title="Ego AI Calendar API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")

# Function to answer for request
@app.get("/")
def read_root():
    return {"message": "Welcome to Ego AI Calendar API"}