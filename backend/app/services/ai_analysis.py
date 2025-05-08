# backend/app/services/ai_analysis.py
import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

async def analyze_interview(transcript, context):
    """
    Analyze interview transcript using OpenAI
    
    Parameters:
    - transcript: The interview transcript text or structured data
    - context: Dictionary containing interview context (topic, level, skills, etc.)
    
    Returns:
    - Dictionary containing analysis results
    """
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found in environment variables")
    
    # Extract context information
    topic = context.get("interview_topic", "")
    level = context.get("candidate_level", "")
    skills = context.get("required_skills", "")
    focus_areas = context.get("focus_areas", "")
    
    # Format the transcript for better readability
    formatted_transcript = ""
    if isinstance(transcript, list):
        # If transcript is a list of utterances
        for utterance in transcript:
            speaker = f"Speaker {utterance.get('speaker', '?')}"
            text = utterance.get('text', '')
            formatted_transcript += f"{speaker}: {text}\n\n"
    else:
        # If transcript is just text
        formatted_transcript = transcript
    
    # Create the prompt for the LLM
    prompt = f"""
You are an expert technical interviewer reviewing an interview transcript. 

INTERVIEW CONTEXT:
- Topic: {topic}
- Candidate Level: {level}
- Required Skills: {skills}
- Focus Areas: {focus_areas}

INTERVIEW TRANSCRIPT:
{formatted_transcript}

Based on the transcript above, provide a comprehensive analysis in the following JSON format:

{{
  "summary": "A brief 2-3 sentence summary of the interview and the candidate's performance",
  "detailed": {{
    "technical_assessment": "A paragraph evaluating the candidate's technical knowledge and how well they demonstrated the required skills",
    "strengths": ["Strength 1", "Strength 2", "Strength 3"],
    "areas_for_improvement": ["Area 1", "Area 2", "Area 3"],
    "recommendation": "Hire/Consider/Reject with a brief justification",
    "scores": {{
      "technical_knowledge": "Score from 1-10",
      "communication": "Score from 1-10",
      "problem_solving": "Score from 1-10"
    }}
  }}
}}

Ensure your analysis is fair, based solely on the transcript content, and provides specific examples from the interview to support your assessment.
"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    data = {
        "model": "gpt-4",  # or "gpt-3.5-turbo" if you prefer
        "messages": [
            {"role": "system", "content": "You are an expert technical interviewer providing objective analysis."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,  # Lower temperature for more consistent results
        "max_tokens": 1500  # Adjust based on your needs
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OPENAI_API_URL,
                headers=headers,
                json=data,
                timeout=60.0  # Longer timeout for LLM processing
            )
            response.raise_for_status()
            
            # Extract the AI's response
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            
            # Parse the JSON response
            try:
                analysis = json.loads(ai_response)
                return analysis
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw text
                return {"summary": ai_response, "detailed": None}
                
    except Exception as e:
        print(f"Error in AI analysis: {str(e)}")
        return {"error": str(e)}