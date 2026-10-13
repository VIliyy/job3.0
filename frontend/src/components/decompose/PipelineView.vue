<template>
  <div class="pipeline-wrap">
    <div class="progress-row">
      <div class="progress-track">
        <div
          class="progress-fill"
          :class="{
            'is-failed': taskState === 'FAILED',
            'is-running': ['DECOMPOSING', 'INSIGHTING', 'REPORTING'].includes(taskState)
          }"
          :style="{ width: progressPercent + '%' }"
        ></div>
      </div>
      <span class="progress-text" :class="{ 'is-failed': taskState === 'FAILED' }">{{ progressText }}</span>
    </div>
    <div
      class="pipeline"
      :class="{ 'is-processing': ['DECOMPOSING', 'INSIGHTING', 'REPORTING'].includes(taskState) }"
    >
    <template v-for="(seg, index) in segments" :key="seg.id">
      <div
        class="pipe-step"
        :class="'step-' + seg.state"
        :title="seg.desc"
      >
        <span class="step-icon">{{ icon(seg.state) }}</span>
        <span class="step-label">{{ seg.label }}</span>
        <span v-if="seg.version > 1" class="step-ver">v{{ seg.version }}</span>
      </div>
      <span v-if="index < gates.length" class="pipe-arrow">→</span>
      <div
        class="pipe-gate"
        :class="'gate-' + gates[index].state"
        :title="gates[index].name + (gates[index].note ? '（已记录意见）' : '')"
      >
        <span class="gate-key">闸门 {{ gates[index].key }}</span>
        <span v-if="gates[index].note" class="gate-note">✎</span>
      </div>
      <span class="pipe-arrow">→</span>
    </template>
    <div class="pipe-step" :class="{ 'step-done': taskState === 'DONE' }">
      <span class="step-icon">{{ taskState === 'DONE' ? '●' : '○' }}</span>
      <span class="step-label">完成</span>
    </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  taskState: { type: String, default: 'DRAFT' },
  contracts: { type: Object, default: () => ({}) },
  gates: { type: Object, default: () => ({}) }
})

const SEG_DEFS = [
  { id: 'S0', label: '输入解析', desc: '目标识别 + 材料结构化' },
  { id: 'S1', label: '事实拆解', desc: '逐条事实 + 原文锚点' },
  { id: 'S2', label: '洞察生成', desc: '结论引用事实 + 置信度' },
  { id: 'S3', label: '报告合成', desc: '驾驶舱数据 + 导出' }
]

const STATE_AT = {
  DRAFT: -1,
  BRIEF_REVIEW: 0,
  DECOMPOSING: 1,
  FACTS_REVIEW: 1,
  INSIGHTING: 2,
  INSIGHT_REVIEW: 2,
  REPORTING: 3,
  DONE: 3,
  FAILED: null
}

const currentIndex = computed(() => {
  const idx = STATE_AT[props.taskState]
  return idx === undefined || idx === null ? -1 : idx
})

const PROGRESS_AT = {
  DRAFT: 0,
  BRIEF_REVIEW: 1,
  DECOMPOSING: 2,
  FACTS_REVIEW: 3,
  INSIGHTING: 4,
  INSIGHT_REVIEW: 5,
  REPORTING: 6,
  DONE: 8
}
const STATE_LABELS = {
  DRAFT: '草稿',
  BRIEF_REVIEW: '等待确认目标',
  DECOMPOSING: '事实拆解中',
  FACTS_REVIEW: '等待确认事实',
  INSIGHTING: '洞察生成中',
  INSIGHT_REVIEW: '等待确认结论',
  REPORTING: '报告合成中',
  DONE: '已完成',
  FAILED: '已失败'
}
const TOTAL_STEPS = 8

const progressPercent = computed(() => {
  if (props.taskState === 'FAILED') {
    const at = ['S0', 'S1', 'S2'].reduce(
      (acc, name, i) => (props.contracts[name] ? Math.max(acc, i * 2 + 1) : acc),
      0
    )
    return Math.round((at / TOTAL_STEPS) * 100)
  }
  return Math.round(((PROGRESS_AT[props.taskState] ?? 0) / TOTAL_STEPS) * 100)
})

const progressText = computed(() => {
  const label = STATE_LABELS[props.taskState] || props.taskState
  if (props.taskState === 'FAILED') return `${progressPercent.value}% · ${label}，可重试`
  return `${progressPercent.value}% · ${label}`
})

const segments = computed(() => {
  const idx = currentIndex.value
  return SEG_DEFS.map((seg, index) => {
    let state = 'idle'
    if (props.taskState === 'FAILED') state = index === idx ? 'failed' : (index < idx ? 'done' : 'idle')
    else if (index < idx) state = 'done'
    else if (index === idx) state = props.taskState === 'DONE' ? 'done' : 'running'
    return {
      ...seg,
      state,
      version: props.contracts[seg.id]?.version || 1
    }
  })
})

const gates = computed(() => {
  const idx = currentIndex.value
  return ['A', 'B', 'C'].map((key, index) => {
    const g = props.gates[key] || {}
    let state = 'idle'
    if (props.taskState === 'FAILED') state = 'idle'
    else if (index < idx) state = 'approved'
    else if (index === idx) state = 'pending'
    return { key, name: g.name || '', state, note: g.note || '' }
  })
})

function icon(state) {
  return { done: '●', running: '◐', idle: '○', failed: '✕' }[state] || '○'
}
</script>

<style scoped>
.pipeline-wrap { display: flex; flex-direction: column; gap: 10px; }

/* 进度条 */
.progress-row { display: flex; align-items: center; gap: 12px; }
.progress-track {
  flex: 1;
  height: 8px;
  border-radius: 9999px;
  background: var(--surface-stone);
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 9999px;
  background: linear-gradient(90deg, var(--color-action-blue), var(--color-focus-blue));
  transition: width var(--transition-normal);
}
.progress-fill.is-running {
  background-size: 200% 100%;
  animation: progress-flow 1.8s linear infinite;
}
.progress-fill.is-failed { background: var(--color-error); }
.progress-text {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
  min-width: 160px;
  text-align: right;
}
.progress-text.is-failed { color: var(--color-error); }

.pipeline {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding: 6px 0;
}

/* 步骤胶囊（对齐 Optimization 进度条样式） */
.pipe-step {
  position: relative;
  overflow: hidden;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 9999px;
  font-size: 13px;
  font-weight: 500;
  background: var(--surface-stone);
  color: var(--text-muted);
  white-space: nowrap;
}
.step-icon { font-size: 11px; }
.step-label { line-height: 1.4; }
.step-ver {
  font-size: 10px;
  font-weight: 600;
  padding: 0 5px;
  border-radius: 9999px;
  background: rgba(23, 23, 28, 0.08);
  color: var(--text-secondary);
}
.pipe-step.step-running {
  background: rgba(59, 130, 246, 0.1);
  color: var(--color-action-blue);
  animation: node-pulse 2.2s ease-out infinite;
}
.pipe-step.step-running::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(105deg, transparent 25%, rgba(255, 255, 255, 0.52) 50%, transparent 75%);
  transform: translateX(-120%);
  animation: node-scan 2.6s ease-in-out infinite;
  pointer-events: none;
}
.pipe-step.step-running .step-icon { animation: spin 1s linear infinite; display: inline-block; }
.pipe-step.step-done {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}
.pipe-step.step-failed {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
}
@keyframes spin { to { transform: rotate(360deg); } }

/* 闸门胶囊 */
.pipe-gate {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border-radius: 9999px;
  border: 1.5px dashed rgba(234, 88, 12, 0.5);
  background: rgba(245, 158, 11, 0.08);
  color: var(--color-warning);
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}
.pipe-gate.gate-approved {
  border-style: solid;
  border-color: rgba(16, 185, 129, 0.4);
  background: rgba(16, 185, 129, 0.08);
  color: var(--color-success);
  animation: gate-confirm 380ms var(--ease-spring-soft) both;
}
.pipe-gate.gate-pending {
  box-shadow: 0 0 0 3px rgba(234, 88, 12, 0.06);
  animation: gate-wait 2.4s ease-in-out infinite;
}
.pipe-gate.gate-idle {
  border-color: var(--border-default);
  background: var(--surface-stone);
  color: var(--text-subtle);
}
.gate-note { font-size: 10px; }

/* 箭头 */
.pipe-arrow {
  color: var(--text-subtle);
  font-size: 12px;
  flex-shrink: 0;
  transition: color var(--transition-fast);
}
.pipeline.is-processing .pipe-arrow {
  color: var(--color-action-blue);
  animation: arrow-flow 1.6s ease-in-out infinite;
}

@keyframes progress-flow {
  to { background-position: -200% 0; }
}
@keyframes node-pulse {
  70% { box-shadow: 0 0 0 7px transparent; }
  100% { box-shadow: 0 0 0 0 transparent; }
}
@keyframes node-scan {
  0%, 35% { transform: translateX(-120%); }
  70%, 100% { transform: translateX(120%); }
}
@keyframes gate-confirm {
  from { opacity: 0.65; transform: scale(0.92); }
  to { opacity: 1; transform: scale(1); }
}
@keyframes gate-wait {
  50% { box-shadow: 0 0 0 5px rgba(234, 88, 12, 0.025); }
}
@keyframes arrow-flow {
  50% { transform: translateX(2px); }
}

@media (prefers-reduced-motion: reduce) {
  .progress-fill.is-running,
  .pipe-step.step-running,
  .pipe-step.step-running::after,
  .pipe-gate.gate-approved,
  .pipe-gate.gate-pending,
  .pipe-step.step-running .step-icon,
  .pipeline.is-processing .pipe-arrow {
    animation: none;
  }
}
</style>
