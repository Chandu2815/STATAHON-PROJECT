import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar.jsx';
import Sidebar from './components/Sidebar.jsx';
import Login from './pages/Login.jsx';
import Dashboard from './pages/Dashboard.jsx';
import SurveyAI from './pages/SurveyAI.jsx';
import Settings from './pages/Settings.jsx';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    // Check if token exists in localStorage
    const token = localStorage.getItem('authToken');
    if (token) return true;
    
    // Check if token passed from MoSPI in URL
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get('token');
    const email = params.get('email');
    
    if (urlToken && email) {
      // Store the token and email from MoSPI
      localStorage.setItem('authToken', urlToken);
      localStorage.setItem('userEmail', email);
      // Clean up URL
      window.history.replaceState({}, document.title, '/survey-ai');
      return true;
    }
    
    return false;
  });

  const handleLogin = (status) => {
    setIsAuthenticated(status);
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userEmail');
    setIsAuthenticated(false);
  };

  return (
    <Router>
      {isAuthenticated ? (
        <div className="flex h-screen bg-gray-50">
          {/* Sidebar */}
          <Sidebar />

          {/* Main Content */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Navbar */}
            <Navbar onLogout={handleLogout} />

            {/* Page Content */}
            <main className="flex-1 overflow-auto">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/survey-ai" element={<SurveyAI />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
          </div>
        </div>
      ) : (
        <>
          <Login onLogin={handleLogin} />
          <div style={{ position: 'fixed', bottom: '10px', right: '10px', padding: '10px', background: '#000', color: '#0f0', fontFamily: 'monospace', fontSize: '12px', zIndex: 9999 }}>
            Survey AI Loading... ✓
          </div>
        </>
      )}
    </Router>
  );
}
