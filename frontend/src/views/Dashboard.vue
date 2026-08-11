<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <div class="header-left">
        <h1>求职管理系统</h1>
        <span class="subtitle">智能简历优化平台</span>
      </div>
      <div class="header-right">
        <div class="time-display">{{ currentTime }}</div>
        <button class="btn-icon" @click="toggleTheme">
          <span v-if="isDark">Light</span>
          <span v-else>Dark</span>
        </button>
      </div>
    </header>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">简历数量</div>
        <div class="stat-value">{{ stats.resumeVersions }}</div>
        <div class="stat-change">实时数据</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">投递记录</div>
        <div class="stat-value">{{ stats.applications }}</div>
        <div class="stat-change">{{ stats.applicationsThisWeek }} 本周</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">优化次数</div>
        <div class="stat-value">{{ stats.optimizations }}</div>
        <div class="stat-change">实时数据</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">平均分数</div>
        <div class="stat-value">{{ stats.avgScore }}</div>
        <div class="stat-change">实时数据</div>
      </div>
    </div>

    <div class="content-grid">
      <div class="card recent-optimizations">
        <div class="card-header">
          <h2>最近优化</h2>
          <button class="btn-link" @click="$router.push('/optimize')">新建优化</button>
        </div>
        <div class="card-content">
          <div v-if="recentOptimizations.length === 0" class="empty-state">
            <p>暂无优化记录</p>
            <button class="btn-primary" @click="$router.push('/optimize')">开始优化</button>
          </div>
          <div v-else class="optimization-list">
            <div v-for="item in recentOptimizations" :key="item.id" class="optimization-item">
              <div class="item-info">
                <div class="item-title">{{ item.title }}</div>
                <div class="item-meta">{{ item.date }} · {{ item.iterations }}轮迭代</div>
              </div>
              <div class="item-score" :class="getScoreClass(item.score)">
                {{ item.score }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card recent-applications">
        <div class="card-header">
          <h2>投递动态</h2>
          <button class="btn-link" @click="$router.push('/resumes')">查看全部</button>
        </div>
        <div class="card-content">
          <div v-if="recentApplications.length === 0" class="empty-state">
            <p>暂无投递记录</p>
          </div>
          <div v-else class="application-list">
            <div v-for="item in recentApplications" :key="item.id" class="application-item">
              <div class="item-info">
                <div class="item-title">{{ item.company }}</div>
                <div class="item-meta">{{ item.position }} · {{ item.date }}</div>
              </div>
              <div class="item-status" :class="item.status">
                {{ getStatusText(item.status) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="chart-section">
      <div class="card chart-card">
        <div class="card-header">
          <h2>优化趋势</h2>
          <div class="chart-controls">
            <button 
              v-for="period in periods" 
              :key="period"
              class="btn-period"
              :class="{ active: selectedPeriod === period }"
              @click="selectedPeriod = period"
            >
              {{ period }}
            </button>
          </div>
        </div>
        <div class="card-content">
          <div class="chart-placeholder">
            <div class="chart-bars">
              <div v-for="(value, index) in chartData" :key="index" class="chart-bar-container">
                <div class="chart-bar" :style="{ height: value + '%' }"></div>
                <span class="chart-label">{{ chartLabels[index] }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card tips-card">
        <div class="card-header">
          <h2>优化建议</h2>
        </div>
        <div class="card-content">
          <div class="tips-list">
            <div v-for="tip in tips" :key="tip.id" class="tip-item">
              <div class="tip-icon" :class="tip.type"></div>
              <div class="tip-content">
                <div class="tip-title">{{ tip.title }}</div>
                <div class="tip-description">{{ tip.description }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="quick-actions">
      <h2>快捷功能</h2>
      <div class="actions-grid">
        <button class="action-card" @click="$router.push('/optimize')">
          <div class="action-icon optimize"></div>
          <div class="action-text">
            <span class="action-title">简历优化</span>
            <span class="action-desc">AI智能优化简历</span>
          </div>
        </button>
        <button class="action-card" @click="$router.push('/resumes')">
          <div class="action-icon resume"></div>
          <div class="action-text">
            <span class="action-title">简历管理</span>
            <span class="action-desc">管理多个版本</span>
          </div>
        </button>
        <button class="action-card" @click="$router.push('/resumes')">
          <div class="action-icon apply"></div>
          <div class="action-text">
            <span class="action-title">投递记录</span>
            <span class="action-desc">追踪求职进度</span>
          </div>
        </button>
        <button class="action-card" @click="$router.push('/optimize')">
          <div class="action-icon analyze"></div>
          <div class="action-text">
            <span class="action-title">JD分析</span>
            <span class="action-desc">深度解析职位</span>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { resumeApi, applicationApi, optimizeApi } from '@/api'

const isDark = ref(false)
const currentTime = ref('')
const selectedPeriod = ref('7天')

const periods = ['7天', '30天', '90天']

const stats = ref({
  resumeVersions: 0,
  applications: 0,
  applicationsThisWeek: 0,
  optimizations: 0,
  avgScore: 0
})

const recentOptimizations = ref([])
const recentApplications = ref([])

async function loadDashboard() {
  try {
    const [resumeList, appList] = await Promise.all([
      resumeApi.list({ limit: 100 }).catch(() => []),
      applicationApi.list({ limit: 100 }).catch(() => [])
    ])
    const resumes = Array.isArray(resumeList) ? resumeList : []
    const apps = Array.isArray(appList) ? appList : []

    // 统计：简历数、投递数、优化次数与平均分
    let optimizations = 0
    let scoreSum = 0
    const recentOpts = []
    for (const resume of resumes) {
      try {
        const vData = await optimizeApi.versions(resume.id)
        const versions = vData?.versions || []
        optimizations += versions.length
        for (const v of versions.slice(0, 1)) {
          if (v.optimized_score) scoreSum += v.optimized_score
          recentOpts.push({
            id: v.version_id,
            title: resume.version_name || ('简历 ' + resume.id),
            date: v.created_at ? new Date(v.created_at).toLocaleDateString('zh-CN') : '',
            iterations: versions.length,
            score: v.optimized_score || 0
          })
        }
      } catch (e) {
        console.warn('加载版本失败:', e)
      }
    }

    const weekAgo = Date.now() - 7 * 24 * 3600 * 1000
    stats.value = {
      resumeVersions: resumes.length,
      applications: apps.length,
      applicationsThisWeek: apps.filter(a => a.created_at && new Date(a.created_at).getTime() >= weekAgo).length,
      optimizations,
      avgScore: optimizations ? Math.round(scoreSum / optimizations) : 0
    }
    recentOptimizations.value = recentOpts.slice(0, 5).sort((a, b) => (b.date || '').localeCompare(a.date || ''))

    recentApplications.value = apps.slice(0, 5).map(a => ({
      id: a.id,
      company: a.company,
      position: a.position || '',
      date: a.created_at ? new Date(a.created_at).toLocaleDateString('zh-CN') : '',
      status: a.status
    }))
  } catch (e) {
    console.error('加载控制台数据失败:', e)
  }
}

const chartLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const chartData = ref([60, 75, 45, 80, 90, 65, 85])

const tips = ref([
  {
    id: 1,
    type: 'improvement',
    title: '优化建议',
    description: '您的简历在项目管理经验描述上可以更加量化，建议添加具体成果数据'
  },
  {
    id: 2,
    type: 'success',
    title: '面试机会',
    description: '腾讯全栈岗位与您的简历匹配度较高，建议重点准备技术面试'
  },
  {
    id: 3,
    type: 'warning',
    title: '投递提醒',
    description: '您已投递5个职位，建议关注面试进度并及时跟进'
  }
])

let timeInterval = null

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  loadDashboard()
  
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    isDark.value = true
    document.documentElement.classList.add('dark')
  }
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
})

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

const getScoreClass = (score) => {
  if (score >= 85) return 'high'
  if (score >= 70) return 'medium'
  return 'low'
}

const getStatusText = (status) => {
  const statusMap = {
    pending: '待回复',
    interview: '面试中',
    offer: '已 offer',
    rejected: '已拒绝'
  }
  return statusMap[status] || status
}
</script>

<style scoped>
.dashboard {
  background: var(--surface-default);
  min-height: 100vh;
  padding: 24px;
  padding: 32px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  background: var(--surface-elevated);
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-default);
}

.header-left h1 {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.subtitle {
  font-size: 14px;
  color: var(--text-muted);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.time-display {
  font-size: 14px;
  color: var(--text-secondary);
  font-family: var(--font-family-mono);
}

.btn-icon {
  padding: 8px 16px;
  background: var(--surface-stone);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 200ms;
}

.btn-icon:hover {
  background: var(--surface-stone-strong);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--surface-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: 24px;
  box-shadow: var(--shadow-level-1);
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.stat-change {
  font-size: 13px;
  color: var(--text-secondary);
}

.stat-change.positive {
  color: var(--color-success);
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

.card {
  background: var(--surface-elevated);
  border: 1px solid var(--border-default);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-level-1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-default);
}

.card-header h2 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.card-content {
  padding: 20px 24px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-state p {
  color: var(--text-muted);
  margin-bottom: 16px;
}

.optimization-list,
.application-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.optimization-item,
.application-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--surface-default);
  border-radius: var(--radius-sm);
  transition: all 200ms;
}

.optimization-item:hover,
.application-item:hover {
  background: var(--surface-stone);
}

.item-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.item-meta {
  font-size: 12px;
  color: var(--text-muted);
}

.item-score {
  font-size: 20px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: var(--radius-xs);
}

.item-score.high {
  color: var(--color-success);
  background: var(--color-success-soft);
}

.item-score.medium {
  color: var(--color-warning);
  background: var(--color-warning-soft);
}

.item-score.low {
  color: var(--color-error);
  background: var(--color-error-soft);
}

.item-status {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: var(--radius-xs);
  font-weight: 500;
}

.item-status.pending {
  color: var(--color-action-blue);
  background: var(--color-info-soft);
}

.item-status.interview {
  color: var(--color-success);
  background: var(--color-success-soft);
}

.item-status.rejected {
  color: var(--color-error);
  background: var(--color-error-soft);
}

.chart-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

.chart-controls {
  display: flex;
  gap: 8px;
}

.btn-period {
  padding: 6px 12px;
  background: transparent;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xs);
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 200ms;
}

.btn-period:hover {
  background: var(--surface-stone);
}

.btn-period.active {
  background: var(--color-action-blue);
  color: white;
  border-color: var(--color-action-blue);
}

.chart-placeholder {
  height: 240px;
  background: var(--surface-stone);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.chart-bars {
  display: flex;
  gap: 24px;
  align-items: flex-end;
  height: 200px;
}

.chart-bar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.chart-bar {
  width: 40px;
  background: linear-gradient(180deg, var(--color-action-blue), var(--color-focus-blue));
  border-radius: var(--radius-xs) var(--radius-xs) 0 0;
  transition: height 300ms ease;
}

.chart-label {
  font-size: 12px;
  color: var(--text-muted);
}

.tips-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tip-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: var(--surface-default);
  border-radius: var(--radius-sm);
}

.tip-icon {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 6px;
  flex-shrink: 0;
}

.tip-icon.improvement {
  background: var(--color-action-blue);
}

.tip-icon.success {
  background: var(--color-success);
}

.tip-icon.warning {
  background: var(--color-warning);
}

.tip-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.tip-description {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.quick-actions h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--surface-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 200ms;
  text-align: left;
}

.action-card:hover {
  border-color: var(--color-action-blue);
  box-shadow: var(--shadow-level-2);
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.action-icon.optimize {
  background: linear-gradient(135deg, var(--color-action-blue), var(--color-focus-blue));
}

.action-icon.resume {
  background: linear-gradient(135deg, var(--agent-planner), var(--agent-recruiter));
}

.action-icon.apply {
  background: linear-gradient(135deg, var(--agent-writer), var(--agent-interviewer));
}

.action-icon.analyze {
  background: linear-gradient(135deg, var(--agent-advisor), var(--agent-critic));
}

.action-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.action-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.action-desc {
  font-size: 13px;
  color: var(--text-muted);
}

.btn-primary {
  padding: 10px 20px;
  background: var(--color-action-blue);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 200ms;
}

.btn-primary:hover {
  background: var(--color-focus-blue);
}

.btn-link {
  background: none;
  border: none;
  color: var(--color-action-blue);
  font-size: 13px;
  cursor: pointer;
  padding: 0;
}

.btn-link:hover {
  text-decoration: underline;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .content-grid,
  .chart-section {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard {
  background: var(--surface-default);
  min-height: 100vh;
  padding: 24px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-bars {
    gap: 12px;
  }
  
  .chart-bar {
    width: 24px;
  }
}


/* Textarea ???? */
textarea {
  background: var(--surface-input);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  padding: 12px 16px;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  transition: border-color 200ms, background-color 200ms;
}

textarea:focus {
  outline: none;
  border-color: var(--color-action-blue);
}

textarea::placeholder {
  color: var(--text-muted);
}

textarea:disabled {
  background: var(--surface-stone);
  color: var(--text-muted);
  cursor: not-allowed;
}



/* Select ? Input ???? */
select {
  background: var(--surface-input);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  padding: 8px 12px;
  font-family: inherit;
  font-size: 14px;
  cursor: pointer;
  transition: border-color 200ms, background-color 200ms;
}

select:focus {
  outline: none;
  border-color: var(--color-action-blue);
}

select option {
  background: var(--surface-elevated);
  color: var(--text-primary);
}

input[type="text"],
input[type="email"],
input[type="password"],
input[type="number"],
input[type="search"],
input {
  background: var(--surface-input);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  padding: 8px 12px;
  font-family: inherit;
  font-size: 14px;
  transition: border-color 200ms, background-color 200ms;
}

input:focus {
  outline: none;
  border-color: var(--color-action-blue);
}

input::placeholder {
  color: var(--text-muted);
}

input:disabled,
select:disabled {
  background: var(--surface-stone);
  color: var(--text-muted);
  cursor: not-allowed;
}

</style>
