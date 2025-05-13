# setup_db.py
from app.database import engine, Base
from app.models.user import User
from app.models.interview import InterviewSession

def setup_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    setup_database()