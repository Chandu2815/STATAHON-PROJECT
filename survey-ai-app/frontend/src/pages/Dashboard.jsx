import React, { useEffect, useMemo, useState } from 'react';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import {
  Activity,
  ArrowUpRight,
  BarChart3,
  Bell,
  BookOpen,
  Coins,
  Database,
  Gauge,
  Layers,
  Search,
  Settings,
  Sparkles,
  TrendingUp,
} from 'lucide-react';
import { API, normalizeHierarchicalDatasets, countDatasets } from '../lib/api.js';

const CHART_COLORS = ['#1d4ed8', '#059669', '#f97316', '#7c3aed', '#0f766e', '#be123c'];

function formatNumber(value) {
  const numeric = Number(value || 0);
  if (numeric >= 1000000) return `${(numeric / 1000000).toFixed(1)}M`;
  if (numeric >= 1000) return `${Math.round(numeric / 1000)}K`;
  return numeric.toLocaleString();
}

function formatTime(value) {
  if (!value) return 'Just now';
  return new Intl.DateTimeFormat(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
}

function planCapacity(accountType) {
  return accountType === 'researcher' ? 100 : 10;
}

export default function Dashboard() {
  const [datasets, setDatasets] = useState(0);
  const [datasetDistribution, setDatasetDistribution] = useState([]);
  const [recordsByState, setRecordsByState] = useState([]);
  const [queryActivity, setQueryActivity] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [totalRows, setTotalRows] = useState(0);
  const [credits, setCredits] = useState(null);
  const [loading, setLoading] = useState(true);

  const userDisplay =
    localStorage.getItem('userDisplayName') ||
    localStorage.getItem('username') ||
    localStorage.getItem('userEmail') ||
    'Analyst';

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);

        const [datasetsResponse, creditsResponse, analyticsResponse, stateResponse, activityResponse, activitySummaryResponse] =
          await Promise.all([
            API.get('/datasets/hierarchical'),
            API.get('/api/user/credits'),
            API.get('/analytics/summary'),
            API.get('/analytics/column-distribution/plfs.person_household/state_ut_code'),
            API.get('/api/user/activity?limit=8'),
            API.get('/api/user/activity/summary'),
          ]);

        if (datasetsResponse.data?.success) {
          const hierarchicalData = normalizeHierarchicalDatasets(datasetsResponse.data.data || {});
          setDatasets(countDatasets(hierarchicalData));
          setDatasetDistribution(
            Object.entries(hierarchicalData).map(([category, items]) => ({
              name: category,
              datasets: Array.isArray(items) ? items.length : 0,
              rows: (items || []).reduce((sum, item) => sum + Number(item.row_count || 0), 0),
            }))
          );
        }

        if (creditsResponse.ok) {
          setCredits(creditsResponse.data);
          localStorage.setItem('account_type', creditsResponse.data.account_type || 'public');
          localStorage.setItem('credits_remaining', String(creditsResponse.data.credits_remaining ?? 0));
          localStorage.setItem('credits_used', String(creditsResponse.data.credits_used ?? 0));
          window.dispatchEvent(new Event('credits-updated'));
        }

        if (analyticsResponse.data?.success) {
          setTotalRows(Number(analyticsResponse.data.total_rows || 0));
        }

        if (stateResponse.data?.success) {
          setRecordsByState(
            (stateResponse.data.distribution || [])
              .slice(0, 8)
              .map((row) => ({
                state: String(row.label || row.value || '').replace(/^\d+\s*-\s*/, ''),
                records: Number(row.count || 0),
              }))
          );
        }

        if (activityResponse.data?.success) {
          setRecentActivity(activityResponse.data.activity || []);
        }

        if (activitySummaryResponse.data?.success) {
          setQueryActivity(activitySummaryResponse.data.summary || []);
        }
      } catch (err) {
        console.error('Error fetching dashboard stats:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const accountType = credits?.account_type || localStorage.getItem('account_type') || 'public';
  const planLabel = accountType === 'researcher' ? 'Researcher' : 'Public User';
  const capacity = planCapacity(accountType);
  const creditsRemaining = Number(credits?.credits_remaining ?? localStorage.getItem('credits_remaining') ?? 0);
  const creditsUsed = Number(credits?.credits_used ?? localStorage.getItem('credits_used') ?? 0);
  const creditsPercent = Math.max(0, Math.min(100, Math.round((creditsRemaining / capacity) * 100)));

  const activityTotals = useMemo(
    () => queryActivity.reduce((sum, item) => sum + Number(item.queries || 0), 0),
    [queryActivity]
  );

  const kpis = [
    {
      label: 'Datasets',
      value: datasets,
      icon: Database,
      meta: 'Live catalogs',
      gradient: 'from-blue-600 to-indigo-700',
    },
    {
      label: 'Total Records',
      value: formatNumber(totalRows),
      icon: TrendingUp,
      meta: 'Across sources',
      gradient: 'from-emerald-600 to-teal-700',
    },
    {
      label: 'Credits Remaining',
      value: creditsRemaining,
      icon: Coins,
      meta: `${creditsPercent}% available`,
      gradient: 'from-orange-500 to-amber-600',
    },
    {
      label: 'Queries Used',
      value: creditsUsed,
      icon: Gauge,
      meta: `${activityTotals} in last 7 days`,
      gradient: 'from-violet-600 to-fuchsia-700',
    },
  ];

  const actions = [
    { title: 'Explore Data', text: 'Build filtered survey extracts', href: '/survey-ai', icon: Search },
    { title: 'View Analytics', text: 'Open interactive analysis mode', href: '/survey-ai', icon: BarChart3 },
    { title: 'Manage Settings', text: 'Review profile preferences', href: '/settings', icon: Settings },
    { title: 'Documentation', text: 'Read usage guidance', href: '#', icon: BookOpen },
  ];

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-6 sm:px-8 lg:px-10">
      <div className="mx-auto max-w-7xl space-y-8">
        <section className="overflow-hidden rounded-[28px] border border-white bg-gradient-to-br from-slate-950 via-blue-900 to-slate-900 p-6 text-white shadow-2xl shadow-blue-950/20 sm:p-8">
          <div className="flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-3xl">
              <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-blue-100">
                <Sparkles size={14} />
                Survey Intelligence Workspace
              </div>
              <h1 className="text-3xl font-black tracking-tight sm:text-4xl">
                Welcome back, {userDisplay}
              </h1>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-blue-100">
                Monitor survey coverage, query usage, and credit capacity from one executive analytics dashboard.
              </p>
              <div className="mt-6 flex flex-wrap gap-3">
                <span className="rounded-full bg-white px-4 py-2 text-xs font-bold uppercase tracking-wide text-blue-900">
                  {planLabel}
                </span>
                <span className="rounded-full border border-white/20 bg-white/10 px-4 py-2 text-xs font-semibold text-blue-50">
                  {creditsRemaining} credits remaining
                </span>
                <span className="rounded-full border border-white/20 bg-white/10 px-4 py-2 text-xs font-semibold text-blue-50">
                  {creditsUsed} queries used
                </span>
              </div>
            </div>

            <div className="w-full max-w-sm rounded-3xl border border-white/15 bg-white/10 p-5 backdrop-blur">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-widest text-blue-100">Credit Capacity</p>
                  <p className="mt-1 text-3xl font-black">{creditsPercent}%</p>
                </div>
                <div
                  className="grid h-24 w-24 place-items-center rounded-full"
                  style={{
                    background: `conic-gradient(#22c55e ${creditsPercent * 3.6}deg, rgba(255,255,255,.18) 0deg)`,
                  }}
                >
                  <div className="grid h-16 w-16 place-items-center rounded-full bg-slate-950/90 text-sm font-black">
                    {creditsRemaining}
                  </div>
                </div>
              </div>
              <div className="mt-5 h-2 overflow-hidden rounded-full bg-white/15">
                <div className="h-full rounded-full bg-emerald-400" style={{ width: `${creditsPercent}%` }} />
              </div>
            </div>
          </div>
        </section>

        <section className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-4">
          {kpis.map((kpi) => {
            const Icon = kpi.icon;
            return (
              <div
                key={kpi.label}
                className="group rounded-3xl border border-white bg-white p-5 shadow-lg shadow-slate-200/70 transition duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-slate-300/70"
              >
                <div className={`mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br ${kpi.gradient} text-white shadow-lg`}>
                  <Icon size={28} />
                </div>
                <p className="text-xs font-bold uppercase tracking-widest text-slate-400">{kpi.label}</p>
                <div className="mt-2 flex items-end justify-between">
                  <p className="text-3xl font-black text-slate-900">{loading ? '...' : kpi.value}</p>
                  <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-bold uppercase text-slate-500">
                    {kpi.meta}
                  </span>
                </div>
              </div>
            );
          })}
        </section>

        <section className="grid grid-cols-1 gap-6 xl:grid-cols-3">
          <div className="rounded-3xl border border-slate-100 bg-white p-6 shadow-xl shadow-slate-200/60 xl:col-span-1">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-base font-black text-slate-900">Dataset Distribution</h2>
                <p className="text-xs font-medium text-slate-500">Catalog mix by source</p>
              </div>
              <Layers className="text-blue-600" size={22} />
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={datasetDistribution} dataKey="datasets" nameKey="name" innerRadius={62} outerRadius={96} paddingAngle={4}>
                    {datasetDistribution.map((entry, index) => (
                      <Cell key={entry.name} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="rounded-3xl border border-slate-100 bg-white p-6 shadow-xl shadow-slate-200/60 xl:col-span-2">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-base font-black text-slate-900">Records by State</h2>
                <p className="text-xs font-medium text-slate-500">Top PLFS state distribution</p>
              </div>
              <Activity className="text-emerald-600" size={22} />
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={recordsByState} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="state" tick={{ fontSize: 11 }} interval={0} angle={-18} textAnchor="end" height={70} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="records" radius={[10, 10, 0, 0]} fill="#2563eb" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        <section className="grid grid-cols-1 gap-6 xl:grid-cols-3">
          <div className="rounded-3xl border border-slate-100 bg-white p-6 shadow-xl shadow-slate-200/60 xl:col-span-2">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-base font-black text-slate-900">Query Activity</h2>
                <p className="text-xs font-medium text-slate-500">Last 7 days of usage</p>
              </div>
              <Bell className="text-orange-500" size={22} />
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={queryActivity} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                  <defs>
                    <linearGradient id="queryGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563eb" stopOpacity={0.45} />
                      <stop offset="95%" stopColor="#2563eb" stopOpacity={0.02} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Area type="monotone" dataKey="queries" stroke="#2563eb" strokeWidth={3} fill="url(#queryGradient)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="rounded-3xl border border-slate-100 bg-white p-6 shadow-xl shadow-slate-200/60">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <h2 className="text-base font-black text-slate-900">Action Cards</h2>
                <p className="text-xs font-medium text-slate-500">Common workflows</p>
              </div>
              <ArrowUpRight className="text-slate-400" size={20} />
            </div>
            <div className="space-y-3">
              {actions.map((action) => {
                const Icon = action.icon;
                return (
                  <a
                    key={action.title}
                    href={action.href}
                    className="group flex items-center gap-4 rounded-2xl border border-slate-100 bg-slate-50 p-4 transition hover:border-blue-200 hover:bg-blue-50"
                  >
                    <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white text-blue-700 shadow-sm">
                      <Icon size={20} />
                    </div>
                    <div>
                      <h3 className="text-sm font-black text-slate-900">{action.title}</h3>
                      <p className="text-xs font-medium text-slate-500">{action.text}</p>
                    </div>
                  </a>
                );
              })}
            </div>
          </div>
        </section>

        <section className="rounded-3xl border border-slate-100 bg-white p-6 shadow-xl shadow-slate-200/60">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h2 className="text-base font-black text-slate-900">Recent Activity</h2>
              <p className="text-xs font-medium text-slate-500">Real events from your Survey AI workspace</p>
            </div>
            <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-bold text-blue-700">
              {recentActivity.length} events
            </span>
          </div>
          <div className="overflow-hidden rounded-2xl border border-slate-100">
            <table className="min-w-full divide-y divide-slate-100">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left text-[11px] font-black uppercase tracking-widest text-slate-500">Event</th>
                  <th className="px-4 py-3 text-left text-[11px] font-black uppercase tracking-widest text-slate-500">Detail</th>
                  <th className="px-4 py-3 text-left text-[11px] font-black uppercase tracking-widest text-slate-500">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {recentActivity.length > 0 ? (
                  recentActivity.map((item) => (
                    <tr key={item.id} className="hover:bg-slate-50">
                      <td className="px-4 py-4 text-sm font-bold text-slate-900">{item.title}</td>
                      <td className="px-4 py-4 text-sm text-slate-600">{item.detail || item.action}</td>
                      <td className="px-4 py-4 text-sm font-medium text-slate-500">{formatTime(item.created_at)}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="3" className="px-4 py-10 text-center text-sm font-medium text-slate-500">
                      No activity yet. Run a query or open a dataset to populate this table.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
}
