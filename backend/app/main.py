from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path

from .database import engine, Base
from .models import InterviewSession  # This imports all models
from .routers import interviews,signaling  # Add signaling import

# Include routers
app.include_router(interviews.router)
app.include_router(signaling.router)  # Add this line

# Create the database tables
Base.metadata.create_all(bind=engine)

# Create recordings directory if it doesn't exist
RECORDINGS_DIR = Path(__file__).resolve().parent.parent.parent / "recordings"
RECORDINGS_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="AI Interview Co-Pilot API",
    description="API for recording, transcribing, and analyzing interviews",
    version="0.1.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to AI Interview Co-Pilot API"}

# Update the CORS middleware in main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)