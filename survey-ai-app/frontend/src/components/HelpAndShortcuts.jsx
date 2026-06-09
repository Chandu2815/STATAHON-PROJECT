import React, { useState } from 'react';
import { HelpCircle, Keyboard, X } from 'lucide-react';

/**
 * HelpAndShortcuts
 * Floating help button with keyboard shortcuts
 */
export default function HelpAndShortcuts() {
  const [isOpen, setIsOpen] = useState(false);

  const shortcuts = [
    { key: 'Ctrl/Cmd + K', action: 'Clear all filters' },
    { key: 'Ctrl/Cmd + S', action: 'Save analysis' },
  ];

  return (
    <>
      {/* Floating Help Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-8 right-8 p-4 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition z-40"
        title="Help & Shortcuts"
        aria-label="Help menu"
      >
        <HelpCircle size={24} />
      </button>

      {/* Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <Keyboard size={20} className="text-blue-600" />
                <h2 className="text-xl font-bold text-gray-900">Keyboard Shortcuts</h2>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 hover:bg-gray-100 rounded transition"
              >
                <X size={20} className="text-gray-600" />
              </button>
            </div>

            <div className="space-y-4 mb-6">
              {shortcuts.map((shortcut, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded border border-gray-200">
                  <span className="text-sm text-gray-700">{shortcut.action}</span>
                  <code className="text-xs font-mono bg-gray-200 text-gray-800 px-2 py-1 rounded">
                    {shortcut.key}
                  </code>
                </div>
              ))}
            </div>

            <div className="p-4 bg-blue-50 border border-blue-200 rounded mb-6">
              <h3 className="text-sm font-bold text-blue-900 mb-2">💡 Tips</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Use filters to refine your search results</li>
                <li>• Select multiple columns for comprehensive analysis</li>
                <li>• Export data for external analysis tools</li>
              </ul>
            </div>

            <button
              onClick={() => setIsOpen(false)}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition text-sm font-medium"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </>
  );
}
