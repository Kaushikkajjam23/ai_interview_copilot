// frontend/src/services/apiService.js
import { API_URL } from '../config';
import axios from 'axios';

/**
 * Service for handling API calls to the backend
 */
class ApiService {
  /**
   * Fetch interview session data by ID
   * @param {number} sessionId - The interview session ID
   * @returns {Promise<Object>} - The session data
   */
  async fetchSession(sessionId) {
    try {
      const response = await axios.get(`${API_URL}/api/interviews/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching session:', error);
      throw error;
    }
  }

  /**
   * Create a new interview session
   * @param {Object} sessionData - The interview session data
   * @returns {Promise<Object>} - The created session
   */
  async createSession(sessionData) {
    try {
      const response = await axios.post(`${API_URL}/api/interviews/`, sessionData);
      return response.data;
    } catch (error) {
      console.error('Error creating session:', error);
      throw error;
    }
  }

  /**
   * Fetch all interview sessions
   * @returns {Promise<Array>} - Array of session data
   */
  async fetchAllSessions() {
    try {
      const response = await axios.get(`${API_URL}/api/interviews/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching all sessions:', error);
      throw error;
    }
  }

  /**
   * Get the transcript for an interview session
   * @param {number} sessionId - The interview session ID
   * @returns {Promise<Object>} - The transcript data
   */
  async fetchTranscript(sessionId) {
    try {
      const response = await axios.get(`${API_URL}/api/interviews/${sessionId}/transcript`);
      return response.data;
    } catch (error) {
      console.error('Error fetching transcript:', error);
      throw error;
    }
  }

  /**
   * Request AI analysis for an interview session
   * @param {number} sessionId - The interview session ID
   * @returns {Promise<Object>} - The analysis status
   */
  async requestAnalysis(sessionId) {
    try {
      const response = await axios.post(`${API_URL}/api/interviews/${sessionId}/analyze`);
      return response.data;
    } catch (error) {
      console.error('Error requesting analysis:', error);
      throw error;
    }
  }

  /**
   * Get the recording URL for an interview session
   * @param {number} sessionId - The interview session ID
   * @returns {string} - The recording URL
   */
  getRecordingUrl(sessionId) {
    return `${API_URL}/api/interviews/${sessionId}/recording`;
  }
}

export default new ApiService();