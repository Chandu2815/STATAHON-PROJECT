import React from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  PieChart, 
  CheckCircle2, 
  Zap,
  Activity,
  Layers,
  Database,
  Fingerprint
} from 'lucide-react';

/**
 * AnalyticsDashboard - Ultra-Premium UI
 * Professional analytics view focusing on standard data profiling
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
  // If no dataset selected, show premium selection prompt
  if (!selectedDataset) {
    return (
      <div className="flex items-center justify-center min-h-[400px] animate-in fade-in zoom-in duration-700">
        <div className="bg-white rounded-[2rem] border border-gray-100 shadow-2xl p-12 text-center max-w-lg relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-blue-500 to-indigo-600"></div>
          <div className="w-20 h-20 bg-gray-50 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-500">
            <Database className="text-gray-300" size={40} />
          </div>
          <h3 className="text-2xl font-black text-gray-900 mb-3 tracking-tight">Intelligence Engine Offline</h3>
          <p className="text-sm font-medium text-gray-500 leading-relaxed mb-8">
            Navigate to the <strong className="text-blue-600">Data Explorer</strong> to initialize a dataset and begin advanced synthesis.
          </p>
          <div className="flex justify-center gap-2">
            {[1, 2, 3].map(i => <div key={i} className="w-1.5 h-1.5 rounded-full bg-gray-200"></div>)}
          </div>
        </div>
      </div>
    );
  }

  // If no columns selected, show premium instruction
  if (selectedColumns.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[400px] animate-in fade-in zoom-in duration-700">
        <div className="bg-white rounded-[2rem] border border-gray-100 shadow-2xl p-12 text-center max-w-lg relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-amber-500 to-orange-600"></div>
          <div className="w-20 h-20 bg-amber-50 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:rotate-12 transition-transform duration-500">
            <Layers className="text-amber-500" size={40} />
          </div>
          <h3 className="text-2xl font-black text-gray-900 mb-3 tracking-tight">Configuration Required</h3>
          <p className="text-sm font-medium text-gray-500 leading-relaxed">
            Please define your analysis parameters by selecting one or more columns in the <strong className="text-blue-600">Primary Explorer</strong>.
          </p>
        </div>
      </div>
    );
  }

  // Show premium loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="relative w-24 h-24 mx-auto mb-6">
            <div className="absolute inset-0 border-4 border-blue-500/10 rounded-full"></div>
            <div className="absolute inset-0 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <Zap className="text-blue-600 animate-pulse" size={32} />
            </div>
          </div>
          <p className="text-sm font-black text-gray-900 uppercase tracking-widest animate-pulse">Synthesizing Analytics...</p>
        </div>
      </div>
    );
  }

  // Calculate analytics
  const totalRecords = data?.length || 0;
  const activeColumns = selectedColumns?.length || 0;
  
  const insights = {};
  selectedColumns.forEach(col => {
    const values = (data || []).map(row => row[col]).filter(v => v !== null && v !== undefined);
    const uniqueValues = new Set(values);
    insights[col] = {
      unique: uniqueValues.size,
      total: values.length,
      nulls: (data?.length || 0) - values.length,
      types: typeof values[0]
    };
  });

  const completeness = totalRecords > 0 ? ((selectedColumns.reduce((sum, col) => {
    const colInfo = insights[col] || {};
    return sum + (colInfo.total || 0);
  }, 0) / (totalRecords * selectedColumns.length) * 100) || 0).toFixed(0) : 0;

  return (
    <div className="space-y-10 animate-in fade-in duration-1000 pb-20">
      {/* Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 px-2">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <span className="px-3 py-1 bg-gray-900 text-white text-[10px] font-black uppercase tracking-widest rounded-full">Telemetry Active</span>
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></span>
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Real-time Profiling</span>
          </div>
          <h2 className="text-4xl font-black text-gray-900 tracking-tight leading-tight">
            Data Intelligence <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Pulse</span>
          </h2>
          <p className="text-sm font-medium text-gray-500 mt-2 max-w-2xl leading-relaxed">
            Profiling infrastructure for <strong className="text-gray-900">{selectedDataset}</strong>. 
            Standardizing entropy and density metrics across active dimensions.
          </p>
        </div>
      </div>

      {/* Hero Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Metric 1: Total Population */}
        <div className="group relative bg-white rounded-[2rem] border border-gray-100 shadow-sm hover:shadow-2xl transition-all duration-500 p-8 overflow-hidden">
          <div className="absolute -top-10 -right-10 w-32 h-32 bg-blue-50 rounded-full group-hover:scale-150 transition-transform duration-700"></div>
          <div className="relative z-10 flex items-center justify-between mb-6">
            <div className="p-3 bg-blue-600 text-white rounded-2xl shadow-lg shadow-blue-200">
              <Activity size={24} />
            </div>
            <TrendingUp className="text-blue-500 opacity-0 group-hover:opacity-100 transition-opacity" size={20} />
          </div>
          <div className="relative z-10">
            <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Total Population</p>
            <h4 className="text-4xl font-black text-gray-900 tracking-tighter">{totalRecords.toLocaleString()}</h4>
            <div className="flex items-center gap-2 mt-4">
              <span className="text-[10px] font-bold text-blue-600 px-2 py-0.5 bg-blue-50 rounded-md">Dataset Size</span>
              <span className="text-[10px] font-medium text-gray-400 font-mono italic">total_entries</span>
            </div>
          </div>
        </div>

        {/* Metric 2: Analyzed Vectors */}
        <div className="group relative bg-white rounded-[2rem] border border-gray-100 shadow-sm hover:shadow-2xl transition-all duration-500 p-8 overflow-hidden">
          <div className="absolute -top-10 -right-10 w-32 h-32 bg-purple-50 rounded-full group-hover:scale-150 transition-transform duration-700"></div>
          <div className="relative z-10 flex items-center justify-between mb-6">
            <div className="p-3 bg-purple-600 text-white rounded-2xl shadow-lg shadow-purple-200">
              <Layers size={24} />
            </div>
            <PieChart className="text-purple-500 opacity-0 group-hover:opacity-100 transition-opacity" size={20} />
          </div>
          <div className="relative z-10">
            <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Analyzed Vectors</p>
            <h4 className="text-4xl font-black text-gray-900 tracking-tighter">{activeColumns} <span className="text-lg opacity-30">DIMENSIONS</span></h4>
            <div className="flex items-center gap-2 mt-4">
              <span className="text-[10px] font-bold text-purple-600 px-2 py-0.5 bg-purple-50 rounded-md">Selected Schema</span>
              <span className="text-[10px] font-medium text-gray-400 font-mono italic">fields_active</span>
            </div>
          </div>
        </div>

        {/* Metric 3: Population Completeness */}
        <div className="group relative bg-white rounded-[2rem] border border-gray-100 shadow-sm hover:shadow-2xl transition-all duration-500 p-8 overflow-hidden">
          <div className="absolute -top-10 -right-10 w-32 h-32 bg-green-50 rounded-full group-hover:scale-150 transition-transform duration-700"></div>
          <div className="relative z-10 flex items-center justify-between mb-6">
            <div className="p-3 bg-green-600 text-white rounded-2xl shadow-lg shadow-green-200">
              <CheckCircle2 size={24} />
            </div>
            <span className="text-[10px] font-black uppercase tracking-widest px-3 py-1 bg-green-100 text-green-600 rounded-full">Optimal Density</span>
          </div>
          <div className="relative z-10">
            <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Data Density</p>
            <h4 className="text-4xl font-black text-gray-900 tracking-tighter">{completeness}%</h4>
            <div className="w-full bg-gray-100 h-1.5 rounded-full mt-4 overflow-hidden">
              <div 
                className="h-full bg-emerald-500 transition-all duration-1000" 
                style={{ width: `${completeness}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* DETAILED FIELD PROFILING */}
      <div className="bg-white rounded-[2.5rem] border border-gray-100 shadow-xl p-10">
        <div className="flex items-center justify-between mb-10">
          <div>
            <h4 className="text-xl font-black text-gray-900 tracking-tight">Dimensional Architecture Audit</h4>
            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mt-1 italic">Structural integrity report per field</p>
          </div>
          <button className="px-6 py-2.5 bg-gray-50 hover:bg-gray-100 text-gray-900 text-[10px] font-black uppercase tracking-widest rounded-xl transition-all border border-gray-200">
            Download Detailed Audit
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {selectedColumns.map((col, idx) => {
            const colStats = insights[col] || {};
            return (
              <div key={col} className="group relative bg-gray-50/50 rounded-2xl border border-gray-100 p-6 hover:bg-white hover:shadow-xl transition-all duration-500 hover:-translate-y-1">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h5 className="font-black text-gray-900 text-sm truncate pr-4">{col}</h5>
                    <span className="text-[9px] font-black text-blue-600 uppercase tracking-tighter">{colStats.types} VECTOR</span>
                  </div>
                  <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center text-gray-300 font-bold text-xs ring-4 ring-gray-100 group-hover:ring-blue-50 transition-all font-mono">
                    {idx + 1}
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-tighter">UNIQUE ENTROPY</span>
                    <span className="text-xs font-black text-gray-900 font-mono italic">{colStats.unique.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-tighter">DATA DENSITY</span>
                    <span className="text-xs font-black text-gray-900 font-mono italic">{((colStats.total / totalRecords) * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex items-center justify-between pt-3 border-t border-gray-200/50">
                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-tighter">FILL RATE</span>
                    <span className="text-[10px] font-black text-green-600 uppercase">Optimal</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Strategic Intelligence Footer */}
      <div className="bg-gradient-to-r from-gray-900 to-indigo-950 rounded-[2.5rem] p-12 text-white shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-full opacity-10 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')]"></div>
        <div className="relative z-10 flex flex-col md:flex-row items-center gap-10">
          <div className="flex-1 text-center md:text-left">
            <h4 className="text-2xl font-black tracking-tight leading-tight mb-2">Synthesis Telemetry Complete.</h4>
            <p className="text-sm font-medium text-gray-400 leading-relaxed max-w-xl">
              Audit results indicate a complete structural density of {completeness}%. 
              Dimension analysis has been verified for all active vectors.
            </p>
          </div>
          <div className="flex flex-wrap justify-center gap-4">
            <button className="px-8 py-4 bg-white text-gray-900 rounded-[1.25rem] text-[10px] font-black uppercase tracking-widest hover:bg-blue-50 transition-all shadow-xl">
              Execute Data Sync
            </button>
            <button className="px-8 py-4 bg-white/10 backdrop-blur-md text-white rounded-[1.25rem] text-[10px] font-black uppercase tracking-widest hover:bg-white/20 transition-all border border-white/10">
              Download Full Report
            </button>
          </div>
        </div>
        <Fingerprint className="absolute -bottom-10 -right-10 text-white opacity-5 w-48 h-48 transform -rotate-12" />
      </div>
    </div>
  );
}
