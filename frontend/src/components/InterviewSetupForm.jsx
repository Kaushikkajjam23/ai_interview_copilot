import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import axios from 'axios';

// API base URL
const API_URL = 'http://localhost:8000/api';

// Validation schema
const InterviewSchema = Yup.object().shape({
  interviewer_name: Yup.string()
    .min(2, 'Too Short!')
    .max(50, 'Too Long!')
    .required('Required'),
  candidate_name: Yup.string()
    .min(2, 'Too Short!')
    .max(50, 'Too Long!')
    .required('Required'),
  interview_topic: Yup.string()
    .min(5, 'Too Short!')
    .max(100, 'Too Long!')
    .required('Required'),
  candidate_level: Yup.string()
    .required('Please select a candidate level'),
  required_skills: Yup.string()
    .required('Please enter at least one required skill'),
  focus_areas: Yup.string()
    .required('Please enter at least one focus area'),
});

function InterviewSetupForm() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (values) => {
    setIsSubmitting(true);
    setError(null);
    
    try {
      // Send the form data to the backend API
      const response = await axios.post(`${API_URL}/interviews/`, values);
      
      // Get the session ID from the response
      const sessionId = response.data.id;
      
      // Navigate to the interview room with the session ID
      navigate(`/interview/${sessionId}`);
    } catch (err) {
      console.error('Error creating interview session:', err);
      setError(
        err.response?.data?.detail || 
        'An error occurred while creating the interview session. Please try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="setup-form-container">
      <h1>Set Up New Interview</h1>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <Formik
        initialValues={{
          interviewer_name: '',
          candidate_name: '',
          interview_topic: '',
          candidate_level: '',
          required_skills: '',
          focus_areas: '',
        }}
        validationSchema={InterviewSchema}
        onSubmit={handleSubmit}
      >
        {({ isValid }) => (
          <Form className="interview-form">
            <div className="form-group">
              <label htmlFor="interviewer_name">Interviewer Name</label>
              <Field 
                type="text" 
                id="interviewer_name" 
                name="interviewer_name" 
                placeholder="Enter your name"
              />
              <ErrorMessage name="interviewer_name" component="div" className="error" />
            </div>

            <div className="form-group">
              <label htmlFor="candidate_name">Candidate Name</label>
              <Field 
                type="text" 
                id="candidate_name" 
                name="candidate_name" 
                placeholder="Enter candidate name"
              />
              <ErrorMessage name="candidate_name" component="div" className="error" />
            </div>

            <div className="form-group">
              <label htmlFor="interview_topic">Interview Topic</label>
              <Field 
                type="text" 
                id="interview_topic" 
                name="interview_topic" 
                placeholder="E.g., Full Stack Development, Machine Learning, etc."
              />
              <ErrorMessage name="interview_topic" component="div" className="error" />
            </div>

            <div className="form-group">
              <label htmlFor="candidate_level">Candidate Level</label>
              <Field as="select" id="candidate_level" name="candidate_level">
                <option value="">Select level</option>
                <option value="Junior">Junior</option>
                <option value="Mid-level">Mid-level</option>
                <option value="Senior">Senior</option>
                <option value="Lead">Lead</option>
              </Field>
              <ErrorMessage name="candidate_level" component="div" className="error" />
            </div>

            <div className="form-group">
              <label htmlFor="required_skills">Required Skills</label>
              <Field 
                as="textarea" 
                id="required_skills" 
                name="required_skills" 
                placeholder="E.g., Python, React, SQL, System Design (comma separated)"
              />
              <ErrorMessage name="required_skills" component="div" className="error" />
            </div>

            <div className="form-group">
              <label htmlFor="focus_areas">Focus Areas</label>
              <Field 
                as="textarea" 
                id="focus_areas" 
                name="focus_areas" 
                placeholder="E.g., Architecture decisions, API design, Problem solving approach"
              />
              <ErrorMessage name="focus_areas" component="div" className="error" />
            </div>

            <button 
              type="submit" 
              className="submit-button" 
              disabled={isSubmitting || !isValid}
            >
              {isSubmitting ? 'Creating...' : 'Start Interview'}
            </button>
          </Form>
        )}
      </Formik>
    </div>
  );
}

export default InterviewSetupForm;