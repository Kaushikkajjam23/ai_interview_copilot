// frontend/src/App.jsx
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';

// Import actual components from your repository
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import ProtectedRoute from './components/ProtectedRoute';
import InterviewSetupForm from './components/InterviewSetupForm';
import InterviewRoom from './components/InterviewRoom';
import InterviewReview from './components/InterviewReview';
import ScheduleInterview from './components/ScheduleInterview';
import Header from './components/Header';
import NotFound from './components/NotFound';

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="min-h-screen flex flex-col">
          <Header />
          
          <main className="flex-grow container mx-auto px-4 py-6">
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              {/* Protected routes */}
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
              
              <Route path="/setup-interview" element={
                <ProtectedRoute>
                  <InterviewSetupForm />
                </ProtectedRoute>
              } />
              
              {/* Interview room - may need special access control */}
              <Route path="/interview/:id" element={<InterviewRoom />} />
              
              {/* Review page */}
              <Route path="/review/:id" element={
                <ProtectedRoute>
                  <InterviewReview />
                </ProtectedRoute>
              } />
              
              {/* Redirect home to dashboard if logged in, otherwise to login */}
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              
              {/* 404 route */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </main>
          
          <footer className="bg-gray-100 py-4 text-center text-gray-600 text-sm">
            © {new Date().getFullYear()} AI Interview Copilot
          </footer>
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;