import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Search, CheckSquare, Square } from 'lucide-react';

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

  const pageSizeOptions = [10, 25, 50, 100];

  return (
    <div className="rounded-lg overflow-hidden">
      {/* Table Header with Search */}
      <div className="p-5 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-bold text-gray-800 flex items-center gap-2">
            📋 Data Preview
          </h3>
          <span className="text-xs font-semibold px-3 py-1 bg-blue-100 text-blue-700 rounded-full">
            {filteredData.length} row{filteredData.length !== 1 ? 's' : ''}
          </span>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search
            size={18}
            className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
          />
          <input
            type="text"
            placeholder="🔎 Search in table..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition bg-white"
          />
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto bg-white">
        {filteredData.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-gray-500 font-medium">No data to display</p>
            <p className="text-gray-400 text-sm mt-1">Try adjusting your filters or selections</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gradient-to-r from-blue-50 to-blue-25 border-b-2 border-blue-200 sticky top-0">
              <tr>
                <th className="px-4 py-3 text-left">
                  <button
                    onClick={handleSelectAll}
                    className="hover:opacity-70 transition p-1"
                    title="Select all rows"
                  >
                    {selectedRows.size === sortedData.length ? (
                      <CheckSquare size={18} className="text-blue-600" />
                    ) : (
                      <Square size={18} className="text-gray-400" />
                    )}
                  </button>
                </th>
                {columns.map((col) => (
                  <th
                    key={col}
                    onClick={() => handleSort(col)}
                    className="px-6 py-3 text-left font-bold text-gray-700 cursor-pointer hover:bg-blue-100 transition whitespace-nowrap"
                    title={`Click to sort by ${col}`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="truncate">{col}</span>
                      {sortConfig?.key === col && (
                        <span className="text-xs font-bold text-blue-600">
                          {sortConfig.direction === 'asc' ? '↑' : '↓'}
                        </span>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {sortedData.map((row, idx) => (
                <tr
                  key={idx}
                  className={`transition-all ${
                    selectedRows.has(idx) 
                      ? 'bg-blue-50 border-l-4 border-blue-600' 
                      : 'hover:bg-gray-50 border-l-4 border-transparent'
                  }`}
                >
                  <td className="px-4 py-3">
                    <button
                      onClick={() => handleRowSelect(idx)}
                      className="hover:opacity-70 transition p-1"
                    >
                      {selectedRows.has(idx) ? (
                        <CheckSquare size={18} className="text-blue-600" />
                      ) : (
                        <Square size={18} className="text-gray-400" />
                      )}
                    </button>
                  </td>
                  {columns.map((col) => (
                    <td key={col} className="px-6 py-3 text-gray-700">
                      <div className="max-w-xs truncate font-medium">
                        {String(row[col] || '-').substring(0, 100)}
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      <div className="px-6 py-5 border-t border-gray-200 bg-gradient-to-r from-gray-50 to-white flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-700">Show</span>
            <select
              value={pagination.pageSize}
              onChange={(e) => onPageSizeChange(Number(e.target.value))}
              className="px-3 py-1.5 border-2 border-gray-200 rounded-lg text-sm font-medium focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition hover:border-gray-300 cursor-pointer"
            >
              {pageSizeOptions.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
            <span className="text-sm font-medium text-gray-700">rows per page</span>
          </div>
          {selectedRows.size > 0 && (
            <div className="text-sm font-bold text-blue-600 px-3 py-1.5 bg-blue-50 rounded-lg">
              ✓ {selectedRows.size} row{selectedRows.size !== 1 ? 's' : ''} selected
            </div>
          )}
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => onPageChange(Math.max(0, pagination.page - 1))}
            disabled={pagination.page === 0}
            className="p-2 border-2 border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-400 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-white disabled:hover:border-gray-200 transition font-bold"
            title="Previous page"
          >
            <ChevronLeft size={18} className="text-gray-600" />
          </button>

          <span className="text-sm font-bold text-gray-700 min-w-[120px] text-center px-3 py-1.5 bg-blue-50 rounded-lg">
            Page {pagination.page + 1}
          </span>

          <button
            onClick={() => onPageChange(pagination.page + 1)}
            disabled={data.length < pagination.pageSize}
            className="p-2 border-2 border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-400 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-white disabled:hover:border-gray-200 transition font-bold"
            title="Next page"
          >
            <ChevronRight size={18} className="text-gray-600" />
          </button>
        </div>
      </div>
    </div>
  );
}
