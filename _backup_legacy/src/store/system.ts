import { create } from 'zustand'
import { SystemStatus, Agent } from '@/types'

interface SystemState {
  status: SystemStatus | null
  agents: Agent[]
  isLoading: boolean
  error: string | null
  
  setStatus: (status: SystemStatus) => void
  setAgents: (agents: Agent[]) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  updateAgent: (agent: Agent) => void
}

export const useSystemStore = create<SystemState>((set) => ({
  status: null,
  agents: [],
  isLoading: false,
  error: null,
  
  setStatus: (status) => set({ status }),
  
  setAgents: (agents) => set({ agents }),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  setError: (error) => set({ error }),
  
  updateAgent: (agent) => set((state) => ({
    agents: state.agents.map(a => a.agent_id === agent.agent_id ? agent : a),
  })),
}))
