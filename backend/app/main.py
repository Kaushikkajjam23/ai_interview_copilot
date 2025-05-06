from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path
import subprocess

from .database import engine, Base
from .models import InterviewSession  # This imports all models
from .routers import interviews, signaling

# Create recordings directory if it doesn't exist
RECORDINGS_DIR = Path(__file__).resolve().parent.parent.parent / "recordings"
RECORDINGS_DIR.mkdir(exist_ok=True)

# Run migrations on startup
def run_migrations():
    alembic_dir = Path(__file__).resolve().parent.parent / "alembic"
    if alembic_dir.exists():
        subprocess.run(["alembic", "upgrade", "head"], cwd=Path(__file__).resolve().parent.parent)
    else:
        # Fallback to direct table creation if alembic is not set up
        Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Interview Co-Pilot API",
    description="API for recording, transcribing, and analyzing interviews",
    version="0.1.0",
)

# Register the startup event
@app.on_event("startup")
async def startup_event():
    run_migrations()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local development
        "https://ai-interview-copilot.vercel.app",  # Your Vercel domain (update this)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(interviews.router)
app.include_router(signaling.router)

@app.get("/")
async def root():
    return {"message": "Welcome to AI Interview Co-Pilot API"}