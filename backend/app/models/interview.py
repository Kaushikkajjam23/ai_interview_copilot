# app/models/interview.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys to users
    interviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # User information (for backward compatibility and when users are external)
    interviewer_name = Column(String, nullable=False)
    candidate_name = Column(String, nullable=False)
    interviewer_email = Column(String, nullable=True)
    candidate_email = Column(String, nullable=True)
    
    # Interview details
    interview_topic = Column(String, nullable=False)
    candidate_level = Column(String, nullable=False)
    required_skills = Column(Text, nullable=False)
    focus_areas = Column(Text, nullable=False)
    
    # Scheduling fields
    scheduled_time = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)
    is_canceled = Column(Boolean, default=False)
    
    # Recording and analysis fields
    recording_path = Column(String, nullable=True)
    transcript = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    ai_detailed_analysis = Column(JSON, nullable=True)
    transcript_json = Column(JSON, nullable=True)
    
    # Feedback field
    feedback = Column(Text, nullable=True)
    
    # Status fields
    is_processing = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    interviewer = relationship("User", back_populates="interviews_as_interviewer", foreign_keys=[interviewer_id])
    candidate = relationship("User", back_populates="interviews_as_candidate", foreign_keys=[candidate_id])
    creator = relationship("User", back_populates="created_interviews", foreign_keys=[created_by])