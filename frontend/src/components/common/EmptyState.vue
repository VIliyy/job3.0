<template>
  <div class="empty-state-container">
    <div class="empty-icon" :class="iconClass">
      <span class="icon-emoji">{{ icon }}</span>
    </div>
    <h3 class="empty-title">{{ title }}</h3>
    <p class="empty-desc">{{ description }}</p>
    <div v-if="$slots.actions" class="empty-actions">
      <slot name="actions"></slot>
    </div>
    <div v-else-if="actionLabel" class="empty-actions">
      <button @click="$emit('action')" class="empty-action-btn">
        {{ actionLabel }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  type: {
    type: String,
    default: 'default'
  },
  title: {
    type: String,
    default: '????'
  },
  description: {
    type: String,
    default: ''
  },
  actionLabel: {
    type: String,
    default: ''
  }
})

defineEmits(['action'])

const iconMap = {
  resume: { icon: '??', class: 'icon-blue' },
  application: { icon: '??', class: 'icon-purple' },
  search: { icon: '??', class: 'icon-orange' },
  error: { icon: '?', class: 'icon-red' },
  default: { icon: '??', class: 'icon-gray' }
}

const icon = computed(() => iconMap[props.type]?.icon || iconMap.default.icon)
const iconClass = computed(() => iconMap[props.type]?.class || iconMap.default.class)
</script>

<style scoped>
.empty-state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  font-size: 36px;
}

.icon-blue { background: var(--color-info-soft); }
.icon-purple { background: rgba(139, 92, 246, 0.1); }
.icon-orange { background: var(--color-warning-soft); }
.icon-red { background: var(--color-error-soft); }
.icon-gray { background: var(--surface-stone); }

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: var(--text-muted);
  max-width: 300px;
  line-height: 1.5;
  margin-bottom: 20px;
}

.empty-actions {
  display: flex;
  gap: 12px;
}

.empty-action-btn {
  padding: 10px 20px;
  background: var(--color-info);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.empty-action-btn:hover {
  background: var(--color-focus-blue);
}
</style>
