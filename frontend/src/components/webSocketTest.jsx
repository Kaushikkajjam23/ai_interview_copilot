// frontend/src/components/WebSocketTest.jsx
import { useState, useEffect } from 'react';
import { WS_BASE_URL } from '../config';

function WebSocketTest() {
  const [status, setStatus] = useState('Connecting...');
  const [messages, setMessages] = useState([]);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const wsUrl = `${WS_BASE_URL}/ws/test`;
    console.log('Connecting to:', wsUrl);
    
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      setStatus('Connected');
      setMessages(prev => [...prev, 'Connected to WebSocket server']);
    };
    
    ws.onmessage = (event) => {
      setMessages(prev => [...prev, `Received: ${event.data}`]);
    };
    
    ws.onerror = (error) => {
      setStatus('Error');
      setMessages(prev => [...prev, `WebSocket error: ${JSON.stringify(error)}`]);
    };
    
    ws.onclose = () => {
      setStatus('Closed');
      setMessages(prev => [...prev, 'Connection closed']);
    };
    
    setSocket(ws);
    
    return () => {
      ws.close();
    };
  }, []);

  const sendMessage = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send('Hello server');
      setMessages(prev => [...prev, 'Sent: Hello server']);
    }
  };

  return (
    <div>
      <h1>WebSocket Test</h1>
      <p>Status: {status}</p>
      <button onClick={sendMessage} disabled={status !== 'Connected'}>
        Send Test Message
      </button>
      <div style={{ marginTop: '20px' }}>
        <h2>Log:</h2>
        <pre style={{ height: '300px', overflow: 'auto', border: '1px solid #ccc', padding: '10px' }}>
          {messages.map((msg, i) => (
            <div key={i}>{msg}</div>
          ))}
        </pre>
      </div>
    </div>
  );
}

export default WebSocketTest;