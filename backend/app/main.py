from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import subprocess
# Import database models and routers
from .database import engine, Base
from .routers import interviews, signaling
from .models.interview import InterviewSession

# Create tables
Base.metadata.create_all(bind=engine)

# Define the FastAPI app FIRST
app = FastAPI(
    title="AI Interview Co-Pilot API",
    description="API for recording, transcribing, and analyzing interviews",
    version="0.1.0",
)
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
# Register the startup event
@app.on_event("startup")
async def startup_event():
    run_migrations()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local development
        "https://ai-interview-copilot-git-main-kaushik-kajjams-projects.vercel.app",  # Your Vercel domain
        # "*",  # For testing only - remove in production
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