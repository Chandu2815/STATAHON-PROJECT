import React from 'react';
import { Check } from 'lucide-react';

export default function ColumnSelector({
  columns,
  selectedColumns,
  onSelect,
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      <label className="block text-sm font-semibold text-gray-700 mb-4">
        Columns ({selectedColumns.length}/{columns.length})
      </label>

      {columns.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500">Select a dataset first</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {columns.map((column) => (
            <button
              key={column.name}
              onClick={() => onSelect(column.name)}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg border-2 transition text-sm font-medium ${
                selectedColumns.includes(column.name)
                  ? 'border-blue-600 bg-blue-50 text-blue-700'
                  : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
              }`}
            >
              {selectedColumns.includes(column.name) && (
                <Check size={16} />
              )}
              <span className="truncate">{column.name}</span>
              <span className="text-xs opacity-60">({column.type.split('(')[0]})</span>
            </button>
          ))}
        </div>
      )}

      {/* Info */}
      <p className="text-xs text-gray-500 mt-4">
        Select columns to display in the data table
      </p>
    </div>
  );
}
