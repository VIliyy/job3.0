export type DecomposeState =
  | 'DRAFT'
  | 'BRIEF_REVIEW'
  | 'DECOMPOSING'
  | 'FACTS_REVIEW'
  | 'INSIGHTING'
  | 'INSIGHT_REVIEW'
  | 'REPORTING'
  | 'DONE'
  | 'FAILED'

export type DecomposeGateKey = 'A' | 'B' | 'C'
export type DecomposeGateState = 'idle' | 'pending' | 'approved'
export type DecomposeDecisionAction = 'approve' | 'regenerate'
export type DecomposeStage = 'S0' | 'S1' | 'S2' | 'S3'

export interface CreateDecomposeTaskInput {
  content: string
  target?: string
}

export interface DecomposeFact {
  id: string
  kind: string
  content: string
  anchor: string
  confidence: string
}

export interface DecomposeInference {
  id: string
  type: string
  content: string
  evidence: string[]
  confidence: string
}

export interface DecomposeReportSection {
  type: string
  title: string
  content: string
  evidence: string[]
}

export interface DecomposeContractMeta {
  source_type: string
  word_count: number
  target_question: string
  errors: string[]
  data_gaps: string[]
  exported_at?: string
  summary?: string
  sections?: DecomposeReportSection[]
  actions?: string[]
}

export interface DecomposeContract {
  contract_name: DecomposeStage
  version: number
  status: string
  created_at: string
  facts: DecomposeFact[]
  inferences: DecomposeInference[]
  meta: DecomposeContractMeta
}

export interface DecomposeGate {
  id: string
  name: string
  state: DecomposeGateState
  decided_at: string | null
  note: string
}

export interface DecomposeSource {
  content: string
  target: string
}

export interface DecomposeTask {
  id: string
  title: string
  state: DecomposeState
  version: number
  created_at: string
  source: DecomposeSource
  contracts: Partial<Record<DecomposeStage, DecomposeContract>>
  gates: Record<DecomposeGateKey, DecomposeGate>
  error: string | null
}

export interface DecomposeTaskSummary {
  id: string
  title: string
  state: DecomposeState
  version: number
  created_at: string
  error: string | null
  gates: Record<DecomposeGateKey, DecomposeGate>
}

export interface DecideGateInput {
  action: DecomposeDecisionAction
  note?: string
}

export interface DecomposeEvent {
  type: 'thinking' | 'output' | 'gate' | 'complete' | 'error'
  task_id: string
  message?: string
  contract?: DecomposeStage
  gate?: DecomposeGateKey
  contract_body?: DecomposeContract
}

export interface DecomposeHandlers {
  thinking?: (event: DecomposeEvent) => void
  output?: (event: DecomposeEvent) => void
  gate?: (event: DecomposeEvent) => void
  complete?: (event: DecomposeEvent) => void
  error?: (event: DecomposeEvent) => void
}

export interface DecomposeApi {
  createTask(payload: CreateDecomposeTaskInput): Promise<DecomposeTask>
  listTasks(params?: Record<string, unknown>): Promise<DecomposeTaskSummary[]>
  getTask(id: string | number): Promise<DecomposeTask>
  getGates(taskId: string | number): Promise<DecomposeGate[]>
  decideGate(gateId: string | number, data: DecideGateInput): Promise<DecomposeTask>
  rerun(taskId: string | number, fromStage: DecomposeStage): Promise<{ id: string; state: DecomposeState; version: number }>
  deleteTask(taskId: string | number): Promise<{ ok: boolean; id: string }>
  exportTask(taskId: string | number): Promise<{ markdown: string; filename: string }>
  subscribeEvents(taskId: string | number, handlers: DecomposeHandlers): () => void
}
