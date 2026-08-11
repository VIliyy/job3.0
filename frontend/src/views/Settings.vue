<template>
  <div class="settings-page">
    <h1>Settings</h1>
    <p>Configure AI API Key</p>
    
    <div class="section">
      <h2>AI Settings</h2>
      <div class="status-card">
        <span>{{ statusText }}</span>
      </div>
      
      <div class="form-group">
        <label>API Key</label>
        <input v-model="apiKey" type="password" placeholder="sk-..." class="input" />
      </div>
      
      <button @click="saveAPIKey" class="btn-save">Save</button>
    </div>
    
    <div class="section">
      <h2>Local Data</h2>
      <button @click="clearData" class="btn-clear">Clear All</button>
    </div>
    
    <div v-if="message" class="toast" :class="messageType">{{ message }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue"

const apiKey = ref("")
const saving = ref(false)
const message = ref("")
const messageType = ref("success")
const aiEnabled = ref(false)

const statusText = computed(() => aiEnabled.value ? "[OK] AI 已启用" : "[X] 未配置 API Key")

onMounted(async () => {
  try {
    const { settingsApi } = await import("@/api")
    const status = await settingsApi.getAIStatus()
    aiEnabled.value = status.ai_enabled || false
  } catch (e) {
    console.error(e)
  }
})

const showMsg = (msg: string, type = "success") => {
  message.value = msg
  messageType.value = type
  setTimeout(() => { message.value = "" }, 3000)
}

const saveAPIKey = async () => {
  if (!apiKey.value) return
  saving.value = true
  try {
    const { settingsApi } = await import("@/api")
    await settingsApi.setDeepSeekKey(apiKey.value)
    aiEnabled.value = true
    showMsg("API Key 已保存")
    apiKey.value = ""
  } catch (err: any) {
    showMsg(err.message || "保存失败", "error")
  } finally {
    saving.value = false
  }
}

const clearData = () => {
  if (confirm("Clear all data?")) {
    localStorage.clear()
    showMsg("Data cleared")
  }
}
</script>



<style scoped>
.settings-page { max-width: 800px; margin: 0 auto; padding: 24px;
  background: var(--surface-default); }
h1 { font-size: 36px; margin: 0 0 8px 0; }
.section { background: var(--color-canvas); border: 1px solid var(--color-border-light); border-radius: 22px; padding: 24px; margin-bottom: 24px; }
.section h2 { font-size: 18px; margin: 0 0 20px 0; }
.status-card { padding: 16px; background: rgba(245, 158, 11, 0.1); border-radius: 12px; margin-bottom: 20px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 14px; font-weight: 500; margin-bottom: 8px; }
.input { width: 100%; padding: 12px 16px; border: 1px solid var(--color-border-light); border-radius: 8px; font-size: 14px; }
.btn-save { width: 100%; padding: 14px; background: var(--color-primary); color: white; border: none; border-radius: 10px; cursor: pointer; }
.btn-clear { padding: 8px 16px; background: rgba(239, 68, 68, 0.1); color: var(--color-error); border: 1px solid var(--color-error); border-radius: 8px; cursor: pointer; }
.toast { position: fixed; bottom: 32px; left: 50%; transform: translateX(-50%); padding: 12px 24px; border-radius: 10px; font-size: 14px; z-index: 1000; }
.toast.success { background: var(--color-success); color: white; }
.toast.error { background: var(--color-error); color: white; }
textarea { background: var(--surface-input); color: var(--text-primary); border: 1px solid var(--border-default); border-radius: var(--radius-sm); padding: 12px 16px; font-family: inherit; font-size: 14px; line-height: 1.6; resize: vertical; transition: border-color 200ms, background-color 200ms; } textarea:focus { outline: none; border-color: var(--color-action-blue); } textarea::placeholder { color: var(--text-muted); } textarea:disabled { background: var(--surface-stone); color: var(--text-muted); cursor: not-allowed; }

/* === Dark Mode Optimizations === */
:root.dark .settings-page { background: var(--color-background); }
:root.dark h1 { color: #f4f4f5; }
:root.dark p { color: #a1a1aa; }
:root.dark .section { background: #242429; border-color: #3f3f46; }
:root.dark .section h2 { color: #e4e4e7; }
:root.dark .status-card { background: rgba(245, 158, 11, 0.15); }
:root.dark .form-group label { color: #e4e4e7; }
:root.dark .input { background: #2a2a30; border-color: #3f3f46; color: #f4f4f5; }
:root.dark .input::placeholder { color: #71717a; }
:root.dark .btn-save { background: #4c6ee6; }
:root.dark .btn-save:hover { background: #5c7cfa; }
:root.dark .btn-clear { background: rgba(239, 68, 68, 0.15); color: #f87171; border-color: rgba(239, 68, 68, 0.5); }
:root.dark .btn-clear:hover { background: rgba(239, 68, 68, 0.25); }
:root.dark textarea { background: #2a2a30; border-color: #3f3f46; color: #f4f4f5; }
</style>