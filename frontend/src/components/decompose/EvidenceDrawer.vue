<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="visible" class="drawer-backdrop" @click.self="$emit('close')">
        <aside class="drawer">
          <div class="drawer-head">
            <h3>证据链</h3>
            <button class="drawer-close" @click="$emit('close')">✕</button>
          </div>
          <div v-if="inference" class="drawer-body">
            <div class="chain">
              <div class="chain-conclusion">
                <span class="chain-label">结论</span>
                <span class="chain-type">{{ typeLabel(inference.type) }}</span>
                <p>{{ inference.content }}</p>
              </div>
              <div class="chain-arrow">↓ 引用 {{ (inference.evidence || []).length }} 条事实</div>
              <div v-for="fact in linkedFacts" :key="fact.id" class="chain-fact">
                <span class="fact-id">{{ fact.id }}</span>
                <span class="fact-kind">{{ kindLabel(fact.kind) }}</span>
                <p>
                  <template v-if="linkMap[fact.id]">
                    <span>{{ linkMap[fact.id].before }}</span>
                    <a
                      :href="linkMap[fact.id].url"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="fact-link"
                    >{{ linkMap[fact.id].url }}</a>
                    <span>{{ linkMap[fact.id].after }}</span>
                  </template>
                  <template v-else>{{ fact.content }}</template>
                </p>
                <div class="fact-foot">
                  <span class="anchor">锚点：{{ fact.anchor }}</span>
                  <ConfidenceBadge :level="fact.confidence || 'C3'" />
                </div>
              </div>
              <div v-if="linkedFacts.length === 0" class="chain-empty">该结论未关联事实条目</div>
            </div>
          </div>
        </aside>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import ConfidenceBadge from './ConfidenceBadge.vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  inference: { type: Object, default: null },
  facts: { type: Array, default: () => [] }
})
defineEmits(['close'])

const linkedFacts = computed(() => {
  const evidence = props.inference?.evidence || []
  return props.facts.filter((f) => evidence.includes(f.id))
})

function extractLink(text) {
  const m = String(text || '').match(/https?:\/\/[^\s）)】》"'，。；;]+/)
  if (!m) return null
  const url = m[0]
  return { url, before: text.slice(0, m.index), after: text.slice(m.index + url.length) }
}
const linkMap = computed(() => {
  const map = {}
  linkedFacts.value.forEach((f) => {
    const link = extractLink(f.content)
    if (link) map[f.id] = link
  })
  return map
})

const TYPE_LABELS = {
  usp: '卖点', pricing: '定价', risk: '风险', opportunity: '机会',
  brief: '目标', cluster: '聚类', info: '信息'
}
const KIND_LABELS = {
  requirement: '要求', pricing: '价格', link: '链接', duration: '时长',
  reputation: '口碑', info: '信息', source_meta: '材料概况'
}
function typeLabel(t) { return TYPE_LABELS[t] || t }
function kindLabel(k) { return KIND_LABELS[k] || k }
</script>

<style scoped>
.drawer-backdrop {
  position: fixed; inset: 0; z-index: var(--z-modal-backdrop);
  background: rgba(0, 0, 0, 0.35);
  display: flex; justify-content: flex-end;
}
.drawer {
  width: 440px; max-width: 90vw; height: 100%;
  background: var(--surface-canvas);
  box-shadow: var(--shadow-level-5);
  display: flex; flex-direction: column;
}
.drawer-head {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; border-bottom: 1px solid var(--border-default);
}
.drawer-head h3 { font-size: 16px; font-weight: 600; }
.drawer-close {
  border: none; background: none; font-size: 14px; color: var(--text-muted); padding: 4px 8px;
}
.drawer-close:hover { color: var(--text-primary); }
.drawer-body { padding: 16px 20px; overflow-y: auto; }
.chain-conclusion {
  border: 1px solid rgba(59, 130, 246, 0.4); border-radius: 12px;
  background: var(--color-info-soft); padding: 12px 14px;
}
.chain-label {
  font-size: 11px; font-weight: 700; color: var(--color-action-blue);
  margin-right: 6px;
}
.chain-type {
  font-size: 11px; padding: 1px 10px; border-radius: 9999px;
  background: var(--surface-stone); color: var(--text-secondary);
}
.chain-conclusion p { font-size: 13.5px; margin-top: 8px; line-height: 1.6; }
.chain-arrow { font-size: 12px; color: var(--text-muted); margin: 12px 0; text-align: center; }
.chain-fact {
  border: 1px solid var(--border-default); border-radius: 10px;
  padding: 10px 12px; margin-bottom: 8px; background: var(--surface-elevated);
}
.chain-fact p { font-size: 13px; line-height: 1.6; margin: 6px 0; }
.fact-link {
  color: var(--color-action-blue);
  text-decoration: underline;
  word-break: break-all;
  cursor: pointer;
}
.fact-link:hover { color: var(--color-focus-blue); }
.fact-id { font-size: 11px; font-weight: 700; font-family: var(--font-family-mono); color: var(--color-action-blue); }
.fact-kind {
  font-size: 11px; padding: 1px 7px; border-radius: 8px;
  background: var(--surface-stone); color: var(--text-secondary); margin-left: 6px;
}
.fact-foot { display: flex; justify-content: space-between; align-items: center; }
.anchor { font-size: 11px; color: var(--text-muted); }
.chain-empty { color: var(--text-muted); font-size: 13px; text-align: center; padding: 24px 0; }

.drawer-enter-active, .drawer-leave-active { transition: transform var(--transition-normal), opacity var(--transition-normal); }
.drawer-enter-from, .drawer-leave-to { transform: translateX(100%); opacity: 0; }
</style>