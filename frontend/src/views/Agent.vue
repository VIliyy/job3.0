<template>
  <div class="agent-page">
    <div class="status-bar">
      <div class="resume-status" :class="{ active: hasResume }">
        <span>{{ hasResume ? '[OK] 已上传简历' : '[X] 暂无简历' }}</span>
        <a v-if="!hasResume" href="/resumes" class="status-link">去上传</a>
      </div>
      <div class="api-status" :class="{ active: aiEnabled }">
        <span>{{ aiEnabled ? '[OK] AI 已启用' : '[X] AI 未配置' }}</span>
        <a v-if="!aiEnabled" href="/settings" class="status-link">去配置</a>
      </div>
      <div class="api-model" v-if="aiEnabled && aiModel">
        <span>{{ aiModel }}</span>
      </div>
    </div>

    <div class="chat-area" ref="chatArea">
      <div class="messages">
        <div v-if="messages.length === 0" class="welcome">
          <div class="welcome-icon">AI</div>
          <h2>求职助手</h2>
          <p class="welcome-desc">我可以帮你分析 JD、匹配岗位、优化简历、生成打招呼语</p>
          <div class="example-list">
            <button @click="sendExample(1)" class="example-btn">📊 分析 JD 匹配度</button>
            <button @click="sendExample(2)" class="example-btn">💬 生成打招呼语</button>
            <button @click="sendExample(3)" class="example-btn">📄 查看我的简历</button>
            <button @click="sendExample(4)" class="example-btn">🚀 优化我的简历</button>
          </div>
        </div>

        <div v-for="(msg, index) in messages" :key="index" class="message" :class="msg.role">
          <div class="message-avatar">{{ msg.role === "user" ? "我" : "AI" }}</div>
          <div class="message-content">
            <div class="message-text">{{ msg.content }}</div>
            <div v-if="msg.actions && msg.actions.length" class="message-actions">
              <button v-for="act in msg.actions" :key="act" class="action-chip" @click="inputMessage = act; sendMessage()">
                {{ act }}
              </button>
            </div>
            <div class="message-time">{{ msg.time }}</div>
          </div>
        </div>

        <div v-if="isTyping" class="message bot">
          <div class="message-avatar">AI</div>
          <div class="message-content">
            <div class="message-text typing">
              <span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>
              <span class="typing-hint">{{ typingHint }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="input-area">
      <textarea
        v-model="inputMessage"
        @keydown.enter.exact.prevent="sendMessage"
        class="message-input"
        rows="2"
        placeholder="输入消息，回车发送…"
      ></textarea>
      <button @click="sendMessage" :disabled="!inputMessage.trim() || isTyping" class="send-btn">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from "vue"
import { agentApi, resumeApi, aiStatusApi } from "@/api"
import { toast } from "@/composables/useToast"

const messages = ref([])
const inputMessage = ref("")
const isTyping = ref(false)
const typingHint = ref("正在思考…")
const chatArea = ref(null)

const hasResume = ref(false)
const aiEnabled = ref(false)
const aiModel = ref("")
const resumeText = ref("")

const EXAMPLES = {
  1: "帮我分析一下这个 JD 和我的简历匹配度如何",
  2: "帮我生成一份打招呼语",
  3: "查看我的简历",
  4: "帮我优化简历"
}

async function loadStatus() {
  try {
    const list = await resumeApi.list({ limit: 100 })
    hasResume.value = Array.isArray(list) && list.length > 0
    if (hasResume.value && list[0]?.id) {
      const detail = await resumeApi.get(list[0].id)
      resumeText.value = detail?.content || ""
    }
  } catch (e) {
    console.error("加载简历状态失败:", e)
  }
  try {
    const status = await aiStatusApi.getStatus()
    aiEnabled.value = !!status?.ai_enabled
    aiModel.value = status?.model || status?.provider || ""
  } catch (e) {
    console.error("加载 AI 状态失败:", e)
  }
}

const sendExample = (type) => {
  const text = EXAMPLES[type]
  if (text) {
    inputMessage.value = text
    sendMessage()
  }
}

function buildHistory() {
  return messages.value
    .slice(-20)
    .map(m => ({ role: m.role === "user" ? "user" : "assistant", content: m.content }))
}

function scrollToBottom() {
  nextTick(() => {
    if (chatArea.value) chatArea.value.scrollTop = chatArea.value.scrollHeight
  })
}

const sendMessage = async () => {
  const msg = inputMessage.value.trim()
  if (!msg || isTyping.value) return

  inputMessage.value = ""
  messages.value.push({ role: "user", content: msg, time: new Date().toLocaleTimeString() })
  scrollToBottom()

  const botMsg = { role: "bot", content: "", time: "", actions: [] }
  messages.value.push(botMsg)
  isTyping.value = true
  typingHint.value = "正在思考…"
  scrollToBottom()

  const history = buildHistory().slice(0, -1)
  const chatState = {
    has_resume: hasResume.value,
    resume_text: (resumeText.value || "").slice(0, 3000)
  }

  try {
    let streamed = false
    try {
      streamed = await streamChat(msg, history, botMsg, chatState)
    } catch (e) {
      console.warn("流式对话失败，改用普通接口:", e)
    }

    if (!streamed) {
      typingHint.value = "正在处理…"
      const data = await agentApi.chat(msg, history, chatState)
      botMsg.content = data.response || "（无回复）"
      botMsg.actions = data.suggested_actions || []
    }
  } catch (e) {
    botMsg.content = "抱歉，处理请求时出现错误：" + (e.message || e)
    toast.error("对话失败: " + (e.message || e))
  } finally {
    botMsg.time = new Date().toLocaleTimeString()
    isTyping.value = false
    scrollToBottom()
  }
}

async function streamChat(msg, history, botMsg, state) {
  const response = await agentApi.chatStream(msg, history, state || null)
  if (!response.ok) {
    throw new Error("HTTP " + response.status)
  }
  if (!response.body) throw new Error("浏览器不支持流式响应")

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""
  let gotContent = false

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    let sep
    while ((sep = buffer.indexOf("\n\n")) !== -1) {
      const rawEvent = buffer.slice(0, sep)
      buffer = buffer.slice(sep + 2)

      let eventType = "message"
      let dataLine = ""
      for (const line of rawEvent.split("\n")) {
        if (line.startsWith("event:")) eventType = line.slice(6).trim()
        else if (line.startsWith("data:")) dataLine += line.slice(5).trim()
      }
      if (!dataLine) continue

      let payload
      try { payload = JSON.parse(dataLine) } catch { continue }

      if (eventType === "thinking" && payload.text) {
        typingHint.value = payload.text
      } else if (eventType === "content" && typeof payload.char === "string") {
        botMsg.content += payload.char
        gotContent = true
        scrollToBottom()
      } else if (eventType === "action" && Array.isArray(payload.actions)) {
        botMsg.actions = payload.actions
      } else if (eventType === "error") {
        botMsg.content += "\n[错误] " + (payload.message || "")
      }
    }
  }
  return gotContent
}

onMounted(async () => {
  await loadStatus()
  const saved = localStorage.getItem("agent_messages")
  if (saved) {
    try { messages.value = JSON.parse(saved) } catch {}
  }
})
</script>

<style scoped>
.agent-page {
  background: var(--surface-default);
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  background: var(--surface-default);
}

.status-bar {
  display: flex;
  gap: 24px;
  padding: 12px 24px;
  background: var(--surface-elevated);
  border-bottom: 1px solid var(--border-default);
  font-size: 13px;
  align-items: center;
}

.resume-status, .api-status, .api-model {
  color: var(--text-muted);
}

.resume-status.active, .api-status.active {
  color: var(--color-success);
}

.api-model {
  margin-left: auto;
  color: var(--text-subtle);
  font-size: 12px;
}

.status-link {
  margin-left: 8px;
  color: var(--color-info);
  text-decoration: none;
  font-size: 12px;
}

.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.messages {
  max-width: 800px;
  margin: 0 auto;
}

.welcome {
  text-align: center;
  padding: 60px 20px;
}

.welcome-icon {
  width: 72px;
  height: 72px;
  margin: 0 auto 16px;
  border-radius: 20px;
  background: linear-gradient(135deg, var(--color-action-blue), var(--color-focus-blue));
  color: white;
  font-size: 28px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome h2 { font-size: 24px; font-weight: 700; margin-bottom: 8px; }
.welcome-desc { color: var(--text-muted); margin-bottom: 28px; }

.example-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  max-width: 560px;
  margin: 0 auto;
}

.example-btn {
  padding: 12px 20px;
  background: var(--surface-elevated);
  border: 1px solid var(--border-default);
  border-radius: 12px;
  cursor: pointer;
  font-size: 14px;
}

.example-btn:hover {
  background: var(--color-action-blue);
  color: white;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  background: var(--surface-stone);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  flex-shrink: 0;
}

.message.bot .message-avatar {
  background: linear-gradient(135deg, var(--color-action-blue), var(--color-focus-blue));
  color: white;
}

.message-content {
  max-width: 70%;
}

.message-text {
  background: var(--surface-elevated);
  padding: 12px 16px;
  border-radius: 16px;
  line-height: 1.7;
  font-size: 14px;
  white-space: pre-wrap;
  word-break: break-word;
}

.message.user .message-text {
  background: var(--color-action-blue);
  color: white;
}

.message-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.action-chip {
  padding: 6px 12px;
  background: var(--surface-elevated);
  border: 1px solid var(--color-info);
  color: var(--color-info);
  border-radius: 14px;
  font-size: 12px;
  cursor: pointer;
}

.action-chip:hover {
  background: var(--color-info);
  color: white;
}

.message-time {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
}

.message-text.typing {
  display: flex;
  align-items: center;
  gap: 4px;
  min-width: 120px;
}

.typing-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--text-subtle);
  animation: blink 1.2s infinite;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
  0%, 60%, 100% { opacity: 0.3; }
  30% { opacity: 1; }
}

.typing-hint {
  margin-left: 8px;
  font-size: 13px;
  color: var(--text-subtle);
}

.input-area {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  background: var(--surface-elevated);
  border-top: 1px solid var(--border-default);
}

.message-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--border-default);
  border-radius: 12px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
}

.message-input:focus {
  outline: none;
  border-color: var(--color-action-blue);
}

.send-btn {
  padding: 12px 24px;
  background: var(--color-action-blue);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  cursor: pointer;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

</style>
