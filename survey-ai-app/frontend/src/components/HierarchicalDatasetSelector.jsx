import React, { useState, useMemo } from 'react';
import { ChevronDown, Database, Search, X } from 'lucide-react';

/**
 * HierarchicalDatasetSelector - Premium UI
 * Beautiful, modern, and interactive dataset selector
 */
export default function HierarchicalDatasetSelector({ 
  datasets = {}, 
  selectedDataset, 
  onSelect 
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedCategories, setExpandedCategories] = useState({});

  // Premium Category Metadata
  const categoryMetadata = {
    HCES: { 
      icon: '📊', 
      emoji: '🏘️',
      title: 'HCES',
      description: 'Household Consumption & Expenditure Survey',
      color: 'blue',
      gradient: 'from-blue-500 via-blue-600 to-indigo-600'
    },
    PLFS: { 
      icon: '👷', 
      emoji: '💼',
      title: 'PLFS',
      description: 'Periodic Labour Force Survey',
      color: 'green',
      gradient: 'from-green-500 via-emerald-600 to-teal-600'
    },
    SURVEY: { 
      icon: '📋', 
      emoji: '📝',
      title: 'SURVEY',
      description: 'Survey Data & Analysis',
      color: 'purple',
      gradient: 'from-purple-500 via-violet-600 to-indigo-600'
    },
    OTHER: { 
      icon: '📁', 
      emoji: '🗂️',
      title: 'OTHER',
      description: 'Additional Datasets',
      color: 'amber',
      gradient: 'from-amber-500 via-orange-600 to-red-600'
    },
  };

  const flatDatasets = useMemo(() => {
    if (typeof datasets === 'string') return [];
    return Object.values(datasets).flat().filter(Boolean);
  }, [datasets]);

  const filteredHierarchical = useMemo(() => {
    const filtered = {};
    Object.entries(datasets).forEach(([category, items]) => {
      const categoryItems = items.filter((item) =>
        item.toLowerCase().includes(searchTerm.toLowerCase())
      );
      if (categoryItems.length > 0) {
        filtered[category] = categoryItems;
      }
    });
    return filtered;
  }, [datasets, searchTerm]);

  const sortedCategories = Object.entries(filteredHierarchical).sort((a, b) => {
    const order = { HCES: 1, PLFS: 2, SURVEY: 3, OTHER: 4 };
    return (order[a[0]] || 5) - (order[b[0]] || 5);
  });

  const toggleCategory = (category) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const colorClasses = {
    blue: 'border-blue-300 bg-blue-50 hover:bg-blue-100',
    green: 'border-green-300 bg-green-50 hover:bg-green-100',
    purple: 'border-purple-300 bg-purple-50 hover:bg-purple-100',
    amber: 'border-amber-300 bg-amber-50 hover:bg-amber-100',
  };

  return (
    <div className="bg-white rounded-lg border-2 border-gray-200 p-4 shadow-md relative z-10">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <label className="text-lg font-bold text-gray-900 flex items-center gap-2">
          <span className="text-2xl">📊</span>
          <span>Select Dataset</span>
        </label>
      </div>

      {/* Main Dropdown Button - Premium Style */}
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full flex items-center justify-between px-4 py-3 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white rounded-lg hover:shadow-lg focus:outline-none focus:ring-3 focus:ring-blue-300 transition-all font-semibold group"
        >
          <div className="flex items-center gap-3 flex-1 text-left">
            <div className="bg-white bg-opacity-20 p-1.5 rounded group-hover:bg-opacity-30 transition">
              <Database size={20} />
            </div>
            <div>
              <div className="text-xs opacity-90 font-medium">Dataset</div>
              <div className="text-sm font-semibold">
                {selectedDataset ? `✓ ${selectedDataset}` : 'Choose dataset...'}
              </div>
            </div>
          </div>
          <ChevronDown
            size={20}
            className={`transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`}
          />
        </button>

        {/* Premium Dropdown Menu */}
        {isOpen && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white border-2 border-blue-200 rounded-lg shadow-2xl z-[9999] max-h-[500px] overflow-hidden flex flex-col">
            {/* Search Header */}
            <div className="sticky top-0 bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 px-4 py-3 border-b-2 border-blue-100">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-blue-600 pointer-events-none" size={18} />
                <input
                  type="text"
                  placeholder="Search datasets..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-9 py-2 border-2 border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400 text-sm bg-white placeholder-gray-500"
                  autoFocus
                />
                {searchTerm && (
                  <button
                    onClick={() => setSearchTerm('')}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition"
                  >
                    <X size={18} />
                  </button>
                )}
              </div>
            </div>

            {/* Dataset List */}
            <div className="overflow-y-auto flex-1">
              {sortedCategories.length > 0 ? (
                sortedCategories.map(([category, items]) => {
                  const meta = categoryMetadata[category] || { 
                    icon: '📂', 
                    emoji: '📂',
                    title: category, 
                    description: category,
                    gradient: 'from-gray-500 to-gray-600'
                  };
                  const isExpanded = expandedCategories[category] !== false;
                  
                  return (
                    <div key={category} className="border-b border-gray-100 last:border-b-0">
                      {/* Category Header - Interactive */}
                      <button
                        onClick={() => toggleCategory(category)}
                        className={`w-full px-4 py-3 hover:bg-blue-50 transition-all flex items-center justify-between group border-l-4 ${colorClasses[meta.color]}`}
                      >
                        <div className="flex items-center gap-3 flex-1 text-left">
                          <span className="text-3xl transform group-hover:scale-110 transition-transform">{meta.emoji}</span>
                          <div>
                            <div className="font-bold text-sm text-gray-900 group-hover:text-gray-950">
                              {meta.title}
                            </div>
                            <div className="text-xs text-gray-600">
                              {items.length} dataset{items.length !== 1 ? 's' : ''}
                            </div>
                          </div>
                        </div>
                        <ChevronDown 
                          size={18} 
                          className={`text-gray-600 group-hover:text-gray-900 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`}
                        />
                      </button>

                      {/* Dataset Items - Beautiful List */}
                      {isExpanded && (
                        <div className="bg-gradient-to-b from-gray-50 to-white border-t border-gray-100">
                          {items.map((dataset, index) => (
                            <button
                              key={dataset}
                              onClick={() => {
                                onSelect(dataset);
                                setIsOpen(false);
                                setSearchTerm('');
                              }}
                              className={`w-full text-left px-6 py-2 transition-all flex items-center justify-between group font-medium border-l-4 text-sm ${
                                selectedDataset === dataset
                                  ? 'bg-gradient-to-r from-blue-200 to-indigo-200 text-blue-900 shadow-sm border-l-blue-600'
                                  : 'text-gray-700 border-l-transparent hover:bg-blue-50 hover:border-l-blue-400'
                              } ${index === items.length - 1 ? '' : 'border-b border-gray-100'}`}
                            >
                              <div className="flex items-center gap-2 flex-1">
                                <Database 
                                  size={16} 
                                  className={selectedDataset === dataset ? 'text-blue-700' : 'text-blue-600 group-hover:text-blue-700'} 
                                />
                                <span>{dataset}</span>
                              </div>
                              {selectedDataset === dataset && (
                                <span className="text-lg">✓</span>
                              )}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })
              ) : (
                <div className="p-8 text-center">
                  <Database size={40} className="mx-auto mb-2 text-gray-300" />
                  <p className="text-sm font-semibold text-gray-500">No datasets found</p>
                  <p className="text-xs text-gray-400 mt-1">Try: "{searchTerm}"</p>
                </div>
              )}
            </div>

            {/* Footer Stats */}
            <div className="bg-gradient-to-r from-gray-100 to-gray-50 px-4 py-2 border-t border-gray-200 flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-700">
                  📈 {filteredHierarchical ? Object.values(filteredHierarchical).flat().length : 0} matching
                </span>
              </div>
              <span className="font-semibold text-blue-600">
                Total: {flatDatasets.length}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
