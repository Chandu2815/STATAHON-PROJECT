import React, { useState, useEffect, useMemo } from 'react';
import { ChevronDown, Info, Loader2 } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';

export default function HierarchicalDatasetSelector({ selectedDataset, onSelect }) {
  const [categories, setCategories] = useState({});
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHierarchicalDatasets();
  }, []);

  const fetchHierarchicalDatasets = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/datasets/hierarchical`);
      if (response.data.success) {
        setCategories(response.data.data);
      }
    } catch (err) {
      console.error('Error fetching hierarchical datasets:', err);
    } finally {
      setLoading(false);
    }
  };

  const categoryOrder = ['HCES', 'PLFS', 'Survey', 'Other'];
  const categoryIcons = {
    'HCES': '🏠',
    'PLFS': '📊',
    'Survey': '📋',
    'Other': '📁'
  };

  const categoryDescriptions = {
    'HCES': 'Household Consumption & Expenditure Survey',
    'PLFS': 'Periodic Labour Force Survey',
    'Survey': 'General Survey Data',
    'Other': 'Additional Datasets'
  };

  const sortedCategories = useMemo(() => {
    const sorted = Object.keys(categories)
      .sort((a, b) => categoryOrder.indexOf(a) - categoryOrder.indexOf(b))
      .reduce((obj, key) => {
        obj[key] = categories[key];
        return obj;
      }, {});
    return sorted;
  }, [categories]);

  // Total statistics
  const totalDatasets = Object.values(categories).reduce((sum, items) => sum + items.length, 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8 bg-gray-50 rounded border border-gray-300">
        <Loader2 className="animate-spin text-blue-900 mr-2" size={20} />
        <span className="text-sm text-gray-700">Loading datasets...</span>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-start gap-2">
        <Info size={16} className="text-blue-900 mt-0.5 flex-shrink-0" />
        <div className="text-xs text-gray-700">
          <span className="font-bold">Available datasets:</span> {totalDatasets} across {Object.keys(categories).length} categories
        </div>
      </div>

      {/* Step 1: Select Category */}
      <div>
        <label className="text-xs font-bold text-gray-900 uppercase tracking-wide block mb-3">
          1️⃣ SELECT CATEGORY
        </label>
        <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-2">
          {Object.entries(sortedCategories).map(([category, datasets]) => (
            <button
              key={category}
              onClick={() => {
                setSelectedCategory(category);
              }}
              title={categoryDescriptions[category]}
              className={`p-3 rounded font-semibold text-sm transition border-2 group ${
                selectedCategory === category
                  ? 'bg-blue-900 text-white border-blue-900 shadow-md'
                  : 'bg-white text-gray-800 border-gray-300 hover:border-blue-500 hover:bg-gray-50'
              }`}
            >
              <span className="block text-lg mb-1">
                {categoryIcons[category] || '📁'}
              </span>
              <span className="block font-bold text-xs">{category}</span>
              <span className={`block text-xs mt-1 opacity-75 ${
                selectedCategory === category ? 'text-blue-100' : 'text-gray-600'
              }`}>
                {datasets.length} items
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Step 2: Select Dataset from Category */}
      {selectedCategory && (
        <div className="space-y-3 p-4 bg-gray-50 rounded-lg border border-gray-300">
          <div>
            <label className="text-xs font-bold text-gray-900 uppercase tracking-wide block mb-2">
              2️⃣ SELECT DATASET FROM {selectedCategory.toUpperCase()}
            </label>
            <p className="text-xs text-gray-600 mb-3">
              📋 {categoryDescriptions[selectedCategory]} • {(categories[selectedCategory] || []).length} available
            </p>
          </div>

          {/* Dataset Dropdown */}
          <div className="relative">
            <select
              value={selectedDataset || ''}
              onChange={(e) => onSelect(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-400 rounded text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-900 focus:border-blue-900 appearance-none pr-8 bg-white hover:border-gray-500 transition cursor-pointer"
            >
              <option value="">-- Select a dataset --</option>
              {(categories[selectedCategory] || []).map((dataset) => (
                <option key={dataset} value={dataset}>
                  {dataset.replace(/_/g, ' ').toUpperCase()}
                </option>
              ))}
            </select>
            <ChevronDown
              size={16}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-600 pointer-events-none"
            />
          </div>
        </div>
      )}

      {/* Currently Selected Dataset Info */}
      {selectedDataset && (
        <div className="p-4 bg-blue-50 border-l-4 border-l-blue-900 rounded-r">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs text-gray-900 font-bold uppercase tracking-wide">
                ✓ Selected Dataset
              </p>
              <p className="text-lg font-bold text-blue-900 mt-1">
                {selectedDataset.replace(/_/g, ' ').toUpperCase()}
              </p>
              <p className="text-xs text-gray-600 mt-2">
                Category: <span className="font-semibold">{selectedCategory}</span>
              </p>
            </div>
            <button
              onClick={() => {
                onSelect(null);
                setSelectedCategory(null);
              }}
              className="text-xs font-bold text-gray-600 hover:text-gray-900 px-2 py-1 hover:bg-gray-200 rounded transition"
              title="Clear selection"
            >
              CLEAR
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
