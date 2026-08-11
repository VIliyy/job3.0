<template>
  <div class="resumes-page">
    <header class="page-header">
      <h1>简历管理</h1>
      <p class="page-desc">管理多类目标简历，记录投递状态</p>
    </header>

    <div class="category-tabs">
      <button 
        v-for="cat in categories" 
        :key="cat.value"
        :class="['tab-btn', { active: selectedCategory === cat.value }]"
        @click="selectedCategory = cat.value"
      >
        <span class="tab-icon">{{ cat.icon }}</span>
        <span class="tab-label">{{ cat.label }}</span>
        <span class="tab-count">{{ getCategoryCount(cat.value) }}</span>
      </button>
    </div>

    <div class="resume-grid">
      <div
        v-for="resume in filteredResumes"
        :key="resume.id"
        class="resume-card"
        :class="{ active: activeResumeId === resume.id }"
        @click="openDetail(resume)"
      >
        <div class="card-header">
          <span class="card-category" :class="resume.category">
            {{ getCategoryLabel(resume.category) }}
          </span>
          <span class="card-status" :class="resume.status">
            {{ getStatusLabel(resume.status) }}
          </span>
        </div>
        
        <div class="card-body">
          <h3 class="card-title">{{ resume.version_name || '未命名简历' }}</h3>
          <p class="card-meta">
            槽位 {{ resume.slot }} · {{ resume.file_type?.toUpperCase() || 'TXT' }}
          </p>
          <p class="card-date">{{ formatDate(resume.updated_at) }}</p>
        </div>

        <div class="card-footer">
          <button @click.stop="openDetail(resume)" class="btn-action view">查看</button>
          <button @click.stop="optimizeResume(resume)" class="btn-action optimize">优化</button>
          <button @click.stop="applyToJob(resume)" class="btn-action apply">投递</button>
          <button @click.stop="deleteResume(resume)" class="btn-action delete">删除</button>
        </div>
      </div>

      <div class="resume-card add-card" @click="showUploadModal = true">
        <div class="add-icon">+</div>
        <p class="add-text">上传新简历</p>
      </div>
    </div>

    <div class="applications-section">
      <div class="section-header">
        <h2>投递记录</h2>
        <select v-model="filterStatus" class="filter-select">
          <option value="">全部状态</option>
          <option v-for="s in applicationStatuses" :key="s.value" :value="s.value">
            {{ s.label }}
          </option>
        </select>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="filteredApplications.length === 0" class="empty-state">
        <p>暂无投递记录</p>
      </div>

      <div v-else class="application-grid">
        <div 
          v-for="app in filteredApplications" 
          :key="app.id"
          class="application-card"
          :class="app.status"
        >
          <div class="app-header">
            <div class="app-company">{{ app.company }}</div>
            <span class="app-status-badge" :class="app.status">
              {{ getAppStatusLabel(app.status) }}
            </span>
          </div>
          <div class="app-body">
            <p class="app-position">{{ app.position || '未指定岗位' }}</p>
            <p class="app-meta">
              <span v-if="app.location">{{ app.location }}</span>
              <span v-if="app.salary">{{ app.salary }}</span>
            </p>
          </div>
          <div class="app-footer">
            <div class="app-date">{{ formatDate(app.created_at) }}</div>
            <button @click="deleteApplication(app)" class="btn-sm danger">删除</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showDetailModal" class="modal-overlay" @click="closeDetail">
      <div class="modal modal-detail" @click.stop>
        <div class="modal-header">
          <h3>{{ detail?.version_name || detail?.filename || '简历详情' }}</h3>
          <button class="modal-close" @click="closeDetail">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-meta">
            <span class="detail-meta-item">槽位 {{ detail?.slot }}</span>
            <span class="detail-meta-item">{{ getCategoryLabel(detail?.category) }}</span>
            <span class="detail-meta-item">{{ getStatusLabel(detail?.status) }}</span>
            <span class="detail-meta-item">更新于 {{ formatDate(detail?.updated_at) }}</span>
          </div>

          <div class="detail-section">
            <h4>简历内容</h4>
            <pre class="resume-content">{{ detail?.content || '（暂无内容）' }}</pre>
          </div>

          <div v-if="versions.length" class="detail-section">
            <h4>版本历史（点击查看对比）</h4>
            <div class="version-list">
              <button
                v-for="v in versions"
                :key="v.version_id"
                class="version-item"
                :class="{ active: viewVersionId === v.version_id }"
                @click="viewVersion(v.version_id)"
              >
                <span class="version-name">{{ v.version_name || 'v' + v.version_number }}</span>
                <span class="version-score" v-if="v.original_score != null">{{ v.original_score }} → {{ v.optimized_score }} 分</span>
                <span class="version-date">{{ formatDate(v.created_at) }}</span>
              </button>
            </div>
          </div>

          <div v-if="compareData" class="detail-section compare-panel">
            <h4>优化对比 v{{ compareData.version_number }}</h4>
            <p v-if="compareData.change_summary" class="compare-summary">{{ compareData.change_summary }}</p>
            <div v-if="compareData.diff_highlights && compareData.diff_highlights.length" class="diff-list">
              <div v-for="(diff, index) in compareData.diff_highlights" :key="index" class="diff-item" :class="diff.type">
                <span class="diff-type-badge">{{ diffTypeLabel(diff.type) }}</span>
                <span class="diff-content">{{ diff.content || diff.new_content }}</span>
              </div>
            </div>
            <div class="compare-columns">
              <div class="compare-col">
                <h5>优化前（{{ compareData.original_score }} 分）</h5>
                <pre>{{ compareData.current_content }}</pre>
              </div>
              <div class="compare-col">
                <h5>优化后（{{ compareData.optimized_score }} 分）</h5>
                <pre>{{ compareData.optimized_content }}</pre>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="deleteResume(detail)" class="btn-cancel danger-outline">删除该简历</button>
          <button @click="closeDetail" class="btn-cancel">关闭</button>
        </div>
      </div>
    </div>

    <div v-if="showUploadModal" class="modal-overlay" @click="showUploadModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>上传简历</h3>
          <button class="modal-close" @click="showUploadModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>简历名称</label>
            <input v-model="uploadData.versionName" placeholder="例如：技术岗-腾讯" class="input" />
          </div>
          <div class="form-group">
            <label>简历类别</label>
            <select v-model="uploadData.category" class="input">
              <option v-for="cat in categories.slice(1)" :key="cat.value" :value="cat.value">
                {{ cat.icon }} {{ cat.label }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>简历内容</label>
            <textarea v-model="uploadData.content" rows="10" class="input textarea" placeholder="粘贴简历文本内容..."></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showUploadModal = false" class="btn-cancel">取消</button>
          <button @click="saveTextResume" class="btn-primary" :disabled="!uploadData.content">
            保存
          </button>
        </div>
      </div>
    </div>

    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteConfirm">
      <div class="modal modal-confirm" @click.stop>
        <div class="modal-header">
          <h3>删除简历</h3>
          <button class="modal-close" @click="closeDeleteConfirm">×</button>
        </div>
        <div class="modal-body">
          <p class="confirm-text">
            确定删除「{{ pendingDelete?.version_name || pendingDelete?.filename || '这份简历' }}」吗？
            <br />删除后不可恢复。
          </p>
        </div>
        <div class="modal-footer">
          <button @click="closeDeleteConfirm" class="btn-cancel">取消</button>
          <button @click="confirmDelete" class="btn-primary btn-danger">确认删除</button>
        </div>
      </div>
    </div>

    <div v-if="showApplyModal" class="modal-overlay" @click="showApplyModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>记录投递</h3>
          <button class="modal-close" @click="showApplyModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>公司名称 *</label>
            <input v-model="applyData.company" class="input" />
          </div>
          <div class="form-group">
            <label>岗位名称</label>
            <input v-model="applyData.position" class="input" />
          </div>
          <div class="form-group">
            <label>薪资范围</label>
            <input v-model="applyData.salary" class="input" />
          </div>
          <div class="form-group">
            <label>工作地点</label>
            <input v-model="applyData.location" class="input" />
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showApplyModal = false" class="btn-cancel">取消</button>
          <button @click="submitApplication" class="btn-primary" :disabled="!applyData.company">
            确认投递
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { resumeApi, applicationApi, optimizeApi } from '@/api'
import { toast } from '@/composables/useToast'

const router = useRouter()

const resumes = ref([])
const applications = ref([])
const activeResumeId = ref(null)
const selectedCategory = ref('all')
const filterStatus = ref('')
const loading = ref(false)
const isLoadingResumes = ref(false)
const isLoadingApps = ref(false)
const showUploadModal = ref(false)
const showApplyModal = ref(false)
const showDetailModal = ref(false)
const detail = ref(null)
const versions = ref([])
const compareData = ref(null)
const viewVersionId = ref(null)
const showDeleteModal = ref(false)
const pendingDelete = ref(null)

const uploadData = ref({ content: '', versionName: '', category: 'tech', slot: 1 })
const applyData = ref({ resume_id: null, company: '', position: '', salary: '', location: '' })

const categories = [
  { value: 'all', label: '全部', icon: '📋', count: 0 },
  { value: 'tech', label: '技术', icon: '💻', count: 0 },
  { value: 'product', label: '产品', icon: '📱', count: 0 },
  { value: 'ops', label: '运营', icon: '📊', count: 0 },
  { value: 'other', label: '其他', icon: '📄', count: 0 }
]

const applicationStatuses = [
  { value: 'pending', label: '待处理' },
  { value: 'submitted', label: '已投递' },
  { value: 'viewed', label: '已查看' },
  { value: 'interview', label: '面试中' },
  { value: 'offer', label: '录用' },
  { value: 'rejected', label: '拒绝' }
]

const filteredResumes = computed(() => {
  if (selectedCategory.value === 'all') return resumes.value
  return resumes.value.filter(r => r.category === selectedCategory.value)
})

const filteredApplications = computed(() => {
  if (!filterStatus.value) return applications.value
  return applications.value.filter(a => a.status === filterStatus.value)
})

function getCategoryCount(category) {
  if (category === 'all') return resumes.value.length
  return resumes.value.filter(r => r.category === category).length
}

function getCategoryLabel(category) {
  const cat = categories.find(c => c.value === category)
  return cat ? cat.label : '其他'
}

function getStatusLabel(status) {
  const labels = { draft: '草稿', processing: '优化中', optimized: '已优化', applied: '已投递' }
  return labels[status] || status
}

function getAppStatusLabel(status) {
  const s = applicationStatuses.find(a => a.value === status)
  return s ? s.label : status
}

function formatDate(date) {
  if (!date) return '未知'
  return new Date(date).toLocaleDateString('zh-CN')
}

async function loadData() {
  loading.value = true
  try {
    const [resumeData, appData] = await Promise.all([
      resumeApi.list().catch(() => []),
      applicationApi.list().catch(() => [])
    ])
    resumes.value = resumeData || []
    applications.value = appData || []
  } catch (e) {
    console.error('加载失败:', e)
  } finally {
    loading.value = false
  }
}

function selectResume(resume) {
  activeResumeId.value = resume.id
}

function diffTypeLabel(type) {
  return { added: '新增', removed: '删除', modified: '修改' }[type] || type || '修改'
}

async function openDetail(resume) {
  activeResumeId.value = resume.id
  detail.value = null
  versions.value = []
  compareData.value = null
  viewVersionId.value = null
  showDetailModal.value = true
  try {
    detail.value = await resumeApi.get(resume.id)
    await loadVersions(resume.id)
  } catch (e) {
    toast.error('加载简历详情失败: ' + e.message)
  }
}

function closeDetail() {
  showDetailModal.value = false
  detail.value = null
  versions.value = []
  compareData.value = null
  viewVersionId.value = null
}

async function loadVersions(resumeId) {
  try {
    const data = await optimizeApi.versions(resumeId)
    versions.value = data?.versions || []
  } catch (e) {
    console.error('加载版本历史失败:', e)
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
    compareData.value = await optimizeApi.compare(detail.value.id, versionId)
  } catch (e) {
    toast.error('加载对比失败: ' + e.message)
  }
}

function deleteResume(resume) {
  if (!resume || !resume.id) return
  pendingDelete.value = resume
  showDeleteModal.value = true
}

function closeDeleteConfirm() {
  showDeleteModal.value = false
  pendingDelete.value = null
}

async function confirmDelete() {
  const resume = pendingDelete.value
  closeDeleteConfirm()
  if (!resume) return
  try {
    await resumeApi.delete(resume.id)
    closeDetail()
    toast.success('简历已删除')
    loadData()
  } catch (e) {
    toast.error('删除失败: ' + e.message)
  }
}

function optimizeResume(resume) {
  router.push({ path: '/optimize', query: { resumeId: resume.id } })
}

function applyToJob(resume) {
  applyData.value.resume_id = resume.id
  applyData.value.company = ''
  applyData.value.position = ''
  showApplyModal.value = true
}

async function submitApplication() {
  try {
    await applicationApi.create(applyData.value)
    showApplyModal.value = false
    loadData()
    toast.success('投递记录已保存')
  } catch (e) {
    toast.error('提交失败: ' + e.message)
  }
}

async function deleteApplication(app) {
  if (!window.confirm('确定删除这条投递记录？')) return
  try {
    await applicationApi.delete(app.id)
    loadData()
    toast.success('投递记录已删除')
  } catch (e) {
    toast.error('删除失败: ' + e.message)
  }
}

async function saveTextResume() {
  if (!uploadData.value.content) return
  const usedSlots = resumes.value.map(r => r.slot)
  const availableSlot = [1, 2, 3, 4].find(s => !usedSlots.includes(s)) || 1
  try {
    await resumeApi.saveText(availableSlot, uploadData.value.content, uploadData.value.category, uploadData.value.versionName)
    showUploadModal.value = false
    loadData()
    toast.success('简历已保存')
  } catch (e) {
    toast.error('保存失败: ' + e.message)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.resumes-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
  background: var(--surface-default);
}
.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 28px; font-weight: 700; margin-bottom: 4px; }
.page-desc { font-size: 15px; color: var(--text-secondary); }
.category-tabs { display: flex; gap: 8px; margin-bottom: 24px; flex-wrap: wrap; }
.tab-btn { display: flex; align-items: center; gap: 8px; padding: 10px 16px; background: var(--surface-elevated); border: 1px solid var(--border-default); border-radius: 8px; font-size: 14px; cursor: pointer; }
.tab-btn.active { background: var(--color-info); border-color: var(--color-info); color: white; }
.tab-count { background: rgba(0,0,0,0.1); padding: 2px 8px; border-radius: 10px; font-size: 12px; }
.resume-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; margin-bottom: 40px; }
.resume-card { background: var(--surface-elevated); border-radius: 12px; padding: 20px; border: 2px solid transparent; cursor: pointer; transition: all 200ms; }
.resume-card:hover { border-color: var(--border-default); }
.resume-card.active { border-color: var(--color-info); }
.resume-card.add-card { border: 2px dashed var(--border-default); display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 180px; color: var(--text-muted); }
.resume-card.add-card:hover { border-color: var(--color-info); color: var(--color-info); }
.add-icon { font-size: 48px; margin-bottom: 8px; }
.add-text { font-size: 14px; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.card-category { font-size: 11px; font-weight: 600; padding: 4px 8px; border-radius: 4px; background: var(--surface-stone); color: var(--text-secondary); }
.card-category.tech { background: rgba(59,130,246,0.1); color: var(--color-info); }
.card-category.product { background: rgba(139,92,246,0.1); color: var(--agent-planner); }
.card-status { font-size: 11px; padding: 4px 8px; border-radius: 4px; background: var(--surface-stone); }
.card-body { margin-bottom: 16px; }
.card-title { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
.card-meta, .card-date { font-size: 13px; color: var(--text-muted); margin-bottom: 4px; }
.card-footer { display: flex; gap: 8px; }
.btn-action { flex: 1; padding: 8px; border: 1px solid var(--border-default); border-radius: 6px; font-size: 12px; cursor: pointer; }
.btn-action.optimize { background: rgba(59,130,246,0.1); border-color: rgba(59,130,246,0.3); color: var(--color-info); }
.btn-action.apply { background: rgba(16,185,129,0.1); border-color: rgba(16,185,129,0.3); color: var(--color-success); }
.btn-action.view { background: rgba(139,92,246,0.1); border-color: rgba(139,92,246,0.3); color: var(--agent-planner); }
.btn-action.delete { background: rgba(239,68,68,0.08); border-color: rgba(239,68,68,0.3); color: var(--color-error); }
.danger-outline { border-color: rgba(239,68,68,0.4) !important; color: var(--color-error) !important; }
.btn-danger { background: var(--color-error) !important; border-color: var(--color-error) !important; }
.confirm-text { font-size: 14px; line-height: 1.8; color: var(--text); }
.modal-detail { max-width: 860px; }
.detail-meta { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 16px; font-size: 13px; color: var(--text-muted); }
.detail-section { margin-bottom: 20px; }
.detail-section h4 { font-size: 15px; font-weight: 600; margin-bottom: 8px; }
.resume-content { background: var(--surface-stone); border-radius: 8px; padding: 14px; white-space: pre-wrap; word-break: break-word; font-size: 13px; line-height: 1.7; max-height: 300px; overflow-y: auto; }
.version-list { display: flex; flex-direction: column; gap: 8px; }
.version-item { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 14px; border: 1px solid var(--border-default); border-radius: 8px; background: var(--surface-elevated); cursor: pointer; font-size: 13px; width: 100%; }
.version-item.active { border-color: var(--color-info); background: rgba(59,130,246,0.06); }
.version-name { font-weight: 600; }
.version-score { color: var(--color-info); }
.version-date { color: var(--text-muted); font-size: 12px; }
.compare-summary { font-size: 13px; color: var(--text-secondary); background: rgba(59,130,246,0.06); padding: 10px 12px; border-radius: 8px; margin-bottom: 10px; }
.diff-list { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.diff-item { display: flex; gap: 8px; align-items: flex-start; font-size: 13px; padding: 6px 10px; border-radius: 6px; background: var(--surface-stone); }
.diff-item.added { background: rgba(16,185,129,0.08); }
.diff-item.removed { background: rgba(239,68,68,0.08); }
.diff-type-badge { flex-shrink: 0; font-size: 11px; font-weight: 600; padding: 2px 6px; border-radius: 4px; background: var(--surface-default); }
.compare-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.compare-col h5 { font-size: 13px; margin-bottom: 6px; color: var(--text-secondary); }
.compare-col pre { background: var(--surface-stone); border-radius: 8px; padding: 12px; white-space: pre-wrap; word-break: break-word; font-size: 12px; line-height: 1.6; max-height: 260px; overflow-y: auto; }
.applications-section { background: var(--surface-elevated); border-radius: 12px; padding: 24px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.section-header h2 { font-size: 20px; font-weight: 600; }
.filter-select { padding: 8px 12px; border: 1px solid var(--border-default); border-radius: 6px; }
.application-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.application-card { background: var(--surface-default); border-radius: 8px; padding: 16px; border-left: 4px solid var(--border-default); }
.application-card.pending { border-left-color: var(--color-warning); }
.application-card.interview { border-left-color: var(--agent-planner); }
.application-card.offer { border-left-color: var(--color-success); }
.application-card.rejected { border-left-color: var(--color-error); }
.app-header { display: flex; justify-content: space-between; margin-bottom: 12px; }
.app-company { font-weight: 600; }
.app-status-badge { font-size: 11px; padding: 4px 8px; background: var(--surface-stone); border-radius: 4px; }
.app-position { font-size: 14px; color: var(--text-secondary); margin-bottom: 4px; }
.app-meta { font-size: 12px; color: var(--text-muted); }
.app-meta span { margin-right: 12px; }
.app-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 12px; }
.app-date { font-size: 12px; color: var(--text-muted); }
.btn-sm { padding: 6px 12px; border: 1px solid var(--border-default); border-radius: 4px; font-size: 12px; cursor: pointer; }
.btn-sm.danger { border-color: rgba(239,68,68,0.3); color: var(--color-error); }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { background: var(--surface-elevated); border-radius: 12px; width: 90%; max-width: 500px; max-height: 90vh; overflow-y: auto; }
.modal-header { display: flex; justify-content: space-between; padding: 20px; border-bottom: 1px solid var(--border-default); }
.modal-header h3 { font-size: 18px; font-weight: 600; }
.modal-close { background: none; border: none; font-size: 24px; cursor: pointer; }
.modal-body { padding: 20px; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; padding: 20px; border-top: 1px solid var(--border-default); }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-weight: 600; font-size: 14px; margin-bottom: 8px; }
.input { width: 100%; padding: 10px; border: 1px solid var(--border-default); border-radius: 6px; font-size: 14px; }
.input:focus { outline: none; border-color: var(--color-info); }
.textarea { resize: vertical; font-family: inherit; }
.btn-primary { padding: 10px 24px; background: var(--color-info); color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-cancel { padding: 10px 24px; background: var(--surface-elevated); border: 1px solid var(--border-default); border-radius: 8px; font-size: 14px; cursor: pointer; }
.loading-state, .empty-state { text-align: center; padding: 40px; color: var(--text-muted); }
.loading-spinner { width: 32px; height: 32px; border: 3px solid var(--border-default); border-top-color: var(--color-info); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 12px; }
@keyframes spin { to { transform: rotate(360deg); } }

/* === Dark Mode Optimizations === */
:root.dark .page-desc { color: #c4c4cc; }
:root.dark .card-title { color: #fafafa; }
:root.dark .card-meta, :root.dark .card-date { color: #a8a8b3; }
:root.dark .resume-content { background: #2d2d35; border: 1px solid #3f3f46; color: #e4e4e7; }
:root.dark .applications-section { background: #242429; border: 1px solid #3f3f46; }
:root.dark .version-item { background: #2a2a30; border-color: #3f3f46; }
:root.dark .version-item.active { background: rgba(76, 110, 230, 0.12); border-color: #4c6ee6; }
:root.dark .compare-summary { background: rgba(76, 110, 230, 0.12); color: #a1a1aa; }
:root.dark .diff-item { background: #35353d; }
:root.dark .diff-item.added { background: rgba(16, 185, 129, 0.15); }
:root.dark .diff-item.removed { background: rgba(239, 68, 68, 0.15); }
:root.dark .compare-col pre { background: #2d2d35; }
:root.dark .application-card { background: #2a2a30; }
:root.dark .app-position { color: #c4c4cc; }
:root.dark .tab-btn { border-color: #3f3f46; }
:root.dark .tab-btn:hover { border-color: #52525b; background: #2a2a30; }
:root.dark .resume-card { border-color: #2f2f35; }
:root.dark .resume-card:hover { border-color: #3f3f46; }
:root.dark .add-card { border-color: #3f3f46; color: #71717a; }
:root.dark .add-card:hover { border-color: #4c6ee6; color: #4c6ee6; }
:root.dark .resume-card.add-card { border-color: #3f3f46; }
:root.dark .filter-select { background: #2a2a30; border-color: #3f3f46; color: #e4e4e7; }
:root.dark .btn-sm { border-color: #3f3f46; }
:root.dark .input { background: #2a2a30; border-color: #3f3f46; color: #e4e4e7; }
:root.dark .modal { background: #242429; }
:root.dark .modal-header, :root.dark .modal-body, :root.dark .modal-footer { border-color: #3f3f46; }
:root.dark .modal-close { color: #71717a; }
:root.dark .loading-spinner { border-color: #3f3f46; }

:root.dark .btn-action { border-color: #3f3f46; color: #a1a1aa; }
:root.dark .btn-action:hover { background: #2a2a30; border-color: #52525b; color: #fafafa; }
:root.dark .btn-action.optimize { background: rgba(76, 110, 230, 0.15); border-color: rgba(76, 110, 230, 0.5); color: #6b8cff; }
:root.dark .btn-action.apply { background: rgba(16, 185, 129, 0.15); border-color: rgba(16, 185, 129, 0.5); color: #34d399; }
:root.dark .btn-action.view { background: rgba(139, 92, 246, 0.15); border-color: rgba(139, 92, 246, 0.5); color: #a78bfa; }
:root.dark .btn-action.delete { background: rgba(239, 68, 68, 0.15); border-color: rgba(239, 68, 68, 0.5); color: #f87171; }
:root.dark .btn-action.optimize:hover { background: rgba(76, 110, 230, 0.25); }
:root.dark .btn-action.apply:hover { background: rgba(16, 185, 129, 0.25); }
:root.dark .btn-action.view:hover { background: rgba(139, 92, 246, 0.25); }
:root.dark .btn-action.delete:hover { background: rgba(239, 68, 68, 0.25); }
</style>
