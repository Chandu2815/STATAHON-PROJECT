import React, { useState } from 'react';
import { ChevronDown, Database } from 'lucide-react';
import DatasetSelector from './DatasetSelector.jsx';

/**
 * HierarchicalDatasetSelector
 * Wrapper around DatasetSelector for hierarchical dataset organization
 */
export default function HierarchicalDatasetSelector({ 
  datasets = [], 
  selectedDataset, 
  onSelect 
}) {
  // For now, this is a simple wrapper around DatasetSelector
  // Can be enhanced later for hierarchical grouping
  
  return (
    <DatasetSelector
      datasets={datasets}
      selectedDataset={selectedDataset}
      onSelect={onSelect}
    />
  );
}
