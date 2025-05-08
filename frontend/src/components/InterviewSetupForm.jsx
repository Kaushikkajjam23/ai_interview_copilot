import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { API_URL } from '../config'; // Import API_URL directly

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

  const handleSubmit = async (values, { setSubmitting }) => {
    setIsSubmitting(true);
    setError(null);
    
    try {
      console.log('Submitting to:', `${API_URL}/api/interviews/`);
      console.log('Form data:', values);
      
      // Test if the API is reachable
      try {
        const pingResponse = await fetch(`${API_URL}/api/interviews/`, {
          method: 'OPTIONS',
        });
        console.log('API ping response:', pingResponse.status);
      } catch (pingErr) {
        console.error('API ping failed:', pingErr);
      }
      
      const response = await fetch(`${API_URL}/api/interviews/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });
      
      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to create interview session');
      }
      
      console.log('Success! Interview created:', data);
      navigate(`/interview/${data.id}?role=interviewer`);
    } catch (err) {
      console.error('Error creating interview:', err);
      setError(`An error occurred while creating the interview session: ${err.message}`);
    } finally {
      setIsSubmitting(false);
      setSubmitting(false);
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
        {({ isValid, isSubmitting: formikSubmitting }) => (
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
              disabled={isSubmitting || formikSubmitting || !isValid}
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