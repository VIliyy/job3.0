<template>
  <div class="gate-panel">
    <div class="gate-head">
      <span class="gate-badge">闸门 {{ gate.key }}</span>
      <span class="gate-title">{{ gate.name }}</span>
      <span v-if="contractVersion > 1" class="gate-ver">契约 v{{ contractVersion }}</span>
    </div>

    <div v-if="gate.state === 'approved'" class="gate-approved">
      <span class="approved-mark">✓</span> 已确认<template v-if="gate.note"> · {{ gate.note }}</template>
    </div>

    <template v-else>
      <div class="gate-body">
        <slot></slot>
      </div>

      <div class="gate-form">
        <textarea
          v-model="note"
          class="input note-input"
          rows="2"
          placeholder="意见（可选）：修改拆解目标 / 标记错误事实 / 补充要求…"
        ></textarea>
        <div class="gate-actions">
          <button class="btn-secondary" @click="decide('regenerate')" :disabled="busy">
            {{ busy === 'regenerate' ? '重跑中…' : '重新生成' }}
          </button>
          <button class="btn-primary" @click="decide('approve')" :disabled="busy">
            {{ busy === 'approve' ? '处理中…' : '确认，继续' }}
          </button>
        </div>
        <div v-if="flagsNote" class="flags-note">
          已标记：{{ flagsNote }}
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  gate: { type: Object, required: true },
  contractVersion: { type: Number, default: 1 },
  flags: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['decide'])
const note = ref('')
const busy = ref(null)

const flagsNote = computed(() => {
  const entries = Object.entries(props.flags).filter(([, v]) => v)
  if (entries.length === 0) return ''
  const label = { ok: '对', wrong: '错', missing: '缺' }
  return entries.map(([id, v]) => `${id}(${label[v]})`).join(' ')
})

async function decide(action) {
  busy.value = action
  try {
    await emit('decide', { action, note: note.value.trim() })
    note.value = ''
  } finally {
    busy.value = null
  }
}
</script>

<style scoped>
.gate-panel {
  border: 1px solid rgba(234, 88, 12, 0.35);
  border-radius: 12px;
  background: rgba(245, 158, 11, 0.05);
  padding: 20px;
}
.gate-head { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
.gate-badge {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-warning);
  background: rgba(245, 158, 11, 0.15);
  border-radius: 9999px;
  padding: 2px 12px;
}
.gate-title { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.gate-ver {
  font-size: 11px;
  color: var(--text-secondary);
  background: var(--surface-stone);
  padding: 1px 8px;
  border-radius: 9999px;
  margin-left: auto;
}
.gate-body { margin-bottom: 14px; }
.gate-form { display: flex; flex-direction: column; gap: 10px; }
.note-input { resize: vertical; }
.gate-actions { display: flex; gap: 10px; justify-content: flex-end; }
.btn-primary {
  padding: 9px 22px;
  background: var(--color-action-blue);
  color: #fff;
  border: none;
  border-radius: 8px;
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
.gate-approved {
  font-size: 13px;
  color: var(--color-success);
  display: flex;
  align-items: center;
  gap: 6px;
}
.approved-mark {
  width: 18px; height: 18px;
  border-radius: 50%;
  background: rgba(16, 185, 129, 0.15);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
}
.flags-note { font-size: 12px; color: var(--color-warning); }
</style>