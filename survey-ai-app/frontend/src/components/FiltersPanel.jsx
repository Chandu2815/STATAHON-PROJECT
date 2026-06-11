import React, { useMemo, useCallback } from 'react';
import { Filter as FilterIcon, ChevronDown, AlertCircle } from 'lucide-react';

const distinctOptionsCache = new Map();

export default function FiltersPanel({
  columns,
  selectedColumns,
  data,
  filters,
  onChange,
  selectedDataset,
  uxProfile,
}) {
  const filterConfig = uxProfile?.filters || null;
  const columnByName = useMemo(
    () => Object.fromEntries(columns.map((col) => [col.name, col])),
    [columns]
  );

  // Memoize filterable columns so the reference is stable across renders
  const filterableColumns = useMemo(() => {
    if (filterConfig?.length) {
      return filterConfig
        .map((config) => ({
          ...(columnByName[config.name] || { name: config.name, type: 'unknown' }),
          ...config,
        }))
        .filter((col) => columnByName[col.name]);
    }
    return columns.filter((col) => selectedColumns.includes(col.name) && !col.hidden);
  }, [columns, selectedColumns, filterConfig, columnByName]);

  // Serialized column-name list for use as a stable useEffect dependency
  const filterableColumnNames = useMemo(
    () => filterableColumns.map((c) => c.name).join(','),
    [filterableColumns]
  );
  const filterLoadSignature = useMemo(
    () =>
      filterableColumns
        .map((column) => `${column.name}:${column.depends_on ? filters[column.depends_on] || '' : ''}`)
        .join('|'),
    [filterableColumns, filters]
  );

  const [distinctValues, setDistinctValues] = React.useState({});
  const [loadingDistinct, setLoadingDistinct] = React.useState({});
  const [filterErrors, setFilterErrors] = React.useState({});

  // ── Distinct values for every non-reference column ──
  //    Loaded once per dataset/column and cached so selections do not reload the grid.
  React.useEffect(() => {
    if (!selectedDataset || !filterableColumnNames) return;

    const columnsToLoad = filterableColumns.filter((column) => !column.depends_on || filters[column.depends_on]);
    const skippedCols = filterableColumns
      .filter((column) => column.depends_on && !filters[column.depends_on])
      .map((column) => column.name);
    if (skippedCols.length > 0) {
      setLoadingDistinct(prev => {
        const next = { ...prev };
        skippedCols.forEach((col) => {
          next[col] = false;
        });
        return next;
      });
    }

    const cacheKeyFor = (column) => {
      const parentPart = column.depends_on ? `${column.depends_on}=${filters[column.depends_on] || ''}` : 'base';
      return `${selectedDataset}:${column.name}:${parentPart}`;
    };
    const missingCols = columnsToLoad.filter((column) => !distinctOptionsCache.has(cacheKeyFor(column)));

    const cachedValues = {};
    columnsToLoad.forEach((column) => {
      const cached = distinctOptionsCache.get(cacheKeyFor(column));
      if (cached) cachedValues[column.name] = cached;
    });
    if (Object.keys(cachedValues).length > 0) {
      setDistinctValues(prev => ({ ...prev, ...cachedValues }));
    }

    if (missingCols.length === 0) {
      return;
    }

    let cancelled = false;
    const fetchDistinct = async () => {
      const newLoadingState = {};
      missingCols.forEach(column => newLoadingState[column.name] = true);
      setLoadingDistinct(prev => ({ ...prev, ...newLoadingState }));
      
      const results = {};
      
      await Promise.all(
        missingCols.map(async (column) => {
          const colName = column.name;
          try {
            const params = new URLSearchParams({ limit: '10000' });
            if (column.depends_on) {
              params.set('filters', JSON.stringify({ [column.depends_on]: filters[column.depends_on] }));
            }
            const url = `/api/ai/distinct/${selectedDataset}/${colName}?${params.toString()}`;
            const res = await fetch(url).then((r) => r.json());
            
            if (!cancelled && res.success) {
              results[colName] = res.data.map((v) => {
                if (v && typeof v === 'object' && Object.prototype.hasOwnProperty.call(v, 'value')) {
                  return {
                    value: v.value,
                    label: String(v.label ?? v.value).substring(0, 120),
                  };
                }
                return {
                  value: v,
                  label: String(v).substring(0, 80),
                };
              });
              distinctOptionsCache.set(cacheKeyFor(column), results[colName]);
              console.log(`[Filter] ${colName}: ${results[colName].length} options`);
            } else if (!cancelled) {
              setFilterErrors(prev => ({...prev, [colName]: res.error || 'Failed to load'}));
            }
          } catch (e) {
            if (!cancelled) {
              console.error(`Failed distinct for ${colName}:`, e);
              setFilterErrors(prev => ({...prev, [colName]: 'Network error'}));
            }
          } finally {
            if (!cancelled) {
              setLoadingDistinct(prev => ({...prev, [colName]: false}));
            }
          }
        })
      );
      
      if (!cancelled) {
        setDistinctValues(prev => ({ ...prev, ...results }));
      }
    };
    
    fetchDistinct();

    return () => {
      cancelled = true;
    };
  }, [selectedDataset, filterableColumnNames, filterLoadSignature]);

  // ── Local unique-value fallback (computed from current data) ──
  const uniqueValues = useMemo(() => {
    const values = {};
    filterableColumns.forEach((column) => {
      if (['state_code', 'district_code'].includes(column.name.toLowerCase())) return;
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
      const changedColumn = filterableColumns.find((col) => col.name === columnName);
      (changedColumn?.cascades_to || []).forEach((child) => {
        delete newFilters[child];
      });
      console.log(`[Filter Change] ${columnName} = ${value}`, newFilters);
      onChange(newFilters);
    },
    [filters, onChange, filterableColumns]
  );

  const handleClearAll = useCallback(() => {
    console.log('[Filter] Clearing all filters');
    onChange({});
  }, [onChange]);

  // Get available options for a filter column
  const getFilterOptions = (columnName) => {
    if (distinctValues[columnName] && distinctValues[columnName].length > 0) {
      return distinctValues[columnName];
    }

    return (uniqueValues[columnName] || []).map((val) => ({
      value: val,
      label: String(val).substring(0, 80),
    }));
  };

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
        {filterErrors.reference && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-xs text-red-700 flex items-start gap-2">
            <AlertCircle size={14} className="mt-0.5 shrink-0" />
            <span>{filterErrors.reference}</span>
          </div>
        )}

        {filterableColumns.length === 0 ? (
          <div className="text-center py-8 bg-gray-50 rounded">
            <p className="text-gray-700 font-medium">No filters available</p>
            <p className="text-gray-600 text-xs">Select columns to add filters</p>
          </div>
        ) : (
          <div className="space-y-4">
            {Object.keys(loadingDistinct).some(col => loadingDistinct[col]) && (
              <p className="text-xs text-gray-400 italic animate-pulse">
                Loading filter options…
              </p>
            )}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filterableColumns.map((column) => {
                const options = getFilterOptions(column.name);
                const isLoading = loadingDistinct[column.name] || false;
                const hasError = filterErrors[column.name];
                const displayName = (column.label || column.name.replace(/_/g, ' ')).toUpperCase();
                const parentMissing = column.depends_on && !filters[column.depends_on];

                return (
                  <div key={column.name} className="space-y-2">
                    <label className="text-xs font-bold text-gray-900 uppercase tracking-wide flex items-center justify-between">
                      <span>{displayName}</span>
                      {isLoading && <span className="text-[10px] text-gray-400 font-normal">Loading...</span>}
                    </label>
                    <div className="relative">
                      <select
                        value={filters[column.name] || ''}
                        onChange={(e) =>
                          handleFilterChange(column.name, e.target.value)
                        }
                        disabled={isLoading || parentMissing}
                        className={`w-full px-4 py-2 border rounded text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-900 focus:border-blue-900 appearance-none pr-8 bg-white hover:border-gray-500 transition cursor-pointer ${
                          isLoading ? 'opacity-50 cursor-not-allowed' : ''
                        } ${hasError ? 'border-red-300 bg-red-50' : 'border-gray-400'}`}
                      >
                        <option value="">
                          {isLoading 
                            ? '-- Loading...' 
                            : parentMissing
                            ? `-- Select ${(columnByName[column.depends_on]?.label || column.depends_on).replace(/_/g, ' ')} first`
                            : hasError 
                            ? '-- Error loading'
                            : `-- Select ${column.label || column.name.replace(/_/g, ' ')} --`}
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
                    {hasError && (
                      <p className="text-[10px] text-red-600 flex items-start gap-1">
                        <AlertCircle size={12} className="mt-0.5 shrink-0" />
                        {hasError}
                      </p>
                    )}
                    {filters[column.name] && (
                      <p className="text-[10px] text-blue-600 font-medium">
                        ✓ Selected: {filters[column.name]}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Active Filters Summary */}
            {Object.keys(filters).length > 0 && (
              <div className="mt-6 pt-4 border-t border-gray-300">
                <p className="text-xs font-bold text-gray-900 mb-3 uppercase tracking-wide">
                  Active Filters: {Object.keys(filters).length}
                </p>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(filters).map(([key, value]) => (
                    <div
                      key={key}
                      className="inline-flex items-center gap-2 bg-blue-50 text-blue-900 rounded text-xs font-semibold px-3 py-1.5 border border-blue-200"
                    >
                      <span>
                        {key.replace(/_/g, ' ')}: {value}
                      </span>
                      <button
                        onClick={() => handleFilterChange(key, '')}
                        className="hover:text-blue-700 font-bold text-blue-600"
                        title="Remove this filter"
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
