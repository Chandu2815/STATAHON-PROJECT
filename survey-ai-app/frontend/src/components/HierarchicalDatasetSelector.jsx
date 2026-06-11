import React, { useState, useMemo } from 'react';
import { 
  Database, 
  Search, 
  Layers, 
  PieChart, 
  TrendingUp, 
  FileText,
  BarChart3,
  Calendar,
  ChevronRight,
  ArrowLeft
} from 'lucide-react';

/**
 * HierarchicalDatasetSelector - Inline Premium Explorer
 * Robust, permanent hierarchy for a more "proper" structural layout
 */
export default function HierarchicalDatasetSelector({ 
  datasets = {}, 
  selectedDataset, 
  onSelect 
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeCategory, setActiveCategory] = useState(null); // null means show category list

  // Professional Category Metadata
  const getDatasetName = (item) => {
    if (typeof item === 'string') return item;
    if (item && typeof item === 'object' && item.name) return item.name;
    return String(item);
  };

  const getDatasetDisplayName = (item) => {
    if (typeof item === 'string') return item;
    if (item && typeof item === 'object') {
      return item.display_name || item.name || String(item);
    }
    return String(item);
  };

  const categoryMetadata = {
    Public: {
      icon: <FileText size={18} />,
      title: 'Public Datasets',
      subtitle: 'PUB',
      theme: 'text-sky-600',
      bg: 'bg-sky-50',
      accent: 'bg-sky-600'
    },
    'Economic Census': {
      icon: <BarChart3 size={18} />,
      title: 'Economic Census',
      subtitle: 'EC',
      theme: 'text-orange-600',
      bg: 'bg-orange-50',
      accent: 'bg-orange-600'
    },
    HCES: { 
      icon: <PieChart size={18} />, 
      title: 'Housing & Consumption',
      subtitle: 'HCES',
      theme: 'text-blue-600',
      bg: 'bg-blue-50',
      accent: 'bg-blue-600'
    },
    PLFS: { 
      icon: <TrendingUp size={18} />, 
      title: 'Labour & Employment',
      subtitle: 'PLFS',
      theme: 'text-emerald-600',
      bg: 'bg-emerald-50',
      accent: 'bg-emerald-600'
    },
    Other: { 
      icon: <Layers size={18} />, 
      title: 'Reference Materials',
      subtitle: 'Misc',
      theme: 'text-amber-600',
      bg: 'bg-amber-50',
      accent: 'bg-amber-600'
    },
  };

  const categories = Object.entries(datasets).filter(([_, items]) => items.length > 0);

  const filteredItems = useMemo(() => {
    if (!activeCategory) return [];
    return (datasets[activeCategory] || []).filter(item => 
      getDatasetName(item).toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [datasets, activeCategory, searchTerm]);

  // If a dataset is selected and we are in category view, we might want to highlight it
  // But let's focus on the navigation flow

  return (
    <div className="flex flex-col h-[450px] bg-white rounded-2xl overflow-hidden border border-gray-100 shadow-sm">
      
      {/* Dynamic Header / Breadcrumbs */}
      <div className="px-5 py-4 border-b border-gray-50 bg-gray-50/50 flex items-center justify-between">
        {activeCategory ? (
          <button 
            onClick={() => setActiveCategory(null)}
            className="flex items-center gap-2 group transition-all"
          >
            <div className="p-1 rounded-lg bg-white border border-gray-100 group-hover:border-blue-200 group-hover:text-blue-600 transition-all">
              <ArrowLeft size={14} />
            </div>
            <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest group-hover:text-gray-900 transition-colors">
              Categories
            </span>
            <ChevronRight size={12} className="text-gray-300" />
            <span className={`text-[10px] font-black uppercase tracking-widest ${categoryMetadata[activeCategory]?.theme || 'text-gray-900'}`}>
              {activeCategory}
            </span>
          </button>
        ) : (
          <div className="flex items-center gap-2">
            <Layers size={14} className="text-gray-400" />
            <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">
              Data Taxonomy
            </span>
          </div>
        )}
        
        <div className="text-[10px] font-bold text-gray-300 italic">
          {categories.length} Repositories
        </div>
      </div>

      {/* Global Search (Only in item view) */}
      {activeCategory && (
        <div className="px-5 py-3 border-b border-gray-50 bg-white">
          <div className="relative group">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-300 group-focus-within:text-blue-500 transition-colors" />
            <input 
              type="text"
              placeholder="Search in category..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-gray-50 border-none rounded-xl pl-9 pr-3 py-2 text-[11px] font-medium focus:ring-2 focus:ring-blue-500/20 transition-all placeholder-gray-400"
            />
          </div>
        </div>
      )}

      {/* Main Navigation View */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-3">
        {!activeCategory ? (
          /* Category List - Grid for better "Proper" look */
          <div className="grid grid-cols-1 gap-3 animate-in fade-in zoom-in duration-300">
            {categories.map(([cat, items]) => {
              const meta = categoryMetadata[cat] || { title: cat, theme: 'text-gray-600', bg: 'bg-gray-50', accent: 'bg-gray-600' };
              const isSelectedCategory = (datasets[cat] || []).some(
                (item) => getDatasetName(item) === selectedDataset
              );

              return (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  className={`w-full text-left p-4 rounded-2xl border-2 transition-all duration-300 flex items-center gap-4 group ${
                    isSelectedCategory 
                      ? 'border-blue-100 bg-blue-50/30' 
                      : 'border-transparent hover:border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-500 ${meta.bg} ${meta.theme} group-hover:scale-110 shadow-sm`}>
                    {meta.icon}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-black text-gray-900 uppercase tracking-tight">{meta.title}</h4>
                      <ChevronRight size={14} className="text-gray-300 group-hover:translate-x-1 transition-transform" />
                    </div>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="text-[10px] font-bold text-gray-400">{items.length} Datasets</span>
                      {isSelectedCategory && (
                        <span className="flex items-center gap-1 text-[9px] font-black text-blue-600 uppercase italic">
                          <div className="w-1 h-1 rounded-full bg-blue-600 animate-pulse"></div>
                          Active Source
                        </span>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        ) : (
          /* Items List */
          <div className="space-y-1.5 animate-in fade-in slide-in-from-right-4 duration-300">
            {filteredItems.length > 0 ? filteredItems.map((dataset) => {
              const datasetName = getDatasetName(dataset);
              return (
              <button
                key={datasetName}
                onClick={() => onSelect(datasetName)}
                className={`w-full text-left px-4 py-3 rounded-xl border transition-all duration-300 flex items-center justify-between group ${
                  selectedDataset === datasetName
                    ? 'bg-blue-600 border-blue-600 text-white shadow-lg shadow-blue-200'
                    : 'bg-white border-transparent hover:bg-gray-50 hover:border-gray-200 text-gray-700'
                }`}
              >
                <div className="flex items-center gap-3 truncate">
                  <Database size={14} className={selectedDataset === datasetName ? 'text-blue-100' : 'text-gray-400 group-hover:text-blue-500'} />
                  <div className="truncate">
                    <span className="block text-[11px] font-bold truncate">{getDatasetDisplayName(dataset)}</span>
                    <span className="block text-[9px] font-medium uppercase tracking-widest text-gray-400 truncate">{dataset.schema || activeCategory}</span>
                  </div>
                </div>
                {selectedDataset === datasetName && (
                  <div className="w-5 h-5 bg-white/20 rounded-full flex items-center justify-center">
                    <span className="text-[9px] font-black">✓</span>
                  </div>
                )}
              </button>
            );
            }) : (
              <div className="py-12 text-center">
                <div className="w-12 h-12 bg-gray-50 rounded-xl flex items-center justify-center mx-auto mb-3">
                  <Search className="text-gray-200" size={24} />
                </div>
                <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest">No matching datasets</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Selection Footer Stats */}
      <div className="px-5 py-3 border-t border-gray-50 bg-gray-50/30">
        {selectedDataset ? (
           <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-600"></div>
                <span className="text-[9px] font-black text-gray-900 uppercase tracking-[.1em] truncate max-w-[120px]">
                  {selectedDataset}
                </span>
              </div>
              <span className="text-[9px] font-bold text-gray-400 italic">Connected</span>
           </div>
        ) : (
          <div className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-gray-200"></div>
            <span className="text-[9px] font-bold text-gray-400 uppercase tracking-widest leading-none">
              Awaiting selection
            </span>
          </div>
        )}
      </div>
    </div>
  );
}


