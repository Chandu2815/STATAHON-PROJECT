import React, { useState } from 'react';
import { ChevronDown, Database } from 'lucide-react';

export default function DatasetSelector({ datasets, selectedDataset, onSelect }) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredDatasets = datasets.filter((dataset) =>
    dataset.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      <label className="block text-sm font-semibold text-gray-700 mb-3">
        Dataset
      </label>

      {/* Dropdown Button */}
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full flex items-center justify-between px-4 py-3 bg-white border border-gray-300 rounded-lg hover:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
        >
          <div className="flex items-center gap-2">
            <Database size={18} className="text-blue-600" />
            <span className="text-gray-800 font-medium">
              {selectedDataset || 'Select a dataset...'}
            </span>
          </div>
          <ChevronDown
            size={18}
            className={`text-gray-600 transition ${isOpen ? 'rotate-180' : ''}`}
          />
        </button>

        {/* Dropdown Menu */}
        {isOpen && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-72 overflow-hidden flex flex-col">
            {/* Search Input */}
            <div className="p-3 border-b border-gray-200">
              <input
                type="text"
                placeholder="Search datasets..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                autoFocus
              />
            </div>

            {/* Dataset List */}
            <div className="overflow-y-auto">
              {filteredDatasets.length > 0 ? (
                filteredDatasets.map((dataset) => (
                  <button
                    key={dataset}
                    onClick={() => {
                      onSelect(dataset);
                      setIsOpen(false);
                      setSearchTerm('');
                    }}
                    className={`w-full text-left px-4 py-3 hover:bg-blue-50 transition flex items-center gap-2 ${
                      selectedDataset === dataset
                        ? 'bg-blue-100 text-blue-700 font-semibold'
                        : 'text-gray-700'
                    }`}
                  >
                    <Database size={16} />
                    {dataset}
                  </button>
                ))
              ) : (
                <div className="p-4 text-center text-gray-500 text-sm">
                  No datasets found
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Helper Text */}
      <p className="text-xs text-gray-500 mt-3">
        {datasets.length} dataset{datasets.length !== 1 ? 's' : ''} available
      </p>
    </div>
  );
}
