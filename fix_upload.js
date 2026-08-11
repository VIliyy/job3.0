const fs = require('fs');

const uploadVue = `<template>
  <div class="upload-page">
    <div class="page-header">
      <div>
        <h1>上传分析</h1>
        <p class="subtitle">上传简历或JD，获取AI智能分析</p>
      </div>
    </div>

    <!-- 上传选项卡 -->
    <div class="upload-tabs">
      <button
        @click="activeTab = 'resume'"
        class="tab-btn"
        :class="{ active: activeTab === 'resume' }"
      >
        📄 上传简历
      </button>
      <button
        @click="activeTab = 'jd'"
        class="tab-btn"
        :class="{ active: activeTab === 'jd' }"
      >
        📋 上传JD
      </button>
      <button
        @click="activeTab = 'text'"
        class="tab-btn"
        :class="{ active: activeTab === 'text' }"
      >
        ✏️ 粘贴文本
      </button>
    </div>

    <!-- 上传简历 -->
    <div v-if="activeTab === 'resume'" class="upload-content">
      <div class="upload-area" @click="triggerFileInput('resume')">
        <input ref="resumeInput" type="file" accept=".pdf,.doc,.docx" @change="handleFileSelect($event, 'resume')" hidden />
        <div class="upload-icon">📄</div>
        <div class="upload-text">点击上传简历或拖拽文件到此处</div>
        <div class="upload-hint">支持 PDF、Word 格式，最大 10MB</div>
      </div>

      <div v-if="resumeFile" class="selected-file">
        <div class="file-info">
          <span class="file-icon">✓</span>
          <span class="file-name">{{ resumeFile.name }}</span>
          <span class="file-size">{{ formatFileSize(resumeFile.size) }}</span>
        </div>
        <button @click="resumeFile = null" class="file-remove">×</button>
      </div>

      <div class="action-buttons">
        <button @click="uploadResume" class="btn-primary" :disabled="!resumeFile || uploading">
          {{ uploading ? '上传中...' : '上传并分析' }}
        </button>
      </div>
    </div>

    <!-- 上传JD -->
    <div v-if="activeTab === 'jd'" class="upload-content">
      <div class="upload-area" @click="triggerFileInput('jd')">
        <input ref="jdInput" type="file" accept=".pdf,.doc,.docx,.txt" @change="handleFileSelect($event, 'jd')" hidden />
        <div class="upload-icon">📋</div>
        <div class="upload-text">点击上传职位描述或拖拽文件到此处</div>
        <div class="upload-hint">支持 PDF、Word、TXT 格式</div>
      </div>

      <div v-if="jdFile" class="selected-file">
        <div class="file-info">
          <span class="file-icon">✓</span>
          <span class="file-name">{{ jdFile.name }}</span>
          <span class="file-size">{{ formatFileSize(jdFile.size) }}</span>
        </div>
        <button @click="jdFile = null" class="file-remove">×</button>
      </div>

      <div class="action-buttons">
        <button @click="uploadJD" class="btn-primary" :disabled="!jdFile || uploading">
          {{ uploading ? '上传中...' : '上传并解析' }}
        </button>
      </div>
    </div>

    <!-- 粘贴文本 -->
    <div v-if="activeTab === 'text'" class="upload-content">
      <div class="text-input-area">
        <div class="input-label">粘贴职位描述（JD）</div>
        <textarea
          v-model="jdText"
          class="textarea"
          rows="12"
          placeholder="在此粘贴职位描述内容..."
        ></textarea>
        <div class="char-count">字符数: {{ jdText.length }}</div>
      </div>

      <div class="action-buttons">
        <button @click="analyzeText" class="btn-primary" :disabled="!jdText.trim() || analyzing">
          {{ analyzing ? '分析中...' : '开始分析' }}
        </button>
      </div>
    </div>

    <!-- 分析结果 -->
    <div v-if="analysisResult" class="analysis-result">
      <div class="result-header">
        <h2>📊 分析结果</h2>
        <button @click="analysisResult = null" class="btn-close">×</button>
      </div>

      <div class="score-card">
        <div class="score-circle" :class="getScoreClass(analysisResult.score)">
          <span class="score-value">{{ analysisResult.score }}</span>
          <span class="score-label">匹配度</span>
        </div>
        <div class="score-text">
          <h3>{{ getScoreText(analysisResult.score) }}</h3>
          <p>{{ getScoreDesc(analysisResult.score) }}</p>
        </div>
      </div>

      <div class="result-section">
        <h3>🎯 关键技能要求</h3>
        <div class="skills-list">
          <div v-for="(skill, index) in analysisResult.skills" :key="index" class="skill-item">
            <span class="skill-name">{{ skill.name }}</span>
            <span class="skill-level" :class="skill.level">{{ skill.levelText }}</span>
          </div>
        </div>
      </div>

      <div class="result-section">
        <h3>💡 优化建议</h3>
        <div class="suggestions-list">
          <div v-for="(suggestion, index) in analysisResult.suggestions" :key="index" class="suggestion-item">
            <span class="suggestion-icon">{{ suggestion.type === 'strong' ? '✓' : '!' }}</span>
            <div class="suggestion-content">
              <div class="suggestion-title">{{ suggestion.title }}</div>
              <div class="suggestion-desc">{{ suggestion.description }}</div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab !== 'resume'" class="result-section">
        <h3>📄 建议使用的简历版本</h3>
        <div class="resume-selection">
          <div
            v-for="i in 4"
            :key="i"
            class="resume-option"
            :class="{ selected: selectedResumeVersion === i }"
            @click="selectedResumeVersion = i"
          >
            <div class="resume-icon">📄</div>
            <div class="resume-name">版本 {{ i }}</div>
            <div v-if="resumes[i]" class="resume-status">已上传</div>
            <div v-else class="resume-status empty">未上传</div>
          </div>
        </div>
        <button @click="optimizeResume" class="btn-secondary" :disabled="!selectedResumeVersion">
          ✨ 根据JD优化简历
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="uploading || analyzing" class="loading-overlay">
      <div class="loading-spinner"></div>
      <div class="loading-text">{{ uploading ? '文件上传中...' : 'AI分析中...' }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const activeTab = ref('resume')
const resumeFile = ref(null)
const jdFile = ref(null)
const jdText = ref('')
const uploading = ref(false)
const analyzing = ref(false)
const analysisResult = ref(null)
const selectedResumeVersion = ref(1)
const resumes = reactive({})

const resumeInput = ref(null)
const jdInput = ref(null)

const triggerFileInput = (type) => {
  if (type === 'resume') {
    resumeInput.value?.click()
  } else if (type === 'jd') {
    jdInput.value?.click()
  }
}

const handleFileSelect = (event, type) => {
  const file = event.target.files[0]
  if (file) {
    if (type === 'resume') {
      resumeFile.value = file
    } else if (type === 'jd') {
      jdFile.value = file
    }
  }
}

const uploadResume = async () => {
  if (!resumeFile.value) return
  uploading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    resumes[1] = { name: resumeFile.value.name }
    alert('简历上传成功！')
  } catch (error) {
    console.error('上传失败:', error)
    alert('上传失败，请重试')
  } finally {
    uploading.value = false
  }
}

const uploadJD = async () => {
  if (!jdFile.value) return
  uploading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    analyzeJD('文件上传')
  } catch (error) {
    console.error('上传失败:', error)
    alert('上传失败，请重试')
    uploading.value = false
  }
}

const analyzeText = () => {
  if (!jdText.value.trim()) return
  analyzeJD('文本粘贴')
}

const analyzeJD = (source) => {
  analyzing.value = true
  setTimeout(() => {
    analysisResult.value = {
      score: Math.floor(Math.random() * 30) + 70,
      skills: [
        { name: 'Python', level: 'required', levelText: '必备' },
        { name: 'Django/Flask', level: 'required', levelText: '必备' },
        { name: 'MySQL', level: 'preferred', levelText: '优先' },
        { name: 'Redis', level: 'preferred', levelText: '优先' },
        { name: 'Docker', level: 'optional', levelText: '加分' }
      ],
      suggestions: [
        { type: 'strong', title: '突出Python开发经验', description: '简历中应强调3年以上的Python实际项目经验' },
        { type: 'strong', title: '补充框架实践', description: '建议添加Django或Flask的实际项目经验描述' },
        { type: 'normal', title: '数据库经验', description: '可补充MySQL或PostgreSQL的使用经验' },
        { type: 'normal', title: 'DevOps技能', description: '有Docker/Kubernetes经验会增加竞争力' }
      ]
    }
    analyzing.value = false
    uploading.value = false
  }, 3000)
}

const optimizeResume = () => {
  if (!selectedResumeVersion.value) return
  alert('将根据JD优化简历版本 ' + selectedResumeVersion.value + '...')
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const getScoreClass = (score) => {
  if (score >= 90) return 'excellent'
  if (score >= 75) return 'good'
  if (score >= 60) return 'average'
  return 'poor'
}

const getScoreText = (score) => {
  if (score >= 90) return '非常匹配！'
  if (score >= 75) return '匹配度良好'
  if (score >= 60) return '基本匹配'
  return '匹配度较低'
}

const getScoreDesc = (score) => {
  if (score >= 90) return '您的简历与该职位高度匹配，建议重点投递'
  if (score >= 75) return '简历与职位要求较为匹配，可以投递'
  if (score >= 60) return '简历基本符合要求，建议优化后投递'
  return '简历与职位要求有一定差距，建议针对性优化'
}
</script>

<style scoped>
.upload-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 32px;
}

.page-header h1 {
  font-size: 48px;
  font-weight: 500;
  color: var(--color-primary);
  margin: 0;
  letter-spacing: -1.44px;
}

.subtitle {
  color: var(--color-text-muted);
  margin: 8px 0 0 0;
}

.upload-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 32px;
  background: var(--color-soft-stone);
  padding: 8px;
  border-radius: 16px;
}

.tab-btn {
  flex: 1;
  padding: 12px 20px;
  background: transparent;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 150ms;
}

.tab-btn:hover {
  background: rgba(255, 255, 255, 0.5);
}

.tab-btn.active {
  background: var(--color-canvas);
  color: var(--color-primary);
  box-shadow: var(--shadow-level-1);
}

.upload-content {
  background: var(--color-canvas);
  border: 1px solid var(--color-border-light);
  border-radius: 22px;
  padding: 32px;
  margin-bottom: 32px;
}

.upload-area {
  border: 2px dashed var(--color-border-light);
  border-radius: 16px;
  padding: 64px 32px;
  text-align: center;
  cursor: pointer;
  transition: all 150ms;
  margin-bottom: 24px;
}

.upload-area:hover {
  border-color: var(--color-action-blue);
  background: var(--color-soft-stone);
}

.upload-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 18px;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.upload-hint {
  font-size: 14px;
  color: var(--color-text-muted);
}

.selected-file {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: var(--color-soft-stone);
  border-radius: 12px;
  margin-bottom: 24px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon {
  font-size: 24px;
  color: var(--color-success);
}

.file-name {
  font-size: 16px;
  font-weight: 500;
}

.file-size {
  font-size: 14px;
  color: var(--color-text-muted);
}

.file-remove {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--color-error);
  cursor: pointer;
  font-size: 20px;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.btn-primary {
  flex: 1;
  padding: 14px 28px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 150ms;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 12px 24px;
  background: var(--color-soft-stone);
  color: var(--color-primary);
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.text-input-area {
  margin-bottom: 24px;
}

.input-label {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 12px;
}

.textarea {
  width: 100%;
  padding: 16px;
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  line-height: 1.6;
}

.textarea:focus {
  outline: none;
  border-color: var(--color-action-blue);
}

.char-count {
  text-align: right;
  font-size: 13px;
  color: var(--color-text-muted);
  margin-top: 8px;
}

.analysis-result {
  background: var(--color-canvas);
  border: 1px solid var(--color-border-light);
  border-radius: 22px;
  padding: 32px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.result-header h2 {
  font-size: 24px;
  margin: 0;
}

.btn-close {
  width: 32px;
  height: 32px;
  border: none;
  background: var(--color-soft-stone);
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
}

.score-card {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 24px;
  background: var(--color-soft-stone);
  border-radius: 16px;
  margin-bottom: 24px;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-weight: 500;
}

.score-circle.excellent {
  background: rgba(34, 197, 94, 0.2);
  color: var(--color-success);
}

.score-circle.good {
  background: rgba(24, 99, 220, 0.2);
  color: var(--color-action-blue);
}

.score-circle.average {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.score-circle.poor {
  background: rgba(179, 0, 0, 0.2);
  color: var(--color-error);
}

.score-value {
  font-size: 36px;
}

.score-label {
  font-size: 14px;
}

.score-text h3 {
  font-size: 24px;
  margin: 0 0 8px 0;
}

.score-text p {
  color: var(--color-text-muted);
  margin: 0;
}

.result-section {
  margin-bottom: 24px;
}

.result-section:last-child {
  margin-bottom: 0;
}

.result-section h3 {
  font-size: 18px;
  margin: 0 0 16px 0;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.skill-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--color-soft-stone);
  border-radius: 8px;
}

.skill-name {
  font-size: 14px;
  font-weight: 500;
}

.skill-level {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.skill-level.required {
  background: rgba(179, 0, 0, 0.1);
  color: var(--color-error);
}

.skill-level.preferred {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.skill-level.optional {
  background: rgba(34, 197, 94, 0.1);
  color: var(--color-success);
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: var(--color-soft-stone);
  border-radius: 12px;
}

.suggestion-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 16px;
  flex-shrink: 0;
}

.suggestion-item:first-child .suggestion-icon {
  background: var(--color-success);
  color: white;
}

.suggestion-item:last-child .suggestion-icon {
  background: #f59e0b;
  color: white;
}

.suggestion-content {
  flex: 1;
}

.suggestion-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.suggestion-desc {
  font-size: 14px;
  color: var(--color-text-muted);
}

.resume-selection {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.resume-option {
  padding: 16px;
  background: var(--color-soft-stone);
  border: 2px solid transparent;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 150ms;
}

.resume-option:hover {
  border-color: var(--color-action-blue);
}

.resume-option.selected {
  border-color: var(--color-action-blue);
  background: rgba(24, 99, 220, 0.1);
}

.resume-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.resume-name {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.resume-status {
  font-size: 12px;
  color: var(--color-success);
}

.resume-status.empty {
  color: var(--color-text-muted);
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  color: white;
  font-size: 16px;
}
</style>
`;

fs.writeFileSync('E:/job3.0/frontend/src/views/Upload.vue', uploadVue, 'utf8');
console.log('✅ Upload.vue 已成功修复！');
