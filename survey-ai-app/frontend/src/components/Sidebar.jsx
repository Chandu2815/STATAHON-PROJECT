import React, { useCallback } from 'react';
import { BarChart3, Settings, Home } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  // Handle Survey AI redirect with token
  const handleSurveyAIClick = useCallback(() => {
    // Get authentication token from localStorage
    const token = localStorage.getItem('authToken');
    
    // Survey AI external URL
    const surveyAIUrl = 'http://statquery.in/survey-ai';
    
    // Build redirect URL with token if available
    const redirectUrl = token 
      ? `${surveyAIUrl}?token=${encodeURIComponent(token)}`
      : surveyAIUrl;
    
    console.log('🔄 Redirecting to Survey AI:', redirectUrl);
    window.location.href = redirectUrl;
  }, []);

  // Navigation items - Dashboard and Settings use internal navigation
  const navItems = [
    { 
      path: '/', 
      label: 'Dashboard', 
      icon: Home,
      onClick: () => navigate('/')
    },
    { 
      path: '/survey-ai', 
      label: 'Survey AI', 
      icon: BarChart3,
      onClick: handleSurveyAIClick,
      external: true
    },
    { 
      path: '/settings', 
      label: 'Settings', 
      icon: Settings,
      onClick: () => navigate('/settings')
    },
  ];

  return (
    <aside className="w-64 bg-white border-r border-gray-200 shadow-sm">
      <div className="p-6 space-y-8">
        {/* Navigation Items */}
        <nav className="space-y-2">
          {navItems.map(({ path, label, icon: Icon, onClick, external }) => (
            <button
              key={path}
              onClick={onClick}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                !external && isActive(path)
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
              title={external ? 'Opens Survey AI in current window' : ''}
            >
              <Icon size={20} />
              <span className="font-medium">{label}</span>
              {external && <span className="ml-auto text-xs opacity-60">↗</span>}
            </button>
          ))}
        </nav>

        {/* Info Box */}
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 p-4 rounded-lg border border-blue-200">
          <h3 className="text-sm font-bold text-blue-900 mb-2">Survey AI</h3>
          <p className="text-xs text-blue-800">
            Explore datasets dynamically with powerful filtering and visualization tools.
          </p>
        </div>
      </div>
    </aside>
  );
}
