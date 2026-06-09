import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Loader2, AlertCircle, Database, Layers, Filter as FilterIcon, TrendingUp, BarChart3 } from 'lucide-react';
import HierarchicalDatasetSelector from '../components/HierarchicalDatasetSelector.jsx';
import ColumnSelector from '../components/ColumnSelector.jsx';
import FiltersPanel from '../components/FiltersPanel.jsx';
import DataTable from '../components/DataTable.jsx';
import ChartView from '../components/ChartView.jsx';
import DataExportActions from '../components/DataExportActions.jsx';
import HelpAndShortcuts from '../components/HelpAndShortcuts.jsx';
import AnalyticsDashboard from '../components/AnalyticsDashboard.jsx';

// Create axios instance with proper baseURL configuration
// In development: Vite proxy routes /api/ai/* to http://localhost:8001/*
// In production: NGINX reverse proxy routes /api/ai/* to backend
const API = axios.create({
  baseURL: '/api/ai',
  timeout: 10000,
});

export default function SurveyAI() {
  const [datasets, setDatasets] = useState({}); // Hierarchical: { HCES: [...], PLFS: [...], ... }
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [columns, setColumns] = useState([]);
  const [selectedColumns, setSelectedColumns] = useState([]);
  const [data, setData] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({});
  const [pagination, setPagination] = useState({ page: 0, pageSize: 10 });
  const [chartData, setChartData] = useState(null);
  const [activeTab, setActiveTab] = useState('explore'); // 'explore' or 'analytics'

  // Fetch datasets on mount
  useEffect(() => {
    fetchDatasets();

    // Keyboard shortcuts
    const handleKeyPress = (e) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === 'k' || e.key === 'K') {
          e.preventDefault();
          setFilters({}); // Clear filters
        } else if (e.key === 's' || e.key === 'S') {
          e.preventDefault();
          alert('Analysis saved locally!');
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  const fetchDatasets = async () => {
    try {
      setLoading(true);
      console.log('🔄 Fetching hierarchical datasets from /api/ai/datasets/hierarchical');
      const response = await API.get('/datasets/hierarchical');
      console.log('✅ Hierarchical datasets response:', response.data);
      if (response.data.success) {
        // Handle hierarchical structure: { HCES: [...], PLFS: [...], Survey: [...], Other: [...] }
        setDatasets(response.data.data || {});
        const totalCount = response.data.total_datasets || 0;
        console.log('✅ Loaded', totalCount, 'total datasets in', Object.keys(response.data.data).length, 'categories');
        Object.entries(response.data.data).forEach(([category, items]) => {
          console.log(`   📁 ${category}: ${items.length} datasets`);
        });
      } else {
        console.warn('⚠️ API returned success: false');
        setError('API returned unexpected response format');
      }
    } catch (err) {
      console.error('❌ Error fetching datasets:');
      console.error('   Error:', err.message);
      console.error('   Status:', err.response?.status);
      console.error('   Data:', err.response?.data);
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
      setPagination({ page: 0, pageSize: 10 });

      // Fetch columns for selected dataset
      console.log('🔄 Fetching columns for dataset:', dataset);
      const response = await API.get(`/columns/${dataset}`);
      console.log('✅ Columns response:', response.data);
      if (response.data.success) {
        const cols = response.data.columns.map((col) => ({
          name: col.name,
          type: col.type,
        }));
        setColumns(cols);
        console.log('✅ Loaded', cols.length, 'columns');
      }
    } catch (err) {
      console.error('❌ Error fetching columns:');
      console.error('   Error:', err.message);
      console.error('   Status:', err.response?.status);
      console.error('   Data:', err.response?.data);
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
    setPagination({ page: 0, pageSize: 10 });
  };

  const handleFilterChange = (filterObj) => {
    setFilters(filterObj);
    setPagination({ page: 0, pageSize: 10 });
  };

  const fetchData = async () => {
    if (!selectedDataset || selectedColumns.length === 0) {
      setError('Please select a dataset and at least one column');
      return;
    }

    try {
      setLoading(true);
      setError('');

      // Build filter conditions
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

      console.log('🔄 Posting data request:', payload);
      const response = await API.post('/data', payload);
      console.log('✅ Data response received:', response.data);
      if (response.data.success) {
        setData(response.data.data || []);
        console.log('✅ Loaded', response.data.data.length, 'rows');
      } else {
        console.error('⚠️ API returned success: false');
        setError('Failed to fetch data: ' + (response.data.message || 'Unknown error'));
      }
    } catch (err) {
      console.error('❌ Error fetching data:');
      console.error('   Error:', err.message);
      console.error('   Status:', err.response?.status);
      console.error('   Data:', err.response?.data);
      setError('Failed to fetch data. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    if (!selectedDataset) return;

    try {
      console.log('🔄 Fetching statistics for:', selectedDataset);
      const response = await API.get(`/statistics/${selectedDataset}`);
      console.log('✅ Statistics response:', response.data);
      if (response.data.success) {
        setStatistics(response.data.statistics || {});
        console.log('✅ Statistics loaded');
      }
    } catch (err) {
      console.error('❌ Error fetching statistics:');
      console.error('   Error:', err.message);
      console.error('   Status:', err.response?.status);
    }
  };

  useEffect(() => {
    if (selectedDataset && selectedColumns.length > 0) {
      fetchData();
      fetchStatistics();
    }
  }, [selectedDataset, selectedColumns, filters, pagination]);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Minimal Header - Clean & Professional */}
      <div className="sticky top-0 z-30 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 sm:px-8 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-blue-900">Data Explorer</h1>
            {selectedDataset && (
              <p className="text-xs text-gray-600 mt-1">
                Dataset: <span className="font-semibold text-orange-600">{selectedDataset}</span>
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-visible">
        <div className="max-w-7xl mx-auto px-6 sm:px-8 py-6 space-y-6">
          {/* Tab Navigation - Subtle */}
          <div className="flex gap-6 border-b border-gray-300 pb-4">
            <button
              onClick={() => setActiveTab('explore')}
              className={`px-2 py-2 font-semibold text-sm transition flex items-center gap-2 ${
                activeTab === 'explore'
                  ? 'text-blue-900 border-b-2 border-orange-500'
                  : 'text-gray-600 border-b-2 border-transparent hover:text-gray-900'
              }`}
            >
              <Layers size={16} />
              Explore
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`px-2 py-2 font-semibold text-sm transition flex items-center gap-2 ${
                activeTab === 'analytics'
                  ? 'text-blue-900 border-b-2 border-orange-500'
                  : 'text-gray-600 border-b-2 border-transparent hover:text-gray-900'
              }`}
            >
              <BarChart3 size={16} />
              Analytics
            </button>
          </div>

        {/* Error Alert */}
        {error && (
          <div className="p-5 bg-red-50 border-l-4 border-red-600 rounded flex gap-4">
            <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={22} />
            <div>
              <h3 className="font-bold text-red-900">Error</h3>
              <p className="text-red-700 text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Loading State - Initial Load */}
        {loading && Object.keys(datasets).length === 0 && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="p-5 bg-blue-100 rounded-lg mb-5">
              <Loader2 className="animate-spin text-blue-900" size={40} />
            </div>
            <p className="text-gray-900 font-medium text-lg">Loading Datasets</p>
            <p className="text-gray-600 text-sm mt-2">Please wait while we retrieve available datasets</p>
          </div>
        )}

        {/* Loading State - After Column Selection */}
        {loading && selectedDataset && selectedColumns.length > 0 && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="p-5 bg-green-100 rounded-lg mb-5">
              <Loader2 className="animate-spin text-green-900" size={40} />
            </div>
            <p className="text-gray-900 font-medium text-lg">Fetching Data</p>
            <p className="text-gray-600 text-sm mt-2">Retrieving records from {selectedDataset}</p>
          </div>
        )}

          {(!loading || datasets.length > 0) && activeTab === 'explore' && (
            <div className="space-y-6">
              {/* Step 1: Dataset Selection */}
              <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm hover:shadow-md transition">
                <h2 className="text-sm font-bold text-blue-900 mb-4 flex items-center gap-3">
                  <span className="inline-flex items-center justify-center w-7 h-7 bg-blue-900 text-white text-xs font-bold rounded-full">1</span>
                  <span className="text-base">Select Dataset</span>
                </h2>
                <HierarchicalDatasetSelector
                  datasets={datasets}
                  selectedDataset={selectedDataset}
                  onSelect={handleDatasetSelect}
                />
              </div>

              {/* Step 2: Column Selection */}
              {selectedDataset && (
                <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm hover:shadow-md transition">
                  <h2 className="text-sm font-bold text-blue-900 mb-4 flex items-center gap-3">
                    <span className="inline-flex items-center justify-center w-7 h-7 bg-orange-500 text-white text-xs font-bold rounded-full">2</span>
                    <span className="text-base">Select Columns</span>
                    <span className="ml-auto text-xs font-semibold px-3 py-1 bg-orange-100 text-orange-900 rounded-full border border-orange-200">{selectedColumns.length} / {columns.length}</span>
                  </h2>
                <div className="flex items-center justify-between mb-4">
                  <p className="text-sm text-gray-700 font-medium">
                    {selectedColumns.length === 0 && 'Select columns to analyze'}
                    {selectedColumns.length > 0 && selectedColumns.length < columns.length && selectedColumns.length + ' of ' + columns.length + ' selected'}
                    {selectedColumns.length === columns.length && 'All ' + columns.length + ' columns selected'}
                  </p>
                  {columns.length > 0 && (
                    <button
                      onClick={() => {
                        if (selectedColumns.length === columns.length) {
                          columns.forEach(col => {
                            if (selectedColumns.includes(col.name)) {
                              handleColumnSelect(col.name);
                            }
                          });
                        } else {
                          columns.forEach(col => {
                            if (!selectedColumns.includes(col.name)) {
                              handleColumnSelect(col.name);
                            }
                          });
                        }
                      }}
                      className="text-xs font-bold text-orange-600 hover:text-orange-700 hover:underline"
                    >
                      {selectedColumns.length === columns.length ? 'DESELECT ALL' : 'SELECT ALL'}
                    </button>
                  )}
                </div>
                <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2 max-h-56 overflow-y-auto pr-2">
                  {columns.map((col) => (
                    <button
                      key={col.name}
                      onClick={() => handleColumnSelect(col.name)}
                      className={`px-3 py-2.5 rounded text-xs font-semibold transition ${
                        selectedColumns.includes(col.name)
                          ? 'bg-blue-900 text-white border border-blue-900'
                          : 'bg-white text-gray-800 border border-gray-300 hover:bg-gray-50 hover:border-orange-400'
                      }`}
                      title={col.name}
                    >
                      {col.name.length > 9 ? col.name.substring(0, 9) : col.name}
                    </button>
                  ))}
                </div>
              </div>
            )}

              {/* Step 3: Filters */}
              {selectedDataset && selectedColumns.length > 0 && (
                <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm hover:shadow-md transition">
                  <h2 className="text-sm font-bold text-blue-900 mb-4 flex items-center gap-3">
                    <span className="inline-flex items-center justify-center w-7 h-7 bg-green-600 text-white text-xs font-bold rounded-full">3</span>
                    <span className="text-base">Apply Filters</span>
                    <span className="ml-auto text-xs font-semibold px-3 py-1 bg-green-100 text-green-900 rounded-full border border-green-200">{Object.keys(filters).length} Active</span>
                  </h2>
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
                  className="w-full mt-3 px-4 py-2 bg-orange-500 hover:bg-orange-600 disabled:bg-gray-400 text-white font-bold rounded text-sm transition"
                >
                  {loading ? '⏳ Fetching...' : '▶ Fetch & Analyze'}
                </button>
              </div>
            )}

              {/* Step 4: Data Table */}
              {selectedDataset && selectedColumns.length > 0 && (
                <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm hover:shadow-md transition">
                  <h2 className="text-sm font-bold text-blue-900 mb-4 flex items-center gap-3">
                    <span className="inline-flex items-center justify-center w-7 h-7 bg-purple-600 text-white text-xs font-bold rounded-full">4</span>
                    <span className="text-base">Data Results</span>
                    <span className="ml-auto text-xs font-semibold px-3 py-1 bg-purple-100 text-purple-900 rounded-full border border-purple-200">{data.length} Rows</span>
                  </h2>
                <DataTable
                  columns={selectedColumns}
                  data={data}
                  pagination={pagination}
                  onPageChange={(page) =>
                    setPagination({ ...pagination, page })
                  }
                  onPageSizeChange={(pageSize) =>
                    setPagination({ page: 0, pageSize })
                  }
                />
                {data.length > 0 && (
                  <div className="mt-3 p-3 bg-gray-50 border border-gray-300 rounded">
                    <p className="text-xs font-bold text-gray-900 mb-2">📥 Export Results</p>
                    <DataExportActions
                      data={data}
                      selectedColumns={selectedColumns}
                      selectedDataset={selectedDataset}
                    />
                  </div>
                )}
              </div>
            )}

              {/* Step 5: Charts */}
              {data.length > 0 && (
                <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm hover:shadow-md transition">
                  <h2 className="text-sm font-bold text-blue-900 mb-4 flex items-center gap-3">
                    <span className="inline-flex items-center justify-center w-7 h-7 bg-pink-600 text-white text-xs font-bold rounded-full">5</span>
                    <span className="text-base">Charts & Visualizations</span>
                  </h2>
                <ChartView
                  data={data}
                  columns={selectedColumns}
                  statistics={statistics}
                />
              </div>
            )}

            {/* Empty State */}
            {!selectedDataset && (
              <div className="flex flex-col items-center justify-center py-12 text-center bg-white rounded-lg border border-gray-200 p-6">
                <div className="p-3 bg-blue-100 rounded-lg mb-3">
                  <Database size={32} className="text-blue-900 mx-auto" />
                </div>
                <h3 className="text-lg font-bold text-blue-900 mb-2">Welcome to Data Explorer</h3>
                <p className="text-gray-700 text-center max-w-md text-sm mb-4">
                  Select a dataset to begin analyzing. Filter, visualize, and export your data with ease.
                </p>
              </div>
            )}
            </div>
          )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <AnalyticsDashboard 
            selectedDataset={selectedDataset}
            columns={columns}
            selectedColumns={selectedColumns}
            data={data}
            statistics={statistics}
            loading={loading}
            error={error}
          />
        )}
        </div>
      </div>

      {/* Help & Shortcuts Button */}
      <HelpAndShortcuts />
    </div>
  );
}
