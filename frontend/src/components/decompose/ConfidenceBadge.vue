<template>
  <span class="conf-badge" :class="'c-' + level.toLowerCase()" :title="title">
    {{ level.toUpperCase() }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  level: { type: String, default: 'C3' }
})

const title = computed(() => ({
  C1: 'C1 未验证（红）',
  C2: 'C2 单源推断（黄）',
  C3: 'C3 双源或原文直接命中（绿）'
}[props.level.toUpperCase()] || props.level))
</script>

<style scoped>
.conf-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  padding: 1px 10px;
  border-radius: 9999px;
  line-height: 1.6;
  white-space: nowrap;
}
.c-c1 {
  color: var(--color-error);
  background: rgba(239, 68, 68, 0.15);
}
.c-c2 {
  color: var(--color-warning);
  background: rgba(245, 158, 11, 0.15);
}
.c-c3 {
  color: var(--color-success);
  background: rgba(16, 185, 129, 0.15);
}
</style>