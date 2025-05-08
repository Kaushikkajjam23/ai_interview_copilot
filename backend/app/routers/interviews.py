from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import os

from ..database import get_db, SessionLocal
from ..models.interview import InterviewSession
from ..services.transcription import transcribe_audio

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

    class Config:
        orm_mode = True


# -------------------- API Endpoints --------------------

@router.post("/", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
def create_interview_session(
    context: InterviewContextCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new interview session with context information
    """
    new_session = InterviewSession(
        interviewer_name=context.interviewer_name,
        candidate_name=context.candidate_name,
        interview_topic=context.interview_topic,
        candidate_level=context.candidate_level,
        required_skills=context.required_skills,
        focus_areas=context.focus_areas,
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


@router.get("/{session_id}", response_model=InterviewResponse)
def get_interview_session(
    session_id: int,
    db: Session = Depends(get_db)
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
    return session


@router.get("/", response_model=List[InterviewResponse])
def get_all_interview_sessions(
    db: Session = Depends(get_db)
):
    """
    Get all interview sessions
    """
    sessions = db.query(InterviewSession).all()
    return sessions


@router.post("/{session_id}/upload-recording")
async def upload_recording(
    session_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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