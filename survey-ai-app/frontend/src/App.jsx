import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar.jsx';
import Sidebar from './components/Sidebar.jsx';
import Dashboard from './pages/Dashboard.jsx';
import SurveyAI from './pages/SurveyAI.jsx';
import Settings from './pages/Settings.jsx';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    // First check if token exists in localStorage
    const savedToken = localStorage.getItem('authToken');
    const savedEmail = localStorage.getItem('userEmail');
    
    if (savedToken && savedEmail) {
      console.log('✅ Using existing authentication from localStorage');
      console.log('   Email:', savedEmail);
      return true;
    }
    
    // Check if token passed from MoSPI in URL parameters
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get('token');
    const urlEmail = params.get('email');
    
    console.log('🔍 Checking URL parameters...');
    console.log('   Token:', urlToken ? '✓ Present' : '✗ Missing');
    console.log('   Email:', urlEmail ? urlEmail : '✗ Missing');
    
    if (urlToken && urlEmail) {
      // Store the token and email from MoSPI
      localStorage.setItem('authToken', urlToken);
      localStorage.setItem('userEmail', urlEmail);
      
      // Clean up URL - use the correct path based on environment
      const newPath = import.meta.env.DEV ? '/' : '/survey-ai/';
      window.history.replaceState({}, document.title, newPath);
      
      console.log('✅ Authenticated via MoSPI credentials');
      console.log('   Email:', urlEmail);
      console.log('   Token:', urlToken.substring(0, 20) + '...');
      return true;
    }
    
    // No token found
    console.warn('⚠️ No authentication credentials found');
    console.warn('   Please access Survey AI from MoSPI Dashboard');
    return false;
  });

  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userEmail');
    setIsAuthenticated(false);
    // Redirect back to MoSPI
    window.location.href = 'http://localhost:8000/';
  };

  return (
    <Router basename={import.meta.env.DEV ? '/' : '/survey-ai'}>
      {isAuthenticated ? (
        <div className="flex h-screen bg-gray-50">
          {/* Sidebar */}
          <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />

          {/* Main Content */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Navbar */}
            <Navbar onLogout={handleLogout} onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

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
        // No authentication - show error and redirect message
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
          <div className="w-full max-w-md">
            <div className="text-center mb-8">
              <div className="inline-flex items-center gap-2 mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-red-600 to-red-400 rounded-lg flex items-center justify-center">
                  <span className="text-white text-2xl">⚠️</span>
                </div>
                <h1 className="text-3xl font-bold text-gray-800">
                  Survey AI
                </h1>
              </div>
              <p className="text-gray-600">Explore data like never before</p>
            </div>

            <div className="bg-white rounded-2xl shadow-xl p-8">
              <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h2 className="text-lg font-semibold text-yellow-900 mb-2">Authentication Required</h2>
                <p className="text-sm text-yellow-800 mb-4">
                  Survey AI must be accessed from MoSPI (Main Dashboard) with valid credentials.
                </p>
              </div>

              <div className="space-y-4">
                <p className="text-sm text-gray-600 text-center">
                  Please log in through the main MoSPI dashboard to access Survey AI.
                </p>
                <button
                  onClick={() => window.location.href = 'http://localhost:8000/'}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition-all"
                >
                  Go to MoSPI Dashboard
                </button>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200">
                <p className="text-xs text-gray-500 text-center">
                  Survey AI v1.0.0
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </Router>
  );
}
