// frontend/src/services/apiService.js
import { API_URL } from '../config';
import axios from 'axios';

// Fetch interview session data
export const fetchSession = async (sessionId) => {
  try {
    const response = await axios.get(`${API_URL}/api/interviews/${sessionId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching session:', error);
    throw error;
  }
};

// Create a new interview session
export const createSession = async (sessionData) => {
  try {
    const response = await axios.post(`${API_URL}/api/interviews/`, sessionData);
    return response.data;
  } catch (error) {
    console.error('Error creating session:', error);
    throw error;
  }
};

// Upload recording
export const uploadRecording = async (sessionId, recordingBlob) => {
  try {
    const formData = new FormData();
    formData.append('file', recordingBlob, 'recording.webm');
    
    const response = await axios.post(
      `${API_URL}/api/interviews/${sessionId}/upload-recording`, 
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error uploading recording:', error);
    throw error;
  }
};

// Request AI analysis
export const requestAnalysis = async (sessionId) => {
  try {
    const response = await axios.post(`${API_URL}/api/interviews/${sessionId}/analyze`);
    return response.data;
  } catch (error) {
    console.error('Error requesting analysis:', error);
    throw error;
  }
};

// Fetch transcript
export const fetchTranscript = async (sessionId) => {
  try {
    const response = await axios.get(`${API_URL}/api/interviews/${sessionId}/transcript`);
    return response.data;
  } catch (error) {
    console.error('Error fetching transcript:', error);
    throw error;
  }
};

// List all sessions (for admin/history view)
export const listSessions = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/interviews/`);
    return response.data;
  } catch (error) {
    console.error('Error listing sessions:', error);
    throw error;
  }
};