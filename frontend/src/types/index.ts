// Job3.0 ????

// ????
export interface Resume {
  id: number
  slot: number
  filename?: string
  version_name?: string
  category: ResumeCategory
  status: ResumeStatus
  content?: string
  file_type?: string
  current_jd_id?: number
  latest_optimized_version_id?: number
  created_at?: string
  updated_at?: string
}

export type ResumeCategory = 'tech' | 'product' | 'ops' | 'marketing' | 'other'
export type ResumeStatus = 'draft' | 'processing' | 'optimized' | 'applied' | 'archived'

export interface ResumeVersion {
  id: number
  resume_id: number
  version_number: number
  version_name?: string
  content: string
  original_content?: string
  optimization_score?: number
  original_score?: number
  change_summary?: string
  diff_highlights?: DiffHighlight[]
  jd_id?: number
  created_at?: string
}

export interface DiffHighlight {
  type: 'added' | 'removed' | 'modified'
  content: string
  original?: string
  new?: string
}

// ??????
export interface Application {
  id: number
  resume_id?: number
  company: string
  position?: string
  location?: string
  salary?: string
  status: ApplicationStatus
  source_url?: string
  notes?: string
  applied_at?: string
  created_at?: string
  updated_at?: string
}

export type ApplicationStatus = 'pending' | 'viewed' | 'interview' | 'offer' | 'rejected' | 'withdrawn'

// JD ????
export interface JDAnalysis {
  id: number
  company?: string
  position?: string
  source_url?: string
  raw_content: string
  skills?: string[]
  keywords?: string[]
  requirements?: string[]
  preferred_skills?: string[]
  fit_score?: number
  created_at?: string
}

// ????
export interface OptimizationResult {
  version_id: number
  version_number: number
  optimized_content: string
  original_score: number
  optimized_score: number
  change_summary: string
  diff_highlights: DiffHighlight[]
  jd_analysis?: JDAnalysis
}

// ????
export interface ScoreAnalysis {
  scores: number[]
  total_score: number
  labels: string[]
  matched_keywords: string[]
  missing_keywords: string[]
  suggestions: Suggestion[]
}

export interface Suggestion {
  priority: 'high' | 'medium' | 'low'
  text: string
}

// Agent ??
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  time?: string
  actions?: string[]
}

export interface ChatState {
  resume_text?: string
  has_resume?: boolean
  target_jd?: string
  target_company?: string
}

// ????
export interface ExportData {
  resumes: Resume[]
  applications: Application[]
  export_time: string
  version: string
}

// API ??
export interface ApiResponse<T> {
  data?: T
  error?: string
  message?: string
}

// ??
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
