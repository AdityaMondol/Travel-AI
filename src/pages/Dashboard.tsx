import React, { useEffect, useState } from 'react'
import { Activity, Zap, TrendingUp, Clock } from 'lucide-react'
import StatCard from '@/components/StatCard'
import { apiClient } from '@/api/client'
import { useSystemStore } from '@/store/system'

export default function Dashboard() {
  const { status, agents, setStatus, setAgents, isLoading, setLoading } = useSystemStore()
  const [recentTasks, setRecentTasks] = useState<any[]>([])

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const [statusRes, agentsRes] = await Promise.all([
          apiClient.getSystemStatus(),
          apiClient.getAgents(),
        ])
        setStatus(statusRes.data)
        setAgents(agentsRes.data.agents || [])
        setRecentTasks(agentsRes.data.agents?.slice(0, 5) || [])
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [setStatus, setAgents, setLoading])

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="section-title">Dashboard</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={Zap}
          label="Active Agents"
          value={status?.agents.active || 0}
          change={{ value: 12, direction: 'up' }}
        />
        <StatCard
          icon={Activity}
          label="Total Tasks"
          value={agents.length}
          change={{ value: 8, direction: 'up' }}
        />
        <StatCard
          icon={TrendingUp}
          label="Success Rate"
          value="94%"
          change={{ value: 2, direction: 'up' }}
        />
        <StatCard
          icon={Clock}
          label="Avg Response"
          value="245ms"
          change={{ value: 5, direction: 'down' }}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 card">
          <h2 className="text-lg font-semibold text-neutral-900 mb-4">Recent Activity</h2>
          <div className="space-y-3">
            {recentTasks.length > 0 ? (
              recentTasks.map((task, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-neutral-50 rounded-sm">
                  <div>
                    <p className="text-sm font-medium text-neutral-900">{task.agent_type}</p>
                    <p className="text-xs text-neutral-500">Task ID: {task.agent_id}</p>
                  </div>
                  <span className={`badge ${
                    task.state === 'complete' ? 'badge-success' :
                    task.state === 'executing' ? 'badge-info' :
                    'badge-warning'
                  }`}>
                    {task.state}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-sm text-neutral-500">No recent activity</p>
            )}
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-neutral-900 mb-4">System Health</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-neutral-600">CPU Usage</span>
                <span className="text-sm font-medium text-neutral-900">
                  {status?.system.cpu_percent.toFixed(1)}%
                </span>
              </div>
              <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-neutral-900 transition-all"
                  style={{ width: `${status?.system.cpu_percent || 0}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-neutral-600">Memory</span>
                <span className="text-sm font-medium text-neutral-900">
                  {status?.system.memory_mb.toFixed(0)}MB
                </span>
              </div>
              <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-neutral-900 transition-all"
                  style={{ width: `${Math.min((status?.system.memory_mb || 0) / 40, 100)}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold text-neutral-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="p-4 border border-neutral-200 rounded-sm hover:border-neutral-900 hover:bg-neutral-50 transition-all text-left">
            <p className="font-medium text-neutral-900 mb-1">New Research</p>
            <p className="text-xs text-neutral-500">Deep research workflow</p>
          </button>
          <button className="p-4 border border-neutral-200 rounded-sm hover:border-neutral-900 hover:bg-neutral-50 transition-all text-left">
            <p className="font-medium text-neutral-900 mb-1">Generate Code</p>
            <p className="text-xs text-neutral-500">Fullstack generation</p>
          </button>
          <button className="p-4 border border-neutral-200 rounded-sm hover:border-neutral-900 hover:bg-neutral-50 transition-all text-left">
            <p className="font-medium text-neutral-900 mb-1">Browser Task</p>
            <p className="text-xs text-neutral-500">Web automation</p>
          </button>
          <button className="p-4 border border-neutral-200 rounded-sm hover:border-neutral-900 hover:bg-neutral-50 transition-all text-left">
            <p className="font-medium text-neutral-900 mb-1">Data Analysis</p>
            <p className="text-xs text-neutral-500">Visualization</p>
          </button>
        </div>
      </div>
    </div>
  )
}
