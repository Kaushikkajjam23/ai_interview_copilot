from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    interviewer_name = Column(String(100))
    candidate_name = Column(String(100))
    interview_topic = Column(String(200))
    candidate_level = Column(String(50))  # Junior, Mid, Senior, etc.
    required_skills = Column(Text)  # Comma-separated or JSON string
    focus_areas = Column(Text)
    recording_path = Column(String(255), nullable=True)
    transcript = Column(Text, nullable=True)
    transcript_json = Column(JSON, nullable=True)  # Structured transcript with speaker labels
    ai_summary = Column(Text, nullable=True)
    ai_detailed_analysis = Column(JSON, nullable=True)  # Store structured JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_processing = Column(Boolean, default=False)  # Flag for background processing
    is_completed = Column(Boolean, default=False)   # Flag for completed processing
    error_message = Column(Text, nullable=True)     # Store any processing errors
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            "id": self.id,
            "interviewer_name": self.interviewer_name,
            "candidate_name": self.candidate_name,
            "interview_topic": self.interview_topic,
            "candidate_level": self.candidate_level,
            "required_skills": self.required_skills,
            "focus_areas": self.focus_areas,
            "recording_path": self.recording_path,
            "transcript": self.transcript,
            "transcript_json": self.transcript_json,
            "ai_summary": self.ai_summary,
            "ai_detailed_analysis": self.ai_detailed_analysis,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_processing": self.is_processing,
            "is_completed": self.is_completed,
            "error_message": self.error_message
        }