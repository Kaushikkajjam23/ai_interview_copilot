import { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

function InterviewReview() {
  const { sessionId } = useParams();
  const [sessionData, setSessionData] = useState(null);
  const [transcript, setTranscript] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('transcript');
  const [isAnalysisLoading, setIsAnalysisLoading] = useState(false);
  
  const videoRef = useRef(null);
  const pollingIntervalRef = useRef(null);
  
  // Get API URL from environment variable
  const API_URL = import.meta.env.VITE_API_URL;

  // Fetch session data
  useEffect(() => {
    const fetchSessionData = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/interviews/${sessionId}`);
        setSessionData(response.data);
        
        // Check transcript status
        await checkTranscriptStatus();
      } catch (err) {
        console.error('Error fetching session data:', err);
        setError('Failed to load interview session data.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSessionData();
    
    // Clean up polling interval
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, [sessionId]);

  // Function to check transcript status
  const checkTranscriptStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/interviews/${sessionId}/transcript`);
      
      if (response.data.is_processing) {
        // If still processing, start polling if not already
        if (!isPolling) {
          setIsPolling(true);
          pollingIntervalRef.current = setInterval(checkTranscriptStatus, 5000); // Poll every 5 seconds
        }
      } else {
        // Processing finished (either completed or error)
        setIsPolling(false);
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
        }
        
        if (response.data.error_message) {
          setError(`Transcription error: ${response.data.error_message}`);
        } else if (response.data.transcript_json) {
          setTranscript(response.data.transcript_json);
        }
      }
    } catch (err) {
      console.error('Error checking transcript status:', err);
      setError('Failed to check transcript status.');
      setIsPolling(false);
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    }
  };

  // Function to generate AI analysis
  const generateAnalysis = async () => {
    if (!sessionData || !sessionData.transcript) {
      setError('Cannot generate analysis: No transcript available');
      return;
    }
    
    setIsAnalysisLoading(true);
    
    try {
      await axios.post(`${API_URL}/api/interviews/${sessionId}/analyze`);
      
      // Poll for analysis completion
      const pollInterval = setInterval(async () => {
        const response = await axios.get(`${API_URL}/api/interviews/${sessionId}`);
        setSessionData(response.data);
        
        if (response.data.ai_summary) {
          clearInterval(pollInterval);
          setActiveTab('analysis');
          setIsAnalysisLoading(false);
        }
      }, 5000); // Check every 5 seconds
      
      // Stop polling after 2 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        if (isAnalysisLoading) {
          setIsAnalysisLoading(false);
          setError('Analysis is taking longer than expected. Please check back later.');
        }
      }, 120000);
      
    } catch (err) {
      console.error('Error generating analysis:', err);
      setError('Failed to generate analysis. Please try again.');
      setIsAnalysisLoading(false);
    }
  };

  // Function to seek video to specific timestamp
  const seekToTimestamp = (timeInMs) => {
    if (videoRef.current) {
      videoRef.current.currentTime = timeInMs / 1000; // Convert ms to seconds
      videoRef.current.play();
    }
  };

  // Format timestamp from milliseconds to MM:SS
  const formatTimestamp = (ms) => {
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return <div className="loading">Loading interview data...</div>;
  }

  if (error) {
    return <div className="error-container">{error}</div>;
  }

  if (!sessionData) {
    return <div className="error-container">No session data found.</div>;
  }

  return (
    <div className="interview-review">
      <div className="review-header">
        <h1>Review: {sessionData.interview_topic}</h1>
        <div className="session-info">
          <p><strong>Candidate:</strong> {sessionData.candidate_name} ({sessionData.candidate_level})</p>
          <p><strong>Interviewer:</strong> {sessionData.interviewer_name}</p>
        </div>
      </div>

      <div className="video-container">
        {sessionData.recording_path ? (
          <video 
            ref={videoRef}
            controls 
            src={`${API_URL}/api/interviews/${sessionId}/recording`}
            width="100%"
          />
        ) : (
          <div className="no-recording">
            <p>No recording available for this session.</p>
          </div>
        )}
      </div>

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'transcript' ? 'active' : ''}`}
          onClick={() => setActiveTab('transcript')}
        >
          Transcript
        </button>
        <button 
          className={`tab ${activeTab === 'analysis' ? 'active' : ''}`}
          onClick={() => setActiveTab('analysis')}
          disabled={!sessionData?.ai_summary}
        >
          AI Analysis
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'transcript' && (
          <div className="transcript-container">
            {isPolling ? (
              <div className="processing-indicator">
                <div className="spinner"></div>
                <p>Generating transcript... This may take a few minutes.</p>
              </div>
            ) : transcript ? (
              <div className="transcript-content">
                {transcript.map((item, index) => (
                  <div 
                    key={index} 
                    className={`transcript-item ${item.speaker === 'Speaker 1' ? 'interviewer' : 'candidate'}`}
                    onClick={() => seekToTimestamp(item.start_time)}
                  >
                    <div className="transcript-header">
                      <span className="speaker-label">
                        {item.speaker === 'Speaker 1' ? 'Interviewer' : 'Candidate'}
                      </span>
                      <span className="timestamp">{formatTimestamp(item.start_time)}</span>
                    </div>
                    <div className="transcript-text">{item.text}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-transcript">
                <p>No transcript available yet.</p>
              </div>
            )}
            
            {!sessionData.ai_summary && !isAnalysisLoading && transcript && (
              <button 
                className="generate-analysis-button"
                onClick={generateAnalysis}
              >
                Generate AI Analysis
              </button>
            )}
            
            {isAnalysisLoading && (
              <div className="loading-analysis">
                Generating AI analysis...
              </div>
            )}
          </div>
        )}

        {activeTab === 'analysis' && sessionData.ai_summary && (
          <div className="analysis-container">
            <div className="analysis-section">
              <h2>Summary</h2>
              <p>{sessionData.ai_summary}</p>
            </div>
            
            {sessionData.ai_detailed_analysis && (
              <>
                <div className="analysis-section">
                  <h2>Technical Assessment</h2>
                  <p>{sessionData.ai_detailed_analysis.technical_assessment}</p>
                </div>
                
                <div className="analysis-section">
                  <h2>Strengths</h2>
                  <ul>
                    {sessionData.ai_detailed_analysis.strengths.map((strength, index) => (
                      <li key={index}>{strength}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="analysis-section">
                  <h2>Areas for Improvement</h2>
                  <ul>
                    {sessionData.ai_detailed_analysis.areas_for_improvement.map((area, index) => (
                      <li key={index}>{area}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="analysis-section">
                  <h2>Recommendation</h2>
                  <p className="recommendation">{sessionData.ai_detailed_analysis.recommendation}</p>
                </div>
                
                <div className="analysis-section">
                  <h2>Skill Scores</h2>
                  <div className="scores">
                    {Object.entries(sessionData.ai_detailed_analysis.scores || {}).map(([skill, score]) => (
                      <div key={skill} className="score-item">
                        <span className="skill-name">
                          {skill.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                        </span>
                        <div className="score-bar-container">
                          <div 
                            className="score-bar" 
                            style={{width: `${(parseInt(score) / 10) * 100}%`}}
                          ></div>
                          <span className="score-value">{score}/10</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>

      <div className="interview-context">
        <h3>Interview Context</h3>
        <div className="context-item">
          <strong>Required Skills:</strong>
          <p>{sessionData.required_skills}</p>
        </div>
        <div className="context-item">
          <strong>Focus Areas:</strong>
          <p>{sessionData.focus_areas}</p>
        </div>
      </div>
    </div>
  );
}

export default InterviewReview;