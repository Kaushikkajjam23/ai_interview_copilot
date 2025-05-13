// frontend/src/App.jsx
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import ScheduleInterview from './components/ScheduleInterview';
import InterviewRoom from './components/InterviewRoom';
import InterviewReview from './components/InterviewReview';
import NotFound from './components/NotFound';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app-container">
          <Routes>
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            
            <Route path="/schedule-interview" element={
              <ProtectedRoute>
                <ScheduleInterview />
              </ProtectedRoute>
            } />
            
            <Route path="/edit-interview/:sessionId" element={
              <ProtectedRoute>
                <ScheduleInterview isEdit={true} />
              </ProtectedRoute>
            } />
            
            <Route path="/interview/:sessionId" element={
              <ProtectedRoute>
                <InterviewRoom />
              </ProtectedRoute>
            } />
            
            <Route path="/review/:sessionId" element={
              <ProtectedRoute>
                <InterviewReview />
              </ProtectedRoute>
            } />
            
            <Route path="/404" element={<NotFound />} />
            <Route path="*" element={<Navigate to="/404" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;