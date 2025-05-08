import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# For Render deployment, use /tmp directory which is writable
if os.environ.get('RENDER'):
    DB_DIR = Path('/tmp')
else:
    # For local development
    DB_DIR = Path(__file__).resolve().parent.parent / "data"
    DB_DIR.mkdir(exist_ok=True)

# Database URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_DIR}/interview_app.db"
    
# Create SQLAlchemy engine and session
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,  # Fixed: using SQLALCHEMY_DATABASE_URL instead of DATABASE_URL
    # These arguments are only needed for SQLite
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()