import React, { useEffect, useState } from 'react'
import { TrendingUp, Clock, Zap, AlertCircle } from 'lucide-react'
import StatCard from '@/components/StatCard'
import { apiClient } from '@/api/client'

export default function Analytics() {
  const [metrics, setMetrics] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchMetrics = async () => {
      setIsLoading(true)
      try {
        const response = await apiClient.getMetrics()
        setMetrics(response.data)
      } catch (error) {
        console.error('Failed to fetch metrics:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchMetrics()
    const interval = setInterval(fetchMetrics, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="section-title">Analytics</h1>
        <p className="text-muted">System performance and usage metrics</p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="loading-spinner" />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard
              icon={TrendingUp}
              label="Total Requests"
              value={metrics?.requests_total || 0}
            />
            <StatCard
              icon={Clock}
              label="Avg Response Time"
              value={`${(metrics?.avg_response_time || 0).toFixed(0)}ms`}
            />
            <StatCard
              icon={Zap}
              label="Success Rate"
              value={`${(metrics?.success_rate || 0).toFixed(1)}%`}
            />
            <StatCard
              icon={AlertCircle}
              label="Error Rate"
              value={`${(metrics?.error_rate || 0).toFixed(1)}%`}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card">
              <h2 className="text-lg font-semibold text-neutral-900 mb-4">Request Distribution</h2>
              <div className="space-y-3">
                {[
                  { endpoint: '/api/chat', requests: 1240, percentage: 45 },
                  { endpoint: '/api/research', requests: 680, percentage: 25 },
                  { endpoint: '/api/code', requests: 520, percentage: 19 },
                  { endpoint: '/api/browse', requests: 220, percentage: 8 },
                ].map((item) => (
                  <div key={item.endpoint}>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm font-medium text-neutral-900">{item.endpoint}</span>
                      <span className="text-sm text-neutral-600">{item.requests}</span>
                    </div>
                    <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-neutral-900 transition-all"
                        style={{ width: `${item.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="card">
              <h2 className="text-lg font-semibold text-neutral-900 mb-4">System Resources</h2>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm text-neutral-600">CPU Usage</span>
                    <span className="text-sm font-medium text-neutral-900">
                      {metrics?.cpu_percent?.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-neutral-900 transition-all"
                      style={{ width: `${metrics?.cpu_percent || 0}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm text-neutral-600">Memory</span>
                    <span className="text-sm font-medium text-neutral-900">
                      {metrics?.memory_mb?.toFixed(0)}MB
                    </span>
                  </div>
                  <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-neutral-900 transition-all"
                      style={{ width: `${Math.min((metrics?.memory_mb || 0) / 40, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
