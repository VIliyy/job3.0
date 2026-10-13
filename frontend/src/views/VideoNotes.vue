<template>
  <div class="video-notes-page">
    <div class="page-header">
      <h1>视频笔记</h1>
      <p>输入 B站 / 抖音链接或本地音视频，AI 自动生成精炼笔记，可一键导出到 Obsidian 知识库</p>
    </div>

    <div class="layout">
      <div class="left-col">
        <!-- 生成表单 -->
        <div class="card">
          <h2>生成笔记</h2>
          <div class="form-group">
            <label>平台</label>
            <select v-model="form.platform" class="input">
              <option value="auto">自动识别</option>
              <option value="bilibili">哔哩哔哩</option>
              <option value="douyin">抖音</option>
              <option value="local">本地文件</option>
            </select>
          </div>
          <div v-if="form.platform !== 'local'" class="form-group">
            <label>视频链接</label>
            <input v-model="form.videoUrl" class="input" placeholder="https://www.bilibili.com/video/BVxxxx" />
          </div>
          <div v-else class="form-group">
            <label>本地音视频文件</label>
            <input type="file" class="input" accept="video/*,audio/*" @change="onFileChange" />
            <div v-if="form.videoUrl" class="file-hint">已选择：{{ form.videoUrl }}</div>
          </div>
          <div class="form-group">
            <label>笔记风格</label>
            <select v-model="form.style" class="input">
              <option value="minimal">精简</option>
              <option value="detailed">详细</option>
              <option value="tutorial">教程</option>
              <option value="academic">学术</option>
              <option value="meeting_minutes">会议纪要</option>
              <option value="xiaohongshu">小红书</option>
              <option value="summary">极简总结</option>
            </select>
          </div>
          <div class="form-group">
            <label>附加格式</label>
            <div class="checkbox-row">
              <label class="checkbox-inline"><input type="checkbox" value="toc" v-model="form.formats" /> 目录</label>
              <label class="checkbox-inline"><input type="checkbox" value="link" v-model="form.formats" /> 原片跳转</label>
              <label class="checkbox-inline"><input type="checkbox" value="summary" v-model="form.formats" /> AI总结</label>
            </div>
          </div>
          <div class="form-group">
            <label>额外要求（可选）</label>
            <textarea v-model="form.extras" class="input" rows="2" placeholder="例如：重点记录代码示例、结论数据"></textarea>
          </div>
          <div class="form-group">
            <label class="checkbox-inline">
              <input type="checkbox" v-model="form.exportObsidian" /> 生成后自动导出到 Obsidian 知识库
            </label>
          </div>
          <button class="btn-primary" :disabled="busy" @click="submit">{{ busy ? '生成中…' : '开始生成' }}</button>
        </div>

        <!-- Obsidian 配置 -->
        <div class="card">
          <h2>Obsidian 知识库</h2>
          <div class="form-group">
            <label>Vault 根目录路径</label>
            <input v-model="obsidianPath" class="input" placeholder="C:\Users\xxx\Documents\MyVault" />
          </div>
          <div class="config-status" :class="obsidianValid ? 'ok' : 'warn'">{{ obsidianStatus }}</div>
          <div class="form-group">
            <label>LLM 状态</label>
            <div class="config-status" :class="llmConfigured ? 'ok' : 'warn'">{{ llmStatus }}</div>
            <div v-if="!llmConfigured" class="form-hint">在 backend/.env 配置 DEEPSEEK_API_KEY 或 OPENAI_API_KEY</div>
          </div>
          <button class="btn-primary" @click="saveConfig">保存配置</button>
        </div>
      </div>

      <div class="right-col">
        <!-- 任务列表 -->
        <div class="card">
          <h2>任务记录</h2>
          <div v-if="tasks.length === 0" class="empty">暂无任务，粘贴链接开始吧</div>
          <div
            v-for="t in tasks"
            :key="t.task_id"
            class="task-item"
            :class="{ active: current && current.task_id === t.task_id }"
            @click="openTask(t.task_id)"
          >
            <div class="task-head">
              <span class="task-title">{{ t.title || t.video_url.slice(0, 40) }}</span>
              <div class="task-right">
                <span class="badge" :class="t.status.toLowerCase()">{{ statusText(t.status) }}</span>
                <button class="task-delete" title="删除任务" @click.stop="deleteTask(t)">&times;</button>
              </div>
            </div>
            <div class="task-meta">{{ t.platform }} · {{ t.status_message || '排队中' }}</div>
          </div>
        </div>

        <!-- 笔记详情 -->
        <div v-if="current" class="card">
          <div class="detail-head">
            <h2>{{ current.title || '笔记' }}</h2>
            <div class="detail-actions">
              <button v-if="current.markdown && current.status === 'SUCCESS'" class="btn" @click="copyMarkdown">复制</button>
              <button v-if="current.markdown && current.status === 'SUCCESS'" class="btn" @click="exportObsidian">导出 Obsidian</button>
            </div>
          </div>
          <div v-if="current.status === 'FAILED'" class="config-status warn">失败：{{ current.error }}</div>
          <div v-if="current.obsidian_path" class="config-status ok">📓 已导出：{{ current.obsidian_path }}</div>
          <div v-else-if="current.obsidian_message && current.obsidian_message !== '已导出'" class="config-status warn">📓 {{ current.obsidian_message }}</div>
          <div v-if="current.markdown" class="markdown-body" v-html="mdHtml(current.markdown)"></div>
          <div v-else-if="current.status === 'SUCCESS'" class="empty">笔记为空</div>
          <div v-else class="empty">处理中，请稍候…</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { videoApi } from '@/api'
import { toast } from '@/composables/useToast'

const form = reactive({
  platform: 'auto',
  videoUrl: '',
  style: 'minimal',
  formats: [],
  extras: '',
  exportObsidian: false,
  file: null
})
const busy = ref(false)
const tasks = ref([])
const current = ref(null)
const obsidianPath = ref('')
const obsidianValid = ref(false)
const obsidianStatus = ref('未配置')
const llmConfigured = ref(false)
const llmStatus = ref('检查中…')

let timer = null
const ACTIVE = ['PENDING', 'PARSING', 'DOWNLOADING', 'TRANSCRIBING', 'SUMMARIZING', 'OBSIDIAN']

const statusText = (s) => ({
  PENDING: '排队中', PARSING: '解析中', DOWNLOADING: '下载中',
  TRANSCRIBING: '转写中', SUMMARIZING: '总结中', OBSIDIAN: '导出中',
  SUCCESS: '完成', FAILED: '失败'
}[s] || s)

const loadTasks = async () => {
  try {
    tasks.value = await videoApi.listTasks(50)
  } catch (e) { console.error(e) }
}

const openTask = async (taskId) => {
  try {
    current.value = await videoApi.getTask(taskId)
  } catch (e) { console.error(e) }
}

const deleteTask = async (t) => {
  if (!window.confirm('确定删除任务「' + (t.title || t.video_url.slice(0, 40)) + '」？删除后不可恢复。')) return
  try {
    await videoApi.deleteTask(t.task_id)
    toast.success('任务已删除')
    tasks.value = tasks.value.filter((x) => x.task_id !== t.task_id)
    if (current.value && current.value.task_id === t.task_id) current.value = null
  } catch (e) {
    toast.error('删除失败：' + (e.message || e))
  }
}

const refreshCurrent = async () => {
  if (!current.value || !ACTIVE.includes(current.value.status)) return
  try {
    current.value = await videoApi.getTask(current.value.task_id)
    await loadTasks()
  } catch (e) { console.error(e) }
}

const onFileChange = (e) => {
  const file = e.target.files && e.target.files[0]
  if (!file) return
  form.file = file
  form.videoUrl = file.name
}

const submit = async () => {
  if (busy.value) return
  busy.value = true
  try {
    let videoUrl = form.videoUrl
    if (form.platform === 'local') {
      if (!form.file) { alert('请先选择本地文件'); return }
      const up = await videoApi.uploadLocal(form.file)
      videoUrl = up.path
    }
    if (!videoUrl) { alert('请输入视频链接或选择文件'); return }
    const task = await videoApi.generate({
      video_url: videoUrl,
      platform: form.platform,
      style: form.style,
      formats: form.formats,
      extras: form.extras || null,
      export_obsidian: form.exportObsidian
    })
    await loadTasks()
    await openTask(task.task_id)
  } catch (e) {
    alert('生成失败：' + (e.message || e))
  } finally {
    busy.value = false
  }
}

const loadConfig = async () => {
  try {
    const cfg = await videoApi.getConfig()
    obsidianPath.value = cfg.obsidian_vault_path || ''
    obsidianValid.value = !!cfg.obsidian_valid
    obsidianStatus.value = cfg.obsidian_valid ? '✓ Obsidian 库已连接' : ('✗ ' + (cfg.obsidian_message || '未配置'))
    llmConfigured.value = !!cfg.llm_configured
    llmStatus.value = cfg.llm_configured ? ('✓ ' + cfg.llm_provider) : '✗ 未配置 LLM API Key'
  } catch (e) { console.error(e) }
}

const saveConfig = async () => {
  try {
    await videoApi.saveConfig({ obsidian_vault_path: obsidianPath.value })
    await loadConfig()
    alert('配置已保存')
  } catch (e) {
    alert('保存失败：' + (e.message || e))
  }
}

const copyMarkdown = async () => {
  try {
    await navigator.clipboard.writeText(current.value.markdown)
    alert('已复制到剪贴板')
  } catch (e) { alert('复制失败：' + e.message) }
}

const exportObsidian = async () => {
  try {
    const res = await videoApi.exportObsidian(current.value.task_id)
    await openTask(current.value.task_id)
    alert('已导出：' + res.path)
  } catch (e) {
    alert('导出失败：' + (e.message || e))
  }
}

// 极简 Markdown 渲染（先转义 HTML 防注入）
const escapeHtml = (s) => String(s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

const mdHtml = (md) => {
  if (!md) return ''
  let html = ''
  let inCode = false
  let inList = false
  const closeList = () => { if (inList) { html += '</ul>'; inList = false } }
  for (const raw of escapeHtml(md).split('\n')) {
    const line = raw.replace(/\r$/, '')
    const t = line.trim()
    if (t.startsWith('```')) {
      closeList()
      if (inCode) { html += '</code></pre>'; inCode = false }
      else { html += '<pre><code>'; inCode = true }
      continue
    }
    if (inCode) { html += line + '\n'; continue }
    if (/^#{1,4} /.test(line)) {
      closeList()
      const m = line.match(/^(#{1,4}) (.*)$/)
      const level = m[1].length
      html += `<h${level}>${m[2]}</h${level}>`
    } else if (/^\s*[-*] /.test(line)) {
      if (!inList) { html += '<ul>'; inList = true }
      html += `<li>${line.replace(/^\s*[-*] /, '')}</li>`
    } else if (/^\s*---+\s*$/.test(line)) {
      closeList(); html += '<hr/>'
    } else if (t === '') {
      closeList()
    } else {
      closeList()
      html += `<p>${line}</p>`
    }
  }
  closeList()
  if (inCode) html += '</code></pre>'
  return html
}

onMounted(async () => {
  await loadConfig()
  await loadTasks()
  timer = setInterval(() => {
    loadTasks()
    refreshCurrent()
  }, 3000)
})
onBeforeUnmount(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.video-notes-page { max-width: 1200px; margin: 0 auto; padding: 24px; }
.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 30px; margin: 0 0 8px 0; }
.page-header p { color: var(--text-muted); margin: 0; }
.layout { display: grid; grid-template-columns: 380px 1fr; gap: 20px; align-items: start; }
.left-col, .right-col { min-width: 0; }
@media (max-width: 1000px) { .layout { grid-template-columns: 1fr; } }
.card { background: var(--surface-default); border: 1px solid var(--border-default); border-radius: 16px; padding: 20px; margin-bottom: 20px; }
.card h2 { font-size: 16px; margin: 0 0 16px 0; }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-secondary); }
.input { width: 100%; padding: 10px 12px; border: 1px solid var(--border-default); border-radius: 8px; font-size: 14px; background: var(--surface-input); color: var(--text-primary); box-sizing: border-box; }
.input:focus { outline: none; border-color: var(--color-action-blue); }
textarea.input { font-family: inherit; resize: vertical; }
.checkbox-row { display: flex; gap: 16px; flex-wrap: wrap; }
.checkbox-inline { display: inline-flex !important; align-items: center; gap: 6px; font-size: 13px !important; color: var(--text-secondary) !important; cursor: pointer; }
.file-hint, .form-hint { font-size: 12px; color: var(--text-muted); margin-top: 6px; }
.btn-primary { width: 100%; padding: 12px; background: var(--color-action-blue); color: #fff; border: none; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn { padding: 6px 14px; background: transparent; color: var(--color-action-blue); border: 1px solid var(--border-default); border-radius: 8px; font-size: 13px; cursor: pointer; }
.btn:hover { border-color: var(--color-action-blue); }
.config-status { padding: 10px 12px; border-radius: 8px; font-size: 13px; margin-bottom: 12px; }
.config-status.ok { background: rgba(34, 197, 94, 0.1); color: var(--color-success); }
.config-status.warn { background: rgba(245, 158, 11, 0.1); color: var(--color-warning); }
.task-item { padding: 12px; border: 1px solid var(--border-default); border-radius: 10px; margin-bottom: 8px; cursor: pointer; transition: all 150ms; }
.task-item:hover { border-color: var(--color-action-blue); }
.task-item.active { border-color: var(--color-action-blue); background: rgba(37, 99, 235, 0.06); }
.task-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.task-title { font-size: 13px; font-weight: 500; overflow-wrap: anywhere; word-break: break-word; min-width: 0; }
.task-meta { font-size: 12px; color: var(--text-muted); margin-top: 4px; overflow-wrap: anywhere; word-break: break-word; }
.badge { padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600; white-space: nowrap; flex-shrink: 0; }
.task-right { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.task-delete { padding: 2px 8px; background: transparent; color: var(--text-muted); border: 1px solid var(--border-default); border-radius: 6px; font-size: 13px; line-height: 1.4; cursor: pointer; flex-shrink: 0; }
.task-delete:hover { color: var(--color-error); border-color: var(--color-error); }
.badge.success { background: rgba(34, 197, 94, 0.15); color: var(--color-success); }
.badge.failed { background: rgba(239, 68, 68, 0.15); color: var(--color-error); }
.badge.downloading, .badge.transcribing, .badge.summarizing, .badge.parsing, .badge.pending, .badge.obsidian { background: rgba(245, 158, 11, 0.15); color: var(--color-warning); }
.detail-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; flex-wrap: wrap; }
.detail-head h2 { margin-bottom: 8px; min-width: 0; overflow-wrap: anywhere; word-break: break-word; }
.detail-actions { display: flex; gap: 8px; flex-shrink: 0; }
.empty { padding: 24px 0; text-align: center; color: var(--text-muted); font-size: 14px; }
.markdown-body { line-height: 1.7; font-size: 14px; color: var(--text-primary); overflow-wrap: anywhere; word-break: break-word; min-width: 0; }
.markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4 { margin: 16px 0 8px; line-height: 1.4; }
.markdown-body p { margin: 8px 0; }
.markdown-body ul { margin: 8px 0; padding-left: 22px; }
.markdown-body pre { background: var(--surface-stone); border-radius: 8px; padding: 12px; overflow-x: auto; font-size: 13px; }
.markdown-body hr { border: none; border-top: 1px solid var(--border-default); margin: 16px 0; }
</style>
