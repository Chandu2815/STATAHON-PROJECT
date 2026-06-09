import React, { useMemo, useCallback } from 'react';
import { Filter as FilterIcon, ChevronDown, AlertCircle } from 'lucide-react';

const distinctOptionsCache = new Map();
const referenceDataCache = new Map();

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
  const [loadingDistinct, setLoadingDistinct] = React.useState({});
  const [filterErrors, setFilterErrors] = React.useState({});
  const isEconomicCensus = selectedDataset?.startsWith('economic_census.');

  // ── Reference data (states / districts / NIC codes) — fetch once ──
  React.useEffect(() => {
    if (!selectedDataset) return;

    const referenceKey = isEconomicCensus ? 'economic_census' : 'default';
    if (referenceDataCache.has(referenceKey)) {
      setReferenceData(referenceDataCache.get(referenceKey));
      return;
    }

    let cancelled = false;
    const fetchReferences = async () => {
      try {
        const statesUrl = isEconomicCensus ? '/api/ai/reference/ec/states' : '/api/ai/reference/states';
        const districtsUrl = isEconomicCensus ? '/api/ai/reference/ec/districts' : null;
        const [statesRes, districtsRes] = await Promise.all([
          fetch(statesUrl).then((r) => r.json()),
          districtsUrl ? fetch(districtsUrl).then((r) => r.json()) : Promise.resolve({ success: true, data: [] }),
        ]);
        const refs = {
          states: statesRes.success ? statesRes.data : [],
          districts: districtsRes.success ? districtsRes.data : [],
          nicCodes: [],
        };
        referenceDataCache.set(referenceKey, refs);
        if (!cancelled) setReferenceData(refs);
      } catch (err) {
        console.error('Failed to fetch reference data:', err);
        if (!cancelled) {
          setFilterErrors(prev => ({...prev, reference: 'Failed to load reference data'}));
        }
      }
    };
    fetchReferences();
    return () => {
      cancelled = true;
    };
  }, [selectedDataset, isEconomicCensus]);

  // ── Distinct values for every non-reference column ──
  //    Loaded once per dataset/column and cached so selections do not reload the grid.
  React.useEffect(() => {
    if (!selectedDataset || !filterableColumnNames) return;

    const colNames = filterableColumnNames.split(',').filter(Boolean);
    const REFERENCE_COLS = isEconomicCensus ? ['state_code', 'district_code'] : [];
    const colsToFetch = colNames.filter((n) => !REFERENCE_COLS.includes(n.toLowerCase()));
    const missingCols = colsToFetch.filter((col) => !distinctOptionsCache.has(`${selectedDataset}:${col}`));

    const cachedValues = {};
    colsToFetch.forEach((col) => {
      const cached = distinctOptionsCache.get(`${selectedDataset}:${col}`);
      if (cached) cachedValues[col] = cached;
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
      missingCols.forEach(col => newLoadingState[col] = true);
      setLoadingDistinct(prev => ({ ...prev, ...newLoadingState }));
      
      const results = {};
      
      await Promise.all(
        missingCols.map(async (colName) => {
          try {
            const url = `/api/ai/distinct/${selectedDataset}/${colName}?limit=10000`;
            const res = await fetch(url).then((r) => r.json());
            
            if (!cancelled && res.success) {
              results[colName] = res.data.map((v) => ({
                value: v,
                label: String(v).substring(0, 80),
              }));
              distinctOptionsCache.set(`${selectedDataset}:${colName}`, results[colName]);
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
  }, [selectedDataset, filterableColumnNames, isEconomicCensus]);

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
      console.log(`[Filter Change] ${columnName} = ${value}`, newFilters);
      onChange(newFilters);
    },
    [filters, onChange]
  );

  const handleClearAll = useCallback(() => {
    console.log('[Filter] Clearing all filters');
    onChange({});
  }, [onChange]);

  // Get available options for a filter column
  const getFilterOptions = (columnName) => {
    let options = [];

    if (isEconomicCensus && columnName.toLowerCase() === 'state_code') {
      options = referenceData.states.map((s) => ({
        value: s.state_code,
        label: `${s.state_code} - ${s.state_name}`,
      }));
    } else if (isEconomicCensus && columnName.toLowerCase() === 'district_code') {
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
        distinctValues[columnName] &&
        distinctValues[columnName].length > 0
      ) {
        options = distinctValues[columnName];
      } else {
        options = (uniqueValues[columnName] || []).map((val) => ({
          value: val,
          label: String(val).substring(0, 80),
        }));
      }
    }

    return options;
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
                const displayName = column.name.replace(/_/g, ' ').toUpperCase();

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
                        disabled={isLoading}
                        className={`w-full px-4 py-2 border rounded text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-900 focus:border-blue-900 appearance-none pr-8 bg-white hover:border-gray-500 transition cursor-pointer ${
                          isLoading ? 'opacity-50 cursor-not-allowed' : ''
                        } ${hasError ? 'border-red-300 bg-red-50' : 'border-gray-400'}`}
                      >
                        <option value="">
                          {isLoading 
                            ? '-- Loading...' 
                            : hasError 
                            ? '-- Error loading'
                            : `-- Select ${column.name.replace(/_/g, ' ')} --`}
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
