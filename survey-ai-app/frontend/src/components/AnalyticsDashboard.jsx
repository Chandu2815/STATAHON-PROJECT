import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import { AlertCircle, Loader2, TrendingUp, Database, CheckCircle } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8001';

export default function AnalyticsDashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedTable, setSelectedTable] = useState(null);
  const [quality, setQuality] = useState(null);

  useEffect(() => {
    fetchAnalyticsSummary();
  }, []);

  const fetchAnalyticsSummary = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/analytics/summary`);
      if (response.data.success) {
        setSummary(response.data);
      }
    } catch (err) {
      setError('Failed to fetch analytics: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchDataQuality = async (table) => {
    try {
      setLoading(true);
      setSelectedTable(table);
      const response = await axios.get(`${API_BASE_URL}/analytics/data-quality/${table}`);
      if (response.data.success) {
        setQuality(response.data);
      }
    } catch (err) {
      setError('Failed to fetch data quality: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Loader2 className="animate-spin text-blue-900 mb-4" size={40} />
        <p className="text-gray-600">Loading analytics...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded text-red-700 flex gap-3">
          <AlertCircle size={20} className="flex-shrink-0 mt-0.5" />
          <div>{error}</div>
        </div>
      )}

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-6 rounded border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-600 font-semibold uppercase">Total Tables</p>
                <p className="text-3xl font-bold text-blue-900 mt-2">{summary.total_tables}</p>
              </div>
              <Database className="text-blue-200" size={40} />
            </div>
          </div>

          <div className="bg-white p-6 rounded border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-600 font-semibold uppercase">Total Records</p>
                <p className="text-3xl font-bold text-green-900 mt-2">{(summary.total_rows / 1000000).toFixed(1)}M</p>
              </div>
              <TrendingUp className="text-green-200" size={40} />
            </div>
          </div>

          <div className="bg-white p-6 rounded border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-600 font-semibold uppercase">HCES Tables</p>
                <p className="text-3xl font-bold text-purple-900 mt-2">
                  {summary.summary.filter(t => t.table.startsWith('hces_')).length}
                </p>
              </div>
              <CheckCircle className="text-purple-200" size={40} />
            </div>
          </div>

          <div className="bg-white p-6 rounded border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-600 font-semibold uppercase">PLFS Tables</p>
                <p className="text-3xl font-bold text-orange-900 mt-2">
                  {summary.summary.filter(t => t.table.startsWith('plfs_')).length}
                </p>
              </div>
              <CheckCircle className="text-orange-200" size={40} />
            </div>
          </div>
        </div>
      )}

      {/* Table List with Data Quality */}
      {summary && (
        <div className="bg-white rounded border border-gray-200 shadow-sm p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Dataset Overview</h3>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold text-gray-700">Table Name</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-700">Records</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-700">Columns</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-700">Numeric</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-700">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {summary.summary.map((table) => (
                  <tr key={table.table} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{table.table}</td>
                    <td className="px-4 py-3 text-gray-700">{table.rows.toLocaleString()}</td>
                    <td className="px-4 py-3 text-gray-700">{table.columns}</td>
                    <td className="px-4 py-3 text-gray-700">{table.numeric_columns}</td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => fetchDataQuality(table.table)}
                        className="px-3 py-1 text-xs font-medium text-blue-900 bg-blue-100 hover:bg-blue-200 rounded border border-blue-300 transition"
                      >
                        Analyze
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Data Quality Analysis */}
      {quality && (
        <div className="bg-white rounded border border-gray-200 shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-900">Data Quality - {quality.table}</h3>
            <div className="text-right">
              <p className="text-xs text-gray-600">Average Completeness</p>
              <p className="text-2xl font-bold text-blue-900">{quality.average_completeness}%</p>
            </div>
          </div>

          <div className="space-y-2 max-h-60 overflow-y-auto">
            {quality.columns.map((col) => (
              <div key={col.column} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{col.column}</p>
                  <p className="text-xs text-gray-600">{col.type}</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-32 bg-gray-300 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full transition-all"
                      style={{ width: `${col.completeness}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold text-gray-700 w-12">{col.completeness}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
