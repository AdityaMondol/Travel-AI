import React, { useState } from 'react'
import { BookOpen, Code, Globe, BarChart3, Play } from 'lucide-react'
import Modal from '@/components/Modal'

const workflows = [
  {
    id: 'research',
    name: 'Deep Research',
    description: 'Multi-step research with web scraping, PDF parsing, and RAG',
    icon: BookOpen,
    color: 'bg-blue-50',
    tags: ['research', 'rag', 'web-scraping'],
  },
  {
    id: 'code',
    name: 'Code Generation',
    description: 'Test-first code generation with iterative refinement',
    icon: Code,
    color: 'bg-green-50',
    tags: ['code', 'testing', 'generation'],
  },
  {
    id: 'browser',
    name: 'Browser Automation',
    description: 'Intelligent web automation with natural language planning',
    icon: Globe,
    color: 'bg-purple-50',
    tags: ['automation', 'browser', 'web'],
  },
  {
    id: 'analysis',
    name: 'Data Analysis',
    description: 'Comprehensive data analysis and visualization',
    icon: BarChart3,
    color: 'bg-amber-50',
    tags: ['analysis', 'visualization', 'data'],
  },
]

export default function Workflows() {
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [input, setInput] = useState('')

  const handleExecute = (workflowId: string) => {
    setSelectedWorkflow(workflowId)
    setIsModalOpen(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || !selectedWorkflow) return

    console.log(`Executing ${selectedWorkflow} with input: ${input}`)
    setInput('')
    setIsModalOpen(false)
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="section-title">Workflows</h1>
        <p className="text-muted">Execute specialized agent workflows</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {workflows.map((workflow) => {
          const Icon = workflow.icon
          return (
            <div key={workflow.id} className="card">
              <div className="flex items-start gap-4 mb-4">
                <div className={`w-12 h-12 rounded-sm flex items-center justify-center ${workflow.color}`}>
                  <Icon size={24} className="text-neutral-700" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-neutral-900">{workflow.name}</h3>
                  <p className="text-sm text-neutral-500">{workflow.description}</p>
                </div>
              </div>

              <div className="flex flex-wrap gap-2 mb-4">
                {workflow.tags.map((tag) => (
                  <span key={tag} className="badge badge-info">
                    {tag}
                  </span>
                ))}
              </div>

              <button
                onClick={() => handleExecute(workflow.id)}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                <Play size={16} />
                Execute
              </button>
            </div>
          )
        })}
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={`Execute ${workflows.find(w => w.id === selectedWorkflow)?.name}`}
        size="md"
        footer={
          <>
            <button
              onClick={() => setIsModalOpen(false)}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              className="btn-primary"
            >
              Execute
            </button>
          </>
        }
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-neutral-900 mb-2">
              Input
            </label>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Enter your request..."
              className="input-field resize-none"
              rows={4}
            />
          </div>
        </form>
      </Modal>
    </div>
  )
}
