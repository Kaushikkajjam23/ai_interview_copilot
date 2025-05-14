# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging
import os
import subprocess  # Add this import for subprocess.run

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database models
from .database import engine, Base
from .models import interview, user  # Import all model modules
from .routers import interviews, signaling, auth,notification  # Import all routers

# Create tables directly (fallback method)
Base.metadata.create_all(bind=engine)

# Define origins for CORS
origins = [
    "http://localhost:5173",  # Local development
    "https://ai-interview-copilot.vercel.app",  # Your Vercel domain
    "https://ai-interview-copilot-git-main-kaushik-kajjams-projects.vercel.app",  # Your Vercel preview domain
]

# Add frontend URL from environment if available
frontend_url = os.environ.get("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

# Define the FastAPI app
app = FastAPI(
    title="AI Interview Co-Pilot API",
    description="API for recording, transcribing, and analyzing interviews",
    version="0.1.0",
)

# Get environment variables
database_url = os.getenv("DATABASE_URL")
jwt_secret = os.getenv("JWT_SECRET_KEY")

# Create recordings directory if it doesn't exist
RECORDINGS_DIR = Path(__file__).resolve().parent.parent / "recordings"
RECORDINGS_DIR.mkdir(exist_ok=True)

# Run migrations on startup
def run_migrations():
    try:
        alembic_dir = Path(__file__).resolve().parent.parent / "alembic"
        if alembic_dir.exists():
            logger.info("Running database migrations with Alembic...")
            result = subprocess.run(
                ["alembic", "upgrade", "head"], 
                cwd=Path(__file__).resolve().parent.parent,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                logger.error(f"Alembic migration failed: {result.stderr}")
                logger.info("Falling back to direct table creation...")
                Base.metadata.create_all(bind=engine)
            else:
                logger.info("Alembic migrations completed successfully")
        else:
            logger.info("Alembic directory not found, using direct table creation...")
            Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.error(f"Error during migrations: {str(e)}")
        logger.info("Falling back to direct table creation...")
        Base.metadata.create_all(bind=engine)

# Register the startup event
@app.on_event("startup")
async def startup_event():
    run_migrations()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins + ["*"],  # Add wildcard for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(interviews.router)
app.include_router(notification.router)
app.include_router(signaling.router)  # If you have this router

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Interview Copilot API"}

# Add a test endpoint to verify environment variables
@app.get("/api/test-env")
def test_env():
    # Create a settings class or import it if you have one
    class Settings:
        DATABASE_URL = database_url or "sqlite:///./data/interview_app.db"
        JWT_ALGORITHM = "HS256"
        EMAIL_HOST = os.getenv("EMAIL_HOST", "")
        EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
        CORS_ORIGINS = origins

    return {
        "database_url_type": Settings.DATABASE_URL.split("://")[0] if Settings.DATABASE_URL else "sqlite",
        "jwt_algorithm": Settings.JWT_ALGORITHM,
        "email_configured": bool(Settings.EMAIL_HOST and Settings.EMAIL_USERNAME),
        "cors_origins": Settings.CORS_ORIGINS,
    }