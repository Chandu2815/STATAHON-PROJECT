import React, { useState } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  AreaChart,
  Area,
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
import { 
  Download, 
  BarChart3, 
  TrendingUp, 
  PieChart as PieChartIcon, 
  AreaChart as AreaChartIcon,
  Activity,
  Maximize2
} from 'lucide-react';

const COLORS = [
  '#2563eb', // Blue 600
  '#7c3aed', // Violet 600
  '#db2777', // Pink 600
  '#ea580c', // Orange 600
  '#059669', // Emerald 600
  '#0891b2', // Cyan 600
  '#4f46e5', // Indigo 600
  '#d97706', // Amber 600
];

const GRADIENTS = [
  { start: '#3b82f6', end: '#2563eb' },
  { start: '#8b5cf6', end: '#7c3aed' },
  { start: '#ec4899', end: '#db2777' },
  { start: '#f97316', end: '#ea580c' },
  { start: '#10b981', end: '#059669' },
];

export default function ChartView({ data, columns, statistics }) {
  const [chartType, setChartType] = useState('bar'); // bar, line, area
  
  if (!data || data.length === 0) return null;

  // Get numeric columns
  const numericColumns = columns.filter((col) => {
    const sample = data[0]?.[col];
    return typeof sample === 'number' || !isNaN(parseFloat(sample));
  });

  if (numericColumns.length === 0) return null;

  // Prepare data for charts
  const chartableData = data.slice(0, 15).map((row, idx) => {
    const obj = { name: `Entry ${idx + 1}` };
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
    .slice(0, 8)
    .map(([name, value]) => ({ name, value }));

  const exportChartData = () => {
    const headers = numericColumns;
    const csvContent = [
      headers.join(','),
      ...chartableData.map((row) => headers.map(h => row[h]).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.setAttribute('download', `visual-analytics-${new Date().getTime()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white/90 backdrop-blur-md border border-gray-200 p-4 rounded-xl shadow-2xl animate-in zoom-in duration-200">
          <p className="text-xs font-black text-gray-400 uppercase tracking-widest mb-2 italic">{label}</p>
          <div className="space-y-1.5">
            {payload.map((entry, index) => (
              <div key={index} className="flex items-center justify-between gap-6">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }}></div>
                  <span className="text-xs font-bold text-gray-700">{entry.name}</span>
                </div>
                <span className="text-xs font-black text-blue-600">{entry.value.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      {/* Visual Analytics Header */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h3 className="text-xl font-black text-gray-900 tracking-tight flex items-center gap-2">
            <Activity className="text-blue-600" size={24} />
            Visual Intelligence
          </h3>
          <p className="text-xs font-medium text-gray-400 mt-1 uppercase tracking-widest leading-relaxed">
            Dynamic distribution profiling and trend synthesis
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex bg-gray-100 p-1 rounded-xl">
            {[
              { id: 'bar', icon: <BarChart3 size={16} />, label: 'Bar' },
              { id: 'line', icon: <TrendingUp size={16} />, label: 'Line' },
              { id: 'area', icon: <AreaChartIcon size={16} />, label: 'Area' },
            ].map((type) => (
              <button
                key={type.id}
                onClick={() => setChartType(type.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  chartType === type.id 
                    ? 'bg-white text-blue-600 shadow-sm' 
                    : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                {type.icon}
                <span className="hidden sm:inline">{type.label}</span>
              </button>
            ))}
          </div>
          
          <button
            onClick={exportChartData}
            className="flex items-center gap-2 px-4 py-2.5 bg-gray-900 text-white rounded-xl text-xs font-black uppercase tracking-widest hover:bg-gray-800 transition-all shadow-sm active:scale-95"
          >
            <Download size={14} />
            Export
          </button>
        </div>
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Trend / Distribution Analysis */}
        <div className="lg:col-span-8 bg-white rounded-3xl border border-gray-100 shadow-sm p-8 flex flex-col min-h-[500px]">
          <div className="flex items-center justify-between mb-8">
            <h4 className="text-sm font-black text-gray-900 uppercase tracking-[.2em]">Temporal Variance Engine</h4>
            <div className="flex items-center gap-4">
              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest italic">• Real-time Profiling</span>
              <Maximize2 size={16} className="text-gray-300 cursor-pointer hover:text-blue-500 transition-colors" />
            </div>
          </div>

          <div className="flex-1 w-full relative">
            <ResponsiveContainer width="100%" height="100%">
              {chartType === 'bar' ? (
                <BarChart data={chartableData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="4 4" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="name" tick={{ fontSize: 10, fontWeight: 700, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 10, fontWeight: 700, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} cursor={{ fill: '#f8fafc' }} />
                  <Legend iconType="circle" wrapperStyle={{ paddingTop: 30, fontSize: 10, fontWeight: 800, textTransform: 'uppercase', letterSpacing: 1 }} />
                  {numericColumns.slice(0, 3).map((col, idx) => (
                    <Bar 
                      key={col} 
                      dataKey={col} 
                      fill={COLORS[idx % COLORS.length]} 
                      radius={[6, 6, 0, 0]} 
                      barSize={24}
                      animationDuration={1500}
                      animationBegin={idx * 200}
                    />
                  ))}
                </BarChart>
              ) : chartType === 'line' ? (
                <LineChart data={chartableData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={true} horizontal={true} stroke="#f8fafc" />
                  <XAxis dataKey="name" tick={{ fontSize: 10, fontWeight: 700, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 10, fontWeight: 700, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend iconType="circle" wrapperStyle={{ paddingTop: 30, fontSize: 10, fontWeight: 800, textTransform: 'uppercase', letterSpacing: 1 }} />
                  {numericColumns.slice(0, 4).map((col, idx) => (
                    <Line 
                      key={col} 
                      type="monotone" 
                      dataKey={col} 
                      stroke={COLORS[idx % COLORS.length]} 
                      strokeWidth={4} 
                      dot={{ r: 4, strokeWidth: 2, fill: '#fff' }} 
                      activeDot={{ r: 7, strokeWidth: 0, fill: COLORS[idx % COLORS.length] }}
                      animationDuration={1500}
                      strokeDasharray={idx > 1 ? "5 5" : "0"}
                    />
                  ))}
                </LineChart>
              ) : (
                <AreaChart data={chartableData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    {COLORS.map((color, idx) => (
                      <linearGradient key={`grad-${idx}`} id={`colorGrad-${idx}`} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={color} stopOpacity={0.4}/>
                        <stop offset="95%" stopColor={color} stopOpacity={0}/>
                      </linearGradient>
                    ))}
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="name" tick={{ fontSize: 10, fontWeight: 700, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 10, fontWeight: 700, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  {numericColumns.slice(0, 3).map((col, idx) => (
                    <Area 
                      key={col}
                      type="monotone" 
                      dataKey={col} 
                      stroke={COLORS[idx % COLORS.length]} 
                      fillOpacity={1} 
                      fill={`url(#colorGrad-${idx})`} 
                      strokeWidth={3}
                      animationDuration={1500}
                    />
                  ))}
                </AreaChart>
              )}
            </ResponsiveContainer>
          </div>
        </div>

        {/* Categorical Distribution Pie */}
        <div className="lg:col-span-4 flex flex-col gap-8">
          <div className="flex-1 bg-white rounded-3xl border border-gray-100 shadow-sm p-8 flex flex-col">
            <h4 className="text-sm font-black text-gray-900 uppercase tracking-[.2em] mb-8">Compositional Ratio</h4>
            <div className="flex-1 min-h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    animationDuration={1500}
                  >
                    {categoryChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="rgba(255,255,255,0.2)" strokeWidth={2} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            
            <div className="mt-4 space-y-2">
              {categoryChartData.slice(0, 4).map((entry, idx) => (
                <div key={entry.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></div>
                    <span className="text-[10px] font-bold text-gray-500 truncate max-w-[120px]">{entry.name}</span>
                  </div>
                  <span className="text-[10px] font-black text-gray-900">{entry.value}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-gradient-to-br from-blue-600 to-indigo-800 rounded-3xl p-8 text-white shadow-xl relative overflow-hidden group">
            <div className="relative z-10">
              <h5 className="text-[10px] font-bold uppercase tracking-[.3em] opacity-80 mb-2">System Insights</h5>
              <p className="text-lg font-black leading-tight mb-4">Patterns indicate strong correlation in the current cluster.</p>
              <button className="px-4 py-2 bg-white/20 backdrop-blur-md rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-white/30 transition-all">
                View Deep Report
              </button>
            </div>
            <Activity className="absolute -bottom-6 -right-6 text-white/10 w-32 h-32 transform rotate-12 group-hover:scale-110 transition-transform duration-700" />
          </div>
        </div>
      </div>

      {/* Numerical Synthesis Footer */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {Object.entries(statistics || {}).slice(0, 6).map(([key, value], idx) => (
          <div key={key} className="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm hover:shadow-md transition-all group">
            <p className="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-1 truncate">{key}</p>
            <p className="text-xl font-black text-gray-900 group-hover:text-blue-600 transition-colors">
              {typeof value === 'number' ? 
                (value > 1000 ? (value/1000).toFixed(1)+'k' : value.toFixed(1)) : 
                value
              }
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

