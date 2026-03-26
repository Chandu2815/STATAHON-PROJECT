import React, { useState, useMemo } from 'react';
import { ChevronDown, Database, Folder } from 'lucide-react';

/**
 * HierarchicalDatasetSelector
 * Displays datasets organized hierarchically by category (HCES, PLFS, Survey, Other)
 */
export default function HierarchicalDatasetSelector({ 
  datasets = {}, 
  selectedDataset, 
  onSelect 
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Flatten hierarchical datasets for search and counting
  const flatDatasets = useMemo(() => {
    if (typeof datasets === 'string') return []; // Handle error case
    return Object.values(datasets)
      .flat()
      .filter(Boolean);
  }, [datasets]);

  // Filter datasets based on search term
  const filteredHierarchical = useMemo(() => {
    const filtered = {};
    let hasResults = false;
    
    Object.entries(datasets).forEach(([category, items]) => {
      const categoryItems = items.filter((item) =>
        item.toLowerCase().includes(searchTerm.toLowerCase())
      );
      if (categoryItems.length > 0) {
        filtered[category] = categoryItems;
        hasResults = true;
      }
    });
    
    return hasResults ? filtered : {};
  }, [datasets, searchTerm]);

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
          <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-96 overflow-hidden flex flex-col">
            {/* Search Input */}
            <div className="p-3 border-b border-gray-200 sticky top-0 bg-white">
              <input
                type="text"
                placeholder="Search datasets..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                autoFocus
              />
            </div>

            {/* Dataset List - Organized by Category */}
            <div className="overflow-y-auto">
              {Object.keys(filteredHierarchical).length > 0 ? (
                Object.entries(filteredHierarchical).map(([category, items]) => (
                  <div key={category}>
                    {/* Category Header */}
                    <div className="px-4 py-2 bg-gray-50 border-t border-gray-100 sticky top-12">
                      <div className="flex items-center gap-2 text-xs font-semibold text-gray-600 uppercase tracking-wide">
                        <Folder size={14} />
                        {category} ({items.length})
                      </div>
                    </div>

                    {/* Category Items */}
                    {items.map((dataset) => (
                      <button
                        key={dataset}
                        onClick={() => {
                          onSelect(dataset);
                          setIsOpen(false);
                          setSearchTerm('');
                        }}
                        className={`w-full text-left px-6 py-2.5 hover:bg-blue-50 transition flex items-center gap-2 border-l-4 ${
                          selectedDataset === dataset
                            ? 'bg-blue-100 text-blue-700 font-semibold border-l-blue-600'
                            : 'text-gray-700 border-l-transparent'
                        }`}
                      >
                        <Database size={14} />
                        <span className="text-sm">{dataset}</span>
                      </button>
                    ))}
                  </div>
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
        {flatDatasets.length} dataset{flatDatasets.length !== 1 ? 's' : ''} available
      </p>
    </div>
  );
}
