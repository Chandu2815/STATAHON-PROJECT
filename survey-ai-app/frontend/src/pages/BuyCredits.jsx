import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle, AlertCircle, Loader, Zap, CreditCard } from 'lucide-react';
import { API } from '../lib/api.js';

export default function BuyCredits() {
  const navigate = useNavigate();
  const location = useLocation();
  const selectedPlanFromNav = location.state?.selectedPlan;

  const [plans, setPlans] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState(selectedPlanFromNav || null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('razorpay');

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        setLoading(true);
        const response = await API.get('/api/plans');
        if (response.ok && response.data?.success) {
          const allPlans = response.data.plans || [];
          setPlans(allPlans);
          
          // If no plan selected from nav, default to Premium
          if (!selectedPlanFromNav && !selectedPlan) {
            const premiumPlan = allPlans.find(p => p.name === 'Premium');
            if (premiumPlan) setSelectedPlan(premiumPlan);
          }
        }
      } catch (err) {
        console.error('Error fetching plans:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPlans();
  }, [selectedPlanFromNav]);

  const handleInitiatePayment = async () => {
    if (!selectedPlan) {
      alert('Please select a plan');
      return;
    }

    try {
      setProcessing(true);
      setPaymentStatus(null);

      // Step 1: Create payment order
      const orderResponse = await API.post('/api/payments/create-order', {
        plan_id: selectedPlan.id,
        payment_method: paymentMethod,
      });

      if (!orderResponse.ok || !orderResponse.data?.success) {
        throw new Error(orderResponse.data?.error || 'Failed to create order');
      }

      const orderData = orderResponse.data;
      const razorpayOrder = orderData.order;

      // TODO: In production, integrate with actual Razorpay or Stripe
      // For now, simulate payment processing

      // Step 2: Simulate payment verification (would be done server-side in production)
      // In a real app, user would complete payment on Razorpay/Stripe, then server webhook would verify
      setTimeout(async () => {
        try {
          const verifyResponse = await API.post('/api/payments/verify', {
            order_id: razorpayOrder.id,
            payment_id: `pay_${Date.now()}`, // Simulated payment ID
            signature: 'simulated_signature',
          });

          if (verifyResponse.ok && verifyResponse.data?.success) {
            setPaymentStatus({
              type: 'success',
              message: verifyResponse.data.message,
              credits: verifyResponse.data.credits_remaining,
            });

            // Update localStorage
            localStorage.setItem('credits_remaining', String(verifyResponse.data.credits_remaining));
            localStorage.setItem('credits_used', String(verifyResponse.data.credits_used));
            window.dispatchEvent(new Event('credits-updated'));

            // Auto-redirect after 3 seconds
            setTimeout(() => {
              navigate('/');
            }, 3000);
          } else {
            throw new Error(verifyResponse.data?.error || 'Payment verification failed');
          }
        } catch (verifyErr) {
          setPaymentStatus({
            type: 'error',
            message: verifyErr.message || 'Payment verification failed. Please try again.',
          });
          setProcessing(false);
        }
      }, 1500);
    } catch (err) {
      setPaymentStatus({
        type: 'error',
        message: err.message || 'Failed to initiate payment',
      });
      setProcessing(false);
    }
  };

  const subscriptionPlans = plans.filter(p => p.billing === 'monthly' || p.price_inr === 0);
  const extraPlans = plans.filter(p => p.billing === 'one-time' && p.price_inr > 0);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="border-b border-slate-200 bg-white px-4 py-4 sm:px-8 lg:px-10">
        <button
          onClick={() => navigate('/pricing')}
          className="inline-flex items-center gap-2 text-sm font-bold text-blue-600 transition hover:text-blue-700"
        >
          <ArrowLeft size={16} />
          Back to Pricing
        </button>
      </div>

      {/* Main Content */}
      <div className="px-4 py-8 sm:px-8 lg:px-10">
        <div className="mx-auto max-w-4xl">
          <div className="grid gap-8 lg:grid-cols-3">
            {/* Payment Form */}
            <div className="lg:col-span-2">
              <div className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8">
                <h1 className="text-3xl font-black text-slate-900 sm:text-4xl">Buy Credits</h1>
                <p className="mt-2 text-slate-600">
                  Select a plan and complete your purchase securely.
                </p>

                {/* Payment Status Messages */}
                {paymentStatus && (
                  <div className={`mt-6 rounded-2xl p-4 flex items-start gap-3 ${
                    paymentStatus.type === 'success'
                      ? 'bg-emerald-50 text-emerald-900'
                      : 'bg-red-50 text-red-900'
                  }`}>
                    {paymentStatus.type === 'success' ? (
                      <CheckCircle size={20} className="mt-0.5 flex-shrink-0 text-emerald-600" />
                    ) : (
                      <AlertCircle size={20} className="mt-0.5 flex-shrink-0 text-red-600" />
                    )}
                    <div>
                      <p className="font-bold">{paymentStatus.message}</p>
                      {paymentStatus.credits && (
                        <p className="mt-1 text-sm">
                          Total credits remaining: <span className="font-black">{paymentStatus.credits}</span>
                        </p>
                      )}
                      {paymentStatus.type === 'success' && (
                        <p className="mt-1 text-sm">Redirecting to dashboard...</p>
                      )}
                    </div>
                  </div>
                )}

                {/* Plan Selection */}
                <div className="mt-8">
                  <h2 className="mb-4 text-lg font-black text-slate-900">Choose a Plan</h2>

                  {loading ? (
                    <div className="space-y-3">
                      {[1, 2, 3].map((i) => (
                        <div
                          key={i}
                          className="h-20 animate-pulse rounded-xl bg-slate-200"
                        />
                      ))}
                    </div>
                  ) : (
                    <>
                      <div className="mb-6 space-y-3">
                        <p className="text-xs font-bold uppercase tracking-wide text-slate-500">Subscriptions</p>
                        {subscriptionPlans.map((plan) => (
                          <button
                            key={plan.id}
                            onClick={() => setSelectedPlan(plan)}
                            className={`w-full rounded-2xl border-2 p-4 text-left transition ${
                              selectedPlan?.id === plan.id
                                ? 'border-blue-600 bg-blue-50'
                                : 'border-slate-200 bg-white hover:border-slate-300'
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <div>
                                <h3 className="font-black text-slate-900">{plan.name}</h3>
                                <p className="mt-1 text-sm text-slate-600">
                                  {plan.credits} queries {plan.billing === 'monthly' ? '/ month' : ''}
                                </p>
                              </div>
                              <div className="text-right">
                                <p className="text-2xl font-black text-slate-900">₹{Math.floor(plan.price_inr)}</p>
                                <p className="text-xs font-medium text-slate-600">
                                  {plan.billing === 'monthly' ? 'monthly' : 'one-time'}
                                </p>
                              </div>
                            </div>
                          </button>
                        ))}
                      </div>

                      {/* Divider */}
                      <div className="my-6 border-t border-slate-200" />

                      {/* Extra Credits */}
                      <div className="space-y-3">
                        <p className="text-xs font-bold uppercase tracking-wide text-slate-500">Extra Credits</p>
                        <div className="grid grid-cols-3 gap-3">
                          {extraPlans.map((plan) => (
                            <button
                              key={plan.id}
                              onClick={() => setSelectedPlan(plan)}
                              className={`rounded-xl border-2 p-3 text-center transition ${
                                selectedPlan?.id === plan.id
                                  ? 'border-blue-600 bg-blue-50'
                                  : 'border-slate-200 bg-white hover:border-slate-300'
                              }`}
                            >
                              <p className="font-black text-slate-900">₹{Math.floor(plan.price_inr)}</p>
                              <p className="mt-1 text-xs font-bold text-slate-600">{plan.credits} credits</p>
                            </button>
                          ))}
                        </div>
                      </div>
                    </>
                  )}
                </div>

                {/* Payment Method */}
                <div className="mt-8">
                  <h2 className="mb-4 text-lg font-black text-slate-900">Payment Method</h2>
                  <div className="space-y-3">
                    {[
                      { id: 'razorpay', name: 'Razorpay', description: 'Cards, UPI, Wallets' },
                      { id: 'stripe', name: 'Stripe', description: 'International Cards' },
                    ].map((method) => (
                      <label
                        key={method.id}
                        className={`flex items-center rounded-xl border-2 p-3 cursor-pointer transition ${
                          paymentMethod === method.id
                            ? 'border-blue-600 bg-blue-50'
                            : 'border-slate-200 bg-white hover:border-slate-300'
                        }`}
                      >
                        <input
                          type="radio"
                          name="payment_method"
                          value={method.id}
                          checked={paymentMethod === method.id}
                          onChange={(e) => setPaymentMethod(e.target.value)}
                          className="h-4 w-4"
                        />
                        <div className="ml-3 flex-1">
                          <p className="font-black text-slate-900">{method.name}</p>
                          <p className="text-xs text-slate-600">{method.description}</p>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Order Summary */}
            <div className="lg:col-span-1">
              <div className="rounded-3xl border border-slate-200 bg-white p-6 sticky top-6">
                <h2 className="mb-6 text-lg font-black text-slate-900">Order Summary</h2>

                {selectedPlan ? (
                  <>
                    <div className="space-y-4 border-b border-slate-200 pb-4">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-600">{selectedPlan.name}</span>
                        <span className="font-black text-slate-900">
                          ₹{Math.floor(selectedPlan.price_inr)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-slate-500">Credits</span>
                        <span className="inline-flex items-center gap-1 font-black text-orange-600">
                          <Zap size={14} />
                          {selectedPlan.credits}
                        </span>
                      </div>
                    </div>

                    <div className="mt-4 flex items-center justify-between">
                      <span className="text-lg font-black text-slate-900">Total</span>
                      <span className="text-3xl font-black text-blue-600">
                        ₹{Math.floor(selectedPlan.price_inr)}
                      </span>
                    </div>

                    <button
                      onClick={handleInitiatePayment}
                      disabled={processing}
                      className={`mt-6 w-full flex items-center justify-center gap-2 rounded-2xl px-4 py-3 text-sm font-black uppercase tracking-wider transition ${
                        processing
                          ? 'bg-slate-300 text-slate-600 cursor-not-allowed'
                          : 'bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:shadow-lg hover:shadow-blue-600/30'
                      }`}
                    >
                      {processing ? (
                        <>
                          <Loader size={16} className="animate-spin" />
                          Processing...
                        </>
                      ) : (
                        <>
                          <CreditCard size={16} />
                          Complete Payment
                        </>
                      )}
                    </button>

                    <p className="mt-4 text-center text-xs text-slate-500">
                      ✓ Secure payment via {paymentMethod === 'razorpay' ? 'Razorpay' : 'Stripe'}
                    </p>
                  </>
                ) : (
                  <p className="text-center text-slate-600">Select a plan to see summary</p>
                )}

                {/* Security Info */}
                <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600">
                  <p className="font-semibold text-slate-900 mb-1">🔒 Your payment is secure</p>
                  <p>
                    We use industry-standard encryption (SSL/TLS) and PCI-DSS compliant payment processors.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
