// frontend/src/config.js
// config.js
const LOCAL_API_URL = 'http://localhost:8000/api';
const DEPLOYMENT_API_URL = 'https://ai-interview-copilot.onrender.com/api';

// Export the correct API URL based on the environment
export const API_URL = process.env.NODE_ENV === 'production' ? DEPLOYMENT_API_URL : LOCAL_API_URL;
export const WS_BASE_URL = 'wss://ai-interview-copilot.onrender.com/ws';