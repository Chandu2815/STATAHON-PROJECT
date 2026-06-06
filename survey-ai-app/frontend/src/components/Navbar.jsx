import React from 'react';
import { LogOut, User, Menu } from 'lucide-react';

export default function Navbar({ onLogout, onMenuClick }) {
  const userEmail = localStorage.getItem('userEmail');
  const userDisplay = userEmail || 'User';

  return (
    <nav className="bg-gradient-to-r from-blue-900 via-blue-800 to-blue-900 border-b-4 border-orange-500 shadow-lg">
      <div className="px-4 sm:px-8 py-4 sm:py-5 flex items-center justify-between">
        {/* Left: Menu Button */}
        <div className="flex items-center gap-2 sm:gap-3">
          <button
            onClick={onMenuClick}
            className="p-2 hover:bg-blue-700 rounded-lg transition-colors text-white"
            title="Toggle menu"
          >
            <Menu size={24} />
          </button>
        </div>

        {/* Center: Title */}
        <div className="text-center mx-4">
          <h1 className="text-xl sm:text-2xl font-bold text-white">Survey AI</h1>
          <p className="text-xs text-blue-100 mt-0.5 hidden sm:block">Government Data Analytics</p>
        </div>

        {/* Right: User Profile & Logout */}
        <div className="flex items-center gap-3 sm:gap-5">
          <div className="flex items-center gap-2 sm:gap-3 bg-white bg-opacity-10 px-3 sm:px-5 py-2 rounded-lg border border-white border-opacity-20">
            <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center flex-shrink-0">
              <User size={18} className="text-white" />
            </div>
            <span className="text-xs sm:text-sm font-medium text-white hidden sm:inline">{userDisplay}</span>
          </div>
          
          <button
            onClick={onLogout}
            className="flex items-center gap-1 sm:gap-2 bg-red-500 hover:bg-red-600 text-white px-3 sm:px-5 py-2 rounded-lg transition-colors font-semibold text-xs sm:text-sm whitespace-nowrap"
          >
            <LogOut size={18} />
            <span className="hidden sm:inline">Logout</span>
          </button>
        </div>
      </div>
    </nav>
  );
}
