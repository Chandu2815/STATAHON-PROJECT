import React, { useMemo } from 'react';
import { X, Filter as FilterIcon, ChevronDown } from 'lucide-react';

export default function FiltersPanel({
  columns,
  selectedColumns,
  data,
  filters,
  onChange,
}) {
  const filterableColumns = columns.filter((col) =>
    selectedColumns.includes(col.name)
  );

  // Extract unique values from data for each column
  const uniqueValues = useMemo(() => {
    const values = {};
    filterableColumns.forEach((column) => {
      const unique = [...new Set(
        data
          .map((row) => row[column.name])
          .filter((val) => val !== null && val !== undefined && val !== '')
      )].sort();
      values[column.name] = unique;
    });
    return values;
  }, [data, filterableColumns]);

  const handleFilterChange = (columnName, value) => {
    const newFilters = { ...filters };
    if (value === '') {
      delete newFilters[columnName];
    } else {
      newFilters[columnName] = value;
    }
    onChange(newFilters);
  };

  const handleClearAll = () => {
    onChange({});
  };

  return (
    <div className="overflow-hidden">
      {/* Header */}
      <div className="pb-4 border-b border-gray-300 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gray-200 rounded">
            <FilterIcon size={20} className="text-gray-700" />
          </div>
          <div>
            <label className="text-sm font-bold text-gray-900 block">
              Filter Data
            </label>
            <p className="text-xs text-gray-600">
              Select values to narrow results
            </p>
          </div>
        </div>
        {Object.keys(filters).length > 0 && (
          <button
            onClick={handleClearAll}
            className="text-xs font-bold text-gray-700 hover:text-gray-900 px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded transition"
          >
            Clear Filters
          </button>
        )}
      </div>

      <div className="pt-5">
        {filterableColumns.length === 0 ? (
          <div className="text-center py-8 bg-gray-50 rounded">
            <p className="text-gray-700 font-medium">No filters available</p>
            <p className="text-gray-600 text-xs">Select columns to add filters</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filterableColumns.map((column) => (
                <div key={column.name} className="space-y-2">
                  <label className="text-xs font-bold text-gray-900 uppercase tracking-wide block">
                    {column.name}
                  </label>
                  <div className="relative">
                    <select
                      value={filters[column.name] || ''}
                      onChange={(e) => handleFilterChange(column.name, e.target.value)}
                      className="w-full px-4 py-2 border border-gray-400 rounded text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-900 focus:border-blue-900 appearance-none pr-8 bg-white hover:border-gray-500 transition cursor-pointer"
                    >
                      <option value="">-- Select value --</option>
                      {(uniqueValues[column.name] || []).map((value, idx) => (
                        <option key={idx} value={value}>
                          {String(value).substring(0, 50)}
                        </option>
                      ))}
                    </select>
                    <ChevronDown
                      size={16}
                      className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-600 pointer-events-none"
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Active Filters Summary */}
            {Object.keys(filters).length > 0 && (
              <div className="mt-6 pt-4 border-t border-gray-300">
                <p className="text-xs font-bold text-gray-900 mb-3 uppercase tracking-wide">Active Filters:</p>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(filters).map(([key, value]) => (
                    <div
                      key={key}
                      className="inline-flex items-center gap-2 bg-gray-200 text-gray-900 rounded text-xs font-semibold px-3 py-1.5 border border-gray-400"
                    >
                      <span>{key}: {value}</span>
                      <button
                        onClick={() => handleFilterChange(key, '')}
                        className="hover:text-gray-700 font-bold"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
