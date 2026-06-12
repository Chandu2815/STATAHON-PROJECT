import React, { useState } from 'react';
import { AlertTriangle, X, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function RechargeModal({ isOpen, onClose }) {
  const navigate = useNavigate();

  if (!isOpen) return null;

  const handleBuyCredits = () => {
    onClose();
    navigate('/buy-credits');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
      <div className="relative w-full max-w-md overflow-hidden rounded-3xl bg-white shadow-2xl shadow-slate-900/30 animate-in fade-in zoom-in duration-300">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-lg p-1.5 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
        >
          <X size={20} />
        </button>

        {/* Header */}
        <div className="bg-gradient-to-br from-red-50 to-orange-50 p-6 sm:p-8">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-red-100">
              <AlertTriangle size={24} className="text-red-600" />
            </div>
            <div>
              <h2 className="text-lg font-black text-slate-900">Out of Credits</h2>
              <p className="text-sm font-medium text-slate-600">You've used all your available queries</p>
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="p-6 sm:p-8">
          <p className="text-sm text-slate-700 leading-relaxed">
            To continue using Survey AI's powerful features, you'll need to recharge your credits. Choose a plan that works for you—monthly subscriptions offer the best value for heavy users.
          </p>

          {/* Quick Stats */}
          <div className="mt-6 grid grid-cols-2 gap-3">
            <div className="rounded-xl bg-slate-50 p-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Premium Plan</p>
              <p className="mt-1 text-lg font-black text-slate-900">₹99</p>
              <p className="text-[10px] font-medium text-slate-600">100 queries</p>
            </div>
            <div className="rounded-xl bg-blue-50 p-3 border-2 border-blue-200">
              <p className="text-xs font-semibold uppercase tracking-wide text-blue-600">Ultra Plan</p>
              <p className="mt-1 text-lg font-black text-blue-900">₹399</p>
              <p className="text-[10px] font-medium text-blue-700">500 queries</p>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="mt-8 flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 rounded-xl border-2 border-slate-200 px-4 py-3 text-sm font-black text-slate-900 transition hover:border-slate-300 hover:bg-slate-50"
            >
              Maybe Later
            </button>
            <button
              onClick={handleBuyCredits}
              className="flex-1 flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-3 text-sm font-black text-white transition hover:shadow-lg hover:shadow-blue-600/30"
            >
              <Zap size={16} />
              Buy Credits
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
