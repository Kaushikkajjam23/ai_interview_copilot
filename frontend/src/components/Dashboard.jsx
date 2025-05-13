// frontend/src/components/Dashboard.jsx
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { API_URL } from '../config';

function Dashboard() {
  const [interviews, setInterviews] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('upcoming');
  
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchInterviews();
  }, []);

  const fetchInterviews = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/interviews/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch interviews');
      }
      
      const data = await response.json();
      setInterviews(data);
    } catch (err) {
      console.error('Error fetching interviews:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const getFilteredInterviews = () => {
    const now = new Date();
    
    switch (activeTab) {
      case 'upcoming':
        return interviews.filter(interview => 
          new Date(interview.scheduled_time) > now && !interview.is_canceled && !interview.is_completed
        );
      case 'past':
        return interviews.filter(interview => 
          (new Date(interview.scheduled_time) < now || interview.is_completed) && !interview.is_canceled
        );
      case 'canceled':
        return interviews.filter(interview => interview.is_canceled);
      default:
        return interviews;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not scheduled';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Welcome, {user?.full_name}</h1>
        <button
          className="new-interview-button"
          onClick={() => navigate('/schedule-interview')}
        >
          Schedule New Interview
        </button>
      </div>
      
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'upcoming' ? 'active' : ''}`}
          onClick={() => setActiveTab('upcoming')}
        >
          Upcoming Interviews
        </button>
        <button 
          className={`tab ${activeTab === 'past' ? 'active' : ''}`}
          onClick={() => setActiveTab('past')}
        >
          Past Interviews
        </button>
        <button 
          className={`tab ${activeTab === 'canceled' ? 'active' : ''}`}
          onClick={() => setActiveTab('canceled')}
        >
          Canceled Interviews
        </button>
      </div>
      
      {isLoading ? (
        <div className="loading">Loading interviews...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : getFilteredInterviews().length === 0 ? (
        <div className="no-interviews">
          No {activeTab} interviews found.
        </div>
      ) : (
        <div className="interviews-list">
          {getFilteredInterviews().map(interview => (
            <div key={interview.id} className="interview-card">
              <div className="interview-info">
                <h3>{interview.interview_topic}</h3>
                <p><strong>Candidate:</strong> {interview.candidate_name}</p>
                <p><strong>Scheduled:</strong> {formatDate(interview.scheduled_time)}</p>
                <p><strong>Status:</strong> {
                  interview.is_canceled ? 'Canceled' : 
                  interview.is_completed ? 'Completed' : 
                  'Scheduled'
                }</p>
              </div>
              
              <div className="interview-actions">
                {!interview.is_canceled && !interview.is_completed && (
                  <Link 
                    to={`/interview/${interview.id}?role=interviewer`}
                    className="action-button join"
                  >
                    Join Interview
                  </Link>
                )}
                
                {interview.is_completed && (
                  <Link 
                    to={`/review/${interview.id}`}
                    className="action-button review"
                  >
                    View Results
                  </Link>
                )}
                
                <Link 
                  to={`/edit-interview/${interview.id}`}
                  className="action-button edit"
                >
                  Edit
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Dashboard;