import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Determine if we're on Heroku (Heroku sets DATABASE_URL environment variable)
is_heroku = "DATABASE_URL" in os.environ

# Database URL configuration
if is_heroku:
    # Use PostgreSQL on Heroku
    DATABASE_URL = os.environ["DATABASE_URL"]
    # Fix for Heroku PostgreSQL URL format
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    # Use SQLite locally
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATABASE_URL = f"sqlite:///{BASE_DIR}/database.db"
    
# Create SQLAlchemy engine and session
engine = create_engine(
    DATABASE_URL,
    # These arguments are only needed for SQLite
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()