import axios from 'axios'

type AnyRecord = Record<string, unknown>
type Id = string | number
type ApiResult<T = any> = Promise<T>
type RequestConfig = AnyRecord & { signal?: AbortSignal }

type ApiClient = {
  get<T = any>(url: string, config?: RequestConfig): ApiResult<T>
  post<T = any>(url: string, data?: unknown, config?: RequestConfig): ApiResult<T>
  put<T = any>(url: string, data?: unknown, config?: RequestConfig): ApiResult<T>
  delete<T = any>(url: string, config?: RequestConfig): ApiResult<T>
}


const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api'

const rawApiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' }
})

rawApiClient.interceptors.request.use(
  config => config,
  error => Promise.reject(error)
)

rawApiClient.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response) {
      const message = error.response.data?.detail || 'Request failed'
      console.error('API Error:', message)
      return Promise.reject(new Error(message))
    } else if (error.request) {
      console.error('Network Error:', error.message)
      return Promise.reject(new Error('Network error'))
    } else {
      return Promise.reject(error)
    }
  }
)

const apiClient = rawApiClient as unknown as ApiClient

export default apiClient

// ============ Resume API v2.0 ============
export const resumeApi = {
  list: (params: AnyRecord = {}): ApiResult<any> => apiClient.get('/resumes', { params }),
  get: (id: Id) => apiClient.get('/resumes/' + id),
  create: (data: AnyRecord) => apiClient.post('/resumes', data),
  update: (id: Id, data: AnyRecord) => apiClient.put('/resumes/' + id, data),
  delete: (id: Id) => apiClient.delete('/resumes/' + id),
  upload: (file: File, slot = 1, category = 'other', versionName: string | null = null) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('slot', String(slot))
    formData.append('category', category)
    if (versionName) formData.append('version_name', versionName)
    return apiClient.post('/resumes/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  saveText: (slot: number, content: string, category = 'other', versionName: string | null = null) => {
    return apiClient.post('/resumes/save-text', { slot, content, category, version_name: versionName })
  },
  getVersions: (resumeId: Id) => apiClient.get('/resumes/' + resumeId + '/versions'),
  createVersion: (resumeId: Id, data: AnyRecord) => apiClient.post('/resumes/' + resumeId + '/versions', data)
}

// ============ Application API v2.0 ============
export const applicationApi = {
  list: (params: AnyRecord = {}): ApiResult<any> => apiClient.get('/applications', { params }),
  get: (id: Id) => apiClient.get('/applications/' + id),
  create: (data: AnyRecord) => apiClient.post('/applications', data),
  update: (id: Id, data: AnyRecord) => apiClient.put('/applications/' + id, data),
  delete: (id: Id) => apiClient.delete('/applications/' + id),
  getByResume: (resumeId: Id) => apiClient.get('/applications/by-resume/' + resumeId),
  updateStatus: (id: Id, status: string) => apiClient.post('/applications/' + id + '/status', null, { params: { status } })
}

// ============ JD API v2.0 ============
export const jdApi = {
  list: (params: AnyRecord = {}) => apiClient.get('/jd', { params }),
  get: (id: Id) => apiClient.get('/jd/' + id),
  create: (data: AnyRecord) => apiClient.post('/jd', data),
  update: (id: Id, data: AnyRecord) => apiClient.put('/jd/' + id, data),
  delete: (id: Id) => apiClient.delete('/jd/' + id),
  analyze: (data: AnyRecord) => apiClient.post('/jd/analyze', data)
}

// ============ Optimize API v2.0 ============
export const optimizeApi = {
  full: (data: AnyRecord, config: RequestConfig = {}) => apiClient.post('/optimize/full', data, config),
  analyzeJd: (data: AnyRecord, config: RequestConfig = {}) => apiClient.post('/optimize/analyze-jd', data, config),
  compare: (resumeId: Id, versionId: Id | null = null) => {
    const params = versionId ? { version_id: versionId } : {}
    return apiClient.get('/optimize/compare/' + resumeId, { params })
  },
  versions: (resumeId: Id) => apiClient.get('/optimize/versions/' + resumeId)
}

// ============ Legacy APIs (keep for compatibility) ============
export const greetingApi = {
  listTemplates: () => apiClient.get('/greeting/templates'),
  createTemplate: (data: AnyRecord) => apiClient.post('/greeting/templates', data),
  updateTemplate: (id: Id, data: AnyRecord) => apiClient.put('/greeting/templates/' + id, data),
  deleteTemplate: (id: Id) => apiClient.delete('/greeting/templates/' + id),
  generate: (templateId: Id, jdContent: string, resumeContent: string | null = null) => apiClient.post('/greeting/generate', { template_id: templateId, jd_content: jdContent, resume_content: resumeContent })
}

export const agentApi = {
  chat: (message: string, history: unknown[] = [], state: unknown = null) => apiClient.post('/agent/chat', { message, history, state }),
  chatStream: (message: string, history: unknown[] = [], state: unknown = null) => {
    return fetch(API_BASE_URL + '/stream/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history, state, stream_thinking: true })
    })
  },
  getActions: () => apiClient.get('/agent/actions'),
  getWorkflow: () => apiClient.get('/agent/workflow')
}

export const agentHistoryApi = {
  list: () => apiClient.get('/agent/history'),
  get: (chatId: Id) => apiClient.get('/agent/history/' + chatId),
  save: (data: AnyRecord) => apiClient.post('/agent/history', data),
  delete: (chatId: Id) => apiClient.delete('/agent/history/' + chatId),
  clear: () => apiClient.delete('/agent/history')
}

export const matchApi = {
  analyze: (resumeText: string, jdContent: string, useAi = true) => apiClient.post('/match/analyze', { resume_text: resumeText, jd_content: jdContent, use_ai: useAi }),
  streamAnalyze: (resumeText: string, jdContent: string, useAi = true) => apiClient.post('/match/stream-analyze', { resume_text: resumeText, jd_content: jdContent, use_ai: useAi }, { responseType: 'stream' })
}

export const aiStatusApi = {
  getStatus: () => apiClient.get('/ai/status'),
  setDeepSeekKey: (apiKey: string, model?: string) => apiClient.post('/ai/set-api-key', { provider: 'deepseek', api_key: apiKey, model: model || 'deepseek-chat' })
}

export const settingsApi = {
  getAIStatus: () => apiClient.get('/ai/status'),
  setAPIKey: (provider: string, apiKey: string, model: string) => apiClient.post('/ai/set-api-key', { provider, api_key: apiKey, model }),
  setDeepSeekKey: (apiKey: string, model?: string) => apiClient.post('/ai/set-api-key', { provider: 'deepseek', api_key: apiKey, model: model || 'deepseek-chat' })
}

// ============ Score API ============
export const scoreApi = {
  analyze: (resumeContent: string, jdContent: string) => apiClient.post('/optimize/analyze-score', {
    resume_content: resumeContent,
    jd_content: jdContent
  })
}

// ============ Export API ============
export const exportApi = {
  exportAll: () => apiClient.get('/export/all'),
  exportResume: (resumeId: Id, includeVersions = true) => 
    apiClient.get('/export/resume/' + resumeId, { params: { include_versions: includeVersions } }),
  exportResumeText: (resumeId: Id) => apiClient.get('/export/resume-text/' + resumeId),
  exportApplications: (params: AnyRecord = {}) => apiClient.get('/export/applications', { params }),
  downloadBackup: async () => {
    const response = await fetch(API_BASE_URL + '/export/backup')
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const contentDisposition = response.headers.get('Content-Disposition') || ''
    let filename = 'job3_backup.json'
    if (contentDisposition) {
      const match = contentDisposition.match(/filename[^;\n"']+/i)
      if (match) {
        filename = match[0].replace('filename', '').replace('=', '').trim()
      }
    }
    a.download = decodeURIComponent(filename)
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }
}


// ============ Video Notes API锛堣棰戠瑪璁帮級 ============
export const videoApi = {
  generate: (data: AnyRecord) => apiClient.post('/video-notes/generate', data),
  listTasks: (limit = 50) => apiClient.get('/video-notes/tasks', { params: { limit } }),
  getTask: (taskId: Id) => apiClient.get('/video-notes/tasks/' + taskId),
  uploadLocal: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/video-notes/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  getConfig: () => apiClient.get('/video-notes/config'),
  saveConfig: (data: AnyRecord) => apiClient.post('/video-notes/config', data),
  exportObsidian: (taskId: Id) => apiClient.post('/video-notes/tasks/' + taskId + '/export-obsidian'),
  deleteTask: (taskId: Id) => apiClient.delete('/video-notes/tasks/' + taskId)
}


// ============ Dashboard API锛堟帶鍒跺彴鑱氬悎缁熻锛?============
export const dashboardApi = {
  stats: (params: AnyRecord = {}) => apiClient.get('/dashboard/stats', { params })
}
