# backend/app/services/transcription.py
import os
import httpx
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
if not ASSEMBLYAI_API_KEY:
    raise ValueError("ASSEMBLYAI_API_KEY not found in environment variables")

# AssemblyAI API endpoints
UPLOAD_ENDPOINT = "https://api.assemblyai.com/v2/upload"
TRANSCRIPT_ENDPOINT = "https://api.assemblyai.com/v2/transcript"

async def transcribe_audio(audio_file_path, session_id):
    """
    Transcribe an audio file using AssemblyAI
    
    Args:
        audio_file_path (str): Path to the audio file
        session_id (int): Interview session ID
    
    Returns:
        dict: Transcription result
    """
    # Check if file exists
    file_path = Path(audio_file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {audio_file_path}")
    
    # Set up headers with API key
    headers = {
        "authorization": ASSEMBLYAI_API_KEY,
        "content-type": "application/json"
    }
    
    print(f"Uploading file: {audio_file_path}")
    
    # Step 1: Upload the file
    async with httpx.AsyncClient() as client:
        with open(audio_file_path, "rb") as f:
            response = await client.post(
                UPLOAD_ENDPOINT,
                headers=headers,
                data=f
            )
        
        if response.status_code != 200:
            raise Exception(f"Error uploading file: {response.text}")
        
        upload_url = response.json()["upload_url"]
        
        print(f"File uploaded successfully. URL: {upload_url}")
        
        # Step 2: Submit the audio for transcription
        transcript_request = {
            "audio_url": upload_url,
            "speaker_labels": True,  # Enable speaker diarization
            "speakers_expected": 2,  # We expect 2 speakers (interviewer and candidate)
            "language_code": "en"    # Specify language (optional)
        }
        
        response = await client.post(
            TRANSCRIPT_ENDPOINT,
            json=transcript_request,
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Error submitting transcription request: {response.text}")
        
        transcript_id = response.json()["id"]
        
        print(f"Transcription job submitted. ID: {transcript_id}")
        
        # Step 3: Poll for transcription completion
        polling_endpoint = f"{TRANSCRIPT_ENDPOINT}/{transcript_id}"
        while True:
            response = await client.get(polling_endpoint, headers=headers)
            transcript = response.json()
            
            if transcript["status"] == "completed":
                print("Transcription completed successfully")
                
                # Process the transcript to extract text and utterances
                text = transcript.get("text", "")
                utterances = []
                
                # Extract utterances with speaker information
                if "utterances" in transcript:
                    utterances = [
                        {
                            "speaker": utterance["speaker"],
                            "text": utterance["text"],
                            "start": utterance["start"],
                            "end": utterance["end"]
                        }
                        for utterance in transcript["utterances"]
                    ]
                
                return {
                    "text": text,
                    "utterances": utterances
                }
                
            elif transcript["status"] == "error":
                raise Exception(f"Transcription error: {transcript.get('error', 'Unknown error')}")
            
            print(f"Transcription status: {transcript['status']}. Waiting...")
            await asyncio.sleep(5)  # Poll every 5 seconds