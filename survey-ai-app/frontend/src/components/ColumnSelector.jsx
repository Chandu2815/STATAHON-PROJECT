import React from 'react';
import { Check, Square, CheckSquare2 } from 'lucide-react';

export default function ColumnSelector({
  columns,
  selectedColumns,
  onSelect,
}) {
  const handleSelectAll = () => {
    if (selectedColumns.length === columns.length) {
      // Deselect all
      // Don't do anything, user needs to click individual columns
    } else {
      // Select all
      columns.forEach(col => {
        if (!selectedColumns.includes(col.name)) {
          onSelect(col.name);
        }
      });
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <label className="block text-sm font-semibold text-gray-700">
          📋 Columns ({selectedColumns.length}/{columns.length})
        </label>
        {columns.length > 0 && (
          <button
            onClick={handleSelectAll}
            className="text-xs text-blue-600 hover:text-blue-700 font-medium"
          >
            {selectedColumns.length === columns.length ? 'Deselect All' : 'Select All'}
          </button>
        )}
      </div>

      {columns.length === 0 ? (
        <div className="text-center py-8 bg-gray-50 rounded-lg">
          <p className="text-gray-500 font-medium">Select a dataset first to see columns</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
            {columns.map((column) => {
              const isSelected = selectedColumns.includes(column.name);
              return (
                <button
                  key={column.name}
                  onClick={() => onSelect(column.name)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg border-2 transition text-left ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50 text-blue-900 shadow-md'
                      : 'border-gray-300 bg-white text-gray-700 hover:border-blue-400 hover:bg-blue-50'
                  }`}
                >
                  {isSelected ? (
                    <CheckSquare2 size={18} className="text-blue-600 flex-shrink-0" />
                  ) : (
                    <Square size={18} className="text-gray-400 flex-shrink-0" />
                  )}
                  <div className="flex-1 min-w-0">
                    <span className="font-medium truncate block">{column.name}</span>
                    <span className="text-xs opacity-60">{column.type.split('(')[0]}</span>
                  </div>
                </button>
              );
            })}
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-xs text-blue-800">
              ✓ <strong>Select columns</strong> above to display them in the data table
            </p>
          </div>
        </>
      )}
    </div>
  );
}
