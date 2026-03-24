import React, { useState } from 'react';
import { HelpCircle, X } from 'lucide-react';

export default function HelpAndShortcuts() {
  const [showHelp, setShowHelp] = useState(false);

  const shortcuts = [
    { key: 'Ctrl + S', action: 'Save current analysis' },
    { key: 'Ctrl + E', action: 'Export data' },
    { key: 'Ctrl + F', action: 'Search datasets' },
    { key: 'Ctrl + K', action: 'Clear filters' },
    { key: 'Ctrl + C', action: 'Copy selected data' },
    { key: 'Tab', action: 'Navigate between fields' },
    { key: 'Esc', action: 'Close dialogs' },
  ];

  const tips = [
    'Use search to quickly find datasets by name',
    'Select multiple columns to analyze different fields together',
    'Apply filters to narrow down your analysis scope',
    'Export data in CSV, JSON, or copy to clipboard',
    'Hover over fields for detailed descriptions',
    'Use arrow keys to navigate dropdown options',
  ];

  return (
    <>
      {/* Help Button */}
      <button
        onClick={() => setShowHelp(!showHelp)}
        className="fixed bottom-6 right-6 p-3 bg-blue-900 text-white rounded-full shadow-lg hover:bg-blue-800 transition z-40"
        title="Help & Shortcuts (Ctrl + ?)"
      >
        <HelpCircle size={24} />
      </button>

      {/* Help Modal */}
      {showHelp && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-96 overflow-y-auto">
            {/* Header */}
            <div className="sticky top-0 bg-blue-900 text-white p-6 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">Help & Shortcuts</h2>
                <p className="text-blue-100 text-sm mt-1">Learn how to use the Survey Dashboard efficiently</p>
              </div>
              <button
                onClick={() => setShowHelp(false)}
                className="p-2 hover:bg-blue-800 rounded transition"
              >
                <X size={24} />
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Quick Tips */}
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-3">💡 Quick Tips</h3>
                <ul className="space-y-2">
                  {tips.map((tip, idx) => (
                    <li key={idx} className="flex gap-3 text-sm text-gray-700">
                      <span className="text-blue-900 font-bold">•</span>
                      <span>{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Keyboard Shortcuts */}
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-3">⌨️ Keyboard Shortcuts</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {shortcuts.map((shortcut, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-3 bg-gray-50 border border-gray-300 rounded"
                    >
                      <span className="text-sm text-gray-700">{shortcut.action}</span>
                      <code className="px-2.5 py-1 bg-gray-800 text-white text-xs font-bold rounded">
                        {shortcut.key}
                      </code>
                    </div>
                  ))}
                </div>
              </div>

              {/* Workflow Guide */}
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-3">📊 Standard Workflow</h3>
                <div className="space-y-3">
                  <div className="flex gap-3">
                    <div className="text-2xl">1️⃣</div>
                    <div>
                      <p className="font-bold text-sm text-gray-900">Select Category & Dataset</p>
                      <p className="text-xs text-gray-600">Choose from hierarchical categories or search</p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <div className="text-2xl">2️⃣</div>
                    <div>
                      <p className="font-bold text-sm text-gray-900">Choose Columns</p>
                      <p className="text-xs text-gray-600">Select which fields to analyze</p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <div className="text-2xl">3️⃣</div>
                    <div>
                      <p className="font-bold text-sm text-gray-900">Apply Filters</p>
                      <p className="text-xs text-gray-600">Narrow down data by specific values</p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <div className="text-2xl">4️⃣</div>
                    <div>
                      <p className="font-bold text-sm text-gray-900">View Results & Export</p>
                      <p className="text-xs text-gray-600">Analyze data, charts, and download results</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="bg-gray-50 p-4 border-t border-gray-300 flex justify-between items-center">
              <p className="text-xs text-gray-600">
                💬 Need more help? Contact support
              </p>
              <button
                onClick={() => setShowHelp(false)}
                className="px-4 py-2 bg-blue-900 text-white text-sm font-bold rounded hover:bg-blue-800 transition"
              >
                Got it!
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
