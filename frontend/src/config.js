// frontend/src/config.js
export const API_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-production-api.com' 
  : 'http://localhost:8000';
export const WS_BASE_URL = 'wss://ai-interview-copilot.onrender.com/ws';