// Auto-detect API base: relative URL works both locally and in Docker nginx
const API_BASE = import.meta.env.VITE_API_URL || ''

const getApiKey = () => localStorage.getItem('api_key')

const authHeaders = (): Record<string, string> => {
  const key = getApiKey()
  return key ? { 'X-API-Key': key } : {}
}

export const api = {
  async uploadFile(file: File): Promise<{ file_path: string; storage_key: string }> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      headers: authHeaders(),
      body: formData,
    })
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }))
      throw new Error(error.detail || 'Upload failed')
    }
    return response.json()
  },

  async runPipeline(filePath: string, datasetId: string): Promise<{ job_id: string; status: string }> {
    const apiKey = getApiKey()
    if (!apiKey) throw new Error('Not authenticated. Please login first.')
    const response = await fetch(`${API_BASE}/pipeline/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-API-Key': apiKey },
      body: JSON.stringify({ file_path: filePath, dataset_id: datasetId }),
    })
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to start pipeline' }))
      throw new Error(error.detail || 'Failed to start pipeline')
    }
    return response.json()
  },

  async getStatus(jobId: string) {
    const response = await fetch(`${API_BASE}/pipeline/${jobId}/status`, { headers: authHeaders() })
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get status' }))
      throw new Error(error.detail || 'Failed to get status')
    }
    return response.json()
  },

  async getAllJobs() {
    const response = await fetch(`${API_BASE}/pipeline/all`, { headers: authHeaders() })
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get jobs' }))
      throw new Error(error.detail || 'Failed to get jobs')
    }
    return response.json()
  },

  async getAnalytics(jobId: string) {
    const response = await fetch(`${API_BASE}/pipeline/${jobId}/analytics`, { headers: authHeaders() })
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to get analytics' }))
      throw new Error(error.detail || 'Failed to get analytics')
    }
    return response.json()
  },

  async login(username: string, password: string): Promise<{ api_key: string }> {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }))
      throw new Error(error.detail || 'Login failed')
    }
    return response.json()
  },

  subscribeToEvents(jobId: string, onMessage: (data: any) => void) {
    const eventSource = new EventSource(`${API_BASE}/pipeline/${jobId}/events`)
    eventSource.onmessage = (event) => {
      try { onMessage(JSON.parse(event.data)) } catch (e) { console.error('Failed to parse event:', e) }
    }
    eventSource.onerror = () => eventSource.close()
    return () => eventSource.close()
  },
}

export type PipelineStatus = 'PENDING' | 'RUNNING' | 'COMPLETE' | 'FAILED'
export type PipelineStage = { stage_name: string; status: PipelineStatus; output?: any }
export type PipelineJob = {
  job_id: string; dataset_id: string; file_path: string; status: PipelineStatus
  total_tokens_used?: number; total_cost_usd?: number; stages?: PipelineStage[]; created_at?: string
}
