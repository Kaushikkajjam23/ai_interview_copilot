# backend/create_db.py
from app.database import Base, engine
from app.models.interview import InterviewSession

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()