<template>
  <main class="settings-page">
    <header class="page-header">
      <div class="eyebrow">工作台配置</div>
      <div class="header-row">
        <div>
          <h1>设置</h1>
          <p>管理 AI 服务、知识库和本地偏好，让工具箱更贴合你的工作方式。</p>
        </div>
        <div class="header-mark" aria-hidden="true">偏好</div>
      </div>
    </header>

    <div class="settings-layout">
      <section class="settings-section ai-section" aria-labelledby="ai-title">
        <div class="section-heading">
          <div>
            <span class="section-kicker">01 / 智能能力</span>
            <h2 id="ai-title">AI 服务</h2>
            <p>选择一个服务商，登录控制台创建密钥后即可启用 AI 功能。</p>
          </div>
          <div class="connection-badge" :class="{ connected: aiEnabled }">
            <span class="status-dot" aria-hidden="true"></span>
            {{ aiEnabled ? '已连接' : '等待配置' }}
          </div>
        </div>

        <div class="provider-grid" role="radiogroup" aria-label="选择 AI 服务商">
          <button
            v-for="provider in providers"
            :key="provider.id"
            type="button"
            class="provider-card"
            :class="{ selected: selectedProvider === provider.id }"
            role="radio"
            :aria-checked="selectedProvider === provider.id"
            @click="selectProvider(provider.id)"
          >
            <span class="provider-symbol" :class="provider.id">{{ provider.symbol }}</span>
            <span class="provider-copy">
              <strong>{{ provider.name }}</strong>
              <small>{{ provider.description }}</small>
            </span>
            <span class="provider-check" aria-hidden="true">{{ selectedProvider === provider.id ? '✓' : '' }}</span>
          </button>
        </div>

        <div class="setup-guide">
          <div class="guide-icon" aria-hidden="true">↗</div>
          <div class="guide-copy">
            <strong>还没有 {{ currentProvider.name }} 密钥？</strong>
            <p>前往服务商控制台登录，创建一个 API 密钥，再回到这里完成连接。</p>
          </div>
          <a
            class="guide-link"
            :href="currentProvider.consoleUrl"
            target="_blank"
            rel="noreferrer"
          >
            前往控制台
          </a>
        </div>

        <div class="form-grid">
          <div class="form-group form-group-wide">
            <label for="api-key">API 密钥</label>
            <div class="input-with-action">
              <input
                id="api-key"
                v-model="apiKey"
                :type="showApiKey ? 'text' : 'password'"
                :placeholder="currentProvider.placeholder"
                autocomplete="off"
              />
              <button
                type="button"
                class="input-action"
                :aria-label="showApiKey ? '隐藏 API 密钥' : '显示 API 密钥'"
                @click="showApiKey = !showApiKey"
              >
                {{ showApiKey ? '隐藏' : '显示' }}
              </button>
            </div>
            <span class="field-hint">密钥只会用于当前项目的 AI 请求，不会显示完整内容。</span>
          </div>

          <div class="form-group">
            <label for="model">模型</label>
            <select id="model" v-model="model">
              <option v-for="option in currentProvider.models" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
        </div>

        <div class="section-actions">
          <span class="save-note">{{ aiEnabled ? `当前使用 ${providerLabel}` : '配置后即可使用简历分析和 AI 助手' }}</span>
          <button type="button" class="primary-button" :disabled="saving || !apiKey" @click="saveAPIKey">
            {{ saving ? '保存中…' : '保存 AI 配置' }}
          </button>
        </div>
      </section>

      <section class="settings-section obsidian-section" aria-labelledby="obsidian-title">
        <div class="section-heading">
          <div>
            <span class="section-kicker">02 / 内容出口</span>
            <h2 id="obsidian-title">Obsidian 知识库</h2>
            <p>设置视频笔记的导出位置，生成后可以一键写入你的知识库。</p>
          </div>
          <div class="connection-badge" :class="{ connected: obsidianValid }">
            <span class="status-dot" aria-hidden="true"></span>
            {{ obsidianValid ? '路径已连接' : '等待配置' }}
          </div>
        </div>

        <div class="form-group">
          <label for="obsidian-path">知识库根目录</label>
          <input id="obsidian-path" v-model="obsidianPath" class="text-input" placeholder="例如：E:\\obsidian-vault" />
          <span class="field-hint">请输入本机 Obsidian Vault 的完整路径。</span>
        </div>

        <div class="path-status" :class="obsidianValid ? 'status-ok' : 'status-warn'" role="status">
          <span class="status-icon" aria-hidden="true">{{ obsidianValid ? '✓' : '!' }}</span>
          <span>{{ obsidianStatus }}</span>
        </div>

        <div class="section-actions">
          <span class="save-note">导出功能会使用这个目录创建 Markdown 笔记</span>
          <button type="button" class="secondary-button" :disabled="saving" @click="saveObsidian">
            {{ saving ? '保存中…' : '保存知识库配置' }}
          </button>
        </div>
      </section>

      <section class="settings-section local-section" aria-labelledby="local-title">
        <div class="section-heading compact-heading">
          <div>
            <span class="section-kicker">03 / 当前设备</span>
            <h2 id="local-title">本地偏好</h2>
            <p>清除当前浏览器保存的界面偏好，不会删除服务器上的简历、投递或聊天记录。</p>
          </div>
        </div>
        <button type="button" class="danger-button" @click="clearData">清除本地偏好</button>
      </section>
    </div>

    <div v-if="message" class="toast" :class="messageType" role="status">{{ message }}</div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

type ProviderId = 'deepseek' | 'openai'

interface ProviderOption {
  id: ProviderId
  name: string
  symbol: string
  description: string
  placeholder: string
  consoleUrl: string
  models: Array<{ value: string; label: string }>
}

const providers: ProviderOption[] = [
  {
    id: 'deepseek',
    name: 'DeepSeek',
    symbol: 'D',
    description: '适合日常求职分析',
    placeholder: '请输入 DeepSeek API 密钥',
    consoleUrl: 'https://platform.deepseek.com/api_keys',
    models: [
      { value: 'deepseek-chat', label: 'DeepSeek Chat' },
      { value: 'deepseek-reasoner', label: 'DeepSeek Reasoner' }
    ]
  },
  {
    id: 'openai',
    name: 'OpenAI',
    symbol: 'O',
    description: '适合复杂内容生成',
    placeholder: '请输入 OpenAI API 密钥',
    consoleUrl: 'https://platform.openai.com/api-keys',
    models: [
      { value: 'gpt-4o-mini', label: 'GPT-4o mini' },
      { value: 'gpt-4o', label: 'GPT-4o' }
    ]
  }
]

const selectedProvider = ref<ProviderId>('deepseek')
const apiKey = ref('')
const model = ref('deepseek-chat')
const showApiKey = ref(false)
const saving = ref(false)
const message = ref('')
const messageType = ref<'success' | 'error'>('success')
const aiEnabled = ref(false)
const obsidianPath = ref('')
const obsidianValid = ref(false)
const obsidianStatus = ref('尚未配置知识库路径')

const currentProvider = computed(() => providers.find((provider) => provider.id === selectedProvider.value) ?? providers[0])
const providerLabel = computed(() => currentProvider.value.name)

const selectProvider = (provider: ProviderId) => {
  selectedProvider.value = provider
  model.value = providers.find((item) => item.id === provider)?.models[0]?.value ?? ''
  apiKey.value = ''
}

onMounted(async () => {
  try {
    const { settingsApi } = await import('@/api')
    const status = await settingsApi.getAIStatus()
    aiEnabled.value = Boolean(status.ai_enabled)
    if (status.provider === 'deepseek' || status.provider === 'openai') {
      selectedProvider.value = status.provider
      model.value = status.model || currentProvider.value.models[0].value
    }
  } catch (error) {
    console.error(error)
  }

  try {
    const { videoApi } = await import('@/api')
    const config = await videoApi.getConfig()
    obsidianPath.value = config.obsidian_vault_path || ''
    obsidianValid.value = Boolean(config.obsidian_valid)
    obsidianStatus.value = config.obsidian_valid
      ? '知识库已连接，可以导出笔记'
      : (config.obsidian_message || '尚未配置知识库路径')
  } catch (error) {
    console.error(error)
  }
})

const showMsg = (text: string, type: 'success' | 'error' = 'success') => {
  message.value = text
  messageType.value = type
  globalThis.setTimeout(() => { message.value = '' }, 3000)
}

const saveAPIKey = async () => {
  if (!apiKey.value) return
  saving.value = true
  try {
    const { settingsApi } = await import('@/api')
    await settingsApi.setAPIKey(selectedProvider.value, apiKey.value, model.value)
    aiEnabled.value = true
    showMsg(`${currentProvider.value.name} 配置已保存`)
    apiKey.value = ''
    showApiKey.value = false
  } catch (error: any) {
    showMsg(error.message || '保存失败，请检查密钥后重试', 'error')
  } finally {
    saving.value = false
  }
}

const saveObsidian = async () => {
  saving.value = true
  try {
    const { videoApi } = await import('@/api')
    await videoApi.saveConfig({ obsidian_vault_path: obsidianPath.value })
    const config = await videoApi.getConfig()
    obsidianValid.value = Boolean(config.obsidian_valid)
    obsidianStatus.value = config.obsidian_valid
      ? '知识库已连接，可以导出笔记'
      : (config.obsidian_message || '路径无效，请检查目录是否存在')
    showMsg('知识库配置已保存')
  } catch (error: any) {
    showMsg(error.message || '保存失败，请检查路径后重试', 'error')
  } finally {
    saving.value = false
  }
}

const clearData = () => {
  if (globalThis.confirm('确定要清除本地偏好吗？')) {
    globalThis.localStorage.removeItem('theme')
    document.documentElement.classList.remove('dark')
    showMsg('本地偏好已清除')
  }
}
</script>

<style scoped>
.settings-page {
  --settings-ink: var(--text-primary);
  --settings-muted: var(--text-body);
  --settings-line: var(--border-default);
  width: min(100%, 1040px);
  margin: 0 auto;
  padding: 40px 32px 72px;
}

.page-header { margin-bottom: 32px; }
.eyebrow, .section-kicker {
  color: var(--color-action-blue);
  font-size: 12px;
  font-weight: var(--font-weight-semibold);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.header-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  margin-top: 10px;
}
h1 {
  color: var(--settings-ink);
  font-size: clamp(34px, 5vw, 52px);
  letter-spacing: -0.04em;
  line-height: 1;
}
.page-header p { max-width: 620px; margin-top: 12px; color: var(--settings-muted); font-size: 16px; }
.header-mark { border: 1px solid var(--border-default); border-radius: var(--radius-pill); padding: 8px 14px; color: var(--text-secondary); font-size: 12px; white-space: nowrap; }
.settings-layout { display: grid; gap: 16px; }
.settings-section { border: 1px solid var(--settings-line); border-radius: var(--radius-lg); background: var(--surface-elevated); padding: 28px; box-shadow: var(--shadow-level-1); }
.section-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 24px; margin-bottom: 24px; }
.section-heading h2 { margin-top: 8px; color: var(--settings-ink); font-size: 24px; letter-spacing: -0.03em; }
.section-heading p { max-width: 560px; margin-top: 8px; color: var(--settings-muted); font-size: 14px; }
.connection-badge { display: inline-flex; align-items: center; gap: 8px; flex-shrink: 0; border: 1px solid var(--border-default); border-radius: var(--radius-pill); padding: 7px 11px; color: var(--text-muted); font-size: 12px; font-weight: var(--font-weight-medium); }
.connection-badge.connected { border-color: rgba(22, 163, 74, 0.25); color: var(--color-success); }
.status-dot { width: 7px; height: 7px; border-radius: 50%; background: currentColor; }
.provider-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.provider-card { position: relative; display: flex; align-items: center; gap: 12px; min-width: 0; border: 1px solid var(--border-default); border-radius: var(--radius-md); background: var(--surface-canvas); padding: 15px; text-align: left; transition: border-color var(--transition-fast), background-color var(--transition-fast), transform var(--transition-fast); }
.provider-card:hover { border-color: var(--border-focus); transform: translateY(-1px); }
.provider-card.selected { border-color: var(--color-action-blue); background: var(--color-info-soft); box-shadow: inset 0 0 0 1px var(--color-action-blue); }
.provider-symbol { display: grid; width: 36px; height: 36px; flex: 0 0 36px; place-items: center; border-radius: 10px; background: var(--color-primary); color: var(--text-on-dark); font-size: 16px; font-weight: var(--font-weight-bold); }
.provider-symbol.openai { background: var(--color-deep-green); }
.provider-copy { display: grid; gap: 4px; min-width: 0; }
.provider-copy strong { color: var(--settings-ink); font-size: 14px; }
.provider-copy small { overflow: hidden; color: var(--settings-muted); font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.provider-check { width: 20px; margin-left: auto; color: var(--color-action-blue); font-weight: var(--font-weight-bold); text-align: center; }
.setup-guide { display: flex; align-items: center; gap: 12px; margin: 20px 0 24px; border: 1px solid rgba(24, 99, 220, 0.16); border-radius: var(--radius-md); background: var(--color-info-soft); padding: 14px 16px; }
.guide-icon { display: grid; width: 32px; height: 32px; flex: 0 0 32px; place-items: center; border-radius: 9px; background: var(--surface-canvas); color: var(--color-action-blue); font-size: 18px; font-weight: var(--font-weight-semibold); }
.guide-copy { min-width: 0; }
.guide-copy strong { color: var(--settings-ink); font-size: 13px; }
.guide-copy p { margin-top: 3px; color: var(--settings-muted); font-size: 12px; }
.guide-link { flex-shrink: 0; color: var(--color-action-blue); font-size: 13px; font-weight: var(--font-weight-semibold); white-space: nowrap; }
.form-grid { display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(180px, 0.8fr); gap: 16px; }
.form-group { display: grid; gap: 8px; min-width: 0; }
label { color: var(--settings-ink); font-size: 13px; font-weight: var(--font-weight-semibold); }
input, select { width: 100%; min-height: 44px; border: 1px solid var(--border-default); border-radius: var(--radius-sm); background: var(--surface-input); color: var(--settings-ink); padding: 10px 12px; font-size: 14px; transition: border-color var(--transition-fast), box-shadow var(--transition-fast), background-color var(--transition-fast); }
input::placeholder { color: var(--text-muted); }
input:focus, select:focus { border-color: var(--border-focus); box-shadow: 0 0 0 3px var(--color-info-soft); }
.input-with-action { position: relative; }
.input-with-action input { padding-right: 66px; }
.input-action { position: absolute; top: 50%; right: 8px; transform: translateY(-50%); color: var(--color-action-blue); font-size: 12px; font-weight: var(--font-weight-semibold); }
.field-hint { color: var(--text-muted); font-size: 12px; line-height: 1.5; }
.section-actions { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--border-subtle); }
.save-note { color: var(--text-muted); font-size: 12px; }
.primary-button, .secondary-button, .danger-button { min-height: 42px; border-radius: var(--radius-sm); padding: 10px 16px; font-size: 13px; font-weight: var(--font-weight-semibold); transition: transform var(--transition-fast), opacity var(--transition-fast), background-color var(--transition-fast); }
.primary-button { background: var(--color-primary); color: var(--text-on-dark); }
.secondary-button { border: 1px solid var(--border-strong); background: var(--surface-canvas); color: var(--settings-ink); }
.danger-button { border: 1px solid rgba(220, 38, 38, 0.28); background: var(--color-error-soft); color: var(--color-error); }
.primary-button:hover:not(:disabled), .secondary-button:hover:not(:disabled), .danger-button:hover:not(:disabled) { transform: translateY(-1px); }
.primary-button:disabled, .secondary-button:disabled { opacity: 0.5; cursor: not-allowed; }
.path-status { display: flex; align-items: center; gap: 10px; border-radius: var(--radius-sm); padding: 13px 14px; font-size: 13px; }
.status-ok { background: var(--color-success-soft); color: var(--color-success); }
.status-warn { background: var(--color-warning-soft); color: var(--color-warning); }
.status-icon { display: grid; width: 20px; height: 20px; flex: 0 0 20px; place-items: center; border-radius: 50%; background: currentColor; color: var(--surface-canvas); font-size: 12px; font-weight: var(--font-weight-bold); }
.compact-heading { margin-bottom: 20px; }
.local-section { display: flex; align-items: center; justify-content: space-between; gap: 24px; }
.local-section .section-heading { margin-bottom: 0; }
.toast { position: fixed; right: 24px; bottom: 24px; z-index: var(--z-toast); max-width: min(360px, calc(100vw - 48px)); border-radius: var(--radius-sm); padding: 12px 16px; box-shadow: var(--shadow-level-3); color: white; font-size: 13px; }
.toast.success { background: var(--color-success); }
.toast.error { background: var(--color-error); }

@media (max-width: 720px) {
  .settings-page { padding: 28px 16px 48px; }
  .header-row, .section-heading, .local-section, .section-actions { align-items: flex-start; flex-direction: column; }
  .header-mark, .connection-badge { align-self: flex-start; }
  .settings-section { padding: 22px 18px; }
  .provider-grid, .form-grid { grid-template-columns: 1fr; }
  .setup-guide { align-items: flex-start; flex-wrap: wrap; }
  .guide-link { width: 100%; margin-left: 44px; }
  .primary-button, .secondary-button, .danger-button { width: 100%; }
}
</style>
