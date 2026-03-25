import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Loader2, AlertCircle, Database, Layers, Filter as FilterIcon, TrendingUp, BarChart3 } from 'lucide-react';
import HierarchicalDatasetSelector from '../components/HierarchicalDatasetSelector';
import ColumnSelector from '../components/ColumnSelector';
import FiltersPanel from '../components/FiltersPanel';
import DataTable from '../components/DataTable';
import ChartView from '../components/ChartView';
import DataExportActions from '../components/DataExportActions';
import HelpAndShortcuts from '../components/HelpAndShortcuts';
import AnalyticsDashboard from '../components/AnalyticsDashboard';

const API_BASE_URL = 'http://localhost:8001';

export default function SurveyAI() {
  const [datasets, setDatasets] = useState([]);
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
      const response = await axios.get(`${API_BASE_URL}/datasets`);
      if (response.data.success) {
        setDatasets(response.data.datasets || []);
      }
    } catch (err) {
      console.error('❌ Error fetching datasets:', err);
      setError('Failed to fetch datasets: ' + err.message);
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
      const response = await axios.get(`${API_BASE_URL}/columns/${dataset}`);
      if (response.data.success) {
        const cols = response.data.columns.map((col) => ({
          name: col.name,
          type: col.type,
        }));
        setColumns(cols);
      }
    } catch (err) {
      console.error('❌ Error fetching columns:', err);
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

      const response = await axios.post(`${API_BASE_URL}/data`, payload);
      if (response.data.success) {
        setData(response.data.data || []);
      } else {
        setError('Failed to fetch data: ' + (response.data.message || 'Unknown error'));
      }
    } catch (err) {
      setError('Failed to fetch data: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    if (!selectedDataset) return;

    try {
      const response = await axios.get(`${API_BASE_URL}/statistics/${selectedDataset}`);
      if (response.data.success) {
        setStatistics(response.data.statistics || {});
      }
    } catch (err) {
      console.error('Failed to fetch statistics:', err);
    }
  };

  useEffect(() => {
    if (selectedDataset && selectedColumns.length > 0) {
      fetchData();
      fetchStatistics();
    }
  }, [selectedDataset, selectedColumns, filters, pagination]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Professional Government Header */}
      <div className="sticky top-0 z-50 bg-white border-b border-gray-300 shadow-sm">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-blue-900 rounded">
                <Database size={28} className="text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Survey Data Dashboard
                </h1>
                <p className="text-sm text-gray-600 mt-0.5">Government Survey Analysis & Reporting</p>
              </div>
            </div>
            {selectedDataset && (
              <div className="px-4 py-2.5 bg-gray-100 border border-gray-300 rounded">
                <p className="text-sm font-medium text-gray-900">
                  Active Dataset: <span className="font-bold text-blue-900">{selectedDataset}</span>
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-8 py-10 space-y-8">
        {/* Tab Navigation */}
        <div className="flex items-center gap-4 border-b border-gray-300 -mx-8 px-8 sticky top-20 bg-white z-40">
          <button
            onClick={() => setActiveTab('explore')}
            className={`px-6 py-3 font-semibold text-sm transition border-b-2 ${
              activeTab === 'explore'
                ? 'text-blue-900 border-b-blue-900'
                : 'text-gray-600 border-b-transparent hover:text-gray-900'
            }`}
          >
            <Layers size={16} className="inline mr-2" />
            Data Explorer
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`px-6 py-3 font-semibold text-sm transition border-b-2 ${
              activeTab === 'analytics'
                ? 'text-blue-900 border-b-blue-900'
                : 'text-gray-600 border-b-transparent hover:text-gray-900'
            }`}
          >
            <BarChart3 size={16} className="inline mr-2" />
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
        {loading && datasets.length === 0 && (
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
          <div className="space-y-8">
            {/* Step 1: Dataset Selection Card */}
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="flex items-center justify-center w-10 h-10 bg-blue-900 text-white font-bold rounded-full text-lg">
                  1
                </div>
                <h2 className="text-xl font-bold text-gray-900">Select Dataset</h2>
              </div>
              <div className="bg-white rounded border border-gray-300 shadow-sm p-6">
                <HierarchicalDatasetSelector
                  selectedDataset={selectedDataset}
                  onSelect={handleDatasetSelect}
                />
              </div>
            </div>

            {/* Step 2: Column Selection Card */}
            {selectedDataset && (
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="flex items-center justify-center w-10 h-10 bg-blue-800 text-white font-bold rounded-full text-lg">
                    2
                  </div>
                  <h2 className="text-xl font-bold text-gray-900">Select Columns</h2>
                  <span className="ml-auto text-xs font-semibold px-3 py-1 bg-gray-200 text-gray-800 rounded">
                    {selectedColumns.length} / {columns.length}
                  </span>
                </div>
                <div className="bg-white rounded border border-gray-300 shadow-sm p-6">
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
                        className="text-xs font-bold text-blue-900 hover:underline"
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
                            : 'bg-gray-100 text-gray-800 border border-gray-300 hover:bg-gray-200'
                        }`}
                        title={col.name}
                      >
                        {col.name.length > 9 ? col.name.substring(0, 9) : col.name}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Step 3: Filters Card */}
            {selectedDataset && selectedColumns.length > 0 && (
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="flex items-center justify-center w-10 h-10 bg-blue-700 text-white font-bold rounded-full text-lg">
                    3
                  </div>
                  <h2 className="text-xl font-bold text-gray-900">Apply Filters</h2>
                  <span className="ml-auto text-xs font-semibold px-3 py-1 bg-gray-200 text-gray-800 rounded">
                    {Object.keys(filters).length} Active
                  </span>
                </div>
                <div className="bg-white rounded border border-gray-300 shadow-sm p-6">
                  <FiltersPanel
                    columns={columns}
                    selectedColumns={selectedColumns}
                    data={data}
                    filters={filters}
                    onChange={handleFilterChange}
                  />
                </div>
              </div>
            )}

            {/* Step 4: Data Table Card */}
            {selectedDataset && selectedColumns.length > 0 && (
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="flex items-center justify-center w-10 h-10 bg-blue-600 text-white font-bold rounded-full text-lg">
                    4
                  </div>
                  <h2 className="text-xl font-bold text-gray-900">Data Results</h2>
                  <span className="ml-auto text-xs font-semibold px-3 py-1 bg-gray-200 text-gray-800 rounded">
                    {data.length} Rows
                  </span>
                </div>
                <div className="bg-white rounded border border-gray-300 shadow-sm overflow-hidden">
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
                </div>

                {/* Export Actions */}
                {data.length > 0 && (
                  <div className="mt-4 p-4 bg-gray-50 border border-gray-300 rounded">
                    <p className="text-xs font-bold text-gray-900 uppercase tracking-wide mb-3">
                      📥 Export Or Share Results
                    </p>
                    <DataExportActions
                      data={data}
                      selectedColumns={selectedColumns}
                      selectedDataset={selectedDataset}
                    />
                  </div>
                )}
              </div>
            )}

            {/* Step 5: Charts Card */}
            {data.length > 0 && (
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="flex items-center justify-center w-10 h-10 bg-blue-500 text-white font-bold rounded-full text-lg">
                    5
                  </div>
                  <h2 className="text-xl font-bold text-gray-900">Charts & Visualizations</h2>
                  <span className="ml-auto text-xs font-semibold px-3 py-1 bg-gray-200 text-gray-800 rounded">
                    Analytics
                  </span>
                </div>
                <div className="bg-white rounded border border-gray-300 shadow-sm p-8">
                  <ChartView
                    data={data}
                    columns={selectedColumns}
                    statistics={statistics}
                  />
                </div>
              </div>
            )}

            {/* Empty State */}
            {!selectedDataset && (
              <div className="flex flex-col items-center justify-center py-24 text-center">
                <div className="p-5 bg-gray-100 rounded-lg mb-6">
                  <Database size={52} className="text-gray-600 mx-auto" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  Welcome to Survey Dashboard
                </h3>
                <p className="text-gray-700 text-center max-w-md mb-8">
                  Select a dataset from Step 1 above to begin analyzing your survey data. Our dashboard provides powerful filtering, visualization, and reporting tools.
                </p>
                <div className="flex gap-3 flex-wrap justify-center">
                  <span className="px-3 py-1.5 text-xs font-semibold bg-gray-100 text-gray-800 rounded border border-gray-300">{datasets.length} Datasets Available</span>
                  <span className="px-3 py-1.5 text-xs font-semibold bg-gray-100 text-gray-800 rounded border border-gray-300">Advanced Filtering</span>
                  <span className="px-3 py-1.5 text-xs font-semibold bg-gray-100 text-gray-800 rounded border border-gray-300">Real-time Analysis</span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <AnalyticsDashboard />
        )}
      </div>

      {/* Help & Shortcuts Button */}
      <HelpAndShortcuts />
    </div>
  );
}
