<template>
  <div class="decompose-page">
    <div class="page-header">
      <h1>信息拆解</h1>
      <p class="page-desc">粘贴一段原始材料，自动完成 解析 → 事实拆解 → 洞察生成 → 报告合成，每段由你把关</p>
    </div>

    <div class="layout">
      <!-- ============ 左列：输入 + 历史 ============ -->
      <div class="left-col">
        <div class="card">
          <h2>新建拆解</h2>
          <div class="form-group">
            <label>原始材料</label>
            <textarea
              v-model="form.content"
              class="input source-input"
              rows="7"
              placeholder="粘贴要拆解的文本（产品描述 / 招聘 JD / 文档片段…）"
            ></textarea>
          </div>
          <div class="form-group">
            <label>拆解目标（可选）</label>
            <input
              v-model="form.target"
              class="input"
              placeholder="例如：提取卖点与风险 / 归纳岗位要求"
            />
          </div>
          <button class="btn-primary" :disabled="busy" @click="createTask">
            {{ busy ? '创建中…' : '开始拆解' }}
          </button>
        </div>

        <div class="card">
          <h2>任务记录</h2>
          <div v-if="tasks.length === 0" class="empty">暂无任务，粘贴材料开始吧</div>
          <div
            v-for="t in tasks"
            :key="t.id"
            class="task-item"
            :class="{ active: current && current.id === t.id }"
            @click="openTask(t.id)"
          >
            <div class="task-head">
              <span class="task-title">{{ t.title }}</span>
              <span class="badge" :class="badgeClass(t.state)">{{ stateText(t.state) }}</span>
              <button class="task-del" title="删除任务" @click.stop="onDeleteTask(t.id)">✕</button>
            </div>
            <div class="task-meta">
              {{ t.created_at.slice(5, 16).replace('T', ' ') }} · v{{ t.version }}
              <span v-if="t.error" class="task-error">失败</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ============ 右列：任务视图 ============ -->
      <div class="right-col">
        <div v-if="!current" class="card empty-card">
          <div class="empty">选择左侧任务查看拆解进度，或粘贴材料新建任务</div>
        </div>

        <template v-else>
          <!-- 顶栏 -->
          <div class="task-bar">
            <div>
              <div class="task-bar-title">{{ current.title }}</div>
              <div class="task-bar-meta">
                {{ stateText(current.state) }}
                <template v-if="current.state !== 'DRAFT'">
                  · 任务 v{{ current.version }} · {{ current.created_at.slice(5, 16).replace('T', ' ') }}
                </template>
              </div>
            </div>
            <div class="task-bar-actions">
              <button
                v-if="current.state === 'FAILED'"
                class="btn-primary"
                @click="onRerun('S0')"
              >重试（从头重跑）</button>
              <button
                v-else-if="['DONE', 'REPORTING', 'INSIGHT_REVIEW'].includes(current.state)"
                class="btn-primary"
                :disabled="exporting"
                @click="onExport"
              >{{ exporting ? '导出中…' : '导出 Markdown' }}</button>
              <button
                v-else-if="current.state === 'BRIEF_REVIEW'"
                class="btn-secondary"
                @click="onRerun('S0')"
              >从头重跑</button>
            </div>
          </div>

          <!-- 失败 -->
          <div v-if="current.state === 'FAILED'" class="card error-card">
            <div class="error-title">拆解失败</div>
            <div class="error-msg">{{ current.error }}</div>
            <div class="error-hint">原因已记录，可点击右上角「重试」从头重跑</div>
          </div>

          <!-- 流水线 -->
          <div class="card pipeline-card">
            <PipelineView
              :task-state="current.state"
              :contracts="current.contracts"
              :gates="current.gates"
            />
          </div>

          <!-- 闸门A：Brief 确认 -->
          <div v-if="current.state === 'BRIEF_REVIEW'" class="card">
            <GatePanel
              :gate="current.gates.A"
              :contract-version="(current.contracts.S0 || {}).version || 1"
              @decide="onDecide('A', $event)"
            >
              <div class="brief-box">
                <div class="brief-item">
                  <span class="brief-label">拆解目标</span>
                  <p>{{ briefContent }}</p>
                </div>
                <div class="brief-item">
                  <span class="brief-label">材料概况</span>
                  <p>{{ metaLine }}</p>
                </div>
                <div v-if="current.contracts.S0 && current.contracts.S0.facts.length" class="brief-item">
                  <span class="brief-label">来源事实</span>
                  <div v-for="f in current.contracts.S0.facts" :key="f.id" class="mini-fact">
                    <span class="fact-id">{{ f.id }}</span>{{ f.content }}
                  </div>
                </div>
              </div>
            </GatePanel>
          </div>

          <!-- 运行中提示 -->
          <div v-if="['DECOMPOSING', 'INSIGHTING', 'REPORTING'].includes(current.state)" class="card">
            <div class="running-hint">
              <span class="running-spin">◐</span>
              <span>{{ runningText }}</span>
            </div>
          </div>

          <!-- 闸门B：事实清单 -->
          <div v-if="current.state === 'FACTS_REVIEW'" class="card">
            <GatePanel
              :gate="current.gates.B"
              :contract-version="(current.contracts.S1 || {}).version || 1"
              :flags="flags"
              @decide="onDecide('B', $event)"
            >
              <div class="section-label">已拆出 {{ (current.contracts.S1 || {}).facts?.length || 0 }} 条事实，可标记 对 / 错 / 缺</div>
              <FactList
                :facts="(current.contracts.S1 || {}).facts || []"
                :editable="true"
                v-model:flags="flags"
              />
              <div v-if="dataGaps.length" class="gaps-box">
                <div class="gaps-title">数据缺口</div>
                <div v-for="(gap, i) in dataGaps" :key="i" class="gap-line">· {{ gap }}</div>
              </div>
            </GatePanel>
          </div>

          <!-- 闸门C：结论确认 -->
          <div v-if="current.state === 'INSIGHT_REVIEW'" class="card">
            <GatePanel
              :gate="current.gates.C"
              :contract-version="(current.contracts.S2 || {}).version || 1"
              @decide="onDecide('C', $event)"
            >
              <div class="section-label">以下结论基于已确认事实生成，点击卡片查看证据链</div>
              <div class="conclusion-grid">
                <ConclusionCard
                  v-for="inf in (current.contracts.S2 || {}).inferences || []"
                  :key="inf.id"
                  :inference="inf"
                  @open-evidence="openEvidence(inf)"
                />
              </div>
            </GatePanel>
          </div>

          <!-- 结果驾驶舱 -->
          <div v-if="['REPORTING', 'DONE'].includes(current.state)" class="card">
            <div class="section-label">核心结论（点击卡片查看证据链）</div>
            <div class="conclusion-grid">
              <ConclusionCard
                v-for="inf in conclusionList"
                :key="inf.id"
                :inference="inf"
                @open-evidence="openEvidence(inf)"
              />
            </div>
          </div>

          <!-- 完整报告（直接展示，无需下载） -->
          <div v-if="current.state === 'DONE' && current.contracts.S3" class="card">
            <div class="section-label">完整报告（可直接阅读，也可下载 Markdown 存档）</div>
            <div class="report-body">
              <div class="report-block">
                <div class="report-h">① 执行摘要</div>
                <p class="report-text">{{ execSummary }}</p>
              </div>
              <div class="report-block">
                <div class="report-h">② 结论（按要点）</div>
                <div v-if="execSections.length">
                  <div v-for="sec in execSections" :key="sec.type" class="report-sub">
                    <div class="report-sub-title">{{ sec.title || typeLabel(sec.type) }}</div>
                    <p class="report-text">{{ sec.content }}</p>
                    <div v-if="sec.evidence && sec.evidence.length" class="report-evidence">
                      <span class="report-ev-label">证据</span>
                      <span v-for="e in sec.evidence" :key="e" class="report-ev-chip">{{ e }}</span>
                    </div>
                  </div>
                </div>
                <div v-else class="report-muted">无分要点结论</div>
              </div>
              <div class="report-block">
                <div class="report-h">③ 结论明细</div>
                <div v-for="inf in conclusionList" :key="inf.id" class="report-line">
                  <ConfidenceBadge :level="inf.confidence || 'C2'" />
                  <span class="report-type">{{ typeLabel(inf.type) }}</span>
                  <span class="report-line-text">{{ inf.content }}</span>
                  <span v-if="inf.evidence && inf.evidence.length" class="report-evidence-inline">证据 {{ inf.evidence.join('、') }}</span>
                </div>
              </div>
              <div class="report-block">
                <div class="report-h">④ 事实清单</div>
                <FactList :facts="(current.contracts.S1 || {}).facts || []" :editable="false" />
              </div>
              <div class="report-block">
                <div class="report-h">⑤ 数据缺口</div>
                <div v-if="dataGaps.length" class="gaps-box">
                  <div class="gaps-title">数据缺口</div>
                  <div v-for="(gap, i) in dataGaps" :key="i" class="gap-line">· {{ gap }}</div>
                </div>
                <div v-else class="report-muted">无</div>
              </div>
              <div class="report-block">
                <div class="report-h">⑥ 闸门确认记录</div>
                <div v-if="gateRecords.length">
                  <div v-for="g in gateRecords" :key="g.key" class="report-line">
                    <span class="report-type">闸门 {{ g.key }}</span>
                    <span class="report-line-text">{{ g.name }}</span>
                    <span class="report-muted-inline">{{ g.note ? `意见：${g.note}` : '确认' }} @ {{ g.decided_at || '' }}</span>
                  </div>
                </div>
                <div v-else class="report-muted">无</div>
              </div>
              <div class="report-block">
                <div class="report-h">⑦ 下一步建议</div>
                <div v-if="execActions.length">
                  <div v-for="(a, i) in execActions" :key="i" class="report-line">· {{ a }}</div>
                </div>
                <div v-else class="report-muted">无</div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- 证据链抽屉 -->
    <EvidenceDrawer
      :visible="drawerVisible"
      :inference="drawerInference"
      :facts="(current && current.contracts.S1 && current.contracts.S1.facts) || []"
      @close="drawerVisible = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { decomposeApi } from '../api/decompose'
import type {
  DecomposeEvent,
  DecomposeGateKey,
  DecomposeInference,
  DecomposeState,
  DecomposeTask,
  DecomposeTaskSummary,
  DecideGateInput,
  DecomposeStage
} from '../api/decompose/types'
import { toast } from '../composables/useToast'
import PipelineView from '../components/decompose/PipelineView.vue'
import GatePanel from '../components/decompose/GatePanel.vue'
import FactList from '../components/decompose/FactList.vue'
import ConclusionCard from '../components/decompose/ConclusionCard.vue'
import EvidenceDrawer from '../components/decompose/EvidenceDrawer.vue'

const tasks = ref<DecomposeTaskSummary[]>([])
const current = ref<DecomposeTask | null>(null)
const busy = ref(false)
const exporting = ref(false)
const flags = ref<Record<string, string>>({})
const drawerVisible = ref(false)
const drawerInference = ref<DecomposeInference | null>(null)

const form = reactive<{ content: string; target: string }>({ content: '', target: '' })
let unsubscribe: (() => void) | null = null

const STATE_TEXT: Record<string, string> = {
  DRAFT: '草稿',
  BRIEF_REVIEW: '等待确认目标',
  DECOMPOSING: '事实拆解中',
  FACTS_REVIEW: '等待确认事实',
  INSIGHTING: '洞察生成中',
  INSIGHT_REVIEW: '等待确认结论',
  REPORTING: '报告合成中',
  DONE: '已完成',
  FAILED: '失败'
}
function stateText(state: string) { return STATE_TEXT[state] || state }

function badgeClass(state: DecomposeState | string) {
  return {
    DONE: 'ok', BRIEF_REVIEW: 'warn', FACTS_REVIEW: 'warn', INSIGHT_REVIEW: 'warn',
    DECOMPOSING: 'run', INSIGHTING: 'run', REPORTING: 'run',
    FAILED: 'fail', DRAFT: 'idle'
  }[state] || 'idle'
}

const briefContent = computed(() => {
  const s0 = current.value?.contracts?.S0
  const brief = s0?.inferences?.find((i) => i.type === 'brief')
  return brief ? brief.content : '—'
})

const metaLine = computed(() => {
  const s0 = current.value?.contracts?.S0
  const fact = s0?.facts?.[0]
  return fact ? fact.content : '—'
})

const dataGaps = computed(() => {
  const s1 = current.value?.contracts?.S1
  return (s1 && s1.meta && s1.meta.data_gaps) || []
})

const execSummary = computed(() => current.value?.contracts?.S3?.meta?.summary || '—')
const execActions = computed(() => current.value?.contracts?.S3?.meta?.actions || [])
const execSections = computed(() => current.value?.contracts?.S3?.meta?.sections || [])

const gateRecords = computed(() => {
  const gates = current.value?.gates
  const gateKeys: DecomposeGateKey[] = ['A', 'B', 'C']
  return gateKeys
    .map((key) => ({ key, ...(gates?.[key] || {}) }))
    .filter((g) => g.state === 'approved' || g.note)
})

const TYPE_LABELS: Record<string, string> = {
  usp: '卖点', pricing: '定价', risk: '风险', opportunity: '机会',
  audience: '人群', action: '建议', brief: '目标', cluster: '聚类', info: '信息'
}
function typeLabel(type: string) { return TYPE_LABELS[type] || type }

const conclusionList = computed(() => {
  const s3 = current.value?.contracts?.S3
  const s2 = current.value?.contracts?.S2
  return (s3 && s3.inferences) || (s2 && s2.inferences) || []
})

const runningText = computed(() => {
  const labels: Record<string, string> = {
    DECOMPOSING: 'S1 事实拆解中：逐句拆解并标注原文锚点…',
    INSIGHTING: 'S2 洞察生成中：基于已确认事实归纳结论…',
    REPORTING: 'S3 报告合成中：汇总已确认结论…'
  }
  return labels[current.value?.state || ''] || '处理中…'
})

// ---------------- 任务操作 ----------------

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error)
}

async function refreshList(): Promise<void> {
  tasks.value = await decomposeApi.listTasks()
}

async function refreshCurrent(): Promise<void> {
  if (!current.value) return
  try {
    current.value = await decomposeApi.getTask(current.value.id)
  } catch (e: unknown) {
    toast.error(errorMessage(e))
  }
}

function subscribe(id: string): void {
  if (unsubscribe) unsubscribe()
  unsubscribe = decomposeApi.subscribeEvents(id, {
    thinking: () => refreshCurrent(),
    output: () => refreshCurrent(),
    gate: (e: DecomposeEvent) => { refreshCurrent(); refreshList(); toast.info(e.message || '到达闸门，等待确认') },
    complete: () => { refreshCurrent(); refreshList(); toast.success('拆解完成') },
    error: (e: DecomposeEvent) => { refreshCurrent(); refreshList(); toast.error(e.message || '拆解失败') }
  })
}

async function createTask(): Promise<void> {
  if (!form.content.trim()) {
    toast.warning('请先粘贴要拆解的材料')
    return
  }
  busy.value = true
  try {
    const task = await decomposeApi.createTask({ ...form })
    await refreshList()
    await openTask(task.id)
    toast.success('任务已创建')
  } catch (e: unknown) {
    toast.error(errorMessage(e))
  } finally {
    busy.value = false
  }
}

async function onDeleteTask(id: string): Promise<void> {
  const title = tasks.value.find((t) => t.id === id)?.title || '该任务'
  if (!window.confirm(`确定删除「${title}」？删除后不可恢复。`)) return
  try {
    await decomposeApi.deleteTask(id)
    if (unsubscribe) {
      unsubscribe()
      unsubscribe = null
    }
    if (current.value && current.value.id === id) {
      current.value = null
      drawerVisible.value = false
      drawerInference.value = null
    }
    refreshList()
    toast.success('任务已删除')
  } catch (e: unknown) {
    toast.error(errorMessage(e) || '删除失败')
  }
}

async function openTask(id: string): Promise<void> {
  try {
    subscribe(id)
    current.value = await decomposeApi.getTask(id)
    flags.value = {}
  } catch (e: unknown) {
    toast.error(errorMessage(e))
  }
}

async function onDecide(gateKey: DecomposeGateKey, { action, note }: DecideGateInput): Promise<void> {
  const task = current.value
  if (!task) return
  const gate = task.gates[gateKey]
  if (!gate) return
  try {
    await decomposeApi.decideGate(gate.id, { action, note })
    await refreshCurrent()
    await refreshList()
  } catch (e: unknown) {
    toast.error(errorMessage(e))
  }
}

async function onRerun(from: DecomposeStage): Promise<void> {
  if (!current.value) return
  try {
    await decomposeApi.rerun(current.value.id, from)
    await refreshCurrent()
    await refreshList()
    toast.info('已重新启动拆解')
  } catch (e: unknown) {
    toast.error(errorMessage(e))
  }
}

async function onExport() {
  const task = current.value
  if (!task) return
  exporting.value = true
  try {
    const { markdown } = await decomposeApi.exportTask(task.id)
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${task.title.replace(/[\\/:*?"<>|]/g, '_')}.md`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('已导出 Markdown 报告')
  } catch (e: unknown) {
    toast.error(errorMessage(e))
  } finally {
    exporting.value = false
  }
}

function openEvidence(inference: DecomposeInference): void {
  drawerInference.value = inference
  drawerVisible.value = true
}

onMounted(() => { refreshList() })
onUnmounted(() => { if (unsubscribe) unsubscribe() })
</script>

<style scoped>
.decompose-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.page-header { margin-bottom: 24px; }
.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text-primary);
}
.page-desc { font-size: 15px; color: var(--text-secondary); }

.layout { display: grid; grid-template-columns: 380px 1fr; gap: 20px; align-items: start; }
@media (max-width: 1000px) { .layout { grid-template-columns: 1fr; } }
.left-col, .right-col { display: flex; flex-direction: column; gap: 20px; }

/* 卡片（对齐整体设计：elevated 底 + 12px 圆角） */
.card {
  background: var(--surface-elevated);
  border: 1px solid var(--border-default);
  border-radius: 12px;
  padding: 24px;
}
.card h2 { font-size: 16px; font-weight: 600; margin: 0 0 16px; color: var(--text-primary); }
.left-col .card { padding: 20px; }
.empty-card { min-height: 320px; display: flex; align-items: center; justify-content: center; }

/* 表单 */
.form-group { margin-bottom: 14px; }
.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 6px;
  color: var(--text-secondary);
}
.input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-default);
  border-radius: 8px;
  font-size: 14px;
  background: var(--surface-input);
  color: var(--text-primary);
}
.input:focus { outline: none; border-color: var(--color-action-blue); }
textarea.input { font-family: inherit; resize: vertical; line-height: 1.6; }
.source-input { min-height: 140px; }
.form-hint { font-size: 12px; color: var(--text-muted); margin-top: 6px; }

/* 按钮 */
.btn-primary {
  width: 100%;
  padding: 12px;
  background: var(--color-action-blue);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.btn-primary:hover { background: var(--color-focus-blue); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-secondary {
  padding: 9px 20px;
  background: var(--surface-stone);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}
.btn-secondary:hover { border-color: var(--color-action-blue); color: var(--color-action-blue); }
.btn-secondary:disabled { opacity: 0.5; cursor: not-allowed; }

/* 任务列表 */
.task-item {
  padding: 12px;
  border: 1px solid var(--border-default);
  border-radius: 10px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 150ms;
  background: var(--surface-default);
}
.task-item:hover { border-color: var(--color-action-blue); }
.task-item.active { border-color: var(--color-action-blue); background: rgba(37, 99, 235, 0.06); }
.task-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.task-del {
  border: none;
  background: none;
  color: var(--text-muted);
  font-size: 12px;
  padding: 2px 7px;
  border-radius: 6px;
  cursor: pointer;
  flex-shrink: 0;
}
.task-del:hover { color: var(--color-error); background: rgba(239, 68, 68, 0.08); }
.task-title { font-size: 13px; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.task-meta { font-size: 12px; color: var(--text-muted); margin-top: 4px; display: flex; gap: 8px; }
.task-error { color: var(--color-error); }

.badge { padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600; white-space: nowrap; }
.badge.ok { background: rgba(16, 185, 129, 0.15); color: var(--color-success); }
.badge.warn { background: rgba(245, 158, 11, 0.15); color: var(--color-warning); }
.badge.run { background: rgba(59, 130, 246, 0.15); color: var(--color-action-blue); }
.badge.fail { background: rgba(239, 68, 68, 0.15); color: var(--color-error); }
.badge.idle { background: var(--surface-stone); color: var(--text-muted); }

/* 任务顶栏 */
.task-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: var(--surface-elevated);
  border: 1px solid var(--border-default);
  border-radius: 12px;
}
.task-bar-title { font-size: 18px; font-weight: 700; color: var(--text-primary); }
.task-bar-meta { font-size: 13px; color: var(--text-muted); margin-top: 4px; }
.task-bar-actions { display: flex; gap: 10px; }
.task-bar-actions .btn-primary { width: auto; padding: 9px 22px; border-radius: 8px; }

/* 流水线卡片 */
.pipeline-card { padding: 16px 20px; }

/* 失败 */
.error-card { border-color: rgba(239, 68, 68, 0.4); background: rgba(239, 68, 68, 0.05); }
.error-title { font-size: 15px; font-weight: 600; color: var(--color-error); }
.error-msg { font-size: 14px; margin-top: 8px; color: var(--text-primary); }
.error-hint { font-size: 12px; color: var(--text-muted); margin-top: 6px; }

/* 运行中 */
.running-hint {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: var(--text-secondary);
}
.running-spin { color: var(--color-action-blue); animation: spin 1s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }

.section-label { font-size: 13px; color: var(--text-secondary); margin-bottom: 12px; }
.conclusion-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 12px; }

/* Brief 内容 */
.brief-box { display: flex; flex-direction: column; gap: 10px; }
.brief-item {
  background: var(--surface-elevated);
  border: 1px solid var(--border-default);
  border-radius: 10px;
  padding: 12px 14px;
}
.brief-label { font-size: 11px; font-weight: 600; color: var(--color-action-blue); }
.brief-item p { font-size: 14px; margin-top: 4px; line-height: 1.6; color: var(--text-primary); }
.mini-fact { font-size: 13px; color: var(--text-body); margin-top: 6px; }
.fact-id { font-family: var(--font-family-mono); font-weight: 600; color: var(--color-action-blue); margin-right: 6px; }

/* 数据缺口 */
.gaps-box {
  margin-top: 12px;
  border: 1px dashed rgba(234, 88, 12, 0.4);
  border-radius: 8px;
  padding: 10px 14px;
  background: rgba(245, 158, 11, 0.06);
}
.gaps-title { font-size: 12px; font-weight: 600; color: var(--color-warning); }
.gap-line { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }

/* 完整报告 */
.report-body { display: flex; flex-direction: column; gap: 18px; }
.report-block { display: flex; flex-direction: column; gap: 8px; }
.report-h { font-size: 13px; font-weight: 700; color: var(--text-primary); }
.report-text { font-size: 13.5px; line-height: 1.7; color: var(--text-primary); margin: 0; }
.report-muted { font-size: 12.5px; color: var(--text-muted); }
.report-muted-inline { font-size: 12px; color: var(--text-muted); white-space: nowrap; }
.report-sub {
  border: 1px solid var(--border-default);
  border-radius: 10px;
  padding: 10px 14px;
  background: var(--surface-elevated);
}
.report-sub-title { font-size: 12.5px; font-weight: 600; color: var(--color-action-blue); margin-bottom: 6px; }
.report-evidence { display: flex; align-items: center; gap: 6px; margin-top: 8px; flex-wrap: wrap; }
.report-ev-label { font-size: 11px; color: var(--text-muted); }
.report-ev-chip {
  font-size: 11px; font-weight: 600; padding: 1px 8px; border-radius: 9999px;
  background: rgba(59, 130, 246, 0.1); color: var(--color-action-blue);
  font-family: var(--font-family-mono);
}
.report-line { display: flex; align-items: flex-start; gap: 8px; font-size: 13px; line-height: 1.6; flex-wrap: wrap; }
.report-type {
  font-size: 11px; font-weight: 600; padding: 1px 8px; border-radius: 9999px;
  background: var(--surface-stone); color: var(--text-secondary); white-space: nowrap;
}
.report-line-text { flex: 1; min-width: 0; color: var(--text-primary); }
.report-evidence-inline { font-size: 11px; color: var(--color-action-blue); white-space: nowrap; }

/* 空态 */
.empty { padding: 24px 0; text-align: center; color: var(--text-muted); font-size: 14px; }
</style>
