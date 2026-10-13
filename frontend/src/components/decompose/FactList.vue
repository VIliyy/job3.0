<template>
  <div class="fact-list">
    <div v-if="facts.length === 0" class="empty-hint">暂无事实条目</div>
    <div
      v-for="fact in facts"
      :key="fact.id"
      class="fact-item"
      :class="{ flagged: flags[fact.id] }"
    >
      <div class="fact-head">
        <span class="fact-id">{{ fact.id }}</span>
        <span class="fact-kind">{{ kindLabel(fact.kind) }}</span>
        <ConfidenceBadge :level="fact.confidence || 'C3'" />
        <span class="fact-anchor">{{ fact.anchor }}</span>
        <div v-if="editable" class="fact-actions">
          <button
            v-for="opt in flagOptions"
            :key="opt.value"
            class="flag-btn"
            :class="{ active: flags[fact.id] === opt.value }"
            @click="toggleFlag(fact.id, opt.value)"
          >{{ opt.label }}</button>
        </div>
        <span v-else-if="flags[fact.id]" class="flag-tag" :class="'flag-' + flags[fact.id]">
          {{ flagLabel(flags[fact.id]) }}
        </span>
      </div>
      <div class="fact-content">
        <template v-if="linkMap[fact.id]">
          <span>{{ linkMap[fact.id].before }}</span>
          <a
            :href="linkMap[fact.id].url"
            target="_blank"
            rel="noopener noreferrer"
            class="fact-link"
            title="在新标签页打开链接"
          >{{ linkMap[fact.id].url }}</a>
          <span>{{ linkMap[fact.id].after }}</span>
        </template>
        <template v-else>{{ fact.content }}</template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import ConfidenceBadge from './ConfidenceBadge.vue'

function extractLink(text) {
  const m = String(text || '').match(/https?:\/\/[^\s）)】》"'，。；;]+/)
  if (!m) return null
  const url = m[0]
  return { url, before: text.slice(0, m.index), after: text.slice(m.index + url.length) }
}

const props = defineProps({
  facts: { type: Array, default: () => [] },
  editable: { type: Boolean, default: false }
})

const emit = defineEmits(['update:flags'])

const flags = ref({})
const linkMap = computed(() => {
  const map = {}
  props.facts.forEach((f) => {
    const link = extractLink(f.content)
    if (link) map[f.id] = link
  })
  return map
})
const flagOptions = [
  { value: 'ok', label: '对' },
  { value: 'wrong', label: '错' },
  { value: 'missing', label: '缺' }
]

watch(() => props.facts, () => { flags.value = {} }, { deep: true })
watch(flags, (val) => emit('update:flags', { ...val }), { deep: true })

function toggleFlag(id, value) {
  if (flags.value[id] === value) delete flags.value[id]
  else flags.value[id] = value
  emit('update:flags', { ...flags.value })
}

const KIND_LABELS = {
  requirement: '要求',
  pricing: '价格',
  link: '链接',
  duration: '时长',
  reputation: '口碑',
  info: '信息',
  source_meta: '材料概况'
}
function kindLabel(kind) { return KIND_LABELS[kind] || kind }
function flagLabel(value) { return { ok: '已确认', wrong: '标记错误', missing: '标记缺失' }[value] || '' }
</script>

<style scoped>
.fact-list { display: flex; flex-direction: column; gap: 10px; }
.fact-item {
  border: 1px solid var(--border-default);
  border-radius: 10px;
  background: var(--surface-elevated);
  padding: 12px 14px;
  transition: border-color var(--transition-fast);
}
.fact-item.flagged { border-color: var(--color-warning); }
.fact-head { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.fact-id {
  font-size: 11px; font-weight: 700; color: var(--color-action-blue);
  font-family: var(--font-family-mono);
}
.fact-kind {
  font-size: 11px; padding: 1px 8px; border-radius: 9999px;
  background: var(--surface-stone); color: var(--text-secondary);
}
.fact-anchor { font-size: 11px; color: var(--text-muted); margin-left: auto; }
.fact-actions { display: flex; gap: 4px; }
.flag-btn {
  font-size: 11px; padding: 1px 8px; border-radius: 8px;
  border: 1px solid var(--border-default); background: var(--surface-default);
  color: var(--text-secondary);
}
.flag-btn.active {
  border-color: var(--color-warning); color: var(--color-warning);
  background: var(--color-warning-soft); font-weight: 600;
}
.flag-tag { font-size: 11px; font-weight: 600; }
.flag-ok { color: var(--color-success); }
.flag-wrong { color: var(--color-error); }
.flag-missing { color: var(--color-warning); }
.fact-content { font-size: 13.5px; color: var(--text-primary); margin-top: 6px; line-height: 1.6; }
.fact-link {
  color: var(--color-action-blue);
  text-decoration: underline;
  word-break: break-all;
  cursor: pointer;
}
.fact-link:hover { color: var(--color-focus-blue); }
.empty-hint { color: var(--text-muted); font-size: 13px; padding: 12px; text-align: center; }
</style>