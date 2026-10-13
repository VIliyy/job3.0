<template>
  <div class="conclusion-card" :class="'type-' + (inference.type || 'info')" @click="$emit('open-evidence', inference)">
    <div class="card-head">
      <span class="type-tag">{{ typeLabel(inference.type) }}</span>
      <ConfidenceBadge :level="inference.confidence || 'C2'" />
      <span v-if="inference.evidence && inference.evidence.length" class="evidence-hint">
        证据 {{ inference.evidence.length }} 条 ›
      </span>
    </div>
    <div class="card-content">{{ inference.content }}</div>
  </div>
</template>

<script setup>
import ConfidenceBadge from './ConfidenceBadge.vue'

defineProps({
  inference: { type: Object, required: true }
})
defineEmits(['open-evidence'])

const TYPE_LABELS = {
  usp: '卖点',
  pricing: '定价',
  risk: '风险',
  opportunity: '机会',
  brief: '目标',
  cluster: '聚类',
  info: '信息'
}
function typeLabel(type) { return TYPE_LABELS[type] || type }
</script>

<style scoped>
.conclusion-card {
  border: 1px solid var(--border-default);
  border-radius: 12px;
  background: var(--surface-elevated);
  padding: 16px 18px;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.conclusion-card:hover {
  border-color: var(--color-action-blue);
  box-shadow: var(--shadow-level-2);
  transform: translateY(-1px);
}
.type-risk { border-left: 3px solid var(--color-error); }
.type-usp { border-left: 3px solid var(--color-success); }
.type-pricing { border-left: 3px solid var(--color-action-blue); }
.type-opportunity { border-left: 3px solid var(--agent-advisor); }
.card-head { display: flex; align-items: center; gap: 8px; }
.type-tag {
  font-size: 11px; font-weight: 600; padding: 1px 10px; border-radius: 9999px;
  background: var(--surface-stone); color: var(--text-secondary);
}
.evidence-hint { font-size: 11px; color: var(--color-action-blue); margin-left: auto; }
.card-content { font-size: 14px; line-height: 1.6; margin-top: 8px; color: var(--text-primary); }
</style>