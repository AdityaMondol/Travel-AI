import React, { useEffect } from 'react'
import { Zap, Pause, Play, Trash2 } from 'lucide-react'
import { useSystemStore } from '@/store/system'
import { apiClient } from '@/api/client'

export default function Agents() {
  const { agents, setAgents, isLoading, setLoading } = useSystemStore()

  useEffect(() => {
    const fetchAgents = async () => {
      setLoading(true)
      try {
        const response = await apiClient.getAgents()
        setAgents(response.data.agents || [])
      } catch (error) {
        console.error('Failed to fetch agents:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchAgents()
    const interval = setInterval(fetchAgents, 10000)
    return () => clearInterval(interval)
  }, [setAgents, setLoading])

  const getStateColor = (state: string) => {
    switch (state) {
      case 'idle':
        return 'badge-info'
      case 'executing':
        return 'badge-warning'
      case 'complete':
        return 'badge-success'
      case 'error':
        return 'badge-error'
      default:
        return 'badge-info'
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="section-title">Agents</h1>
        <p className="text-muted">Manage and monitor your agent pool</p>
      </div>

      {isLoading && agents.length === 0 ? (
        <div className="flex items-center justify-center h-64">
          <div className="loading-spinner" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent) => (
            <div key={agent.agent_id} className="card">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-neutral-100 rounded-sm flex items-center justify-center">
                    <Zap size={20} className="text-neutral-600" />
                  </div>
                  <div>
                    <p className="font-medium text-neutral-900">{agent.agent_type}</p>
                    <p className="text-xs text-neutral-500">{agent.agent_id}</p>
                  </div>
                </div>
                <span className={`badge ${getStateColor(agent.state)}`}>
                  {agent.state}
                </span>
              </div>

              <div className="space-y-3 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-neutral-600">Tasks Completed</span>
                  <span className="font-medium text-neutral-900">{agent.action_count}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-neutral-600">Cost Used</span>
                  <span className="font-medium text-neutral-900">${agent.cost_used.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-neutral-600">Created</span>
                  <span className="font-medium text-neutral-900">
                    {new Date(agent.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              <div className="flex gap-2 pt-4 border-t border-neutral-200">
                <button className="btn-secondary flex-1 flex items-center justify-center gap-2">
                  {agent.state === 'idle' ? (
                    <>
                      <Play size={16} />
                      Start
                    </>
                  ) : (
                    <>
                      <Pause size={16} />
                      Pause
                    </>
                  )}
                </button>
                <button className="btn-ghost">
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {!isLoading && agents.length === 0 && (
        <div className="card text-center py-12">
          <p className="text-neutral-600 mb-4">No agents available</p>
          <button className="btn-primary">Spawn New Agent</button>
        </div>
      )}
    </div>
  )
}
