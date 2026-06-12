import React from 'react';
import { AlertCircle, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function LowCreditAlert({ credits = 0, onClose }) {
  const navigate = useNavigate();
  const isLow = credits > 0 && credits <= 3;

  if (!isLow) return null;

  const handleBuyCredits = () => {
    navigate('/buy-credits');
  };

  return (
    <div className="animate-in fade-in slide-in-from-top-2 duration-300 rounded-2xl border-l-4 border-red-500 bg-red-50 p-4 shadow-md">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-100 flex-shrink-0 mt-0.5">
            <AlertCircle size={18} className="text-red-600" />
          </div>
          <div className="min-w-0">
            <h3 className="font-black text-red-900">Low credits warning</h3>
            <p className="mt-0.5 text-sm text-red-800">
              You have <span className="font-bold">{credits} {credits === 1 ? 'query' : 'queries'}</span> remaining. Recharge to continue using AI features.
            </p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="flex-shrink-0 text-red-600 transition hover:text-red-700"
        >
          ✕
        </button>
      </div>

      {/* Action Buttons */}
      <div className="mt-4 flex flex-wrap gap-2 pl-11">
        <button
          onClick={handleBuyCredits}
          className="inline-flex items-center gap-2 rounded-lg bg-red-600 px-3 py-1.5 text-xs font-black text-white transition hover:bg-red-700"
        >
          <Zap size={14} />
          Buy Credits Now
        </button>
      </div>
    </div>
  );
}
