import React, { useState } from 'react';
import { Bell, Lock, User, Database } from 'lucide-react';

export default function Settings() {
  const [settings, setSettings] = useState({
    emailNotifications: true,
    darkMode: false,
    autoRefresh: true,
    rowsPerPage: 25,
  });

  const handleToggle = (key) => {
    setSettings({ ...settings, [key]: !settings[key] });
  };

  const handleChange = (key, value) => {
    setSettings({ ...settings, [key]: value });
  };

  const settingsSections = [
    {
      title: 'Account',
      icon: User,
      items: [
        { label: 'Email', value: 'demo@survey-ai.com', type: 'text', disabled: true },
        { label: 'Display Name', value: 'Demo User', type: 'text' },
      ],
    },
    {
      title: 'Notifications',
      icon: Bell,
      items: [
        {
          label: 'Email Notifications',
          type: 'toggle',
          key: 'emailNotifications',
        },
      ],
    },
    {
      title: 'Data',
      icon: Database,
      items: [
        {
          label: 'Rows Per Page',
          type: 'select',
          key: 'rowsPerPage',
          options: [10, 25, 50, 100],
        },
        {
          label: 'Auto Refresh Data',
          type: 'toggle',
          key: 'autoRefresh',
        },
      ],
    },
    {
      title: 'Security',
      icon: Lock,
      items: [
        { label: 'Change Password', type: 'button', action: 'password' },
      ],
    },
  ];

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Settings</h1>
        <p className="text-gray-600 mt-2">Manage your account and preferences</p>
      </div>

      {/* Settings Sections */}
      <div className="space-y-6 max-w-2xl">
        {settingsSections.map((section, idx) => {
          const Icon = section.icon;
          return (
            <div
              key={idx}
              className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm"
            >
              {/* Section Header */}
              <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-200">
                <Icon className="text-blue-600" size={24} />
                <h2 className="text-lg font-semibold text-gray-800">
                  {section.title}
                </h2>
              </div>

              {/* Section Items */}
              <div className="space-y-4">
                {section.items.map((item, itemIdx) => (
                  <div key={itemIdx} className="flex items-center justify-between">
                    <label className="text-sm font-medium text-gray-700">
                      {item.label}
                    </label>

                    {/* Toggle Switch */}
                    {item.type === 'toggle' && (
                      <button
                        onClick={() => handleToggle(item.key)}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          settings[item.key]
                            ? 'bg-blue-600'
                            : 'bg-gray-300'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            settings[item.key]
                              ? 'translate-x-6'
                              : 'translate-x-1'
                          }`}
                        />
                      </button>
                    )}

                    {/* Text Input */}
                    {item.type === 'text' && (
                      <input
                        type="text"
                        defaultValue={item.value}
                        disabled={item.disabled}
                        className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed text-sm"
                      />
                    )}

                    {/* Select Dropdown */}
                    {item.type === 'select' && (
                      <select
                        value={settings[item.key]}
                        onChange={(e) =>
                          handleChange(item.key, Number(e.target.value))
                        }
                        className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      >
                        {item.options?.map((opt) => (
                          <option key={opt} value={opt}>
                            {opt}
                          </option>
                        ))}
                      </select>
                    )}

                    {/* Button */}
                    {item.type === 'button' && (
                      <button className="px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 border border-blue-600 rounded-lg transition">
                        {item.label}
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          );
        })}

        {/* Save Button */}
        <div className="flex gap-4 pt-4">
          <button className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg transition">
            Save Changes
          </button>
          <button className="px-6 py-2 border border-gray-300 text-gray-700 hover:bg-gray-50 font-semibold rounded-lg transition">
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
