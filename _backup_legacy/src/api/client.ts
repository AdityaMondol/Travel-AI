import axios, { AxiosInstance, AxiosError } from 'axios'
import { useAuthStore } from '@/store/auth'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

class APIClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.client.interceptors.request.use((config) => {
      const token = useAuthStore.getState().token
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          useAuthStore.getState().logout()
        }
        return Promise.reject(error)
      }
    )
  }

  async chat(sessionId: string, message: string) {
    return this.client.post('/chat/simple', {
      session_id: sessionId,
      message,
    })
  }

  async chatStream(sessionId: string, message: string) {
    return this.client.post('/chat', {
      session_id: sessionId,
      message,
    }, {
      responseType: 'stream',
    })
  }

  async getAgents() {
    return this.client.get('/agents')
  }

  async getSystemStatus() {
    return this.client.get('/status')
  }

  async getHealth() {
    return this.client.get('/health')
  }

  async getMemory(query?: string, limit?: number) {
    return this.client.get('/memory', {
      params: { query, limit },
    })
  }

  async uploadFile(file: File, sessionId: string) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('session_id', sessionId)

    return this.client.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  }

  async research(query: string) {
    return this.client.post('/research', { query })
  }

  async generateCode(task: string) {
    return this.client.post('/code', { task })
  }

  async browseWeb(goal: string, startUrl?: string) {
    return this.client.post('/browse', { goal, start_url: startUrl })
  }

  async getMetrics() {
    return this.client.get('/metrics')
  }

  async getAuditLogs() {
    return this.client.get('/audit')
  }
}

export const apiClient = new APIClient()
