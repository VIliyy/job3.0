// ============================================================
// 信息拆解 · API 层
// USE_MOCK 切换：true = mock 演示（当前阶段），false = 真实后端
// 真实后端接口见 docs/拆解契约.md 第 6 章
// ============================================================

import { decomposeMock } from './mock'
import apiClient from '../index'
import type {
  CreateDecomposeTaskInput,
  DecomposeApi,
  DecomposeEvent,
  DecomposeHandlers,
  DecomposeStage,
  DecomposeTask,
  DecomposeTaskSummary,
  DecideGateInput
} from './types'

const USE_MOCK = false
export const DECOMPOSE_API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api'

export function buildDecomposeEventsUrl(taskId: string | number): string {
  return `${DECOMPOSE_API_BASE_URL}/decompose/tasks/${taskId}/events`
}

// ---------------- 真实后端实现（M3 阶段启用） ----------------
export const realApi: DecomposeApi = {
  createTask: (payload: CreateDecomposeTaskInput) => apiClient.post<DecomposeTask>('/decompose/tasks', payload),
  listTasks: (params: Record<string, unknown> = {}) => apiClient.get<DecomposeTaskSummary[]>('/decompose/tasks', { params }),
  getTask: (id: string | number) => apiClient.get<DecomposeTask>('/decompose/tasks/' + id),
  getGates: (taskId: string | number) => apiClient.get('/decompose/tasks/' + taskId + '/gates'),
  decideGate: (gateId: string | number, data: DecideGateInput) => apiClient.post<DecomposeTask>('/decompose/gates/' + gateId + '/decide', data),
  rerun: (taskId: string | number, fromStage: DecomposeStage) => apiClient.post<{ id: string; state: DecomposeTask['state']; version: number }>('/decompose/tasks/' + taskId + '/rerun', { from_stage: fromStage }),
  deleteTask: (taskId: string | number) => apiClient.delete<{ ok: boolean; id: string }>('/decompose/tasks/' + taskId),
  exportTask: (taskId: string | number) => apiClient.post<{ markdown: string; filename: string }>('/decompose/tasks/' + taskId + '/export'),
  // SSE：真实版用 EventSource，保持 subscribeEvents(taskId, handlers) -> unsubscribe 形状
  subscribeEvents: (taskId: string | number, handlers: DecomposeHandlers) => {
    const source = new EventSource(buildDecomposeEventsUrl(taskId))
    const parseEvent = (event: Event): DecomposeEvent | null => {
      const data = (event as MessageEvent).data
      if (typeof data !== 'string' || !data) return null
      try {
        return JSON.parse(data) as DecomposeEvent
      } catch {
        return null
      }
    }
    source.addEventListener('thinking', (e) => { const data = parseEvent(e); if (data) handlers.thinking?.(data) })
    source.addEventListener('output', (e) => { const data = parseEvent(e); if (data) handlers.output?.(data) })
    source.addEventListener('gate', (e) => { const data = parseEvent(e); if (data) handlers.gate?.(data) })
    source.addEventListener('complete', (e) => { const data = parseEvent(e); if (data) handlers.complete?.(data) })
    source.addEventListener('error', (e) => { const data = parseEvent(e); if (data) handlers.error?.(data) })
    return () => source.close()
  }
}

export const decomposeApi = USE_MOCK ? decomposeMock : realApi

export { USE_MOCK }
