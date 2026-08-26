/**
 * API 模块类型声明（对应 src/api/index.js）
 */

type AnyRecord = Record<string, unknown>

export interface ApiClient {
  get: (url: string, config?: AnyRecord) => Promise<any>
  post: (url: string, data?: unknown, config?: AnyRecord) => Promise<any>
  put: (url: string, data?: unknown, config?: AnyRecord) => Promise<any>
  delete: (url: string, config?: AnyRecord) => Promise<any>
}

declare const apiClient: ApiClient
export default apiClient

export const resumeApi: {
  list: (params?: AnyRecord) => Promise<any[]>
  get: (id: number) => Promise<any>
  create: (data: AnyRecord) => Promise<any>
  update: (id: number, data: AnyRecord) => Promise<any>
  delete: (id: number) => Promise<any>
  upload: (file: File, slot?: number, category?: string, versionName?: string | null) => Promise<any>
  saveText: (slot: number, content: string, category?: string, versionName?: string | null) => Promise<any>
  getVersions: (resumeId: number) => Promise<any>
  createVersion: (resumeId: number, data: AnyRecord) => Promise<any>
}

export const applicationApi: {
  list: (params?: AnyRecord) => Promise<any[]>
  get: (id: number) => Promise<any>
  create: (data: AnyRecord) => Promise<any>
  update: (id: number, data: AnyRecord) => Promise<any>
  delete: (id: number) => Promise<any>
  getByResume: (resumeId: number) => Promise<any[]>
  updateStatus: (id: number, status: string) => Promise<any>
}

export const jdApi: {
  list: (params?: AnyRecord) => Promise<any[]>
  get: (id: number) => Promise<any>
  create: (data: AnyRecord) => Promise<any>
  update: (id: number, data: AnyRecord) => Promise<any>
  delete: (id: number) => Promise<any>
  analyze: (data: AnyRecord) => Promise<any>
}

export const optimizeApi: {
  full: (data: AnyRecord) => Promise<any>
  analyzeJd: (data: AnyRecord) => Promise<any>
  compare: (resumeId: number, versionId?: number | null) => Promise<any>
  versions: (resumeId: number) => Promise<any>
}

export const greetingApi: {
  listTemplates: () => Promise<any>
  createTemplate: (data: AnyRecord) => Promise<any>
  updateTemplate: (id: number, data: AnyRecord) => Promise<any>
  deleteTemplate: (id: number) => Promise<any>
  generate: (templateId: number, jdContent: string, resumeContent?: string | null) => Promise<any>
}

export const agentApi: {
  chat: (message: string, history?: unknown[], state?: unknown) => Promise<any>
  chatStream: (message: string, history?: unknown[], state?: unknown) => Promise<Response>
  getActions: () => Promise<any>
  getWorkflow: () => Promise<any>
}

export const matchApi: {
  analyze: (resumeText: string, jdContent: string, useAi?: boolean) => Promise<any>
  streamAnalyze: (resumeText: string, jdContent: string, useAi?: boolean) => Promise<any>
}

export const aiStatusApi: {
  getStatus: () => Promise<{ ai_enabled?: boolean; provider?: string; model?: string; message?: string }>
  setDeepSeekKey: (apiKey: string, model?: string) => Promise<any>
}

export const settingsApi: {
  getAIStatus: () => Promise<any>
  setAPIKey: (provider: string, apiKey: string, model: string) => Promise<any>
  setDeepSeekKey: (apiKey: string, model?: string) => Promise<any>
}

export const videoApi: {
  generate: (data: {
    video_url: string
    platform?: string
    style?: string
    formats?: string[]
    extras?: string | null
    export_obsidian?: boolean
  }) => Promise<any>
  listTasks: (limit?: number) => Promise<any[]>
  getTask: (taskId: string) => Promise<any>
  uploadLocal: (file: File) => Promise<{ path: string; url: string }>
  getConfig: () => Promise<{
    obsidian_vault_path?: string
    obsidian_valid?: boolean
    obsidian_message?: string
    llm_configured?: boolean
    llm_provider?: string
    whisper_model?: string
  }>
  saveConfig: (data: { obsidian_vault_path: string }) => Promise<any>
  exportObsidian: (taskId: string) => Promise<{ ok: boolean; path: string }>
}
