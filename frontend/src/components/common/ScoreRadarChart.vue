<template>
  <div class="score-radar">
    <div class="radar-chart" :style="chartStyle">
      <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`">
        <g class="grid">
          <polygon
            v-for="(level, i) in gridLevels"
            :key="'grid-' + i"
            :points="getPolygonPoints(level)"
            class="grid-polygon"
          />
        </g>
        <g class="axes">
          <line
            v-for="(axis, i) in axes"
            :key="'axis-' + i"
            :x1="center"
            :y1="center"
            :x2="getAxisEnd(i, maxRadius)"
            :y2="getAxisEnd(i, maxRadius, true)"
            class="axis-line"
          />
        </g>
        <polygon
          :points="dataPoints"
          class="data-polygon"
          :style="{ fill: fillColor, stroke: strokeColor }"
        />
        <circle
          v-for="(point, i) in dataPointPositions"
          :key="'point-' + i"
          :cx="point.x"
          :cy="point.y"
          r="4"
          class="data-point"
          :style="{ fill: strokeColor }"
        />
        <text
          v-for="(axis, i) in axes"
          :key="'label-' + i"
          :x="getLabelPosition(i).x"
          :y="getLabelPosition(i).y"
          class="axis-label"
          text-anchor="middle"
          dominant-baseline="middle"
        >
          {{ axis.label }}
        </text>
      </svg>
    </div>
    <div class="score-details">
      <div v-for="(axis, i) in axes" :key="'detail-' + i" class="detail-item">
        <div class="detail-header">
          <span class="detail-label">{{ axis.label }}</span>
          <span class="detail-value" :style="{ color: getScoreColor(values[i]) }">
            {{ values[i] }}?
          </span>
        </div>
        <div class="detail-bar">
          <div 
            class="detail-fill" 
            :style="{ width: values[i] + '%', background: getScoreColor(values[i]) }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  values: {
    type: Array,
    default: () => [0, 0, 0, 0, 0]
  },
  labels: {
    type: Array,
    default: () => ["??", "???", "??", "??", "ATS"]
  },
  size: {
    type: Number,
    default: 240
  },
  maxRadius: {
    type: Number,
    default: 100
  }
})

const center = computed(() => props.size / 2)
const axes = computed(() => 
  props.labels.map((label, i) => ({ label, value: props.values[i] || 0 }))
)
const gridLevels = [0.2, 0.4, 0.6, 0.8, 1.0]
const fillColor = computed(() => 'rgba(59, 130, 246, 0.2)')
const strokeColor = computed(() => '#3b82f6')

function getPolygonPoints(level) {
  const r = props.maxRadius * level
  const points = []
  for (let i = 0; i < axes.value.length; i++) {
    const { x, y } = getAxisEnd(i, r)
    points.push(`${x},${y}`)
  }
  return points.join(' ')
}

function getAxisEnd(index, radius, yOnly = false) {
  const angle = (Math.PI * 2 * index) / axes.value.length - Math.PI / 2
  return {
    x: center.value + radius * Math.cos(angle),
    y: center.value + radius * Math.sin(angle)
  }
}

const dataPointPositions = computed(() => {
  return props.values.map((value, i) => {
    const r = (value / 100) * props.maxRadius
    const { x, y } = getAxisEnd(i, r)
    return { x, y }
  })
})

const dataPoints = computed(() => {
  return dataPointPositions.value.map(p => `${p.x},${p.y}`).join(' ')
})

function getLabelPosition(index) {
  const r = props.maxRadius + 24
  const { x, y } = getAxisEnd(index, r)
  return { x, y }
}

function getScoreColor(score) {
  if (score >= 80) return 'var(--color-success)'
  if (score >= 60) return 'var(--color-info)'
  if (score >= 40) return 'var(--color-warning)'
  return 'var(--color-error)'
}

const chartStyle = computed(() => ({
  width: props.size + 'px',
  margin: '0 auto'
}))
</script>

<style scoped>
.score-radar {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.radar-chart {
  flex-shrink: 0;
}

.grid-polygon {
  fill: none;
  stroke: var(--border-default);
  stroke-width: 1;
}

.axis-line {
  stroke: var(--border-default);
  stroke-width: 1;
}

.data-polygon {
  stroke-width: 2;
  transition: all 0.3s ease;
}

.data-point {
  transition: all 0.3s ease;
}

.axis-label {
  font-size: 12px;
  fill: var(--text-muted);
  font-weight: 500;
}

.score-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 8px;
}

.detail-item {
  min-width: 180px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-size: 13px;
}

.detail-label {
  color: var(--text-muted);
}

.detail-value {
  font-weight: 600;
}

.detail-bar {
  height: 6px;
  background: var(--surface-stone);
  border-radius: 3px;
  overflow: hidden;
}

.detail-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}
</style>
