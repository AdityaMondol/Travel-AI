import { create } from 'zustand'
import { ChatSession, Message } from '@/types'

interface ChatState {
  sessions: ChatSession[]
  currentSessionId: string | null
  currentMessages: Message[]
  isLoading: boolean
  
  addSession: (session: ChatSession) => void
  setCurrentSession: (sessionId: string) => void
  addMessage: (message: Message) => void
  setLoading: (loading: boolean) => void
  clearMessages: () => void
  deleteSession: (sessionId: string) => void
}

export const useChatStore = create<ChatState>((set) => ({
  sessions: [],
  currentSessionId: null,
  currentMessages: [],
  isLoading: false,
  
  addSession: (session) => set((state) => ({
    sessions: [session, ...state.sessions],
    currentSessionId: session.session_id,
    currentMessages: session.messages,
  })),
  
  setCurrentSession: (sessionId) => set((state) => {
    const session = state.sessions.find(s => s.session_id === sessionId)
    return {
      currentSessionId: sessionId,
      currentMessages: session?.messages || [],
    }
  }),
  
  addMessage: (message) => set((state) => ({
    currentMessages: [...state.currentMessages, message],
  })),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  clearMessages: () => set({ currentMessages: [] }),
  
  deleteSession: (sessionId) => set((state) => ({
    sessions: state.sessions.filter(s => s.session_id !== sessionId),
    currentSessionId: state.currentSessionId === sessionId ? null : state.currentSessionId,
  })),
}))
