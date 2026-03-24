import React from 'react';
import { LogOut, User } from 'lucide-react';

export default function Navbar({ onLogout }) {
  const userEmail = localStorage.getItem('userEmail') || 'User';

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="px-6 py-4 flex items-center justify-between">
        {/* Left: Empty space */}
        <div className="w-10 h-10"></div>

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
