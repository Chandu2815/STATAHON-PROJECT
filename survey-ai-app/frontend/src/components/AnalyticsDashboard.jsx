import React from 'react';
import { BarChart3, TrendingUp, PieChart, AlertCircle, Loader2 } from 'lucide-react';

/**
 * AnalyticsDashboard
 * Advanced analytics view with real data
 */
export default function AnalyticsDashboard({ 
  selectedDataset, 
  columns, 
  selectedColumns, 
  data, 
  statistics,
  loading,
  error 
}) {
  // If no dataset selected, show selection prompt
  if (!selectedDataset) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded border border-gray-300 shadow-sm p-8">
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <AlertCircle className="text-gray-400 mb-4" size={48} />
            <h3 className="text-lg font-bold text-gray-900 mb-2">No Dataset Selected</h3>
            <p className="text-gray-600">Go to <strong>Data Explorer</strong> tab to select a dataset and columns first</p>
          </div>
        </div>
      </div>
    );
  }

  // If no columns selected, show instruction
  if (selectedColumns.length === 0) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded border border-gray-300 shadow-sm p-8">
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <AlertCircle className="text-blue-400 mb-4" size={48} />
            <h3 className="text-lg font-bold text-gray-900 mb-2">Select Columns</h3>
            <p className="text-gray-600">Go back to <strong>Data Explorer</strong> and select at least one column to analyze</p>
          </div>
        </div>
      </div>
    );
  }

  // Show loading state
  if (loading) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded border border-gray-300 shadow-sm p-8">
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="text-blue-600 animate-spin mb-4" size={40} />
            <p className="text-gray-900 font-medium">Generating Analytics</p>
          </div>
        </div>
      </div>
    );
  }

  // Show error if any
  if (error) {
    return (
      <div className="space-y-6">
        <div className="bg-red-50 border-l-4 border-red-600 p-5 rounded">
          <div className="flex gap-4">
            <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={22} />
            <div>
              <h3 className="font-bold text-red-900">Error Loading Analytics</h3>
              <p className="text-red-700 text-sm mt-1">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Calculate analytics
  const totalRecords = data.length;
  const activeColumns = selectedColumns.length;
  
  // Calculate unique values and data insights
  const insights = {};
  selectedColumns.forEach(col => {
    const values = data.map(row => row[col]).filter(v => v !== null && v !== undefined);
    const uniqueValues = new Set(values);
    insights[col] = {
      unique: uniqueValues.size,
      total: values.length,
      nulls: data.length - values.length,
      types: typeof values[0]
    };
  });

  return (
    <div className="space-y-6">
      <div className="bg-white rounded border border-gray-300 shadow-sm p-8">
        <div className="flex items-center gap-4 mb-6">
          <div className="p-3 bg-purple-100 rounded-lg">
            <BarChart3 className="text-purple-600" size={24} />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900">Advanced Analytics</h3>
            <p className="text-sm text-gray-600">Dataset: <strong>{selectedDataset}</strong></p>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Total Records */}
          <div className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded border border-blue-200">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-sm font-semibold text-blue-900">Total Records</h4>
              <TrendingUp className="text-blue-600" size={20} />
            </div>
            <p className="text-3xl font-bold text-blue-900">{totalRecords.toLocaleString()}</p>
            <p className="text-xs text-blue-700 mt-2">Rows in current selection</p>
          </div>

          {/* Active Columns */}
          <div className="p-6 bg-gradient-to-br from-green-50 to-green-100 rounded border border-green-200">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-sm font-semibold text-green-900">Active Columns</h4>
              <PieChart className="text-green-600" size={20} />
            </div>
            <p className="text-3xl font-bold text-green-900">{activeColumns}</p>
            <p className="text-xs text-green-700 mt-2">Fields analyzed</p>
          </div>

          {/* Data Insights */}
          <div className="p-6 bg-gradient-to-br from-orange-50 to-orange-100 rounded border border-orange-200">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-sm font-semibold text-orange-900">Data Completeness</h4>
              <BarChart3 className="text-orange-600" size={20} />
            </div>
            <p className="text-3xl font-bold text-orange-900">
              {totalRecords > 0 ? ((selectedColumns.reduce((sum, col) => {
                const values = data.map(row => row[col]).filter(v => v !== null && v !== undefined);
                return sum + values.length;
              }, 0) / (totalRecords * selectedColumns.length) * 100) || 0).toFixed(0) : 0}%
            </p>
            <p className="text-xs text-orange-700 mt-2">Non-null values</p>
          </div>
        </div>

        {/* Column Statistics */}
        <div className="p-6 bg-gradient-to-br from-gray-50 to-gray-100 rounded border border-gray-200 mb-8">
          <h4 className="text-sm font-bold text-gray-900 mb-4">Column Statistics</h4>
          <div className="space-y-3">
            {selectedColumns.map((col) => {
              const colStats = insights[col] || {};
              return (
                <div key={col} className="flex items-start justify-between p-3 bg-white rounded border border-gray-200">
                  <div>
                    <p className="font-medium text-gray-900">{col}</p>
                    <div className="text-xs text-gray-600 space-y-0.5 mt-1">
                      <p>• Unique values: <strong>{colStats.unique}</strong></p>
                      <p>• Non-null entries: <strong>{colStats.total}</strong></p>
                      <p>• Missing values: <strong>{colStats.nulls}</strong></p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="inline-block px-2 py-1 bg-blue-100 text-blue-900 text-xs font-medium rounded">
                      {colStats.types}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* How to Use */}
        <div className="p-6 bg-blue-50 border border-blue-200 rounded">
          <h4 className="text-sm font-bold text-blue-900 mb-3">Tips</h4>
          <ul className="text-sm text-blue-800 space-y-2">
            <li>✓ Modify filters in <strong>Data Explorer</strong> to update these analytics</li>
            <li>✓ Add more columns to see additional statistics</li>
            <li>✓ Use export feature to download this data for further analysis</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
