import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Loader2, 
  AlertCircle, 
  Database, 
  Layers, 
  Filter as FilterIcon, 
  TrendingUp, 
  BarChart3,
  Search,
  Settings,
  HelpCircle,
  Zap,
  ArrowRight,
  CheckSquare
} from 'lucide-react';
import HierarchicalDatasetSelector from '../components/HierarchicalDatasetSelector.jsx';
import ColumnSelector from '../components/ColumnSelector.jsx';
import FiltersPanel from '../components/FiltersPanel.jsx';
import DataTable from '../components/DataTable.jsx';
import ChartView from '../components/ChartView.jsx';
import DataExportActions from '../components/DataExportActions.jsx';
import HelpAndShortcuts from '../components/HelpAndShortcuts.jsx';
import AnalyticsDashboard from '../components/AnalyticsDashboard.jsx';

// Create axios instance with proper baseURL configuration
const API = axios.create({
  baseURL: '/api/ai',
  timeout: 10000,
});

export default function SurveyAI() {
  const [datasets, setDatasets] = useState({}); 
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [columns, setColumns] = useState([]);
  const [selectedColumns, setSelectedColumns] = useState([]);
  const [data, setData] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({});
  const [pagination, setPagination] = useState({ page: 0, pageSize: 12 });
  const [activeTab, setActiveTab] = useState('explore'); 

  // Fetch datasets on mount
  useEffect(() => {
    fetchDatasets();

    // Keyboard shortcuts
    const handleKeyPress = (e) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === 'k' || e.key === 'K') {
          e.preventDefault();
          setFilters({}); 
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  const fetchDatasets = async () => {
    try {
      setLoading(true);
      const response = await API.get('/datasets/hierarchical');
      if (response.data.success) {
        setDatasets(response.data.data || {});
      } else {
        setError('API returned unexpected response format');
      }
    } catch (err) {
      setError('Failed to fetch datasets. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  const handleDatasetSelect = async (dataset) => {
    try {
      setSelectedDataset(dataset);
      setSelectedColumns([]);
      setData([]);
      setError('');
      setFilters({});
      setPagination({ page: 0, pageSize: 12 });

      const response = await API.get(`/columns/${dataset}`);
      if (response.data.success && Array.isArray(response.data.columns)) {
        const cols = response.data.columns.map((col) => ({
          name: col.name,
          type: col.type || 'unknown',
        }));
        setColumns(cols);
      } else {
        setColumns([]);
      }
    } catch (err) {
      setError('Failed to fetch columns: ' + err.message);
      setColumns([]);
    }
  };

  const handleColumnSelect = (column) => {
    setSelectedColumns((prev) =>
      prev.includes(column)
        ? prev.filter((col) => col !== column)
        : [...prev, column]
    );
    setPagination({ page: 0, pageSize: 12 });
  };

  const handleFilterChange = (filterObj) => {
    setFilters(filterObj);
    setPagination({ page: 0, pageSize: 12 });
  };

  const fetchData = async () => {
    if (!selectedDataset || selectedColumns.length === 0) {
      setError('Please select a dataset and at least one column');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const filterConditions = {};
      Object.entries(filters).forEach(([key, value]) => {
        if (value && value.toString().trim()) {
          filterConditions[key] = value;
        }
      });

      const payload = {
        table: selectedDataset,
        columns: selectedColumns,
        filters: filterConditions,
        limit: pagination.pageSize,
        offset: pagination.page * pagination.pageSize,
      };

      const response = await API.post('/data', payload);
      if (response.data.success) {
        setData(response.data.data || []);
      } else {
        setError('Failed to fetch data: ' + (response.data.message || 'Unknown error'));
      }
    } catch (err) {
      setError('Failed to fetch data. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    if (!selectedDataset) return;
    try {
      const response = await API.get(`/statistics/${selectedDataset}`);
      if (response.data.success) {
        setStatistics(response.data.statistics || {});
      }
    } catch (err) {}
  };

  useEffect(() => {
    if (selectedDataset && selectedColumns.length > 0) {
      fetchData();
      fetchStatistics();
    }
  }, [selectedDataset, selectedColumns, filters, pagination]);

  return (
    <div className="min-h-screen bg-[#fbfcff] flex flex-col font-sans selection:bg-blue-100 selection:text-blue-900">
      {/* Premium Navigation Header */}
      <nav className="sticky top-0 z-[100] bg-white/80 backdrop-blur-xl border-b border-gray-100 shadow-sm">
        <div className="max-w-[1600px] mx-auto px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl flex items-center justify-center shadow-lg shadow-blue-200">
                <Zap className="text-white ring-2 ring-white/20" size={20} />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-lg font-black text-gray-900 leading-tight tracking-tight">Survey AI</h1>
                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest italic">Intelligence & Analysis</p>
              </div>
            </div>
            
            <div className="h-8 w-[1px] bg-gray-100 mx-2 hidden md:block"></div>
            
            <div className="flex items-center gap-1 bg-gray-50 p-1 rounded-2xl">
              <button
                onClick={() => setActiveTab('explore')}
                className={`flex items-center gap-2 px-6 py-2 rounded-[14px] text-xs font-black uppercase tracking-widest transition-all duration-300 ${
                  activeTab === 'explore'
                    ? 'bg-white text-blue-600 shadow-sm ring-1 ring-gray-100'
                    : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                <Layers size={14} />
                Explore
              </button>
              <button
                onClick={() => setActiveTab('analytics')}
                className={`flex items-center gap-2 px-6 py-2 rounded-[14px] text-xs font-black uppercase tracking-widest transition-all duration-300 ${
                  activeTab === 'analytics'
                    ? 'bg-white text-blue-600 shadow-sm ring-1 ring-gray-100'
                    : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                <BarChart3 size={14} />
                Analytics
              </button>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {selectedDataset && (
              <div className="hidden lg:flex items-center gap-3 px-4 py-2 bg-blue-50/50 rounded-xl border border-blue-100">
                <Database className="text-blue-600" size={16} />
                <span className="text-[11px] font-black text-blue-900 uppercase tracking-tighter truncate max-w-[200px]">{selectedDataset}</span>
              </div>
            )}
            <div className="flex items-center gap-2">
              <button className="p-2 text-gray-400 hover:text-gray-900 transition-colors"><Search size={20} /></button>
              <button className="p-2 text-gray-400 hover:text-gray-900 transition-colors"><Settings size={20} /></button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Intelligent Content Area */}
      <main className="flex-1 w-full max-w-[1600px] mx-auto px-8 py-10">
        {/* Error Notification */}
        {error && (
          <div className="mb-8 p-6 bg-red-50 border-2 border-red-100 rounded-3xl flex items-start gap-4 animate-in slide-in-from-top-4 duration-500">
            <div className="p-2 bg-red-100 text-red-600 rounded-xl"><AlertCircle size={24} /></div>
            <div>
              <h3 className="text-sm font-black text-red-900 uppercase tracking-widest">Protocol Failure</h3>
              <p className="text-xs font-medium text-red-700 mt-1 leading-relaxed">{error}</p>
            </div>
          </div>
        )}

        {activeTab === 'explore' && (
          <div className="max-w-5xl mx-auto space-y-12 pb-20">
            
            {/* Step 1: Dataset Selection */}
            <section className="relative">
              <div className="flex items-center gap-4 mb-8">
                <div className="w-10 h-10 rounded-2xl bg-blue-600 text-white flex items-center justify-center font-black text-sm shadow-xl shadow-blue-100 z-10">01</div>
                <div className="h-[2px] flex-1 bg-gradient-to-r from-blue-600 to-transparent opacity-20"></div>
                <h3 className="text-sm font-black text-gray-900 uppercase tracking-[.3em] pr-4">Primary Source Repository</h3>
              </div>
              <div className="pl-14">
                <HierarchicalDatasetSelector
                  datasets={datasets}
                  selectedDataset={selectedDataset}
                  onSelect={handleDatasetSelect}
                />
              </div>
            </section>

            {/* Step 2: Vector Mapping (Checkboxes) */}
            {selectedDataset && (
              <section className="relative animate-in slide-in-from-bottom-8 duration-700">
                <div className="absolute left-[19px] top-[-48px] bottom-[calc(100%-8px)] w-[2px] bg-gradient-to-b from-blue-600 to-emerald-100 opacity-20"></div>
                <div className="flex items-center gap-4 mb-8">
                  <div className="w-10 h-10 rounded-2xl bg-emerald-600 text-white flex items-center justify-center font-black text-sm shadow-xl shadow-emerald-100 z-10">02</div>
                  <div className="h-[2px] flex-1 bg-gradient-to-r from-emerald-600 to-transparent opacity-20"></div>
                  <h3 className="text-sm font-black text-gray-900 uppercase tracking-[.3em] pr-4">Vector Mapping & Selection</h3>
                </div>
                <div className="pl-14">
                  <div className="bg-white rounded-[2.5rem] border border-gray-100 shadow-sm p-10 group relative overflow-hidden">
                    
                    {/* Enhanced Header with Prominent Select All */}
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10 pb-10 border-b border-gray-50">
                      <div>
                        <h4 className="text-lg font-black text-gray-900 uppercase tracking-tight italic">Schema Identification</h4>
                        <p className="text-xs font-medium text-gray-400 mt-1">Found {columns.length} potential vectors in {selectedDataset}</p>
                      </div>
                      
                      <div className="flex items-center gap-3">
                        <button 
                          onClick={() => setSelectedColumns(columns.map(c => c.name))}
                          className="px-6 py-3 bg-emerald-600 text-white text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-100 active:scale-95"
                        >
                          Select All Fields
                        </button>
                        <button 
                          onClick={() => setSelectedColumns([])}
                          className="px-6 py-3 bg-gray-50 text-gray-400 text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-red-50 hover:text-red-500 transition-all active:scale-95 border border-transparent hover:border-red-100"
                        >
                          Clear Selection
                        </button>
                        <div className="h-8 w-[1px] bg-gray-100 mx-2"></div>
                        <div className="flex flex-col items-end">
                           <span className="text-[10px] font-black text-emerald-600 uppercase tabular-nums">{selectedColumns.length} Active</span>
                           <span className="text-[8px] font-bold text-gray-300 uppercase tracking-tighter">Mapped Vectors</span>
                        </div>
                      </div>
                    </div>

                    {columns.length > 0 ? (
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-5 max-h-[600px] overflow-y-auto custom-scrollbar pr-4 py-2">
                        {columns.map((col) => {
                          const isActive = selectedColumns.includes(col.name);
                          return (
                            <button
                              key={col.name}
                              onClick={() => handleColumnSelect(col.name)}
                              className={`group relative text-left p-4 rounded-2xl border-2 transition-all duration-300 flex flex-col justify-between min-h-[110px] ${
                                isActive 
                                  ? 'bg-emerald-50/50 border-emerald-500 shadow-lg shadow-emerald-50' 
                                  : 'bg-white border-gray-100 hover:border-emerald-200 hover:bg-gray-50/20'
                              }`}
                            >
                              <div className="flex items-start justify-between gap-3 w-full">
                                <div className={`text-[10px] sm:text-[11px] font-black uppercase tracking-tight break-words leading-[1.3] flex-1 ${isActive ? 'text-emerald-900' : 'text-gray-400'}`}>
                                  {col.name.replace(/_/g, ' ')}
                                </div>
                                <div className={`shrink-0 w-5 h-5 rounded-lg border-2 flex items-center justify-center transition-all duration-300 ${
                                  isActive 
                                    ? 'bg-emerald-600 border-emerald-600 text-white' 
                                    : 'bg-white border-gray-200 group-hover:border-emerald-300'
                                }`}>
                                  {isActive && <CheckSquare size={12} strokeWidth={3} />}
                                </div>
                              </div>
                              
                              <div className="flex items-center justify-between mt-auto pt-4">
                                <div className="flex flex-col gap-0.5">
                                  <span className={`text-[8px] font-black uppercase tracking-tighter px-2 py-0.5 rounded-md self-start ${isActive ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-50 text-gray-400'}`}>
                                    {col.type}
                                  </span>
                                  <span className="text-[7px] font-bold text-gray-300 uppercase tracking-widest mt-1">Audit Verified</span>
                                </div>
                                {isActive && (
                                  <div className="flex items-center gap-1">
                                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                                    <div className="text-[8px] font-black text-emerald-400 uppercase tracking-tighter">Active</div>
                                  </div>
                                )}
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    ) : (
                      <div className="py-20 text-center">
                        <div className="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-dashed border-gray-200">
                          <Layers className="text-gray-200" size={32} />
                        </div>
                        <h4 className="text-sm font-black text-gray-400 uppercase tracking-widest italic">No schema fields detected</h4>
                        <p className="text-[10px] font-bold text-gray-300 mt-1">Please try re-selecting the primary source</p>
                      </div>
                    )}
                  </div>
                </div>
              </section>
            )}

            {/* Step 3: Conditional Logic (Filters) */}
            {selectedDataset && selectedColumns.length > 0 && (
              <section className="relative animate-in slide-in-from-bottom-8 duration-700">
                <div className="absolute left-[19px] top-[-48px] bottom-[calc(100%-8px)] w-[2px] bg-gradient-to-b from-emerald-600 to-violet-100 opacity-20"></div>
                <div className="flex items-center gap-4 mb-8">
                  <div className="w-10 h-10 rounded-2xl bg-violet-600 text-white flex items-center justify-center font-black text-sm shadow-xl shadow-violet-100 z-10">03</div>
                  <div className="h-[2px] flex-1 bg-gradient-to-r from-violet-600 to-transparent opacity-20"></div>
                  <h3 className="text-sm font-black text-gray-900 uppercase tracking-[.3em] pr-4">Conditional Logic Engine</h3>
                </div>
                <div className="pl-14">
                  <div className="bg-white rounded-[2.5rem] border border-gray-100 shadow-sm p-10">
                    <FiltersPanel
                      columns={columns}
                      selectedColumns={selectedColumns}
                      data={data}
                      filters={filters}
                      onChange={handleFilterChange}
                    />
                    <button
                      onClick={fetchData}
                      disabled={loading}
                      className="w-full mt-10 group relative overflow-hidden bg-gray-900 text-white rounded-2xl p-5 flex items-center justify-center gap-3 hover:bg-gray-800 transition-all shadow-2xl active:scale-95"
                    >
                       {loading ? <Loader2 className="animate-spin" size={20} /> : <Zap size={20} />}
                       <span className="text-xs font-black uppercase tracking-[.3em]">{loading ? 'Synthesizing...' : 'Saturate & Pulse System'}</span>
                    </button>
                  </div>
                </div>
              </section>
            )}

            {/* Step 4: Data Representation (Table) */}
            {selectedDataset && selectedColumns.length > 0 && data.length > 0 && (
              <section className="relative animate-in slide-in-from-bottom-8 duration-700">
                <div className="absolute left-[19px] top-[-48px] bottom-[calc(100%-8px)] w-[2px] bg-gradient-to-b from-violet-600 to-indigo-100 opacity-20"></div>
                <div className="flex items-center gap-4 mb-8">
                  <div className="w-10 h-10 rounded-2xl bg-indigo-600 text-white flex items-center justify-center font-black text-sm shadow-xl shadow-indigo-100 z-10">04</div>
                  <div className="h-[2px] flex-1 bg-gradient-to-r from-indigo-600 to-transparent opacity-20"></div>
                  <h3 className="text-sm font-black text-gray-900 uppercase tracking-[.3em] pr-4">Active Topology Representation</h3>
                </div>
                <div className="pl-14">
                  <div className="bg-white rounded-[3rem] border border-gray-100 shadow-xl overflow-hidden">
                    <div className="p-8 border-b border-gray-50 flex items-center justify-between bg-gradient-to-r from-white to-gray-50/50">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center">
                          <Database size={20} />
                        </div>
                        <div>
                          <h4 className="text-xs font-black text-gray-900 uppercase tracking-widest leading-none">High Fidelity Grid</h4>
                          <p className="text-[10px] font-bold text-gray-400 mt-1 uppercase tracking-tighter">Verified Entry Retrieval</p>
                        </div>
                      </div>
                      <DataExportActions
                        data={data}
                        selectedColumns={selectedColumns}
                        selectedDataset={selectedDataset}
                      />
                    </div>
                    <div className="p-2">
                      <DataTable
                        columns={selectedColumns}
                        data={data}
                        pagination={pagination}
                        onPageChange={(page) => setPagination({ ...pagination, page })}
                        onPageSizeChange={(pageSize) => setPagination({ page: 0, pageSize })}
                      />
                    </div>
                  </div>
                </div>
              </section>
            )}

            {/* Step 5: Data Visualization (Charts) */}
            {data.length > 0 && (
              <section className="relative animate-in slide-in-from-bottom-8 duration-700">
                <div className="absolute left-[19px] top-[-48px] bottom-[calc(100%-8px)] w-[2px] bg-gradient-to-b from-indigo-600 to-transparent opacity-20"></div>
                <div className="flex items-center gap-4 mb-8">
                  <div className="w-10 h-10 rounded-2xl bg-rose-600 text-white flex items-center justify-center font-black text-sm shadow-xl shadow-rose-100 z-10">05</div>
                  <div className="h-[2px] flex-1 bg-gradient-to-r from-rose-600 to-transparent opacity-20"></div>
                  <h3 className="text-sm font-black text-gray-900 uppercase tracking-[.3em] pr-4">Synthesized Visualization</h3>
                </div>
                <div className="pl-14">
                  <div className="bg-white rounded-[3rem] border border-gray-100 shadow-xl p-8">
                    <ChartView
                      data={data}
                      columns={selectedColumns}
                      statistics={statistics}
                    />
                  </div>
                </div>
              </section>
            )}
          </div>
        )}

        {/* Analytics Mode Output */}
        {activeTab === 'analytics' && (
          <div className="max-w-5xl mx-auto">
            <AnalyticsDashboard 
              selectedDataset={selectedDataset}
              columns={columns}
              selectedColumns={selectedColumns}
              data={data}
              statistics={statistics}
              loading={loading}
              error={error}
            />
          </div>
        )}
      </main>

      <HelpAndShortcuts />
    </div>
  );
}

