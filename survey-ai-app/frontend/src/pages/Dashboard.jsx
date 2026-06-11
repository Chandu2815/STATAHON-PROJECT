import React, { useEffect, useState } from 'react';
import { BarChart3, Database, Users, TrendingUp } from 'lucide-react';
import { API, normalizeHierarchicalDatasets, countDatasets } from '../lib/api.js';

export default function Dashboard() {
  const [datasets, setDatasets] = useState(0);
  const [totalRows, setTotalRows] = useState('0');
  const [loading, setLoading] = useState(true);

  console.log('[Dashboard] render state', {
    datasets,
    totalRows,
    loading,
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        // Fetch hierarchical datasets
        console.log('🔄 Fetching hierarchical datasets...');
        const datasetsResponse = await API.get('/datasets/hierarchical');
        console.log('✅ Hierarchical datasets response:', datasetsResponse.data);
        if (datasetsResponse.data?.success) {
          const hierarchicalData = normalizeHierarchicalDatasets(datasetsResponse.data.data || {});
          const totalDatasets = countDatasets(hierarchicalData);
          setDatasets(totalDatasets);
          console.log('✅ Total datasets:', totalDatasets);
        } else {
          console.error('❌ Hierarchical datasets API error:', datasetsResponse.data?.error);
        }

        // Fetch total records from analytics summary
        console.log('🔄 Fetching analytics summary...');
        const analyticsResponse = await API.get('/analytics/summary');
        console.log('✅ Analytics response:', analyticsResponse.data);
        if (analyticsResponse.data?.success && analyticsResponse.data.total_rows) {
          const rows = analyticsResponse.data.total_rows;
          // Format total rows (if > 1M show as M, else show as K)
          if (rows >= 1000000) {
            setTotalRows((rows / 1000000).toFixed(1) + 'M');
          } else if (rows >= 1000) {
            setTotalRows(Math.round(rows / 1000) + 'K');
          } else {
            setTotalRows(rows.toString());
          }
        }
      } catch (err) {
        console.error('❌ Error fetching stats:');
        console.error('   Error:', err.message);
        console.error('   Status:', err.status);
        console.error('   Data:', err.data);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const stats = [
    { icon: Database, label: 'Datasets', value: datasets, color: 'blue' },
    { icon: TrendingUp, label: 'Total Records', value: totalRows, color: 'purple' },
    { icon: BarChart3, label: 'Active Queries', value: '0', color: 'green' },
    { icon: Users, label: 'Team Members', value: '1', color: 'pink' },
  ];

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header Section */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-blue-900 mb-1">Dashboard</h1>
        <p className="text-gray-600 text-sm">Overview of your survey data</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((stat, idx) => {
          const Icon = stat.icon;
          const colorBorders = {
            blue: 'border-l-blue-900',
            purple: 'border-l-orange-500',
            green: 'border-l-green-600',
            pink: 'border-l-pink-600',
          };
          const colorIcons = {
            blue: 'bg-blue-100 text-blue-900',
            purple: 'bg-orange-100 text-orange-900',
            green: 'bg-green-100 text-green-900',
            pink: 'bg-pink-100 text-pink-900',
          };

          return (
            <div
              key={idx}
              className={`bg-white rounded-lg border-l-4 ${colorBorders[stat.color]} p-4 shadow-sm hover:shadow-md transition`}
            >
              <div className={`w-10 h-10 ${colorIcons[stat.color]} rounded flex items-center justify-center mb-3`}>
                <Icon size={20} />
              </div>
              <p className="text-gray-600 text-xs font-medium mb-1">{stat.label}</p>
              <p className="text-2xl font-bold text-blue-900">{stat.value}</p>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
        <h2 className="text-base font-bold text-blue-900 mb-4">Quick Links</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a
            href="/survey-ai"
            className="block p-4 bg-blue-50 border border-blue-200 rounded hover:shadow-md transition"
          >
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 bg-blue-900 text-white rounded flex items-center justify-center flex-shrink-0">
                <BarChart3 size={18} />
              </div>
              <div>
                <h3 className="font-bold text-blue-900 text-sm mb-1">Explore Data</h3>
                <p className="text-blue-700 text-xs">Interactive filters and visualizations</p>
              </div>
            </div>
          </a>
          <div className="block p-4 bg-orange-50 border border-orange-200 rounded">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 bg-orange-500 text-white rounded flex items-center justify-center flex-shrink-0">
                <Database size={18} />
              </div>
              <div>
                <h3 className="font-bold text-orange-900 text-sm mb-1">Documentation</h3>
                <p className="text-orange-700 text-xs">Learn how to use Survey AI</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
