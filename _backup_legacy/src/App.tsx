/// <reference types="vite/client" />

import { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/auth'
import Layout from '@/components/Layout'
import Auth from '@/pages/Auth'
import Dashboard from '@/pages/Dashboard'
import Chat from '@/pages/Chat'
import Agents from '@/pages/Agents'
import Workflows from '@/pages/Workflows'
import Analytics from '@/pages/Analytics'
import Settings from '@/pages/Settings'
import Toast from '@/components/Toast'

export default function App() {
  const { isAuthenticated } = useAuthStore()
  const [toasts, setToasts] = useState<Array<{ id: string; type: 'success' | 'error' | 'info' | 'warning'; message: string }>>([])

  const addToast = (type: 'success' | 'error' | 'info' | 'warning', message: string) => {
    const id = `toast_${Date.now()}`
    setToasts(prev => [...prev, { id, type, message }])
  }

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }

  useEffect(() => {
    (window as any).addToast = addToast
  }, [])

  return (
    <BrowserRouter>
      <Routes>
        {!isAuthenticated ? (
          <Route path="*" element={<Auth />} />
        ) : (
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/agents" element={<Agents />} />
            <Route path="/workflows" element={<Workflows />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        )}
      </Routes>

      <div className="fixed bottom-6 right-6 space-y-3 z-40">
        {toasts.map(toast => (
          <Toast
            key={toast.id}
            id={toast.id}
            type={toast.type}
            message={toast.message}
            onClose={removeToast}
          />
        ))}
      </div>
    </BrowserRouter>
  )
}
