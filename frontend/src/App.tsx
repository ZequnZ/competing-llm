import { useEffect, useState } from 'react'
import { fetchLLMs, fetchBatchCompletion } from './api/client'
import type { LLMInfo, ChatResponse } from './api/client'
import { LLMSelector } from './components/LLMSelector'
import { ChatInput } from './components/ChatInput'
import { ResponseGrid } from './components/ResponseGrid'

function App() {
  const [llms, setLlms] = useState<LLMInfo[]>([])
  const [selectedIds, setSelectedIds] = useState<number[]>([])
  const [prompt, setPrompt] = useState('')
  const [responses, setResponses] = useState<Record<number, ChatResponse>>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchLLMs()
      .then(setLlms)
      .catch(err => {
        console.error(err);
        setError('Failed to load LLMs');
      })
  }, [])

  const handleToggleLLM = (id: number) => {
    setSelectedIds(prev => 
      prev.includes(id) 
        ? prev.filter(i => i !== id) 
        : [...prev, id]
    )
  }

  const handleSubmit = async () => {
    if (!prompt.trim() || selectedIds.length === 0) return
    
    setLoading(true)
    setResponses({}) // Clear previous responses
    setError(null)

    try {
      const results = await fetchBatchCompletion(prompt, selectedIds)
      const newResponses: Record<number, ChatResponse> = {}
      results.forEach(r => {
        newResponses[r.llm_id] = r
      })
      setResponses(newResponses)
    } catch (err) {
      setError('Failed to fetch responses')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto p-4 max-w-6xl space-y-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">LLM Arena</h1>
        <p className="text-muted-foreground">Select models and compare their responses.</p>
      </div>

      {error && (
        <div className="bg-destructive/15 text-destructive px-4 py-3 rounded-md text-sm font-medium">
          {error}
        </div>
      )}

      <div className="space-y-4">
        <h2 className="text-lg font-semibold">1. Select Models</h2>
        <LLMSelector 
          llms={llms} 
          selectedIds={selectedIds} 
          onToggle={handleToggleLLM} 
        />
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-semibold">2. Enter Prompt</h2>
        <ChatInput 
          value={prompt} 
          onChange={setPrompt} 
          onSubmit={handleSubmit}
          disabled={loading || selectedIds.length === 0}
        />
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-semibold">3. Compare Responses</h2>
        <ResponseGrid 
          selectedLLMs={llms.filter(l => selectedIds.includes(l.llm_id))}
          responses={responses}
          loading={loading}
        />
      </div>
    </div>
  )
}

export default App
