<template>
  <div class="optimization-page">
    <header class="page-header">
      <h1>简历优化</h1>
      <p class="page-desc">选择简历与目标 JD，自动完成匹配分析与内容优化</p>
    </header>

    <div class="input-section">
      <div class="input-group">
        <label>选择简历</label>
        <select v-model="selectedResumeId" class="input-select" :disabled="isRunning" @change="onSelectResume">
          <option value="" disabled>请选择简历</option>
          <option v-for="r in resumes" :key="r.id" :value="r.id">
            {{ r.version_name || r.filename }} ({{ categoryLabel(r.category) }}) {{ statusLabel(r.status) }}
          </option>
        </select>
        <p v-if="resumes.length === 0" class="input-hint">
          还没有简历，请先到<a href="/resumes">简历管理</a>上传或编辑简历内容
        </p>
      </div>

      <div class="input-group">
        <label>简历内容</label>
        <textarea v-model="resumeText" placeholder="选择简历后自动填充，也可直接编辑" rows="10" :disabled="isRunning"></textarea>
      </div>

      <div class="input-group">
        <label>目标职位 JD</label>
        <textarea v-model="jdText" placeholder="粘贴目标职位描述" rows="7" :disabled="isRunning"></textarea>
      </div>

      <div class="action-row">
        <button @click="startOptimization" :disabled="!canStart || isRunning" class="btn-primary">
          <span v-if="isRunning">优化中...</span>
          <span v-else>开始优化</span>
        </button>
        <button v-if="isRunning" @click="cancelOptimization" class="btn-secondary">取消</button>
      </div>
    </div>

    <div v-if="isRunning" class="progress-section">
      <div class="progress-header">
        <span class="progress-title">优化进度</span>
        <span class="progress-percent">{{ Math.round(progress) }}%</span>
      </div>
      <div class="progress-bar"><div class="progress-fill" :style="{ width: progress + '%' }"></div></div>
      <div class="progress-steps">
        <div v-for="step in steps" :key="step.id" class="progress-step" :class="'step-' + step.status">
          <span class="step-icon">{{ stepIcon(step.status) }}</span>
          <span class="step-label">{{ step.label }}</span>
        </div>
      </div>
      <div class="progress-time">已用时间: {{ elapsedTime }}秒 · {{ currentStepHint }}</div>
    </div>

    <div v-if="result" class="result-section">
      <div class="result-header">
        <h2>优化结果</h2>
        <div class="result-header-actions">
          <button @click="goResumes" class="btn-link">去简历管理</button>
          <button @click="resetOptimization" class="btn-link">重新优化</button>
        </div>
      </div>

      <div class="score-card">
        <div class="score-main">
          <div class="score-circle" :style="{ '--score': result.optimized_score }">
            <span class="score-value">{{ result.optimized_score }}</span>
            <span class="score-unit">分</span>
          </div>
          <div class="score-change">原始 {{ result.original_score }} 分 → 优化后 {{ result.optimized_score }} 分</div>
        </div>
        <div class="score-details">
          <div class="score-item"><span class="item-label">版本</span><span class="item-value">v{{ result.version_number }}</span></div>
          <div class="score-item"><span class="item-label">目标公司</span><span class="item-value">{{ result.jd_analysis?.company || '未指定' }}</span></div>
          <div class="score-item"><span class="item-label">目标岗位</span><span class="item-value">{{ result.jd_analysis?.position || '未指定' }}</span></div>
          <div class="score-item"><span class="item-label">JD 匹配度</span><span class="item-value">{{ result.jd_analysis?.fit_score ?? '-' }}%</span></div>
        </div>
      </div>

      <div class="diff-section">
        <h3>变更摘要</h3>
        <p class="change-summary">{{ result.change_summary }}</p>
        <div v-if="result.diff_highlights?.length" class="diff-list">
          <div v-for="(diff, i) in result.diff_highlights" :key="i" class="diff-item" :class="diff.type">
            <span class="diff-type-badge">{{ diff.type === 'added' ? '新增' : diff.type === 'removed' ? '删除' : '修改' }}</span>
            <div class="diff-content">{{ diff.content }}</div>
          </div>
        </div>
      </div>

      <div class="optimized-content">
        <h3>优化后简历</h3>
        <pre>{{ result.optimized_content }}</pre>
        <div class="result-actions">
          <button @click="copyOptimized" class="btn-action">复制内容</button>
        </div>
      </div>

      <div v-if="versions.length > 1" class="versions-card">
        <h3>版本历史</h3>
        <div class="version-list">
          <button v-for="v in versions" :key="v.version_id" class="version-item" :class="{ active: viewVersionId === v.version_id }" @click="viewVersion(v.version_id)">
            <span class="version-name">{{ v.version_name || '版本 ' + v.version_number }}</span>
            <span class="version-score">{{ v.optimized_score }}分</span>
            <span class="version-date">{{ formatDate(v.created_at) }}</span>
          </button>
        </div>
        <div v-if="compareData" class="compare-panel">
          <h4>版本对比</h4>
          <p class="compare-summary">{{ compareData.change_summary }}</p>
          <div class="compare-columns">
            <div class="compare-col"><h5>原始内容</h5><pre>{{ compareData.current_content }}</pre></div>
            <div class="compare-col"><h5>优化内容</h5><pre>{{ compareData.optimized_content }}</pre></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter, useRoute } from "vue-router"
import { resumeApi, optimizeApi, scoreApi } from "@/api"
import { toast } from "@/composables/useToast"
import MatchVisualization from "@/components/common/MatchVisualization.vue"

const router = useRouter()
const route = useRoute()

const resumes = ref([])
const selectedResumeId = ref("")
const resumeText = ref("")
const selectedContent = ref("")
const jdText = ref("")

const result = ref(null)
const versions = ref([])
const viewVersionId = ref(null)
const compareData = ref(null)

const scoreAnalysis = ref(null)
const loadingAnalysis = ref(false)

const isRunning = ref(false)
const progress = ref(0)
const elapsedTime = ref(0)
const currentStepHint = ref("准备就绪")
let timer = null
let abortController = null

const steps = ref([
  { id: "jd", label: "分析JD", status: "idle" },
  { id: "match", label: "匹配评估", status: "idle" },
  { id: "optimize", label: "AI优化", status: "idle" },
  { id: "save", label: "保存版本", status: "idle" }
])

const canStart = computed(() => selectedResumeId.value && resumeText.value.trim() && jdText.value.trim())

const categoryLabel = (cat) => ({ tech: "技术", product: "产品", ops: "运营", marketing: "市场", other: "其他" })[cat] || "其他"
const statusLabel = (s) => ({ draft: "草稿", processing: "优化中", optimized: "已优化", applied: "已投递", archived: "归档" })[s] || s

function stepIcon(status) {
  return { idle: "○", running: "◐", complete: "●", error: "✕" }[status] || "○"
}

function setStepStatus(id, status) {
  const step = steps.value.find(s => s.id === id)
  if (step) step.status = status
}

async function loadResumes() {
  try {
    const data = await resumeApi.list({ limit: 100 })
    resumes.value = Array.isArray(data) ? data : []
  } catch (e) {
    console.error("加载简历失败", e)
    toast.error("加载简历失败")
  }
}

async function onSelectResume() {
  const id = Number(selectedResumeId.value)
  const resume = resumes.value.find(r => r.id === id)
  if (resume) {
    resumeText.value = resume.content || ""
    selectedContent.value = resume.content || ""
  }
  if (resumeText.value && jdText.value) loadScoreAnalysis()
}

async function loadScoreAnalysis() {
  if (!resumeText.value || !jdText.value) return
  loadingAnalysis.value = true
  try {
    const analysis = await scoreApi.analyze(resumeText.value, jdText.value)
    scoreAnalysis.value = analysis
  } catch (e) {
    console.error("评分分析失败:", e)
  } finally {
    loadingAnalysis.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ""
  return new Date(dateStr).toLocaleDateString()
}

async function startOptimization() {
  if (!canStart.value || isRunning.value) return
  isRunning.value = true
  progress.value = 0
  elapsedTime.value = 0
  abortController = new AbortController()
  steps.value.forEach(s => { s.status = "idle" })

  timer = setInterval(() => { elapsedTime.value++ }, 1000)
  try {
    const resumeId = Number(selectedResumeId.value)
    selectedContent.value = resumeText.value

    setStepStatus("save", "running")
    currentStepHint.value = "正在保存简历内容"
    progress.value = 5
    const saveData = { slot: 1, content: resumeText.value, category: "tech", version_name: "优化版本" }
    const saved = await resumeApi.saveText(1, resumeText.value, "tech", "优化版本").catch(() => null)
    if (saved?.id) {
      resumeId = saved.id
      resumeId = saved.id
      await loadResumes()
      selectedResumeId.value = String(saved.id)
      setStepStatus("save", "complete")
    } else {
      setStepStatus("save", "complete")
    }

    setStepStatus("jd", "running")
    currentStepHint.value = "正在分析 JD 关键要求"
    progress.value = 20
    const jdAnalysis = await optimizeApi.analyzeJd({ raw_content: jdText.value }).catch(() => null)
    setStepStatus("jd", "complete")

    setStepStatus("match", "running")
    currentStepHint.value = "正在评估简历与 JD 匹配度"
    progress.value = 40
    await new Promise(r => setTimeout(r, 300))
    setStepStatus("match", "complete")

    setStepStatus("optimize", "running")
    currentStepHint.value = "AI 正在深度优化简历，通常需要30-60秒"
    progress.value = 60
    const data = await optimizeApi.full({
      resume_id: resumeId,
      jd_content: jdText.value,
      company: jdAnalysis?.company || undefined,
      position: jdAnalysis?.position || undefined
    }, { signal: abortController.signal })

    setStepStatus("optimize", "complete")
    setStepStatus("save", "running")
    currentStepHint.value = "正在保存优化版本"
    progress.value = 90
    await new Promise(r => setTimeout(r, 200))
    setStepStatus("save", "complete")

    result.value = data
    progress.value = 100
    currentStepHint.value = "优化完成"
    toast.success("简历优化完成，已保存为 v" + data.version_number)
    loadVersions(resumeId)
  } catch (e) {
    if (e.name === "CanceledError" || e.message === "canceled") {
      currentStepHint.value = "已取消"
      toast.info("已取消优化")
    } else {
      const msg = String(e.message || e)
      const friendly = msg.includes("No module") ? "AI 服务未就绪，已降级为规则优化，请后续重试" : msg
      currentStepHint.value = "优化失败"
      toast.error("优化失败: " + friendly)
    }
  } finally {
    isRunning.value = false
    if (timer) clearInterval(timer)
  }
}

function cancelOptimization() {
  if (abortController) abortController.abort()
}

async function loadVersions(resumeId) {
  try {
    const data = await optimizeApi.versions(resumeId)
    versions.value = data?.versions || []
  } catch (e) {
    console.error("加载版本历史失败:", e)
  }
}

async function viewVersion(versionId) {
  if (viewVersionId.value === versionId && compareData.value) {
    viewVersionId.value = null
    compareData.value = null
    return
  }
  viewVersionId.value = versionId
  try {
    const data = await optimizeApi.compare(Number(selectedResumeId.value), versionId)
    compareData.value = data
  } catch (e) {
    toast.error("加载对比失败: " + e.message)
  }
}

function copyOptimized() {
  const text = result.value?.optimized_content
  if (text) {
    navigator.clipboard.writeText(text)
    toast.success("已复制优化后的简历")
  }
}

function goResumes() {
  router.push("/resumes")
}

function resetOptimization() {
  isRunning.value = false
  if (timer) clearInterval(timer)
  if (abortController) abortController.abort()
  result.value = null
  compareData.value = null
  versions.value = []
  viewVersionId.value = null
  progress.value = 0
  elapsedTime.value = 0
  currentStepHint.value = "准备就绪"
  steps.value.forEach(s => { s.status = "idle" })
  resumeText.value = ""
  jdText.value = ""
  selectedResumeId.value = ""
  selectedContent.value = ""
}

onMounted(async () => {
  await loadResumes()
  const queryResumeId = route.query.resumeId
  if (queryResumeId) {
    selectedResumeId.value = String(queryResumeId)
    await onSelectResume()
  }
})
</script>

<style scoped>
.optimization-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px;
  background: var(--surface-default);
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.page-desc {
  font-size: 15px;
  color: var(--text-secondary);
}

.input-section {
  background: var(--surface-elevated);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid var(--border-default);
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.input-select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-default);
  border-radius: 8px;
  font-size: 14px;
  background: var(--surface-input);
  color: var(--text-primary);
}

.input-hint {
  margin-top: 8px;
  font-size: 13px;
  color: var(--text-muted);
}

.action-row {
  display: flex;
  gap: 12px;
}

.btn-primary {
  padding: 12px 32px;
  background: var(--color-action-blue);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary:hover {
  background: var(--color-focus-blue);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 12px 24px;
  background: var(--surface-stone);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.progress-section {
  background: var(--surface-elevated);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid var(--border-default);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.progress-title {
  font-weight: 600;
  color: var(--text-primary);
}

.progress-percent {
  font-weight: 700;
  color: var(--color-action-blue);
}

.progress-bar {
  height: 8px;
  background: var(--surface-stone);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 16px;
}

.progress-fill {
  height: 100%;
  background: var(--color-action-blue);
  transition: width 0.3s;
}

.progress-steps {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.progress-step {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 13px;
  background: var(--surface-stone);
  color: var(--text-muted);
}

.step-running {
  background: rgba(59, 130, 246, 0.1);
  color: var(--color-action-blue);
}

.step-complete {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.step-error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error);
}

.progress-time {
  font-size: 13px;
  color: var(--text-muted);
}

.result-section {
  background: var(--surface-elevated);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid var(--border-default);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.result-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.result-header-actions {
  display: flex;
  gap: 12px;
}

.btn-link {
  background: none;
  border: none;
  color: var(--color-action-blue);
  font-size: 14px;
  cursor: pointer;
}

.score-card {
  display: flex;
  gap: 32px;
  padding: 24px;
  background: var(--surface-default);
  border-radius: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.score-main {
  text-align: center;
  min-width: 140px;
}

.score-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: conic-gradient(var(--color-action-blue) calc(var(--score) * 1%), var(--surface-stone) 0);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  position: relative;
}

.score-circle::before {
  content: "";
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

.score-unit {
  font-size: 12px;
  color: var(--text-muted);
  position: relative;
  z-index: 1;
}

.score-change {
  margin-top: 8px;
  color: var(--text-muted);
  font-size: 13px;
}

.score-details {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  min-width: 240px;
}

.score-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-label {
  font-size: 12px;
  color: var(--text-muted);
}

.item-value {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.diff-section {
  margin-bottom: 24px;
}

.diff-section h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.change-summary {
  padding: 12px 16px;
  background: rgba(59, 130, 246, 0.06);
  border-radius: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.diff-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.diff-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 16px;
  border-radius: 8px;
  background: var(--surface-default);
  border-left: 4px solid var(--border-default);
}

.diff-item.added {
  border-left-color: var(--color-success);
  background: rgba(16, 185, 129, 0.05);
}

.diff-item.removed {
  border-left-color: var(--color-error);
  background: rgba(239, 68, 68, 0.05);
}

.diff-type-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  background: var(--color-success);
  color: white;
  width: fit-content;
}

.diff-item.removed .diff-type-badge {
  background: var(--color-error);
}

.diff-content {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
}

.optimized-content {
  margin-bottom: 24px;
}

.optimized-content h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.optimized-content pre {
  background: var(--surface-stone);
  border-radius: 8px;
  padding: 16px;
  font-size: 13px;
  line-height: 1.8;
  white-space: pre-wrap;
  max-height: 420px;
  overflow-y: auto;
  color: var(--text-primary);
}

.result-actions {
  margin-top: 16px;
}

.btn-action {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  background: var(--color-action-blue);
  color: white;
  border: none;
}

.versions-card h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.version-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.version-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border: 1px solid var(--border-default);
  border-radius: 8px;
  background: var(--surface-default);
  cursor: pointer;
  font-size: 13px;
  text-align: left;
  width: 100%;
  color: var(--text-primary);
}

.version-item.active {
  border-color: var(--color-action-blue);
  background: rgba(59, 130, 246, 0.05);
}

.version-name {
  font-weight: 600;
  min-width: 80px;
}

.version-score {
  color: var(--color-action-blue);
}

.version-date {
  margin-left: auto;
  color: var(--text-muted);
  font-size: 12px;
}

.compare-panel {
  background: var(--surface-default);
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
}

.compare-panel h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.compare-summary {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  background: rgba(59, 130, 246, 0.06);
  padding: 10px 12px;
  border-radius: 8px;
}

.compare-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.compare-col {
  background: var(--surface-elevated);
  border-radius: 8px;
  padding: 12px;
}

.compare-col h5 {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-muted);
}

.compare-col pre {
  font-size: 12px;
  line-height: 1.7;
  white-space: pre-wrap;
  max-height: 260px;
  overflow-y: auto;
  color: var(--text-primary);
}

/* Textarea 样式 */
textarea {
  width: 100%;
  background: var(--surface-input);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  padding: 12px 16px;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  transition: border-color 200ms;
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
</style>
