import React from 'react';
import { LogOut, User, ArrowLeft } from 'lucide-react';

export default function Navbar({ onLogout }) {
  const userEmail = localStorage.getItem('userEmail') || 'User';
  
  // Get MOSPI dashboard URL from environment or use relative path for NGINX
  const mosPIDashboardURL = import.meta.env.VITE_MOSPI_URL || '/dashboard';
  
  const handleBackToMospi = (e) => {
    if (mosPIDashboardURL.startsWith('http')) {
      // Absolute URL - open in same window
      window.location.href = mosPIDashboardURL;
    } else {
      // Relative URL - navigate normally
      window.location.href = mosPIDashboardURL;
    }
  };

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="px-6 py-4 flex items-center justify-between">
        {/* Left: Back to Dashboard Button */}
        <button 
          onClick={handleBackToMospi}
          className="flex items-center gap-2 bg-blue-50 text-blue-600 px-4 py-2 rounded-lg hover:bg-blue-100 transition-colors font-medium cursor-pointer"
          title="Go back to MoSPI dashboard"
        >
          <ArrowLeft size={18} />
          Back to MoSPI
        </button>

        {/* Center: Title */}
        <div className="text-center">
          <h1 className="text-lg font-semibold text-gray-800">Survey AI</h1>
        </div>

        {/* Right: User Profile & Logout */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3 bg-gray-100 px-4 py-2 rounded-full">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
              <User size={18} className="text-white" />
            </div>
            <span className="text-sm font-medium text-gray-700">{userEmail}</span>
          </div>
          
          <button
            onClick={onLogout}
            className="flex items-center gap-2 bg-red-50 text-red-600 px-4 py-2 rounded-lg hover:bg-red-100 transition-colors"
          >
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
