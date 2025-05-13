# backend/app/routers/interviews.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from pathlib import Path
import os

from ..database import get_db, SessionLocal
from ..models.interview import InterviewSession
from ..models.user import User
from ..services.transcription import transcribe_audio
from ..auth.utils import get_current_user
from ..services.email_service import send_interview_invitation, send_interview_feedback

router = APIRouter(
    prefix="/api/interviews",
    tags=["interviews"],
)

# Create a directory to store recordings
RECORDINGS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "recordings"
RECORDINGS_DIR.mkdir(exist_ok=True)


# -------------------- Pydantic Schemas --------------------

class InterviewContextCreate(BaseModel):
    interviewer_name: str
    candidate_name: str
    interview_topic: str
    candidate_level: str
    required_skills: str
    focus_areas: str
    candidate_email: Optional[EmailStr] = None
    scheduled_time: Optional[datetime] = None

class InterviewUpdate(BaseModel):
    interview_topic: Optional[str] = None
    candidate_level: Optional[str] = None
    required_skills: Optional[str] = None
    focus_areas: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    is_canceled: Optional[bool] = None
    feedback: Optional[str] = None

class InterviewResponse(BaseModel):
    id: int
    interviewer_name: str
    candidate_name: str
    interview_topic: str
    candidate_level: str
    required_skills: str
    focus_areas: str
    recording_path: Optional[str] = None
    transcript: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_detailed_analysis: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    is_completed: bool
    is_processing: Optional[bool] = False
    error_message: Optional[str] = None
    transcript_json: Optional[list] = None
    interviewer_id: Optional[int] = None
    candidate_id: Optional[int] = None
    scheduled_time: Optional[datetime] = None
    is_canceled: Optional[bool] = False

    class Config:
        orm_mode = True


# -------------------- API Endpoints --------------------

@router.post("/", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
def create_interview_session(
    context: InterviewContextCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new interview session with context information
    """
    try:
        print(f"Creating new interview session: {context}")
        
        # If candidate email is provided, check if they exist or create them
        candidate_id = None
        if context.candidate_email:
            candidate = db.query(User).filter(User.email == context.candidate_email).first()
            if not candidate:
                # Create a new user for the candidate with a temporary password
                from ..auth.utils import get_password_hash
                import secrets
                
                temp_password = secrets.token_urlsafe(8)
                hashed_password = get_password_hash(temp_password)
                
                candidate = User(
                    email=context.candidate_email,
                    hashed_password=hashed_password,
                    full_name=context.candidate_name or context.candidate_email.split('@')[0]
                )
                db.add(candidate)
                db.commit()
                db.refresh(candidate)
            
            candidate_id = candidate.id
        
        new_session = InterviewSession(
            interviewer_name=context.interviewer_name or current_user.full_name,
            interviewer_id=current_user.id,
            candidate_name=context.candidate_name,
            candidate_id=candidate_id,
            interview_topic=context.interview_topic,
            candidate_level=context.candidate_level,
            required_skills=context.required_skills,
            focus_areas=context.focus_areas,
            scheduled_time=context.scheduled_time
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        print(f"Created session with ID: {new_session.id}")
        
        # Send email notification to candidate if scheduled time is provided
        if context.candidate_email and context.scheduled_time:
            interview_link = f"https://ai-interview-copilot.vercel.app/interview/{new_session.id}?role=candidate"
            send_interview_invitation(
                background_tasks=background_tasks,
                to_email=context.candidate_email,
                candidate_name=context.candidate_name,
                interviewer_name=current_user.full_name,
                interview_topic=context.interview_topic,
                scheduled_time=context.scheduled_time.strftime("%Y-%m-%d %H:%M"),
                interview_link=interview_link
            )
        
        return new_session
    except Exception as e:
        print(f"Error creating session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create interview session: {str(e)}"
        )


@router.get("/{session_id}", response_model=InterviewResponse)
def get_interview_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific interview session
    """
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session with ID {session_id} not found"
        )
    
    # Check if user is authorized to access this interview
    if (session.interviewer_id != current_user.id and 
        session.candidate_id != current_user.id and 
        not current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this interview"
        )
    
    return session


@router.get("/", response_model=List[InterviewResponse])
def get_all_interview_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    role: str = "interviewer"
):
    """
    Get all interview sessions for the current user
    """
    if current_user.is_admin:
        # Admins can see all interviews
        sessions = db.query(InterviewSession).all()
    elif role == "interviewer":
        # Get interviews where user is the interviewer
        sessions = db.query(InterviewSession).filter(
            InterviewSession.interviewer_id == current_user.id
        ).all()
    else:
        # Get interviews where user is the candidate
        sessions = db.query(InterviewSession).filter(
            InterviewSession.candidate_id == current_user.id
        ).all()
    
    return sessions


@router.put("/{session_id}", response_model=InterviewResponse)
def update_interview_session(
    session_id: int,
    interview_data: InterviewUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an interview session
    """
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session with ID {session_id} not found"
        )
    
    # Check if user is authorized to update this interview
    if session.interviewer_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the interviewer or admin can update this interview"
        )
    
    # Update fields if provided
    for field, value in interview_data.dict(exclude_unset=True).items():
        setattr(session, field, value)
    
    db.commit()
    db.refresh(session)
    
    # If feedback was provided, send email to candidate
    if interview_data.feedback and session.candidate_id:
        candidate = db.query(User).filter(User.id == session.candidate_id).first()
        if candidate and candidate.email:
            review_link = f"https://ai-interview-copilot.vercel.app/review/{session_id}"
            
            send_interview_feedback(
                background_tasks=background_tasks,
                to_email=candidate.email,
                candidate_name=candidate.full_name,
                interviewer_name=current_user.full_name,
                interview_topic=session.interview_topic,
                feedback_summary=interview_data.feedback[:200] + "..." if len(interview_data.feedback) > 200 else interview_data.feedback,
                review_link=review_link
            )
    
    return session


@router.post("/{session_id}/upload-recording")
async def upload_recording(
    session_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a recording file for a specific interview session
    """
    # Check if the session exists
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session with ID {session_id} not found"
        )
    
    # Check if user is authorized to upload recording
    if (session.interviewer_id != current_user.id and 
        session.candidate_id != current_user.id and 
        not current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload recording for this interview"
        )
    
    # Create a unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".webm"
    filename = f"session_{session_id}_{timestamp}{file_extension}"
    file_path = RECORDINGS_DIR / filename
    
    # Save the file
    try:
        with open(file_path, "wb") as buffer:
            contents = await file.read()
            buffer.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save recording: {str(e)}"
        )
    
    # Update the session with the recording path
    relative_path = f"recordings/{filename}"
    session.recording_path = relative_path
    session.is_processing = True
    db.commit()
    
    # Start transcription in the background
    background_tasks.add_task(
        process_transcription,
        str(file_path),
        session_id
    )
    
    return {
        "message": "Recording uploaded successfully. Transcription started.",
        "filename": filename,
        "path": relative_path
    }


async def process_transcription(file_path, session_id):
    """
    Process transcription for an uploaded recording
    """
    try:
        # Get a new DB session (since we're in a background task)
        db_session = SessionLocal()
        
        # Get the interview session
        session = db_session.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            print(f"Session {session_id} not found")
            return
        
        # Update session status
        session.is_processing = True
        db_session.commit()
        
        # Call the transcription service
        transcript_result = await transcribe_audio(file_path, session_id)
        
        # Extract transcript text and utterances
        transcript_text = transcript_result.get("text", "")
        utterances = transcript_result.get("utterances", [])
        
        # Format the transcript with speaker labels
        formatted_transcript = []
        for utterance in utterances:
            speaker = f"Speaker {utterance['speaker']}"
            text = utterance['text']
            start = utterance['start']
            end = utterance['end']
            
            formatted_transcript.append({
                "speaker": speaker,
                "text": text,
                "start_time": start,
                "end_time": end
            })
        
        # Update the session with the transcript
        session.transcript = transcript_text
        session.transcript_json = formatted_transcript
        db_session.commit()
        
        print(f"Transcription completed for session {session_id}")
        
        # Get interview context for AI analysis
        context = {
            "interview_topic": session.interview_topic,
            "candidate_level": session.candidate_level,
            "required_skills": session.required_skills,
            "focus_areas": session.focus_areas
        }
        
        # Perform AI analysis
        from ..services.ai_analysis import analyze_interview
        analysis_result = await analyze_interview(formatted_transcript, context)
        
        # Update the session with the analysis results
        session.ai_summary = analysis_result.get("summary")
        session.ai_detailed_analysis = analysis_result.get("detailed")
        session.is_processing = False
        session.is_completed = True
        db_session.commit()
        
        print(f"AI analysis completed for session {session_id}")
        
    except Exception as e:
        print(f"Error processing transcription: {str(e)}")
        # Update session status on error
        try:
            session = db_session.query(InterviewSession).filter(InterviewSession.id == session_id).first()
            if session:
                session.is_processing = False
                session.error_message = str(e)
                db_session.commit()
        except Exception as inner_e:
            print(f"Error updating session status: {str(inner_e)}")
    finally:
        db_session.close()


@router.get("/{session_id}/recording")
async def get_recording(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Serve the recording file for a specific interview session
    """
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session with ID {session_id} not found"
        )
    
    # Check if user is authorized to access this recording
    if (session.interviewer_id != current_user.id and 
        session.candidate_id != current_user.id and 
        not current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this recording"
        )

    if not session.recording_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No recording found for session with ID {session_id}"
        )

    file_path = Path(__file__).resolve().parent.parent.parent.parent / session.recording_path
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording file not found"
        )

    return FileResponse(path=file_path)


@router.get("/{session_id}/transcript")
async def get_transcript(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the transcript for a specific interview session
    """
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session with ID {session_id} not found"
        )
    
    # Check if user is authorized to access this transcript
    if (session.interviewer_id != current_user.id and 
        session.candidate_id != current_user.id and 
        not current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this transcript"
        )
    
    return {
        "is_processing": session.is_processing,
        "is_completed": session.is_completed,
        "error_message": session.error_message,
        "transcript": session.transcript,
        "transcript_json": session.transcript_json
    }


@router.post("/{session_id}/analyze", response_model=dict)
async def analyze_interview_endpoint(
    session_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI analysis for an interview
    """
    # Check if the session exists
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session with ID {session_id} not found"
        )
    
    # Check if user is authorized to analyze this interview
    if (session.interviewer_id != current_user.id and 
        not current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the interviewer or admin can analyze this interview"
        )
    
    if not session.transcript:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot analyze: No transcript available"
        )
    
    # Get interview context
    context = {
        "interview_topic": session.interview_topic,
        "candidate_level": session.candidate_level,
        "required_skills": session.required_skills,
        "focus_areas": session.focus_areas
    }
    
    # Start analysis in background
    background_tasks.add_task(
        analyze_interview_background,
        session_id,
        session.transcript_json or session.transcript,
        context
    )
    
    return {
        "message": "Analysis started",
        "status": "processing"
    }


async def analyze_interview_background(session_id, transcript, context):
    """
    Background task to analyze an interview
    """
    try:
        # Get a new DB session
        db_session = SessionLocal()
        
        # Get the interview session
        session = db_session.query(InterviewSession).filter(InterviewSession.id == session_id).first()
        if not session:
            print(f"Session {session_id} not found")
            return
        
        # Perform AI analysis
        from ..services.ai_analysis import analyze_interview
        analysis_result = await analyze_interview(transcript, context)
        
        # Update the session with the analysis results
        session.ai_summary = analysis_result.get("summary")
        session.ai_detailed_analysis = analysis_result.get("detailed")
        db_session.commit()
        
        print(f"AI analysis completed for session {session_id}")
        
    except Exception as e:
        print(f"Error in analysis background task: {str(e)}")
    finally:
        db_session.close()


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an interview session
    """
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session with ID {session_id} not found"
        )
    
    # Check if user is authorized to delete this interview
    if session.interviewer_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the interviewer or admin can delete this interview"
        )
    
    # Delete the recording file if it exists
    if session.recording_path:
        file_path = Path(__file__).resolve().parent.parent.parent.parent / session.recording_path
        if file_path.exists():
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting recording file: {str(e)}")
    
    # Delete the interview from the database
    db.delete(session)
    db.commit()
    
    return None