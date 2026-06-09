import React, { useState } from 'react';
import { Download, Share2, FileJson, FileText, Copy, Check } from 'lucide-react';

/**
 * DataExportActions
 * Export/Share functionality for query results
 */
export default function DataExportActions({ 
  data = [], 
  selectedColumns = [], 
  selectedDataset = '' 
}) {
  const [copied, setCopied] = useState(false);

  const exportAsJSON = () => {
    const jsonStr = JSON.stringify(data, null, 2);
    const element = document.createElement('a');
    element.setAttribute('href', 'data:application/json;charset=utf-8,' + encodeURIComponent(jsonStr));
    element.setAttribute('download', `${selectedDataset}_export_${Date.now()}.json`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const exportAsCSV = () => {
    let csv = selectedColumns.join(',') + '\n';
    data.forEach(row => {
      csv += selectedColumns.map(col => {
        const value = row[col];
        return typeof value === 'string' && value.includes(',') 
          ? `"${value}"` 
          : value;
      }).join(',') + '\n';
    });
    
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv));
    element.setAttribute('download', `${selectedDataset}_export_${Date.now()}.csv`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const copyToClipboard = () => {
    const text = JSON.stringify(data, null, 2);
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="flex flex-wrap gap-3">
      <button
        onClick={exportAsJSON}
        className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition text-sm font-medium"
        title="Download data as JSON"
      >
        <FileJson size={16} />
        Export as JSON
      </button>

      <button
        onClick={exportAsCSV}
        className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition text-sm font-medium"
        title="Download data as CSV"
      >
        <FileText size={16} />
        Export as CSV
      </button>

      <button
        onClick={copyToClipboard}
        className="inline-flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition text-sm font-medium"
        title="Copy to clipboard"
      >
        {copied ? (
          <>
            <Check size={16} />
            Copied!
          </>
        ) : (
          <>
            <Copy size={16} />
            Copy JSON
          </>
        )}
      </button>
    </div>
  );
}
