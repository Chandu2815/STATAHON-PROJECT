import React, { useEffect, useState } from 'react';
import { BarChart3, Database, Users, TrendingUp } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';

export default function Dashboard() {
  const [datasets, setDatasets] = useState(0);
  const [totalRows, setTotalRows] = useState('0');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        // Fetch datasets
        const datasetsResponse = await axios.get(`${API_BASE_URL}/datasets`);
        if (datasetsResponse.data.success) {
          setDatasets(datasetsResponse.data.datasets?.length || 0);
        }

        // Fetch total records from analytics summary
        const analyticsResponse = await axios.get(`${API_BASE_URL}/analytics/summary`);
        if (analyticsResponse.data.success && analyticsResponse.data.total_rows) {
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
        console.error('Failed to fetch stats:', err);
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
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome back! Here's an overview of your data</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, idx) => {
          const Icon = stat.icon;
          const colorClasses = {
            blue: 'from-blue-500 to-blue-600',
            purple: 'from-purple-500 to-purple-600',
            green: 'from-green-500 to-green-600',
            pink: 'from-pink-500 to-pink-600',
          };

          return (
            <div
              key={idx}
              className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition"
            >
              <div className={`w-12 h-12 bg-gradient-to-br ${colorClasses[stat.color]} rounded-lg flex items-center justify-center mb-4`}>
                <Icon className="text-white" size={24} />
              </div>
              <p className="text-gray-600 text-sm mb-1">{stat.label}</p>
              <p className="text-2xl font-bold text-gray-800">{stat.value}</p>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          Get Started
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a
            href="/survey-ai"
            className="block p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg hover:shadow-md transition"
          >
            <h3 className="font-semibold text-blue-900 mb-1">Explore Data</h3>
            <p className="text-blue-700 text-sm">
              Start exploring datasets with interactive filters and visualizations
            </p>
          </a>
          <div className="block p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-lg">
            <h3 className="font-semibold text-purple-900 mb-1">Documentation</h3>
            <p className="text-purple-700 text-sm">
              Learn how to use Survey AI effectively with our guides
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
