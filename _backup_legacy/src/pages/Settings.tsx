import React, { useState } from 'react'
import { Save, Key, Bell, Lock } from 'lucide-react'
import { useAuthStore } from '@/store/auth'

export default function Settings() {
  const { user } = useAuthStore()
  const [apiKeys, setApiKeys] = useState<string[]>([])
  const [showNewKeyForm, setShowNewKeyForm] = useState(false)
  const [keyName, setKeyName] = useState('')

  const handleCreateKey = (e: React.FormEvent) => {
    e.preventDefault()
    if (!keyName.trim()) return

    const newKey = `sk_${Math.random().toString(36).substr(2, 20)}`
    setApiKeys([...apiKeys, newKey])
    setKeyName('')
    setShowNewKeyForm(false)
  }

  const handleDeleteKey = (index: number) => {
    setApiKeys(apiKeys.filter((_, i) => i !== index))
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="section-title">Settings</h1>
      </div>

      <div className="max-w-2xl space-y-6">
        {/* Profile Settings */}
        <div className="card">
          <h2 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
            <Lock size={20} />
            Profile
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-neutral-900 mb-2">
                Username
              </label>
              <input
                type="text"
                value={user?.username || ''}
                disabled
                className="input-field opacity-50 cursor-not-allowed"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-900 mb-2">
                Email
              </label>
              <input
                type="email"
                value={user?.email || ''}
                disabled
                className="input-field opacity-50 cursor-not-allowed"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-900 mb-2">
                Role
              </label>
              <input
                type="text"
                value={user?.role || ''}
                disabled
                className="input-field opacity-50 cursor-not-allowed"
              />
            </div>
            <button className="btn-primary flex items-center gap-2">
              <Save size={16} />
              Save Changes
            </button>
          </div>
        </div>

        {/* API Keys */}
        <div className="card">
          <h2 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
            <Key size={20} />
            API Keys
          </h2>
          <p className="text-sm text-neutral-600 mb-4">
            Manage your API keys for programmatic access
          </p>

          {apiKeys.length > 0 && (
            <div className="space-y-2 mb-4">
              {apiKeys.map((key, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-neutral-50 rounded-sm">
                  <code className="text-xs font-mono text-neutral-600">
                    {key.slice(0, 10)}...{key.slice(-10)}
                  </code>
                  <button
                    onClick={() => handleDeleteKey(idx)}
                    className="btn-ghost text-red-600 hover:text-red-700"
                  >
                    Delete
                  </button>
                </div>
              ))}
            </div>
          )}

          {showNewKeyForm ? (
            <form onSubmit={handleCreateKey} className="space-y-3 p-4 bg-neutral-50 rounded-sm">
              <input
                type="text"
                value={keyName}
                onChange={(e) => setKeyName(e.target.value)}
                placeholder="Key name (e.g., Production API)"
                className="input-field"
              />
              <div className="flex gap-2">
                <button type="submit" className="btn-primary flex-1">
                  Create Key
                </button>
                <button
                  type="button"
                  onClick={() => setShowNewKeyForm(false)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <button
              onClick={() => setShowNewKeyForm(true)}
              className="btn-secondary w-full"
            >
              + Create New Key
            </button>
          )}
        </div>

        {/* Notifications */}
        <div className="card">
          <h2 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
            <Bell size={20} />
            Notifications
          </h2>
          <div className="space-y-4">
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" defaultChecked className="w-4 h-4" />
              <span className="text-sm text-neutral-900">Task completion notifications</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" defaultChecked className="w-4 h-4" />
              <span className="text-sm text-neutral-900">Error alerts</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" className="w-4 h-4" />
              <span className="text-sm text-neutral-900">Weekly summary</span>
            </label>
          </div>
        </div>

        {/* Quota */}
        <div className="card">
          <h2 className="text-lg font-semibold text-neutral-900 mb-4">Monthly Quota</h2>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-neutral-600">Usage</span>
                <span className="text-sm font-medium text-neutral-900">
                  ${user?.quota_used_usd.toFixed(2)} / ${user?.quota_monthly_usd.toFixed(2)}
                </span>
              </div>
              <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-neutral-900 transition-all"
                  style={{
                    width: `${((user?.quota_used_usd || 0) / (user?.quota_monthly_usd || 1)) * 100}%`,
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
