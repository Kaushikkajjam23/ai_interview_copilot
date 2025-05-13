// frontend/src/components/ScheduleInterview.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { API_URL } from '../config';
import DateTimePicker from 'react-datetime-picker';
import 'react-datetime-picker/dist/DateTimePicker.css';

function ScheduleInterview() {
  const [formData, setFormData] = useState({
    candidate_email: '',
    interview_topic: '',
    candidate_level: 'Junior',
    required_skills: '',
    focus_areas: '',
  });
  const [scheduledTime, setScheduledTime] = useState(new Date());
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/interviews/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          scheduled_time: scheduledTime.toISOString()
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to schedule interview');
      }
      
      const data = await response.json();
      navigate('/dashboard', { 
        state: { message: 'Interview scheduled successfully!' } 
      });
    } catch (err) {
      console.error('Error scheduling interview:', err);
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="schedule-interview-container">
      <h1>Schedule New Interview</h1>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="interview-form">
        <div className="form-group">
          <label htmlFor="candidate_email">Candidate Email</label>
          <input
            type="email"
            id="candidate_email"
            name="candidate_email"
            value={formData.candidate_email}
            onChange={handleChange}
            required
            placeholder="Enter candidate email"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="interview_topic">Interview Topic</label>
          <input
            type="text"
            id="interview_topic"
            name="interview_topic"
            value={formData.interview_topic}
            onChange={handleChange}
            required
            placeholder="E.g., Frontend Development, Machine Learning"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="candidate_level">Candidate Level</label>
          <select
            id="candidate_level"
            name="candidate_level"
            value={formData.candidate_level}
            onChange={handleChange}
            required
          >
            <option value="Junior">Junior</option>
            <option value="Mid-level">Mid-level</option>
            <option value="Senior">Senior</option>
            <option value="Lead">Lead</option>
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="required_skills">Required Skills</label>
          <textarea
            id="required_skills"
            name="required_skills"
            value={formData.required_skills}
            onChange={handleChange}
            required
            placeholder="E.g., HTML, CSS, JavaScript, React"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="focus_areas">Focus Areas</label>
          <textarea
            id="focus_areas"
            name="focus_areas"
            value={formData.focus_areas}
            onChange={handleChange}
            required
            placeholder="E.g., Responsive Design, State Management"
          />
        </div>
        
        <div className="form-group">
          <label>Scheduled Time</label>
          <DateTimePicker
            onChange={setScheduledTime}
            value={scheduledTime}
            className="datetime-picker"
            minDate={new Date()}
            required
          />
        </div>
        
        <div className="form-actions">
          <button
            type="button"
            className="cancel-button"
            onClick={() => navigate('/dashboard')}
          >
            Cancel
          </button>
          
          <button
            type="submit"
            className="submit-button"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Scheduling...' : 'Schedule Interview'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default ScheduleInterview;