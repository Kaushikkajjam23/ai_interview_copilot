from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# Get the database URL from environment variable or use a default SQLite file
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./interview_copilot.db")

# Create the database directory if it doesn't exist
db_path = Path("./interview_copilot.db").resolve().parent
db_path.mkdir(exist_ok=True)

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create all tables
from app.models.interview import Base
Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")