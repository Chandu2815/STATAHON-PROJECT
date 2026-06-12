import React, { useEffect, useRef, useState } from 'react';
import { Bell, ChevronDown, Coins, LogOut, Menu, ShieldCheck, User } from 'lucide-react';
import { API } from '../lib/api.js';

export default function Navbar({ onLogout, onMenuClick }) {
  const userDisplayName = localStorage.getItem('userDisplayName');
  const username = localStorage.getItem('username');
  const userEmail = localStorage.getItem('userEmail');
  const userDisplay = userDisplayName || username || userEmail || 'User';
  const [accountType, setAccountType] = useState(localStorage.getItem('account_type') || 'public');
  const [credits, setCredits] = useState({
    remaining: Number(localStorage.getItem('credits_remaining') || 0),
    used: Number(localStorage.getItem('credits_used') || 0),
  });
  const [profileOpen, setProfileOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const refreshCredits = async () => {
      const response = await API.get('/api/user/credits');
      if (response.ok) {
        const nextAccountType = response.data.account_type || 'public';
        const nextCredits = {
          remaining: Number(response.data.credits_remaining ?? 0),
          used: Number(response.data.credits_used ?? 0),
        };
        setAccountType(nextAccountType);
        setCredits(nextCredits);
        localStorage.setItem('account_type', nextAccountType);
        localStorage.setItem('credits_remaining', String(nextCredits.remaining));
        localStorage.setItem('credits_used', String(nextCredits.used));
      }
    };

    const syncFromStorage = () => {
      setAccountType(localStorage.getItem('account_type') || 'public');
      setCredits({
        remaining: Number(localStorage.getItem('credits_remaining') || 0),
        used: Number(localStorage.getItem('credits_used') || 0),
      });
    };

    const closeOnOutsideClick = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setProfileOpen(false);
      }
    };

    refreshCredits();
    window.addEventListener('credits-updated', syncFromStorage);
    document.addEventListener('mousedown', closeOnOutsideClick);
    return () => {
      window.removeEventListener('credits-updated', syncFromStorage);
      document.removeEventListener('mousedown', closeOnOutsideClick);
    };
  }, []);

  const accountLabel = accountType === 'researcher' ? 'Researcher' : 'Public User';

  return (
    <nav className="sticky top-0 z-50 border-b border-slate-200 bg-white/90 shadow-sm backdrop-blur-xl">
      <div className="flex items-center justify-between px-4 py-3 sm:px-8">
        <div className="flex items-center gap-3">
          <button
            onClick={onMenuClick}
            className="rounded-xl p-2 text-slate-600 transition hover:bg-slate-100 hover:text-blue-700"
            title="Toggle menu"
          >
            <Menu size={24} />
          </button>
          <div>
            <h1 className="text-lg font-black tracking-tight text-slate-950 sm:text-xl">Survey AI</h1>
            <p className="hidden text-xs font-semibold text-slate-500 sm:block">Government Data Analytics</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            className="relative rounded-2xl border border-slate-200 bg-white p-2.5 text-slate-600 shadow-sm transition hover:border-blue-200 hover:text-blue-700"
            title="Notifications"
          >
            <Bell size={19} />
            <span className="absolute right-2 top-2 h-2.5 w-2.5 rounded-full border-2 border-white bg-orange-500" />
          </button>

          <div className="hidden items-center gap-2 rounded-2xl border border-emerald-100 bg-emerald-50 px-3 py-2 text-emerald-800 md:flex">
            <ShieldCheck size={16} />
            <span className="text-xs font-black uppercase tracking-wide">{accountLabel}</span>
          </div>

          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setProfileOpen((open) => !open)}
              className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-3 py-2 shadow-sm transition hover:border-blue-200 hover:shadow-md"
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-700 to-indigo-800 text-white">
                <User size={18} />
              </div>
              <div className="hidden text-left sm:block">
                <p className="max-w-[160px] truncate text-sm font-black text-slate-900">{userDisplay}</p>
                <p className="text-[11px] font-semibold text-slate-500">{credits.remaining} credits left</p>
              </div>
              <ChevronDown size={16} className={`text-slate-400 transition ${profileOpen ? 'rotate-180' : ''}`} />
            </button>

            {profileOpen && (
              <div className="absolute right-0 mt-3 w-80 overflow-hidden rounded-3xl border border-slate-100 bg-white shadow-2xl shadow-slate-300/50">
                <div className="bg-gradient-to-br from-blue-950 to-blue-800 p-5 text-white">
                  <div className="flex items-center gap-3">
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/15">
                      <User size={22} />
                    </div>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-black">{userDisplay}</p>
                      <p className="truncate text-xs text-blue-100">{userEmail || username || 'Authenticated user'}</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-3 p-4">
                  <div className="rounded-2xl bg-slate-50 p-4">
                    <div className="mb-3 flex items-center justify-between">
                      <span className="text-xs font-black uppercase tracking-widest text-slate-500">Plan</span>
                      <span className="rounded-full bg-emerald-100 px-3 py-1 text-[10px] font-black uppercase text-emerald-700">
                        {accountLabel}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Coins size={18} className="text-orange-500" />
                      <p className="text-sm font-bold text-slate-800">
                        {credits.remaining} remaining / {credits.used} used
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={onLogout}
                    className="flex w-full items-center justify-center gap-2 rounded-2xl bg-red-500 px-4 py-3 text-sm font-black text-white transition hover:bg-red-600"
                  >
                    <LogOut size={18} />
                    Logout
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
