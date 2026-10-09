<template>
  <div class="settings-page">
    <h1>Settings</h1>
    <p>Configure AI API Key &amp; 工具箱设置</p>
    
    <div class="section">
      <h2>AI Settings</h2>
      <div class="status-card">
        <span>{{ statusText }}</span>
      </div>
      
      <div class="form-group">
        <label for="api-key">API Key</label>
        <input id="api-key" v-model="apiKey" type="password" placeholder="sk-..." class="input" />
      </div>
      
      <button @click="saveAPIKey" class="btn-save" :disabled="saving || !apiKey">{{ saving ? '保存中...' : '保存' }}</button>
    </div>

    <div class="section">
      <h2>Obsidian 知识库（视频笔记导出）</h2>
      <div class="form-group">
        <label for="obsidian-path">Vault 根目录路径</label>
        <input id="obsidian-path" v-model="obsidianPath" class="input" placeholder="C:\Users\xxx\Documents\MyVault" />
      </div>
      <div class="status-card" :class="obsidianValid ? 'status-ok' : 'status-warn'">
        <span>{{ obsidianStatus }}</span>
      </div>
      <button @click="saveObsidian" class="btn-save" :disabled="saving">{{ saving ? '保存中...' : '保存 Obsidian 配置' }}</button>
    </div>
    
    <div class="section">
      <h2>Local Data</h2>
      <p class="section-hint">仅清除本浏览器中的界面偏好，不会删除服务器上的简历、投递或聊天记录。</p>
      <button @click="clearData" class="btn-clear">清除本地偏好</button>
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
const obsidianPath = ref("")
const obsidianValid = ref(false)
const obsidianStatus = ref("未配置")

const statusText = computed(() => aiEnabled.value ? "[OK] AI 已启用" : "[X] 未配置 API Key")

onMounted(async () => {
  try {
    const { settingsApi } = await import("@/api")
    const status = await settingsApi.getAIStatus()
    aiEnabled.value = status.ai_enabled || false
  } catch (e) {
    console.error(e)
  }
  try {
    const { videoApi } = await import("@/api")
    const cfg = await videoApi.getConfig()
    obsidianPath.value = cfg.obsidian_vault_path || ""
    obsidianValid.value = !!cfg.obsidian_valid
    obsidianStatus.value = cfg.obsidian_valid ? "[OK] Obsidian 库已连接" : "[X] " + (cfg.obsidian_message || "未配置路径")
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

const saveObsidian = async () => {
  saving.value = true
  try {
    const { videoApi } = await import("@/api")
    await videoApi.saveConfig({ obsidian_vault_path: obsidianPath.value })
    const cfg = await videoApi.getConfig()
    obsidianValid.value = !!cfg.obsidian_valid
    obsidianStatus.value = cfg.obsidian_valid ? "[OK] Obsidian 库已连接" : "[X] " + (cfg.obsidian_message || "路径无效")
    showMsg("Obsidian 配置已保存")
  } catch (err: any) {
    showMsg(err.message || "保存失败", "error")
  } finally {
    saving.value = false
  }
}

const clearData = () => {
  if (confirm("Clear all data?")) {
    localStorage.removeItem('theme')
    document.documentElement.classList.remove('dark')
    showMsg("本地偏好已清除")
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
.status-ok { background: rgba(34, 197, 94, 0.1) !important; }
.status-warn { background: rgba(245, 158, 11, 0.1) !important; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 14px; font-weight: 500; margin-bottom: 8px; }
.input { width: 100%; padding: 12px 16px; border: 1px solid var(--color-border-light); border-radius: 8px; font-size: 14px; }
.btn-save { width: 100%; padding: 14px; background: var(--color-primary); color: white; border: none; border-radius: 10px; cursor: pointer; }
.btn-save:disabled { opacity: 0.55; cursor: not-allowed; }
.btn-clear { padding: 8px 16px; background: rgba(239, 68, 68, 0.1); color: var(--color-error); border: 1px solid var(--color-error); border-radius: 8px; cursor: pointer; }
.section-hint { margin: -8px 0 16px; color: var(--text-muted); font-size: 13px; line-height: 1.5; }
.toast { position: fixed; bottom: 32px; left: 50%; transform: translateX(-50%); padding: 12px 24px; border-radius: 10px; font-size: 14px; z-index: 1000; }
.toast.success { background: var(--color-success); color: white; }
.toast.error { background: var(--color-error); color: white; }
textarea { background: var(--surface-input); color: var(--text-primary); border: 1px solid var(--border-default); border-radius: var(--radius-sm); padding: 12px 16px; font-family: inherit; font-size: 14px; line-height: 1.6; resize: vertical; transition: border-color 200ms, background-color 200ms; } textarea:focus { outline: none; border-color: var(--color-action-blue); } textarea::placeholder { color: var(--text-muted); } textarea:disabled { background: var(--surface-stone); color: var(--text-muted); cursor: not-allowed; }

/* === Dark Mode Optimizations === */
:root.dark .settings-page { background: var(--color-background); }
</style>
