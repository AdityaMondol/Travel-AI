import React, { useEffect, useRef, useState } from 'react'
import { Send, Plus, Trash2 } from 'lucide-react'
import { useChatStore } from '@/store/chat'
import { useAuthStore } from '@/store/auth'
import { apiClient } from '@/api/client'
import { Message } from '@/types'

export default function Chat() {
  const { sessions, currentSessionId, currentMessages, addSession, setCurrentSession, addMessage, deleteSession, setLoading, isLoading } = useChatStore()
  const { user } = useAuthStore()
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [currentMessages])

  const handleAutoResize = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px'
    }
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || !user) return

    const sessionId = currentSessionId || `session_${Date.now()}`
    
    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      sender: 'user',
      text: input,
      content: input,
      timestamp: new Date().toISOString(),
    }

    addMessage(userMessage)
    setInput('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }

    setLoading(true)
    try {
      const response = await apiClient.chat(sessionId, input)
      const assistantMessage: Message = {
        id: `msg_${Date.now() + 1}`,
        role: 'assistant',
        sender: 'agent',
        text: response.data.response || 'No response',
        content: response.data.response || 'No response',
        timestamp: new Date().toISOString(),
      }
      addMessage(assistantMessage)
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMessage: Message = {
        id: `msg_${Date.now() + 1}`,
        role: 'assistant',
        sender: 'agent',
        text: 'Failed to process message. Please try again.',
        content: 'Failed to process message. Please try again.',
        timestamp: new Date().toISOString(),
      }
      addMessage(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleNewChat = () => {
    const newSession = {
      id: `session_${Date.now()}`,
      session_id: `session_${Date.now()}`,
      title: 'New Chat',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      messages: [],
    }
    addSession(newSession)
  }

  return (
    <div className="flex h-full">
      <aside className="w-64 border-r border-neutral-200 bg-white flex flex-col">
        <div className="p-4 border-b border-neutral-200">
          <button
            onClick={handleNewChat}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            <Plus size={18} />
            New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {sessions.map((session) => (
            <div
              key={session.session_id}
              className={`p-3 rounded-sm cursor-pointer transition-all group ${
                currentSessionId === session.session_id
                  ? 'bg-neutral-100 text-neutral-900'
                  : 'text-neutral-600 hover:bg-neutral-50'
              }`}
              onClick={() => setCurrentSession(session.session_id)}
            >
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium truncate flex-1">{session.title}</p>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    deleteSession(session.session_id)
                  }}
                  className="opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Trash2 size={16} />
                </button>
              </div>
              <p className="text-xs text-neutral-500 mt-1">
                {new Date(session.created_at).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      </aside>

      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {currentMessages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <p className="text-lg font-semibold text-neutral-900 mb-2">Start a conversation</p>
                <p className="text-neutral-500">Ask anything and Leonore will help you</p>
              </div>
            </div>
          ) : (
            currentMessages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 animate-fadeIn ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="w-8 h-8 bg-neutral-900 rounded-sm flex items-center justify-center flex-shrink-0">
                    <span className="text-white text-xs font-bold">L</span>
                  </div>
                )}
                <div
                  className={`max-w-md px-4 py-3 rounded-sm ${
                    message.role === 'user'
                      ? 'bg-neutral-900 text-white'
                      : 'bg-neutral-100 text-neutral-900'
                  }`}
                >
                  <p className="text-sm leading-relaxed">{message.content}</p>
                </div>
                {message.role === 'user' && (
                  <div className="w-8 h-8 bg-neutral-200 rounded-sm flex items-center justify-center flex-shrink-0 text-xs font-semibold text-neutral-700">
                    {user?.username.charAt(0).toUpperCase()}
                  </div>
                )}
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 bg-neutral-900 rounded-sm flex items-center justify-center flex-shrink-0">
                <span className="text-white text-xs font-bold">L</span>
              </div>
              <div className="bg-neutral-100 px-4 py-3 rounded-sm">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  <div className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="border-t border-neutral-200 bg-white p-4">
          <form onSubmit={handleSendMessage} className="flex gap-3">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => {
                setInput(e.target.value)
                handleAutoResize()
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSendMessage(e as any)
                }
              }}
              placeholder="Ask anything..."
              className="input-field resize-none"
              rows={1}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="btn-primary flex items-center justify-center w-10 h-10 p-0 flex-shrink-0"
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
