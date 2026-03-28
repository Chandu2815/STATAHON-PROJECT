import React from 'react';
import { BarChart3, Settings, Home, ChevronLeft } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function Sidebar({ isOpen, onToggle }) {
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  // Navigation items - Dashboard, Survey AI, and Settings use internal navigation
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
      onClick: () => navigate('/survey-ai')
    },
    { 
      path: '/settings', 
      label: 'Settings', 
      icon: Settings,
      onClick: () => navigate('/settings')
    },
  ];

  return (
    <>
      {/* Sidebar Overlay - Only on Mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 bg-gradient-to-b from-gray-50 to-white border-r border-gray-300 shadow-lg transition-all duration-300 ease-in-out h-screen overflow-y-auto pt-20 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Fixed Header with Close Button */}
        <div className="fixed top-0 left-0 w-64 bg-white border-b border-gray-300 p-4 flex items-center justify-between z-50">
          <div>
            <h2 className="text-lg font-bold text-blue-900">Menu</h2>
          </div>
          <button
            onClick={onToggle}
            className="p-1 hover:bg-gray-200 rounded-lg transition-colors text-gray-700 flex-shrink-0"
            title="Close menu"
          >
            <ChevronLeft size={28} />
          </button>
        </div>

        <div className="p-6 space-y-4">
          {/* Branding Section */}
          <div className="pb-4 border-b border-gray-200">
            <h3 className="text-sm font-bold text-blue-900">Survey AI</h3>
            <p className="text-xs text-gray-600">Data Explorer</p>
          </div>

          {/* Navigation Items */}
          <nav className="space-y-3">
            {navItems.map(({ path, label, icon: Icon, onClick }) => (
              <button
                key={path}
                onClick={() => {
                  onClick();
                  // Close sidebar after navigation
                  onToggle();
                }}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all border-l-4 font-medium ${
                  isActive(path)
                    ? 'bg-blue-900 text-white border-l-orange-500 shadow-md'
                    : 'text-gray-700 hover:bg-gray-100 border-l-transparent hover:text-blue-900'
                }`}
              >
                <Icon size={22} className="flex-shrink-0" />
                <span>{label}</span>
              </button>
            ))}
          </nav>

          {/* Info Box */}
          <div className="mt-8 p-4 bg-blue-50 rounded-lg border-l-4 border-l-blue-900 border border-blue-200">
            <h3 className="text-sm font-bold text-blue-900 mb-2">💡 Quick Tip</h3>
            <p className="text-xs text-blue-800">
              Select Dataset → Columns → Filters → Analyze your survey data interactively
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}
