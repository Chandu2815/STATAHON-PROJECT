import React, { useState } from 'react';
import { 
  ChevronLeft, 
  ChevronRight, 
  Search, 
  CheckSquare, 
  Square,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Info,
  Filter
} from 'lucide-react';

/**
 * DataTable - Professional SaaS UI
 * high-performance data grid with advanced sorting and selection
 */
export default function DataTable({
  columns,
  data,
  pagination,
  onPageChange,
  onPageSizeChange,
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState(null);
  const [selectedRows, setSelectedRows] = useState(new Set());

  const filteredData = data.filter((row) =>
    Object.values(row).some((val) =>
      String(val).toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  const sortedData = [...filteredData];
  if (sortConfig) {
    sortedData.sort((a, b) => {
      const aVal = a[sortConfig.key];
      const bVal = b[sortConfig.key];

      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortConfig.direction === 'asc' ? aVal - bVal : bVal - aVal;
      }

      return sortConfig.direction === 'asc'
        ? String(aVal).localeCompare(String(bVal))
        : String(bVal).localeCompare(String(aVal));
    });
  }

  const handleSort = (key) => {
    setSortConfig((prev) => {
      if (prev?.key === key) {
        return {
          key,
          direction: prev.direction === 'asc' ? 'desc' : 'asc',
        };
      }
      return { key, direction: 'asc' };
    });
  };

  const handleRowSelect = (idx) => {
    const newSelected = new Set(selectedRows);
    if (newSelected.has(idx)) {
      newSelected.delete(idx);
    } else {
      newSelected.add(idx);
    }
    setSelectedRows(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedRows.size === sortedData.length) {
      setSelectedRows(new Set());
    } else {
      setSelectedRows(new Set(sortedData.map((_, idx) => idx)));
    }
  };

  const pageSizeOptions = [12, 24, 48, 96];

  return (
    <div className="flex flex-col h-full">
      {/* Table Management Bar */}
      <div className="px-6 py-4 border-b border-gray-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="relative group">
            <Search
              size={16}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-blue-500 transition-colors"
            />
            <input
              type="text"
              placeholder="Search current slice..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 bg-gray-50 border-none rounded-xl text-xs font-medium focus:ring-2 focus:ring-blue-500/20 transition-all w-full md:w-64"
            />
          </div>
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-gray-50 rounded-lg border border-transparent text-[10px] font-black text-gray-400 uppercase tracking-widest">
            <Filter size={12} />
            {filteredData.length} Results
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Rows per page</span>
          <select
            value={pagination.pageSize}
            onChange={(e) => onPageSizeChange(Number(e.target.value))}
            className="appearance-none bg-gray-50 px-4 py-2 border-none rounded-xl text-xs font-black text-blue-600 focus:ring-2 focus:ring-blue-500/20 cursor-pointer text-center"
          >
            {pageSizeOptions.map((size) => (
              <option key={size} value={size}>{size}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Grid Canvas */}
      <div className="flex-1 overflow-x-auto min-h-[400px]">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50/50">
              <th className="sticky top-0 z-10 px-6 py-4 border-b border-gray-100 bg-gray-50/50 backdrop-blur w-12">
                <button
                  onClick={handleSelectAll}
                  className="w-5 h-5 flex items-center justify-center rounded border-2 border-gray-200 hover:border-blue-400 transition-colors"
                >
                  {selectedRows.size === sortedData.length ? (
                    <CheckSquare size={14} className="text-blue-600" />
                  ) : (
                    <div className={selectedRows.size > 0 ? 'w-2 h-0.5 bg-blue-600 rounded' : ''}></div>
                  )}
                </button>
              </th>
              {columns.map((col) => (
                <th
                  key={col}
                  onClick={() => handleSort(col)}
                  className="sticky top-0 z-10 px-6 py-4 border-b border-gray-100 bg-gray-50/50 backdrop-blur cursor-pointer group"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest group-hover:text-gray-900 transition-colors">
                      {col}
                    </span>
                    <div className={`transition-opacity duration-300 ${sortConfig?.key === col ? 'opacity-100' : 'opacity-0 group-hover:opacity-40'}`}>
                      {sortConfig?.key === col ? (
                        sortConfig.direction === 'asc' ? <ArrowUp size={12} className="text-blue-600" /> : <ArrowDown size={12} className="text-blue-600" />
                      ) : (
                        <ArrowUpDown size={12} />
                      )}
                    </div>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {sortedData.length > 0 ? sortedData.map((row, idx) => (
              <tr
                key={idx}
                className={`group transition-all duration-200 ${
                  selectedRows.has(idx) 
                    ? 'bg-blue-50/30' 
                    : 'hover:bg-gray-50/50'
                }`}
              >
                <td className="px-6 py-4 border-b border-gray-50">
                  <button
                    onClick={() => handleRowSelect(idx)}
                    className={`w-5 h-5 flex items-center justify-center rounded border-2 transition-all ${
                      selectedRows.has(idx) 
                        ? 'border-blue-500 bg-blue-500 text-white' 
                        : 'border-gray-200 hover:border-gray-400'
                    }`}
                  >
                    {selectedRows.has(idx) && <CheckSquare size={12} />}
                  </button>
                </td>
                {columns.map((col) => (
                  <td key={col} className="px-6 py-4 border-b border-gray-50">
                    <div className={`text-xs font-medium truncate max-w-[200px] ${selectedRows.has(idx) ? 'text-blue-900' : 'text-gray-600'}`}>
                      {String(row[col] || '-')}
                    </div>
                  </td>
                ))}
              </tr>
            )) : (
              <tr>
                <td colSpan={columns.length + 1} className="py-20 text-center">
                  <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gray-50 text-gray-300 mb-4 border border-gray-100">
                    <Info size={24} />
                  </div>
                  <h4 className="text-sm font-black text-gray-900 uppercase tracking-widest">No matching records</h4>
                  <p className="text-[10px] font-bold text-gray-400 mt-1">Adjust filters or search parameters</p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Command Bar */}
      <div className="px-8 py-6 border-t border-gray-100 flex items-center justify-between bg-white">
        <div className="flex items-center gap-4">
          <p className="text-[10px] font-bold text-gray-400 uppercase tracking-[.1em]">
            Showing <span className="text-gray-900 font-black">{pagination.page * pagination.pageSize + 1}</span> to <span className="text-gray-900 font-black">{Math.min((pagination.page + 1) * pagination.pageSize, sortedData.length)}</span> of <span className="text-gray-900 font-black">{sortedData.length}</span> entries
          </p>
          {selectedRows.size > 0 && (
            <div className="animate-in zoom-in duration-300 h-6 px-2 bg-blue-600 text-white text-[9px] font-black uppercase tracking-tighter flex items-center rounded-lg shadow-lg shadow-blue-200">
              {selectedRows.size} Selected
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onPageChange(Math.max(0, pagination.page - 1))}
            disabled={pagination.page === 0}
            className="w-10 h-10 flex items-center justify-center rounded-xl border border-gray-100 hover:border-blue-200 hover:bg-blue-50 disabled:opacity-30 disabled:hover:bg-white disabled:hover:border-gray-100 transition-all"
          >
            <ChevronLeft size={18} className="text-gray-400" />
          </button>
          
          <div className="px-4 h-10 flex items-center justify-center bg-gray-50 rounded-xl border border-transparent text-xs font-black text-gray-900 min-w-[100px]">
            PAGE {pagination.page + 1}
          </div>

          <button
            onClick={() => onPageChange(pagination.page + 1)}
            disabled={data.length < pagination.pageSize}
            className="w-10 h-10 flex items-center justify-center rounded-xl border border-gray-100 hover:border-blue-200 hover:bg-blue-50 disabled:opacity-30 disabled:hover:bg-white disabled:hover:border-gray-100 transition-all"
          >
            <ChevronRight size={18} className="text-gray-400" />
          </button>
        </div>
      </div>
    </div>
  );
}
