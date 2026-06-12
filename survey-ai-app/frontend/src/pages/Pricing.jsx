import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, Zap } from 'lucide-react';
import { API } from '../lib/api.js';
import PricingCard from '../components/PricingCard.jsx';

export default function Pricing() {
  const navigate = useNavigate();
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        setLoading(true);
        const response = await API.get('/api/plans');
        if (response.ok && response.data?.success) {
          setPlans(response.data.plans || []);
        }
      } catch (err) {
        console.error('Error fetching plans:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPlans();
  }, []);

  const handleSelectPlan = (plan) => {
    // Navigate to buy credits with plan info
    navigate('/buy-credits', { state: { selectedPlan: plan } });
  };

  // Separate plans into subscriptions and extras
  const subscriptions = plans.filter(p => p.billing === 'monthly' || p.price_inr === 0);
  const extras = plans.filter(p => p.billing === 'one-time' && p.price_inr > 0);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <section className="border-b border-slate-200 bg-white px-4 py-12 sm:px-8 lg:px-10">
        <div className="mx-auto max-w-5xl text-center">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-blue-700">
            <Sparkles size={14} />
            Simple, Transparent Pricing
          </div>

          <h1 className="text-4xl font-black tracking-tight text-slate-950 sm:text-5xl">
            Unlock AI-Powered Analytics
          </h1>
          <p className="mt-4 text-lg text-slate-600">
            Start free with Survey AI. Scale up as your needs grow. All plans include access to 7+ government datasets and real-time analytics.
          </p>

          {/* Key Benefits */}
          <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="font-black text-slate-900">No Credit Card</div>
              <p className="mt-1 text-sm text-slate-600">Start free. Pay only when you upgrade.</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="font-black text-slate-900">Instant Activation</div>
              <p className="mt-1 text-sm text-slate-600">Credits added immediately after payment.</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="font-black text-slate-900">Full Data Access</div>
              <p className="mt-1 text-sm text-slate-600">All plans include access to all datasets.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="px-4 py-12 sm:px-8 lg:px-10">
        <div className="mx-auto max-w-6xl">
          {/* Monthly Plans */}
          <div className="mb-16">
            <h2 className="mb-2 text-2xl font-black text-slate-900">Monthly Plans</h2>
            <p className="mb-8 text-sm font-medium text-slate-600">
              Best for regular users who want reliable access and priority support.
            </p>

            {loading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className="h-96 animate-pulse rounded-3xl bg-slate-200"
                  />
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                {subscriptions.map((plan) => (
                  <PricingCard
                    key={plan.id}
                    plan={plan}
                    isHighlighted={plan.name === 'Premium'}
                    onSelect={handleSelectPlan}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Extra Credits */}
          {extras.length > 0 && (
            <div>
              <h2 className="mb-2 text-2xl font-black text-slate-900">Extra Credits</h2>
              <p className="mb-8 text-sm font-medium text-slate-600">
                Quick boosts for occasional needs. Perfect with any plan.
              </p>

              <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                {extras.map((plan) => (
                  <PricingCard
                    key={plan.id}
                    plan={plan}
                    onSelect={handleSelectPlan}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </section>

      {/* FAQ Section */}
      <section className="border-t border-slate-200 bg-white px-4 py-12 sm:px-8 lg:px-10">
        <div className="mx-auto max-w-3xl">
          <h2 className="mb-8 text-2xl font-black text-slate-900">Frequently Asked Questions</h2>

          <div className="space-y-6">
            {[
              {
                q: 'How do credits work?',
                a: 'Each query to Survey AI consumes 1 credit. Your credits refresh based on your plan. Unused credits roll over to the next billing cycle.',
              },
              {
                q: 'Can I cancel my subscription?',
                a: 'Yes, anytime. No questions asked. Your current billing period remains active until renewal date.',
              },
              {
                q: 'What if I run out of credits mid-month?',
                a: 'Buy extra credits instantly. They\'re added immediately and can be used right away.',
              },
              {
                q: 'Do I get a refund if I don\'t use all my credits?',
                a: 'Unused credits carry over to your next billing cycle. Monthly subscriptions reset every 30 days.',
              },
            ].map((faq, idx) => (
              <div key={idx} className="rounded-xl border border-slate-200 bg-slate-50 p-4 sm:p-6">
                <h3 className="font-black text-slate-900">{faq.q}</h3>
                <p className="mt-2 text-sm text-slate-700">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Footer */}
      <section className="border-t border-slate-200 bg-gradient-to-br from-blue-950 to-blue-900 px-4 py-12 text-white sm:px-8 lg:px-10">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-2xl font-black sm:text-3xl">
            Ready to supercharge your analytics?
          </h2>
          <p className="mt-3 text-blue-100">
            Start with the Free plan. Scale up anytime—no credit card required.
          </p>
          <button
            onClick={() => navigate('/buy-credits')}
            className="mt-6 inline-flex items-center gap-2 rounded-2xl bg-white px-6 py-3 text-base font-black text-blue-900 transition hover:shadow-lg hover:shadow-white/20"
          >
            <Zap size={18} />
            Get Started Now
            <ArrowRight size={18} />
          </button>
        </div>
      </section>
    </div>
  );
}
