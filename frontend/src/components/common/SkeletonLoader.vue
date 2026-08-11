<template>
  <div class="skeleton-loader">
    <div v-for="n in count" :key="n" class="skeleton-item" :style="itemStyle">
      <div v-if="showAvatar" class="skeleton-avatar"></div>
      <div class="skeleton-content">
        <div class="skeleton-line" :style="{ width: titleWidth }"></div>
        <div class="skeleton-line short" :style="{ width: subtitleWidth }"></div>
        <div v-if="showText" class="skeleton-line" :style="{ width: textWidth }"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  count: {
    type: Number,
    default: 3
  },
  type: {
    type: String,
    default: 'card'
  },
  showAvatar: Boolean,
  showText: Boolean,
  titleWidth: {
    type: String,
    default: '60%'
  },
  subtitleWidth: {
    type: String,
    default: '40%'
  },
  textWidth: {
    type: String,
    default: '90%'
  }
})

const itemStyle = computed(() => ({
  padding: props.type === 'card' ? '16px' : '12px 0',
  background: props.type === 'card' ? 'var(--surface-elevated)' : 'transparent',
  borderRadius: props.type === 'card' ? '12px' : '0'
}))
</script>

<style scoped>
.skeleton-loader {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.skeleton-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--surface-stone);
  animation: shimmer 1.5s infinite;
  flex-shrink: 0;
}

.skeleton-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-line {
  height: 14px;
  border-radius: 4px;
  background: var(--surface-stone);
  animation: shimmer 1.5s infinite;
}

.skeleton-line.short {
  height: 12px;
  width: 40%;
}

@keyframes shimmer {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}
</style>
