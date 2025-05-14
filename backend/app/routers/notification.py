# backend/app/routes/notification.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict
from ..database import get_db
from ..models import Interview
from ..auth import get_current_user
from ..email import send_candidate_email, send_interviewer_email

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.post("/email/candidate/{interview_id}", response_model=Dict[str, str])
async def send_candidate_notification(
    interview_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Get interview details
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Check permissions (optional)
    if interview.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to send notifications for this interview")
    
    # Send email in the background
    background_tasks.add_task(
        send_candidate_email,
        recipient_email=interview.candidate_email,
        recipient_name=interview.candidate_name,
        interview_details={
            "topic": interview.interview_topic,
            "scheduled_time": interview.scheduled_time,
            "interviewer_name": interview.interviewer_name
        }
    )
    
    return {"status": "Email notification to candidate queued successfully"}

@router.post("/email/interviewer/{interview_id}", response_model=Dict[str, str])
async def send_interviewer_notification(
    interview_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Get interview details
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Check permissions (optional)
    if interview.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to send notifications for this interview")
    
    # Send email in the background
    background_tasks.add_task(
        send_interviewer_email,
        recipient_email=interview.interviewer_email,
        recipient_name=interview.interviewer_name,
        interview_details={
            "topic": interview.interview_topic,
            "scheduled_time": interview.scheduled_time,
            "candidate_name": interview.candidate_name,
            "candidate_level": interview.candidate_level,
            "required_skills": interview.required_skills,
            "focus_areas": interview.focus_areas
        }
    )
    
    return {"status": "Email notification to interviewer queued successfully"}