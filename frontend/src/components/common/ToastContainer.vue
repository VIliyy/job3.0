<template>
  <div class="toast-container">
    <transition-group name="toast">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="toast-item"
        :class="'toast-' + t.type"
        @click="toast.dismiss(t.id)"
      >
        <span class="toast-icon">{{ getIcon(t.type) }}</span>
        <span class="toast-message">{{ t.message }}</span>
        <span class="toast-close">×</span>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { useToast } from '@/composables/useToast'

const { toast, toasts, getIcon } = useToast()
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 360px;
  pointer-events: none;
}

.toast-item {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: var(--surface-elevated);
  border-radius: 10px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  border-left: 4px solid #3b82f6;
  cursor: pointer;
  font-size: 14px;
}

.toast-success { border-left-color: #10b981; }
.toast-error { border-left-color: #ef4444; }
.toast-warning { border-left-color: #f59e0b; }
.toast-info { border-left-color: #3b82f6; }

.toast-icon {
  font-size: 16px;
  font-weight: 700;
  color: #6b7280;
  flex-shrink: 0;
}

.toast-message {
  flex: 1;
  color: #1f2937;
  line-height: 1.5;
}

.toast-close {
  color: #9ca3af;
  font-size: 18px;
  flex-shrink: 0;
}

.toast-enter-active, .toast-leave-active {
  transition: all 0.25s ease;
}

.toast-enter-from, .toast-leave-to {
  opacity: 0;
  transform: translateX(24px);
}
</style>
