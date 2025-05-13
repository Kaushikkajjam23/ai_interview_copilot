# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # One-to-many relationship with interviews (as interviewer)
    interviews_as_interviewer = relationship(
        "InterviewSession", 
        back_populates="interviewer",
        foreign_keys="InterviewSession.interviewer_id",
        cascade="all, delete-orphan"
    )
    
    # One-to-many relationship with interviews (as candidate)
    interviews_as_candidate = relationship(
        "InterviewSession", 
        back_populates="candidate",
        foreign_keys="InterviewSession.candidate_id",
        cascade="all, delete-orphan"
    )