import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Loader2, AlertCircle } from 'lucide-react';
import DatasetSelector from '../components/DatasetSelector';
import ColumnSelector from '../components/ColumnSelector';
import FiltersPanel from '../components/FiltersPanel';
import DataTable from '../components/DataTable';
import ChartView from '../components/ChartView';

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

  // Fetch datasets on mount
  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/datasets`);
      if (response.data.success) {
        setDatasets(response.data.tables || []);
      }
    } catch (err) {
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
      setFilters({});
      setPagination({ page: 0, pageSize: 10 });
      setLoading(true);

      // Fetch columns for selected dataset
      const response = await axios.get(`${API_BASE_URL}/columns/${dataset}`);
      if (response.data.success) {
        const cols = response.data.columns.map((col) => ({
          name: col.column_name,
          type: col.data_type,
        }));
        setColumns(cols);
      }
    } catch (err) {
      setError('Failed to fetch columns: ' + err.message);
    } finally {
      setLoading(false);
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
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Survey AI Dashboard</h1>
        <p className="text-gray-600 mt-2">Explore and analyze your data dynamically</p>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex gap-3">
          <AlertCircle className="text-red-600" size={24} />
          <div>
            <h3 className="font-semibold text-red-900">Error</h3>
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="animate-spin text-blue-600" size={32} />
          <span className="ml-2 text-gray-600">Loading data...</span>
        </div>
      )}

      {!loading && (
        <>
          {/* Selectors Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Dataset Selector */}
            <DatasetSelector
              datasets={datasets}
              selectedDataset={selectedDataset}
              onSelect={handleDatasetSelect}
            />

            {/* Column Selector */}
            {selectedDataset && (
              <ColumnSelector
                columns={columns}
                selectedColumns={selectedColumns}
                onSelect={handleColumnSelect}
              />
            )}
          </div>

          {/* Filters */}
          {selectedDataset && selectedColumns.length > 0 && (
            <FiltersPanel
              columns={columns}
              selectedColumns={selectedColumns}
              filters={filters}
              onChange={handleFilterChange}
            />
          )}

          {/* Charts Section */}
          {data.length > 0 && (
            <ChartView
              data={data}
              columns={selectedColumns}
              statistics={statistics}
            />
          )}

          {/* Data Table */}
          {selectedDataset && selectedColumns.length > 0 && (
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
          )}

          {/* Empty State */}
          {!selectedDataset && (
            <div className="text-center py-12">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mb-4">
                <span className="text-2xl">📊</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                Select a Dataset
              </h3>
              <p className="text-gray-600">
                Choose a dataset above to begin exploring your data
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
