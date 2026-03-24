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
      <h3 className="text-lg font-semibold text-gray-800 mb-6">
        Data Visualization
      </h3>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Bar Chart - First Numeric Column */}
        {numericColumns.length > 0 && (
          <div className="flex flex-col">
            <h4 className="text-sm font-medium text-gray-700 mb-4">
              {numericColumns[0]} Distribution
            </h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartableData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey={numericColumns[0]} fill="#3b82f6" radius={[8, 8, 0, 0]} />
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
              <LineChart data={chartableData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey={numericColumns[1]}
                  stroke="#8b5cf6"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
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
              <PieChart>
                <Pie
                  data={categoryChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryChartData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
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
              <BarChart data={chartableData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                {numericColumns.slice(0, 3).map((col, idx) => (
                  <Bar
                    key={col}
                    dataKey={col}
                    fill={COLORS[idx % COLORS.length]}
                    radius={[8, 8, 0, 0]}
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
