from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create Fast API app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to answer for request
@app.get("/hello-world")
async def get_hello_world():
    return {"message": "Привет мир!"}