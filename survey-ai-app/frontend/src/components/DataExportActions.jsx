import React from 'react';
import { Download, FileJson, FileText, Copy } from 'lucide-react';

export default function DataExportActions({ data, selectedColumns, selectedDataset }) {
  const exportToCSV = () => {
    if (!data || data.length === 0) {
      alert('No data to export');
      return;
    }

    // Prepare CSV content
    const headers = selectedColumns;
    const csvRows = [headers.join(',')];

    data.forEach((row) => {
      const values = selectedColumns.map((col) => {
        const value = row[col];
        // Handle null, undefined, and values with commas/quotes
        if (value === null || value === undefined) return '';
        const stringValue = String(value);
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
          return `"${stringValue.replace(/"/g, '""')}"`;
        }
        return stringValue;
      });
      csvRows.push(values.join(','));
    });

    const csvContent = csvRows.join('\n');
    downloadFile(csvContent, `${selectedDataset}_export_${new Date().toISOString().slice(0, 10)}.csv`, 'text/csv');
  };

  const exportToJSON = () => {
    if (!data || data.length === 0) {
      alert('No data to export');
      return;
    }

    const filteredData = data.map((row) => {
      const obj = {};
      selectedColumns.forEach((col) => {
        obj[col] = row[col];
      });
      return obj;
    });

    const jsonContent = JSON.stringify(
      {
        metadata: {
          dataset: selectedDataset,
          columns: selectedColumns.length,
          rows: filteredData.length,
          exportedAt: new Date().toISOString(),
        },
        data: filteredData,
      },
      null,
      2
    );

    downloadFile(jsonContent, `${selectedDataset}_export_${new Date().toISOString().slice(0, 10)}.json`, 'application/json');
  };

  const copyToClipboard = () => {
    if (!data || data.length === 0) {
      alert('No data to copy');
      return;
    }

    const headers = selectedColumns;
    const rows = data.map((row) =>
      selectedColumns.map((col) => row[col] || '').join('\t')
    );

    const tsvContent = [headers.join('\t'), ...rows].join('\n');
    navigator.clipboard.writeText(tsvContent).then(() => {
      alert(`✅ Copied ${data.length} rows to clipboard!`);
    });
  };

  const downloadFile = (content, filename, mimeType) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  if (!data || data.length === 0) {
    return null;
  }

  return (
    <div className="flex gap-2 flex-wrap">
      <button
        onClick={exportToCSV}
        className="flex items-center gap-2 px-3 py-2 bg-green-600 text-white text-xs font-bold rounded hover:bg-green-700 transition"
        title="Download data as CSV file"
      >
        <Download size={14} />
        CSV ({data.length} rows)
      </button>
      <button
        onClick={exportToJSON}
        className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white text-xs font-bold rounded hover:bg-blue-700 transition"
        title="Download data as JSON file"
      >
        <FileJson size={14} />
        JSON
      </button>
      <button
        onClick={copyToClipboard}
        className="flex items-center gap-2 px-3 py-2 bg-gray-600 text-white text-xs font-bold rounded hover:bg-gray-700 transition"
        title="Copy data to clipboard as tab-separated values"
      >
        <Copy size={14} />
        Copy
      </button>
    </div>
  );
}
