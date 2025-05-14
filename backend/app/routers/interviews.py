from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from ..database import get_db
from ..models.interview import InterviewSession
from ..models.user import User
from ..auth.utils import get_current_user
from ..services.email_service import send_interview_invitation

router = APIRouter(prefix="/api/interviews", tags=["interviews"])

class InterviewCreate(BaseModel):
    interviewer_name: str
    candidate_name: str
    interview_topic: str
    candidate_level: str
    required_skills: str
    focus_areas: str
    candidate_email: Optional[EmailStr] = None
    scheduled_time: Optional[datetime] = None

@router.post("/", response_model=dict)
async def create_interview(
    interview: InterviewCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Create interview session
        new_session = InterviewSession(
            interviewer_name=interview.interviewer_name,
            interviewer_id=current_user.id,
            candidate_name=interview.candidate_name,
            interview_topic=interview.interview_topic,
            candidate_level=interview.candidate_level,
            required_skills=interview.required_skills,
            focus_areas=interview.focus_areas,
            scheduled_time=interview.scheduled_time,
            candidate_email=interview.candidate_email
        )
        
        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        # Send email if candidate email is provided
        if interview.candidate_email and interview.scheduled_time:
            interview_link = f"https://your-frontend-url.com/interview/{new_session.id}"
            send_interview_invitation(
                background_tasks=background_tasks,
                to_email=interview.candidate_email,
                candidate_name=interview.candidate_name,
                interviewer_name=interview.interviewer_name,
                interview_topic=interview.interview_topic,
                scheduled_time=interview.scheduled_time.strftime("%Y-%m-%d %H:%M"),
                interview_link=interview_link
            )

        return {
            "message": "Interview scheduled successfully",
            "id": new_session.id,
            "email_sent": bool(interview.candidate_email)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule interview: {str(e)}"
        )