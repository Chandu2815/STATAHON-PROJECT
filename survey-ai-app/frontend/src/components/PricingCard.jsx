import React from 'react';
import { Check, Zap } from 'lucide-react';

export default function PricingCard({ plan, isHighlighted = false, onSelect }) {
  const isFreePlan = plan.price_inr === 0;
  
  return (
    <div
      className={`group relative rounded-3xl border transition duration-300 ${
        isHighlighted
          ? 'border-2 border-blue-500 bg-blue-50 shadow-2xl shadow-blue-200/50 ring-2 ring-blue-100'
          : 'border border-slate-200 bg-white shadow-lg shadow-slate-200/30 hover:shadow-xl hover:shadow-slate-300/50'
      }`}
    >
      {/* Highlighted Badge */}
      {isHighlighted && (
        <div className="absolute -top-4 left-1/2 -translate-x-1/2 transform">
          <div className="flex items-center gap-2 rounded-full bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-1 text-white">
            <Zap size={14} />
            <span className="text-xs font-black">BEST VALUE</span>
          </div>
        </div>
      )}

      <div className="p-6 sm:p-8">
        {/* Plan Name */}
        <h3 className="text-lg font-black text-slate-900">{plan.name}</h3>
        {plan.description && (
          <p className="mt-1 text-xs font-medium text-slate-500">{plan.description}</p>
        )}

        {/* Price */}
        <div className="mt-6 flex items-baseline gap-2">
          <span className="text-4xl font-black text-slate-950">₹{Math.floor(plan.price_inr)}</span>
          {plan.billing === 'monthly' && <span className="text-sm font-semibold text-slate-600">/month</span>}
          {plan.billing === 'one-time' && <span className="text-sm font-semibold text-slate-600">one-time</span>}
        </div>

        {/* Credits */}
        <div className="mt-4 flex items-center gap-2 rounded-xl bg-slate-50 px-3 py-2">
          <Zap size={16} className="text-orange-500" />
          <span className="text-sm font-black text-slate-700">{plan.credits} queries included</span>
        </div>

        {/* Features */}
        <ul className="mt-6 space-y-3">
          {plan.features && plan.features.map((feature, idx) => (
            <li key={idx} className="flex items-start gap-3">
              <Check
                size={18}
                className={`mt-0.5 flex-shrink-0 ${
                  isHighlighted ? 'text-blue-600' : 'text-emerald-600'
                }`}
              />
              <span className="text-sm font-medium text-slate-700">{feature}</span>
            </li>
          ))}
        </ul>

        {/* CTA Button */}
        <button
          onClick={() => onSelect(plan)}
          className={`mt-8 w-full rounded-2xl px-4 py-3 text-sm font-black uppercase tracking-wider transition ${
            isHighlighted
              ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:shadow-lg hover:shadow-blue-600/30'
              : isFreePlan
              ? 'border-2 border-slate-200 text-slate-900 hover:border-slate-300 hover:bg-slate-50'
              : 'border-2 border-slate-200 text-slate-900 hover:border-blue-500 hover:bg-blue-50'
          }`}
        >
          {isFreePlan ? 'Get Started' : 'Subscribe Now'}
        </button>
      </div>
    </div>
  );
}
