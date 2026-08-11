// API 类型定义

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: ApiError
}

export interface ApiError {
  code: string
  message: string
  suggestion?: string
}

// 简历相关
export interface Resume {
  id?: number
  slot: number
  filename: string
  version_name?: string
  content?: string
  text?: string
  file_type?: string
  file_size?: number
  created_at?: string
  updated_at?: string
}

export interface ResumeUploadResponse {
  slot: number
  filename: string
  version_name: string
}

export interface ResumeListResponse {
  [slot: number]: Resume
}

// 投递记录相关
export interface Application {
  id: number
  company: string
  position: string
  status: ApplicationStatus
  salary?: string
  location?: string
  url?: string
  notes?: string
  created_at?: string
  updated_at?: string
}

export type ApplicationStatus = 
  | '待处理'
  | '已投递'
  | '笔试中'
  | '面试中'
  | '体检中'
  | 'Offer'
  | '已拒绝'
  | '已撤回'

export interface ApplicationCreate {
  company: string
  position: string
  status?: ApplicationStatus
  salary?: string
  location?: string
  url?: string
}

export interface ApplicationStats {
  total: number
  pending: number
  interview: number
  offer: number
  rejected: number
}

// JD 分析相关
export interface JDAnalysis {
  job_title?: string
  company?: string
  salary?: string
  location?: string
  skills?: string[]
  requirements?: string[]
  benefits?: string[]
  summary?: string
}

export interface JDParseRequest {
  content?: string
  url?: string
}

// AI 对话相关
export interface ChatMessage {
  role: 'user' | 'bot' | 'system'
  content: string
  time?: string
}

export interface ChatRequest {
  message: string
  history?: ChatMessage[]
  state?: Record<string, any>
}

export interface ChatResponse {
  content: string
  thinking?: string
}

export interface StreamChunk {
  type: 'content' | 'thinking' | 'done' | 'error'
  data: string
}

// 打招呼语相关
export interface GreetingTemplate {
  id: number
  name: string
  content: string
  vars: string[]
  isDefault: boolean
}

export interface GreetingGenerateRequest {
  template_id: number
  jd_content?: string
  resume_content?: string
}

export interface GreetingGenerateResponse {
  boss: string
  liepin: string
  email: string
}

// 匹配分析相关
export interface MatchAnalysisRequest {
  resume_text: string
  jd_content: string
  use_ai?: boolean
}

export interface MatchAnalysisResponse {
  score: number
  match_points: string[]
  gaps: string[]
  suggestions: string[]
}

// AI 配置相关
export interface AIStatus {
  enabled: boolean
  provider?: 'deepseek' | 'openai'
  model?: string
}

export interface SetAPIKeyRequest {
  provider: 'deepseek' | 'openai'
  api_key: string
  model?: string
}

// 优化相关
export interface OptimizationRequest {
  resume_text: string
  jd_content: string
}

export interface OptimizationResponse {
  optimized_resume: string
  score: number
  iterations: number
  verdict: 'PASS' | 'NEEDS_IMPROVEMENT' | 'REVISION_REQUIRED'
  status: 'completed' | 'failed' | 'partial'
  messages: AgentMessage[]
}

export interface AgentMessage {
  agent: string
  content: string
  timestamp: string
}

// 工具函数
export type LoadingState = 'idle' | 'loading' | 'success' | 'error'

export interface SelectOption {
  label: string
  value: string | number
}
