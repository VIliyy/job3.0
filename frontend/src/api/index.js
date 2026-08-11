import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' }
})

apiClient.interceptors.request.use(
  config => config,
  error => Promise.reject(error)
)

apiClient.interceptors.response.use(
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

export default apiClient

// ============ Resume API v2.0 ============
export const resumeApi = {
  list: (params = {}) => apiClient.get('/resumes', { params }),
  get: (id) => apiClient.get('/resumes/' + id),
  create: (data) => apiClient.post('/resumes', data),
  update: (id, data) => apiClient.put('/resumes/' + id, data),
  delete: (id) => apiClient.delete('/resumes/' + id),
  upload: (file, slot = 1, category = 'other', versionName = null) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('slot', slot)
    formData.append('category', category)
    if (versionName) formData.append('version_name', versionName)
    return apiClient.post('/resumes/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  saveText: (slot, content, category = 'other', versionName = null) => {
    return apiClient.post('/resumes/save-text', { slot, content, category, version_name: versionName })
  },
  getVersions: (resumeId) => apiClient.get('/resumes/' + resumeId + '/versions'),
  createVersion: (resumeId, data) => apiClient.post('/resumes/' + resumeId + '/versions', data)
}

// ============ Application API v2.0 ============
export const applicationApi = {
  list: (params = {}) => apiClient.get('/applications', { params }),
  get: (id) => apiClient.get('/applications/' + id),
  create: (data) => apiClient.post('/applications', data),
  update: (id, data) => apiClient.put('/applications/' + id, data),
  delete: (id) => apiClient.delete('/applications/' + id),
  getByResume: (resumeId) => apiClient.get('/applications/by-resume/' + resumeId),
  updateStatus: (id, status) => apiClient.post('/applications/' + id + '/status', null, { params: { status } })
}

// ============ JD API v2.0 ============
export const jdApi = {
  list: (params = {}) => apiClient.get('/jd', { params }),
  get: (id) => apiClient.get('/jd/' + id),
  create: (data) => apiClient.post('/jd', data),
  update: (id, data) => apiClient.put('/jd/' + id, data),
  delete: (id) => apiClient.delete('/jd/' + id),
  analyze: (data) => apiClient.post('/jd/analyze', data)
}

// ============ Optimize API v2.0 ============
export const optimizeApi = {
  full: (data) => apiClient.post('/optimize/full', data),
  analyzeJd: (data) => apiClient.post('/optimize/analyze-jd', data),
  compare: (resumeId, versionId = null) => {
    const params = versionId ? { version_id: versionId } : {}
    return apiClient.get('/optimize/compare/' + resumeId, { params })
  },
  versions: (resumeId) => apiClient.get('/optimize/versions/' + resumeId)
}

// ============ Legacy APIs (keep for compatibility) ============
export const greetingApi = {
  listTemplates: () => apiClient.get('/greeting/templates'),
  createTemplate: (data) => apiClient.post('/greeting/templates', data),
  updateTemplate: (id, data) => apiClient.put('/greeting/templates/' + id, data),
  deleteTemplate: (id) => apiClient.delete('/greeting/templates/' + id),
  generate: (templateId, jdContent, resumeContent = null) => apiClient.post('/greeting/generate', { template_id: templateId, jd_content: jdContent, resume_content: resumeContent })
}

export const agentApi = {
  chat: (message, history = [], state = null) => apiClient.post('/agent/chat', { message, history, state }),
  chatStream: (message, history = [], state = null) => {
    return fetch(API_BASE_URL + '/stream/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history, state, stream_thinking: true })
    })
  },
  getActions: () => apiClient.get('/agent/actions'),
  getWorkflow: () => apiClient.get('/agent/workflow')
}

export const matchApi = {
  analyze: (resumeText, jdContent, useAi = true) => apiClient.post('/match/analyze', { resume_text: resumeText, jd_content: jdContent, use_ai: useAi }),
  streamAnalyze: (resumeText, jdContent, useAi = true) => apiClient.post('/match/stream-analyze', { resume_text: resumeText, jd_content: jdContent, use_ai: useAi }, { responseType: 'stream' })
}

export const aiStatusApi = {
  getStatus: () => apiClient.get('/ai/status'),
  setDeepSeekKey: (apiKey, model) => apiClient.post('/ai/set-api-key', { provider: 'deepseek', api_key: apiKey, model: model || 'deepseek-chat' })
}

export const settingsApi = {
  getAIStatus: () => apiClient.get('/ai/status'),
  setAPIKey: (provider, apiKey, model) => apiClient.post('/ai/set-api-key', { provider, api_key: apiKey, model }),
  setDeepSeekKey: (apiKey, model) => apiClient.post('/ai/set-api-key', { provider: 'deepseek', api_key: apiKey, model: model || 'deepseek-chat' })
}

// ============ Score API ============
export const scoreApi = {
  analyze: (resumeContent, jdContent) => apiClient.post('/optimize/analyze-score', {
    resume_content: resumeContent,
    jd_content: jdContent
  })
}

// ============ Export API ============
export const exportApi = {
  exportAll: () => apiClient.get('/export/all'),
  exportResume: (resumeId, includeVersions = true) => 
    apiClient.get('/export/resume/' + resumeId, { params: { include_versions: includeVersions } }),
  exportResumeText: (resumeId) => apiClient.get('/export/resume-text/' + resumeId),
  exportApplications: (params = {}) => apiClient.get('/export/applications', { params }),
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
