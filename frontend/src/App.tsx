import { useEffect, useState } from 'react'
import { isAxiosError } from 'axios'
import { fetchLLMs, fetchCompletion, login as loginRequest, logout as logoutRequest } from './api/client'
import type { LLMInfo, ChatResponse, AuthTokens, LLMSelectionPayload } from './api/client'
import { LLMSelector } from './components/LLMSelector'
import { ChatInput } from './components/ChatInput'
import { ResponseGrid } from './components/ResponseGrid'

const AUTH_STORAGE_KEY = 'supabaseSession'

function App() {
  const [llms, setLlms] = useState<LLMInfo[]>([])
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [prompt, setPrompt] = useState('')
  const [responses, setResponses] = useState<Record<string, ChatResponse>>({})
  const [loadingStates, setLoadingStates] = useState<Record<string, boolean>>({})
  const [error, setError] = useState<string | null>(null)
  const [authTokens, setAuthTokens] = useState<AuthTokens | null>(null)
  const [userEmail, setUserEmail] = useState<string | null>(null)
  const [authForm, setAuthForm] = useState({ email: '', password: '' })
  const [authError, setAuthError] = useState<string | null>(null)
  const [authLoading, setAuthLoading] = useState(false)

  useEffect(() => {
    fetchLLMs()
      .then(setLlms)
      .catch(err => {
        console.error(err);
        setError('Failed to load LLMs');
      })
  }, [])

  useEffect(() => {
    if (typeof window === 'undefined') return
    const stored = window.localStorage.getItem(AUTH_STORAGE_KEY)
    if (!stored) return
    try {
      const parsed = JSON.parse(stored) as { email: string; tokens: AuthTokens }
      setAuthTokens(parsed.tokens)
      setUserEmail(parsed.email)
    } catch (err) {
      console.warn('Failed to parse stored auth session', err)
      window.localStorage.removeItem(AUTH_STORAGE_KEY)
    }
  }, [])

  const handleToggleLLM = (id: string) => {
    setSelectedIds(prev => 
      prev.includes(id) 
        ? prev.filter(i => i !== id) 
        : [...prev, id]
    )
  }

  const safeMessage = (input: unknown) => {
    if (input == null) return 'Login failed'
    if (typeof input === 'string') return input
    if (typeof input === 'object') {
      const maybeDetail = (input as { detail?: unknown }).detail
      if (typeof maybeDetail === 'string') return maybeDetail
      if (Array.isArray(maybeDetail) && maybeDetail.length > 0) {
        const first = maybeDetail[0] as { msg?: string }
        if (typeof first?.msg === 'string') return first.msg
      }
      if ('message' in (input as Record<string, unknown>)) {
        const message = (input as { message?: unknown }).message
        if (typeof message === 'string') return message
      }
    }
    return 'Login failed'
  }

  const handleAuthFieldChange = (field: 'email' | 'password', value: string) => {
    setAuthError(null)
    setAuthForm(prev => ({ ...prev, [field]: value }))
  }

  const handleLogin = async () => {
    if (!authForm.email || !authForm.password) return
    setAuthLoading(true)
    setAuthError(null)
    try {
      const session = await loginRequest(authForm.email, authForm.password)
      setAuthTokens(session.tokens)
      setUserEmail(session.email)
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session))
      }
      setAuthForm(prev => ({ ...prev, password: '' }))
    } catch (err) {
      console.error('Login failed', err)
      if (isAxiosError(err)) {
        setAuthError(safeMessage(err.response?.data ?? err.message))
      } else if (err instanceof Error) {
        setAuthError(err.message)
      } else {
        setAuthError('Login failed')
      }
    } finally {
      setAuthLoading(false)
    }
  }

  const handleLogout = async () => {
    if (!authTokens) return
    setAuthLoading(true)
    setAuthError(null)
    try {
      await logoutRequest(authTokens.access_token)
    } catch (err) {
      console.error('Logout failed', err)
    } finally {
      setAuthTokens(null)
      setUserEmail(null)
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(AUTH_STORAGE_KEY)
      }
      setAuthLoading(false)
    }
  }

  const handleSubmit = async () => {
    if (!prompt.trim() || selectedIds.length === 0) return

    const selectionMap = selectedIds.reduce<Record<string, LLMSelectionPayload>>((acc, id) => {
      const match = llms.find(l => l.llm_id === id)
      if (match) {
        acc[id] = { llm_id: match.llm_id, api_provider: match.api_provider }
      }
      return acc
    }, {})

    const missingIds = selectedIds.filter(id => !selectionMap[id])
    if (missingIds.length > 0) {
      setError(`Missing metadata for models: ${missingIds.join(', ')}`)
      return
    }
    
    setResponses({}) // Clear previous responses
    setError(null)
    
    // Initialize loading states for all selected models
    const initialLoadingStates: Record<string, boolean> = {}
    selectedIds.forEach(id => {
      initialLoadingStates[id] = true
    })
    setLoadingStates(initialLoadingStates)

    // Fire off requests in parallel
    selectedIds.forEach(async (llmId) => {
      const selection = selectionMap[llmId]
      try {
        const response = await fetchCompletion(prompt, selection, authTokens?.access_token)
        setResponses(prev => ({
          ...prev,
          [llmId]: response
        }))
      } catch (err) {
        console.error(`Error fetching ${llmId}:`, err)
        setResponses(prev => ({
          ...prev,
          [llmId]: {
            llm_id: llmId,
            content: '',
            timestamp: new Date().toISOString(),
            error: 'Failed to fetch response'
          }
        }))
      } finally {
        setLoadingStates(prev => ({
          ...prev,
          [llmId]: false
        }))
      }
    })
  }

  const isAnyLoading = Object.values(loadingStates).some(Boolean)
  const disableLogin = authLoading || !authForm.email || !authForm.password
  const disableLogout = authLoading || !authTokens

  return (
    <div className="container mx-auto p-4 max-w-6xl space-y-8">
      <div className="space-y-2">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">LLM Arena</h1>
            <p className="text-muted-foreground">Select models and compare their responses.</p>
          </div>
          <div className="flex flex-col gap-2 items-end">
            {userEmail && (
              <span className="text-sm text-muted-foreground">Signed in as {userEmail}</span>
            )}
            <div className="flex flex-wrap items-center justify-end gap-2">
              <input
                type="email"
                placeholder="Email"
                value={authForm.email}
                onChange={e => handleAuthFieldChange('email', e.target.value)}
                className="border rounded-md px-2 py-1 text-sm"
                disabled={authLoading}
              />
              <input
                type="password"
                placeholder="Password"
                value={authForm.password}
                onChange={e => handleAuthFieldChange('password', e.target.value)}
                className="border rounded-md px-2 py-1 text-sm"
                disabled={authLoading}
              />
              <button
                className="rounded-md bg-primary text-primary-foreground px-3 py-1 text-sm disabled:opacity-50"
                onClick={handleLogin}
                disabled={disableLogin}
              >
                Login
              </button>
              <button
                className="rounded-md border px-3 py-1 text-sm disabled:opacity-50"
                onClick={handleLogout}
                disabled={disableLogout}
              >
                Logout
              </button>
            </div>
            {authError && (
              <span className="text-xs text-red-500">{authError}</span>
            )}
          </div>
        </div>
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
          disabled={isAnyLoading || selectedIds.length === 0}
        />
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-semibold">3. Compare Responses</h2>
        <ResponseGrid 
          selectedLLMs={llms.filter(l => selectedIds.includes(l.llm_id))}
          responses={responses}
          loadingStates={loadingStates}
        />
      </div>
    </div>
  )
}

export default App
