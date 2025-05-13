from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import subprocess
# Import database models and routers
from .database import engine, Base
from .routers import interviews, signaling
from .models.interview import InterviewSession
import os
# Import the settings object
from .config import Settings  # Make sure this import is at the top
frontend_url = os.environ.get("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)
# Create tables
Base.metadata.create_all(bind=engine)

# Define the FastAPI app FIRST
app = FastAPI(
    title="AI Interview Co-Pilot API",
    description="API for recording, transcribing, and analyzing interviews",
    version="0.1.0",
)
database_url = os.getenv("DATABASE_URL")
jwt_secret = os.getenv("JWT_SECRET_KEY")
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

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(interviews.router)
app.include_router(signaling.router)  # If you have this router

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Interview Copilot API"}

# Add a test endpoint to verify environment variables
@app.get("/api/test-env")
def test_env():
    return {
        "database_url_type": Settings.DATABASE_URL.split("://")[0],
        "jwt_algorithm": Settings.JWT_ALGORITHM,
        "email_configured": bool(Settings.EMAIL_HOST and settings.EMAIL_USERNAME),
        "cors_origins": Settings.CORS_ORIGINS,
    }