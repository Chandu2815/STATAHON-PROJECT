import React from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Download } from 'lucide-react';

const COLORS = [
  '#3b82f6',
  '#8b5cf6',
  '#ec4899',
  '#f59e0b',
  '#10b981',
  '#06b6d4',
  '#6366f1',
  '#f97316',
];

export default function ChartView({ data, columns, statistics }) {
  if (!data || data.length === 0) return null;

  // Export chart data as CSV
  const exportChartData = () => {
    // Prepare all chart data
    const chartableData = data.slice(0, 20).map((row) => {
      const obj = {};
      columns.forEach((col) => {
        obj[col] = row[col];
      });
      return obj;
    });

    // Convert to CSV
    const headers = Object.keys(chartableData[0] || {});
    const csvContent = [
      headers.join(','),
      ...chartableData.map((row) =>
        headers.map((header) => {
          const value = row[header];
          // Escape quotes and wrap in quotes if contains comma
          if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
            return `"${value.replace(/"/g, '""')}"`;
          }
          return value;
        }).join(',')
      ),
    ].join('\n');

    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `chart-data-${new Date().getTime()}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Get numeric columns
  const numericColumns = columns.filter((col) => {
    const sample = data[0]?.[col];
    return typeof sample === 'number' || !isNaN(parseFloat(sample));
  });

  if (numericColumns.length === 0) return null;

  // Prepare data for charts
  const chartableData = data.slice(0, 20).map((row) => {
    const obj = {};
    numericColumns.forEach((col) => {
      obj[col] = parseFloat(row[col]) || 0;
    });
    return obj;
  });

  const textColumns = columns.filter(
    (col) => typeof data[0]?.[col] === 'string' || data[0]?.[col] === null
  );

  // Category chart data
  const categoryData = {};
  if (textColumns.length > 0) {
    const firstTextCol = textColumns[0];
    data.forEach((row) => {
      const key = row[firstTextCol] || 'Unknown';
      categoryData[key] = (categoryData[key] || 0) + 1;
    });
  }

  const categoryChartData = Object.entries(categoryData)
    .slice(0, 10)
    .map(([name, value]) => ({ name, value }));

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-800">
          Data Visualization
        </h3>
        <button
          onClick={exportChartData}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-900 hover:bg-blue-800 rounded border border-blue-900 transition"
          title="Export chart data as CSV"
        >
          <Download size={16} />
          Export Data
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Bar Chart - First Numeric Column */}
        {numericColumns.length > 0 && (
          <div className="flex flex-col">
            <h4 className="text-sm font-medium text-gray-700 mb-4">
              {numericColumns[0]} Distribution
            </h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={chartableData}
                margin={{ top: 20, right: 30, left: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#f3f4f6',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                  }}
                />
                <Bar
                  dataKey={numericColumns[0]}
                  fill="#3b82f6"
                  radius={[8, 8, 0, 0]}
                  isAnimationActive={true}
                  animationDuration={800}
                  animationEasing="ease-in-out"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Line Chart - Second Numeric Column */}
        {numericColumns.length > 1 && (
          <div className="flex flex-col">
            <h4 className="text-sm font-medium text-gray-700 mb-4">
              {numericColumns[1]} Trend
            </h4>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart
                data={chartableData}
                margin={{ top: 20, right: 30, left: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#f3f4f6',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey={numericColumns[1]}
                  stroke="#8b5cf6"
                  strokeWidth={2}
                  dot={{ r: 4, fill: '#8b5cf6' }}
                  activeDot={{ r: 6, fill: '#8b5cf6' }}
                  isAnimationActive={true}
                  animationDuration={800}
                  animationEasing="ease-in-out"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Pie Chart - Category Distribution */}
        {categoryChartData.length > 0 && (
          <div className="flex flex-col">
            <h4 className="text-sm font-medium text-gray-700 mb-4">
              Category Distribution
            </h4>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart margin={{ top: 20, right: 30, bottom: 0, left: 0 }}>
                <Pie
                  data={categoryChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  isAnimationActive={true}
                  animationDuration={800}
                  animationEasing="ease-in-out"
                >
                  {categoryChartData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#f3f4f6',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Multi-Series Bar Chart */}
        {numericColumns.length > 1 && (
          <div className="flex flex-col">
            <h4 className="text-sm font-medium text-gray-700 mb-4">
              Numeric Comparison
            </h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={chartableData}
                margin={{ top: 20, right: 30, left: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#f3f4f6',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                  }}
                />
                <Legend />
                {numericColumns.slice(0, 3).map((col, idx) => (
                  <Bar
                    key={col}
                    dataKey={col}
                    fill={COLORS[idx % COLORS.length]}
                    radius={[8, 8, 0, 0]}
                    isAnimationActive={true}
                    animationDuration={800}
                    animationEasing="ease-in-out"
                  />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Statistics Summary */}
      {statistics && (
        <div className="mt-8 pt-8 border-t border-gray-200">
          <h4 className="text-sm font-semibold text-gray-700 mb-4">
            Statistics
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(statistics)
              .slice(0, 8)
              .map(([key, value]) => (
                <div
                  key={key}
                  className="bg-gradient-to-br from-blue-50 to-purple-50 p-4 rounded-lg border border-blue-200"
                >
                  <p className="text-xs text-gray-600">{key}</p>
                  <p className="text-lg font-bold text-blue-900">
                    {typeof value === 'number' ? value.toFixed(2) : value}
                  </p>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
