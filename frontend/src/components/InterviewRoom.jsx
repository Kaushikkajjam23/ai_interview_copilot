import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import recordingService from '../services/recordingService';
import webrtcService from '../services/webrtcService';

function InterviewRoom() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  // Get role from query params or default to interviewer
  const role = new URLSearchParams(location.search).get('role') || 'interviewer';
  
  const [sessionData, setSessionData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [connectionState, setConnectionState] = useState('new');
  const [joinUrl, setJoinUrl] = useState('');
  
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const timerRef = useRef(null);

  // Fetch session data
  useEffect(() => {
    const fetchSessionData = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/interviews/${sessionId}`);
        setSessionData(response.data);
        
        // Generate join URL for candidate
        const baseUrl = window.location.origin;
        setJoinUrl(`${baseUrl}/interview/${sessionId}?role=candidate`);
      } catch (err) {
        console.error('Error fetching session data:', err);
        setError('Failed to load interview session data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSessionData();
  }, [sessionId]);

  // Set up media stream and WebRTC when component mounts
  useEffect(() => {
    const setupMedia = async () => {
      try {
        // Request camera and mic access
        const localStream = await recordingService.requestMediaPermissions();
        
        // Display local video
        if (localVideoRef.current) {
          localVideoRef.current.srcObject = localStream;
        }
        
        // Initialize WebRTC
        await webrtcService.initialize(
          sessionId,
          role,
          localStream,
          (remoteStream) => {
            // Callback when remote stream is received
            if (remoteVideoRef.current) {
              remoteVideoRef.current.srcObject = remoteStream;
            }
            // Set remote stream in recording service
            recordingService.setRemoteStream(remoteStream);
          },
          (state) => {
            // Callback when connection state changes
            setConnectionState(state);
          }
        );
      } catch (err) {
        console.error('Error setting up media:', err);
        setError(err.message);
      }
    };

    setupMedia();

    // Clean up when component unmounts
    return () => {
      recordingService.stopAllTracks();
      webrtcService.close();
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [sessionId, role]);

  // Handle recording timer
  useEffect(() => {
    if (isRecording) {
      timerRef.current = setInterval(() => {
        setRecordingTime(prevTime => prevTime + 1);
      }, 1000);
    } else if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isRecording]);

  const startRecording = () => {
    try {
      recordingService.startRecording();
      setIsRecording(true);
      setRecordingTime(0);
    } catch (err) {
      console.error('Error starting recording:', err);
      setError(err.message);
    }
  };

  const stopRecording = async () => {
    try {
      setIsRecording(false);
      const recordedBlob = await recordingService.stopRecording();
      
      // Upload the recording
      setIsUploading(true);
      await recordingService.uploadRecording(recordedBlob, sessionId);
      setIsUploading(false);
      
      // Navigate to review page
      navigate(`/review/${sessionId}`);
    } catch (err) {
      console.error('Error stopping recording:', err);
      setError(err.message);
      setIsUploading(false);
    }
  };

  // Format seconds to MM:SS
  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // Copy join URL to clipboard
  const copyJoinUrl = () => {
    navigator.clipboard.writeText(joinUrl)
      .then(() => alert('Join URL copied to clipboard!'))
      .catch(err => console.error('Failed to copy URL:', err));
  };

  if (isLoading) {
    return <div className="loading">Loading interview session...</div>;
  }

  if (error) {
    return <div className="error-container">{error}</div>;
  }

  return (
    <div className="interview-room">
      <div className="interview-header">
        <h1>Interview Session #{sessionId}</h1>
        {sessionData && (
          <div className="session-info">
            <p><strong>Topic:</strong> {sessionData.interview_topic}</p>
            <p><strong>Candidate:</strong> {sessionData.candidate_name} ({sessionData.candidate_level})</p>
            <p><strong>Role:</strong> {role === 'interviewer' ? 'Interviewer' : 'Candidate'}</p>
          </div>
        )}
        
        {role === 'interviewer' && (
          <div className="join-url-container">
            <p>Share this link with the candidate:</p>
            <div className="join-url">
              <input type="text" value={joinUrl} readOnly />
              <button onClick={copyJoinUrl}>Copy</button>
            </div>
          </div>
        )}
        
        <div className="connection-status">
          Connection: <span className={`status-${connectionState}`}>{connectionState}</span>
        </div>
      </div>

      <div className="video-grid">
        <div className="video-container remote-video">
          <h3>{role === 'interviewer' ? 'Candidate' : 'Interviewer'}</h3>
          <video 
            ref={remoteVideoRef} 
            autoPlay 
            playsInline
          />
          {connectionState !== 'connected' && (
            <div className="waiting-overlay">
              <p>Waiting for the other participant to join...</p>
            </div>
          )}
        </div>
        
        <div className="video-container local-video">
          <h3>You ({role})</h3>
          <video 
            ref={localVideoRef} 
            autoPlay 
            muted 
            playsInline
          />
        </div>
      </div>
      
      <div className="recording-controls">
        {role === 'interviewer' && (
          <>
            {!isRecording ? (
              <button 
                className="record-button"
                onClick={startRecording}
                disabled={isUploading || connectionState !== 'connected'}
              >
                Start Recording
              </button>
            ) : (
              <button 
                className="stop-button"
                onClick={stopRecording}
                disabled={isUploading}
              >
                Stop Recording
              </button>
            )}
            
            {isRecording && (
              <div className="recording-indicator">
                <span className="recording-dot"></span>
                Recording: {formatTime(recordingTime)}
              </div>
            )}
            
            {isUploading && (
              <div className="upload-indicator">
                Uploading recording...
              </div>
            )}
          </>
        )}
      </div>
      
      {sessionData && (
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
      )}
    </div>
  );
}

export default InterviewRoom;