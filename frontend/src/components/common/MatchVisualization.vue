<template>
  <div class="match-visualization">
    <!-- ????? -->
    <div class="match-header">
      <div class="match-score-section">
        <div class="score-circle-wrapper">
          <div class="score-circle" :style="scoreCircleStyle">
            <span class="score-value">{{ score }}</span>
            <span class="score-label">???</span>
          </div>
          <div v-if="previousScore !== null" class="score-change">
            <span class="change-icon">{{ score > previousScore ? '+' : '' }}{{ score - previousScore }}</span>
            <span class="change-label">vs ???</span>
          </div>
        </div>
        <div class="match-level" :class="levelClass">
          {{ levelText }}
        </div>
      </div>
      
      <div class="keyword-coverage">
        <div class="coverage-header">
          <span class="coverage-title">??????</span>
          <span class="coverage-value">{{ coveragePercent }}%</span>
        </div>
        <div class="coverage-bar">
          <div class="coverage-fill" :style="{ width: coveragePercent + '%' }"></div>
        </div>
        <div class="coverage-stats">
          <span class="stat matched">?? {{ matchedCount }}</span>
          <span class="stat missing">?? {{ missingCount }}</span>
        </div>
      </div>
    </div>
    
    <!-- ????? -->
    <div class="keyword-section">
      <h4 class="section-title">?????</h4>
      
      <div class="keyword-group">
        <div class="group-header">
          <span class="group-icon matched-icon">?</span>
          <span class="group-label">???</span>
        </div>
        <div class="keyword-tags">
          <span 
            v-for="kw in matchedKeywords" 
            :key="kw" 
            class="keyword-tag matched"
          >
            {{ kw }}
          </span>
          <span v-if="matchedKeywords.length === 0" class="no-keywords">
            ???????
          </span>
        </div>
      </div>
      
      <div class="keyword-group">
        <div class="group-header">
          <span class="group-icon missing-icon">?</span>
          <span class="group-label">?????</span>
        </div>
        <div class="keyword-tags">
          <span 
            v-for="kw in missingKeywords" 
            :key="kw" 
            class="keyword-tag missing"
          >
            {{ kw }}
          </span>
          <span v-if="missingKeywords.length === 0" class="no-keywords">
            ????????
          </span>
        </div>
      </div>
    </div>
    
    <!-- ???? -->
    <div v-if="suggestions.length" class="suggestions-section">
      <h4 class="section-title">????</h4>
      <div class="suggestion-list">
        <div 
          v-for="(suggestion, i) in suggestions" 
          :key="i"
          class="suggestion-item"
        >
          <span class="suggestion-priority" :class="'priority-' + suggestion.priority">
            {{ priorityLabels[suggestion.priority] }}
          </span>
          <span class="suggestion-text">{{ suggestion.text }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  score: {
    type: Number,
    default: 0
  },
  previousScore: {
    type: Number,
    default: null
  },
  matchedKeywords: {
    type: Array,
    default: () => []
  },
  missingKeywords: {
    type: Array,
    default: () => []
  },
  suggestions: {
    type: Array,
    default: () => []
  }
})

const priorityLabels = {
  high: '??',
  medium: '??',
  low: '??'
}

const matchedCount = computed(() => props.matchedKeywords.length)
const missingCount = computed(() => props.missingKeywords.length)
const totalCount = computed(() => matchedCount.value + missingCount.value)

const coveragePercent = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((matchedCount.value / totalCount.value) * 100)
})

const levelText = computed(() => {
  if (props.score >= 80) return '????'
  if (props.score >= 60) return '????'
  if (props.score >= 40) return '????'
  return '????'
})

const levelClass = computed(() => {
  if (props.score >= 80) return 'level-excellent'
  if (props.score >= 60) return 'level-good'
  if (props.score >= 40) return 'level-normal'
  return 'level-poor'
})

const scoreCircleStyle = computed(() => {
  const color = props.score >= 60 ? '#3b82f6' : props.score >= 40 ? '#f59e0b' : '#ef4444'
  return {
    background: `conic-gradient(${color} ${props.score}%, var(--surface-stone) 0%)`
  }
})
</script>

<style scoped>
.match-visualization {
  background: var(--surface-elevated);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-default);
}

.match-header {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.match-score-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.score-circle-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.score-circle::before {
  content: '';
  position: absolute;
  width: 80px;
  height: 80px;
  background: var(--surface-elevated);
  border-radius: 50%;
}

.score-value {
  font-size: 28px;
  font-weight: 700;
  position: relative;
  z-index: 1;
  color: var(--text-primary);
}

.score-label {
  font-size: 11px;
  color: var(--text-muted);
  position: relative;
  z-index: 1;
}

.score-change {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 12px;
}

.change-icon {
  color: var(--color-success);
  font-weight: 600;
}

.change-label {
  color: var(--text-muted);
}

.match-level {
  padding: 6px 16px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 600;
}

.level-excellent { background: #10b981; color: white; }
.level-good { background: #3b82f6; color: white; }
.level-normal { background: #f59e0b; color: white; }
.level-poor { background: #ef4444; color: white; }

.keyword-coverage {
  flex: 1;
  min-width: 200px;
}

.coverage-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.coverage-title {
  font-size: 14px;
  color: var(--text-muted);
}

.coverage-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-info);
}

.coverage-bar {
  height: 8px;
  background: var(--surface-stone);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.coverage-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-info), var(--color-focus-blue));
  border-radius: 4px;
  transition: width 0.5s ease;
}

.coverage-stats {
  display: flex;
  gap: 16px;
  font-size: 13px;
}

.stat.matched { color: var(--color-success); }
.stat.missing { color: var(--color-error); }

.keyword-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.keyword-group {
  margin-bottom: 16px;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.group-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.matched-icon { background: var(--color-success-soft); color: var(--color-success); }
.missing-icon { background: var(--color-error-soft); color: var(--color-error); }

.group-label {
  font-size: 13px;
  color: var(--text-muted);
}

.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-tag {
  padding: 4px 12px;
  border-radius: 14px;
  font-size: 13px;
  font-weight: 500;
}

.keyword-tag.matched {
  background: var(--color-success-soft);
  color: var(--color-success);
}

.keyword-tag.missing {
  background: var(--color-error-soft);
  color: var(--color-error);
}

.no-keywords {
  font-size: 13px;
  color: var(--text-muted);
  font-style: italic;
}

.suggestions-section {
  border-top: 1px solid var(--border-default);
  padding-top: 16px;
}

.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 12px;
  background: var(--surface-stone);
  border-radius: 8px;
  font-size: 13px;
}

.suggestion-priority {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.priority-high { background: var(--color-error-soft); color: var(--color-error); }
.priority-medium { background: var(--color-warning-soft); color: var(--color-warning); }
.priority-low { background: var(--color-info-soft); color: var(--color-info); }

.suggestion-text {
  color: var(--text-body);
  line-height: 1.5;
}
</style>
