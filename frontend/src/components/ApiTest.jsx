// frontend/src/components/ApiTest.jsx
import { useState, useEffect } from 'react';
import { API_URL } from '../config';

function ApiTest() {
  const [status, setStatus] = useState('Checking API...');
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const testApi = async () => {
      try {
        setStatus('Sending request to API...');
        const response = await fetch(`${API_URL}/api/interviews/`);
        const data = await response.json();
        
        setStatus(`API connection successful! Found ${data.length} interviews.`);
      } catch (err) {
        console.error('API test failed:', err);
        setError(`API connection failed: ${err.message}`);
        setStatus('Failed');
      }
    };
    
    testApi();
  }, []);
  
  return (
    <div className="api-test">
      <h1>API Connection Test</h1>
      <p>API URL: {API_URL}</p>
      <p>Status: {status}</p>
      {error && <p className="error">{error}</p>}
    </div>
  );
}

export default ApiTest;