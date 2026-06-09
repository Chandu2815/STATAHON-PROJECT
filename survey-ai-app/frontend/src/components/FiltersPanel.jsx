import React, { useMemo, useCallback } from 'react';
import { X, Filter as FilterIcon, ChevronDown } from 'lucide-react';

export default function FiltersPanel({
  columns,
  selectedColumns,
  data,
  filters,
  onChange,
  selectedDataset,
}) {
  // Memoize filterable columns so the reference is stable across renders
  const filterableColumns = useMemo(
    () => columns.filter((col) => selectedColumns.includes(col.name)),
    [columns, selectedColumns]
  );

  // Serialized column-name list for use as a stable useEffect dependency
  const filterableColumnNames = useMemo(
    () => filterableColumns.map((c) => c.name).join(','),
    [filterableColumns]
  );

  const [referenceData, setReferenceData] = React.useState({
    states: [],
    districts: [],
    nicCodes: [],
  });
  const [distinctValues, setDistinctValues] = React.useState({});
  const [loadingDistinct, setLoadingDistinct] = React.useState(false);

  // ── Reference data (states / districts / NIC codes) — fetch once ──
  React.useEffect(() => {
    const fetchReferences = async () => {
      try {
        const [statesRes, districtsRes, nicRes] = await Promise.all([
          fetch('/api/ai/reference/ec/states').then((r) => r.json()),
          fetch('/api/ai/reference/ec/districts').then((r) => r.json()),
          fetch('/api/ai/reference/ec/nic-codes').then((r) => r.json()),
        ]);
        setReferenceData({
          states: statesRes.success ? statesRes.data : [],
          districts: districtsRes.success ? districtsRes.data : [],
          nicCodes: nicRes.success ? nicRes.data : [],
        });
      } catch (err) {
        console.error('Failed to fetch reference data:', err);
      }
    };
    fetchReferences();
  }, []);

  // ── Distinct values for every non-reference column ──
  //    Re-runs when the dataset or the list of selected columns changes.
  React.useEffect(() => {
    if (!selectedDataset || !filterableColumnNames) return;

    const colNames = filterableColumnNames.split(',').filter(Boolean);
    // Skip columns that are covered by dedicated reference tables
    const REFERENCE_COLS = ['state_code', 'district_code'];
    const colsToFetch = colNames.filter((n) => !REFERENCE_COLS.includes(n));

    if (colsToFetch.length === 0) {
      setDistinctValues({});
      return;
    }

    let cancelled = false;
    const fetchDistinct = async () => {
      setLoadingDistinct(true);
      const results = {};
      await Promise.all(
        colsToFetch.map(async (colName) => {
          try {
            const res = await fetch(
              `/api/ai/distinct/${selectedDataset}/${colName}`
            ).then((r) => r.json());
            if (!cancelled && res.success) {
              results[colName] = res.data.map((v) => ({
                value: v,
                label: String(v),
              }));
            }
          } catch (e) {
            console.error(`Failed distinct for ${colName}:`, e);
          }
        })
      );
      if (!cancelled) {
        setDistinctValues(results);
        setLoadingDistinct(false);
      }
    };
    fetchDistinct();

    return () => {
      cancelled = true;
    };
  }, [selectedDataset, filterableColumnNames]);

  // ── Local unique-value fallback (computed from current data) ──
  const uniqueValues = useMemo(() => {
    const values = {};
    filterableColumns.forEach((column) => {
      if (['state_code', 'district_code'].includes(column.name)) return;
      const unique = [
        ...new Set(
          data
            .map((row) => row[column.name])
            .filter((val) => val !== null && val !== undefined && val !== '')
        ),
      ].sort();
      values[column.name] = unique;
    });
    return values;
  }, [data, filterableColumns]);

  // ── Handlers ──
  const handleFilterChange = useCallback(
    (columnName, value) => {
      const newFilters = { ...filters };
      if (value === '') {
        delete newFilters[columnName];
      } else {
        newFilters[columnName] = value;
      }
      onChange(newFilters);
    },
    [filters, onChange]
  );

  const handleClearAll = useCallback(() => {
    onChange({});
  }, [onChange]);

  // ── Render ──
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
            {loadingDistinct && (
              <p className="text-xs text-gray-400 italic animate-pulse">
                Loading filter options…
              </p>
            )}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filterableColumns.map((column) => {
                let options = [];

                if (column.name === 'state_code') {
                  options = referenceData.states.map((s) => ({
                    value: s.state_code,
                    label: `${s.state_code} - ${s.state_name}`,
                  }));
                } else if (column.name === 'district_code') {
                  const filteredDistricts = filters['state_code']
                    ? referenceData.districts.filter(
                        (d) =>
                          String(d.state_code) ===
                          String(filters['state_code'])
                      )
                    : referenceData.districts;
                  options = filteredDistricts.map((d) => ({
                    value: d.district_code,
                    label: `${d.district_code} - ${d.district_name}`,
                  }));
                } else {
                  // Prefer distinct values from backend; fall back to local unique values
                  if (
                    distinctValues[column.name] &&
                    distinctValues[column.name].length > 0
                  ) {
                    options = distinctValues[column.name];
                  } else {
                    options = (uniqueValues[column.name] || []).map((val) => ({
                      value: val,
                      label: String(val).substring(0, 80),
                    }));
                  }
                }

                return (
                  <div key={column.name} className="space-y-2">
                    <label className="text-xs font-bold text-gray-900 uppercase tracking-wide block">
                      {column.name.replace(/_/g, ' ')}
                    </label>
                    <div className="relative">
                      <select
                        value={filters[column.name] || ''}
                        onChange={(e) =>
                          handleFilterChange(column.name, e.target.value)
                        }
                        className="w-full px-4 py-2 border border-gray-400 rounded text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-900 focus:border-blue-900 appearance-none pr-8 bg-white hover:border-gray-500 transition cursor-pointer"
                      >
                        <option value="">
                          -- Select {column.name.replace(/_/g, ' ')} --
                        </option>
                        {options.map((opt, idx) => (
                          <option key={idx} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                      </select>
                      <ChevronDown
                        size={16}
                        className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-600 pointer-events-none"
                      />
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Active Filters Summary */}
            {Object.keys(filters).length > 0 && (
              <div className="mt-6 pt-4 border-t border-gray-300">
                <p className="text-xs font-bold text-gray-900 mb-3 uppercase tracking-wide">
                  Active Filters:
                </p>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(filters).map(([key, value]) => (
                    <div
                      key={key}
                      className="inline-flex items-center gap-2 bg-gray-200 text-gray-900 rounded text-xs font-semibold px-3 py-1.5 border border-gray-400"
                    >
                      <span>
                        {key.replace(/_/g, ' ')}: {value}
                      </span>
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
