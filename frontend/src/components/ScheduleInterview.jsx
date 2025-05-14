// frontend/src/components/ScheduleInterview.jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { API_URL } from '../config';
import DateTimePicker from 'react-datetime-picker';
import 'react-datetime-picker/dist/DateTimePicker.css';
import { toast } from 'react-toastify'; // Make sure to install: npm install react-toastify

function ScheduleInterview() {
  const [formData, setFormData] = useState({
    candidate_email: '',
    candidate_name: '',
    interviewer_name: '',
    interviewer_email: '', // Added interviewer email
    interview_topic: '',
    candidate_level: 'Junior',
    required_skills: '',
    focus_areas: '',
    send_emails: true, // Option to send emails
  });
  const [scheduledTime, setScheduledTime] = useState(new Date());
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [emailStatus, setEmailStatus] = useState({
    candidate: null,
    interviewer: null
  });
  
  const navigate = useNavigate();
  const { user } = useAuth();

  // Auto-fill interviewer details if user is available
  useEffect(() => {
    if (user) {
      setFormData(prev => ({
        ...prev,
        interviewer_name: user.name || '',
        interviewer_email: user.email || ''
      }));
    }
  }, [user]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setEmailStatus({ candidate: null, interviewer: null });
    
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('Authentication token not found. Please log in again.');
      }
      
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
        throw new Error(
          typeof errorData.detail === 'string' 
            ? errorData.detail 
            : 'Failed to schedule interview'
        );
      }
      
      const data = await response.json();
      
      // If emails are enabled, send notifications
      if (formData.send_emails) {
        await sendEmailNotifications(data.id);
      } else {
        toast.success('Interview scheduled successfully! (Email notifications disabled)');
        navigate('/dashboard', { 
          state: { message: 'Interview scheduled successfully!' } 
        });
      }
    } catch (err) {
      console.error('Error scheduling interview:', err);
      setError(typeof err.message === 'string' ? err.message : 'An error occurred while scheduling the interview');
      toast.error('Failed to schedule interview');
    } finally {
      setIsSubmitting(false);
    }
  };

  const sendEmailNotifications = async (interviewId) => {
    try {
      const token = localStorage.getItem('token');
      
      // Send email to candidate
      const candidateEmailResponse = await fetch(`${API_URL}/api/notifications/email/candidate/${interviewId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      // Send email to interviewer
      const interviewerEmailResponse = await fetch(`${API_URL}/api/notifications/email/interviewer/${interviewId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const candidateStatus = candidateEmailResponse.ok ? 'success' : 'failed';
      const interviewerStatus = interviewerEmailResponse.ok ? 'success' : 'failed';
      
      setEmailStatus({
        candidate: candidateStatus,
        interviewer: interviewerStatus
      });

      if (candidateStatus === 'success' && interviewerStatus === 'success') {
        toast.success('Interview scheduled and all notifications sent successfully!');
        setTimeout(() => {
          navigate('/dashboard', { 
            state: { message: 'Interview scheduled and notifications sent!' } 
          });
        }, 3000); // Give user 3 seconds to see the status before redirecting
      } else {
        toast.warning('Interview scheduled but some notifications failed to send.');
      }
    } catch (err) {
      console.error('Error sending email notifications:', err);
      setEmailStatus({
        candidate: 'failed',
        interviewer: 'failed'
      });
      toast.error('Failed to send email notifications');
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
      
      {/* Email Status Alerts */}
      {emailStatus.candidate && (
        <div className={`alert ${emailStatus.candidate === 'success' ? 'alert-success' : 'alert-danger'}`}>
          Candidate Email: {emailStatus.candidate === 'success' ? 'Sent successfully!' : 'Failed to send'}
        </div>
      )}
      
      {emailStatus.interviewer && (
        <div className={`alert ${emailStatus.interviewer === 'success' ? 'alert-success' : 'alert-danger'}`}>
          Interviewer Email: {emailStatus.interviewer === 'success' ? 'Sent successfully!' : 'Failed to send'}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="interview-form">
        <div className="form-section">
          <h3>Candidate Information</h3>
          <div className="form-group">
            <label htmlFor="candidate_name">Candidate Name</label>
            <input
              type="text"
              id="candidate_name"
              name="candidate_name"
              value={formData.candidate_name}
              onChange={handleChange}
              required
              placeholder="Enter candidate name"
            />
          </div>
          
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
        </div>
        
        <div className="form-section">
          <h3>Interviewer Information</h3>
          <div className="form-group">
            <label htmlFor="interviewer_name">Interviewer Name</label>
            <input
              type="text"
              id="interviewer_name"
              name="interviewer_name"
              value={formData.interviewer_name}
              onChange={handleChange}
              required
              placeholder="Enter interviewer name"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="interviewer_email">Interviewer Email</label>
            <input
              type="email"
              id="interviewer_email"
              name="interviewer_email"
              value={formData.interviewer_email}
              onChange={handleChange}
              required
              placeholder="Enter interviewer email"
            />
          </div>
        </div>
        
        <div className="form-section">
          <h3>Interview Details</h3>
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
          
          <div className="form-group checkbox-group">
            <label htmlFor="send_emails" className="checkbox-label">
              <input
                type="checkbox"
                id="send_emails"
                name="send_emails"
                checked={formData.send_emails}
                onChange={handleChange}
              />
              Send email notifications to candidate and interviewer
            </label>
          </div>
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