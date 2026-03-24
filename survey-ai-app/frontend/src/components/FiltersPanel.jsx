import React, { useState } from 'react';
import { ChevronDown, X, Filter } from 'lucide-react';

export default function FiltersPanel({
  columns,
  selectedColumns,
  filters,
  onChange,
}) {
  const [expandedFilters, setExpandedFilters] = useState({});

  const filterableColumns = columns.filter((col) =>
    selectedColumns.includes(col.name)
  );

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

  const isPrimitive = (type) => {
    return ['integer', 'bigint', 'smallint', 'numeric', 'decimal', 'real', 'double'].includes(
      type.toLowerCase()
    );
  };

  const isText = (type) => {
    return ['character', 'varchar', 'text'].includes(type.toLowerCase());
  };

  const isDate = (type) => {
    return ['date', 'timestamp', 'time'].includes(type.toLowerCase());
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Filter size={18} className="text-blue-600" />
          <label className="text-sm font-semibold text-gray-700">
            Filters
          </label>
        </div>
        {Object.keys(filters).length > 0 && (
          <button
            onClick={handleClearAll}
            className="text-xs text-red-600 hover:text-red-700 flex items-center gap-1"
          >
            <X size={14} /> Clear All
          </button>
        )}
      </div>

      {filterableColumns.length === 0 ? (
        <p className="text-gray-500 text-sm">Select columns to add filters</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filterableColumns.map((column) => (
            <div key={column.name} className="border border-gray-200 rounded-lg p-3">
              <button
                onClick={() =>
                  setExpandedFilters({
                    ...expandedFilters,
                    [column.name]: !expandedFilters[column.name],
                  })
                }
                className="w-full flex items-center justify-between mb-2"
              >
                <span className="text-sm font-medium text-gray-700">
                  {column.name}
                </span>
                <ChevronDown
                  size={16}
                  className={`text-gray-600 transition ${
                    expandedFilters[column.name] ? 'rotate-180' : ''
                  }`}
                />
              </button>

              {expandedFilters[column.name] && (
                <div className="space-y-2">
                  {isPrimitive(column.type) ? (
                    // Range Filter for Numbers
                    <div className="space-y-1">
                      <input
                        type="number"
                        placeholder="Min value"
                        value={filters[column.name]?.min || ''}
                        onChange={(e) =>
                          handleFilterChange(column.name, {
                            ...filters[column.name],
                            min: e.target.value,
                          })
                        }
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <input
                        type="number"
                        placeholder="Max value"
                        value={filters[column.name]?.max || ''}
                        onChange={(e) =>
                          handleFilterChange(column.name, {
                            ...filters[column.name],
                            max: e.target.value,
                          })
                        }
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  ) : isText(column.type) || isDate(column.type) ? (
                    // Text/Date Filter
                    <input
                      type={isDate(column.type) ? 'date' : 'text'}
                      placeholder={`Filter by ${column.name}...`}
                      value={filters[column.name] || ''}
                      onChange={(e) => handleFilterChange(column.name, e.target.value)}
                      className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  ) : (
                    // Generic Text Filter
                    <input
                      type="text"
                      placeholder={`Filter by ${column.name}...`}
                      value={filters[column.name] || ''}
                      onChange={(e) => handleFilterChange(column.name, e.target.value)}
                      className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Active Filters Summary */}
      {Object.keys(filters).length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-xs font-medium text-gray-600 mb-2">Active Filters:</p>
          <div className="flex flex-wrap gap-2">
            {Object.entries(filters).map(([key, value]) => (
              <div
                key={key}
                className="inline-flex items-center gap-2 pd bg-blue-100 text-blue-800 rounded-full text-xs font-medium px-3 py-1"
              >
                <span>{key}: {JSON.stringify(value)}</span>
                <button
                  onClick={() => handleFilterChange(key, '')}
                  className="hover:text-blue-600"
                >
                  <X size={12} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
