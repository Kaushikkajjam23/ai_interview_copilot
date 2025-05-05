import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import InterviewSetupForm from './components/InterviewSetupForm';
import InterviewRoom from './components/InterviewRoom';
import InterviewReview from './components/InterviewReview';
import Header from './components/Header';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<InterviewSetupForm />} />
            <Route path="/interview/:sessionId" element={<InterviewRoom />} />
            <Route path="/review/:sessionId" element={<InterviewReview />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;