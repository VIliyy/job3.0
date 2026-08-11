/**
 * Job3.0 应用状态管理
 */

import { defineStore } from "pinia"

// 简历Store
export const useResumeStore = defineStore("resume", {
  state: () => ({
    resumes: {},
    activeSlot: 1,
    loading: false,
    error: null
  }),

  getters: {
    activeResume: (state) => state.resumes[state.activeSlot],
    resumeCount: (state) => Object.keys(state.resumes).length,
    hasResume: (state) => Object.keys(state.resumes).length > 0
  },

  actions: {
    setActiveSlot(slot) {
      if (this.resumes[slot]) {
        this.activeSlot = slot
      }
    },

    addResume(slot, resume) {
      this.resumes[slot] = {
        ...resume,
        updatedAt: new Date().toLocaleDateString()
      }
    },

    updateResume(slot, data) {
      if (this.resumes[slot]) {
        this.resumes[slot] = {
          ...this.resumes[slot],
          ...data
        }
      }
    },

    deleteResume(slot) {
      delete this.resumes[slot]
      if (this.activeSlot === slot) {
        this.activeSlot = null
      }
    },

    clearAll() {
      this.resumes = {}
      this.activeSlot = null
    }
  }
})

// 投递记录Store
export const useApplicationStore = defineStore("application", {
  state: () => ({
    applications: [],
    loading: false,
    error: null
  }),

  getters: {
    totalCount: (state) => state.applications.length,
    interviewCount: (state) =>
      state.applications.filter(a => a.status === "面试中").length,
    offerCount: (state) =>
      state.applications.filter(a => a.status === "Offer").length,
    pendingCount: (state) =>
      state.applications.filter(a => a.status === "待处理").length,
    recentApplications: (state) =>
      state.applications.slice(0, 5)
  },

  actions: {
    addApplication(data) {
      const duplicate = this.applications.find(
        a => a.company.toLowerCase() === data.company.toLowerCase()
      )

      if (duplicate) {
        return { success: false, duplicate: true, data: duplicate }
      }

      this.applications.unshift({
        id: Date.now(),
        ...data,
        date: new Date().toLocaleDateString(),
        notes: ""
      })

      return { success: true }
    },

    updateStatus(id, status) {
      const app = this.applications.find(a => a.id === id)
      if (app) {
        app.status = status
      }
    },

    updateNotes(id, notes) {
      const app = this.applications.find(a => a.id === id)
      if (app) {
        app.notes = notes
      }
    },

    deleteApplication(id) {
      this.applications = this.applications.filter(a => a.id !== id)
    },

    getByStatus(status) {
      if (status === "all") {
        return this.applications
      }
      return this.applications.filter(a => a.status === status)
    }
  }
})

// 打招呼语Store
export const useGreetingStore = defineStore("greeting", {
  state: () => ({
    templates: [
      {
        id: 1,
        name: "技术岗打招呼",
        content: "您好，我是{亮点}的{公司}求职者，对贵司{岗位}岗位很感兴趣，希望能有机会沟通交流。",
        vars: ["公司", "岗位", "亮点"],
        isDefault: true
      },
      {
        id: 2,
        name: "应届生打招呼",
        content: "您好！我是今年的应届毕业生，专业是{亮点}，对贵司{岗位}岗位非常感兴趣，期待能与您交流。",
        vars: ["公司", "岗位", "亮点"],
        isDefault: false
      }
    ],
    activeTemplateId: 1,
    loading: false
  }),

  getters: {
    activeTemplate: (state) =>
      state.templates.find(t => t.id === state.activeTemplateId),
    defaultTemplate: (state) =>
      state.templates.find(t => t.isDefault)
  },

  actions: {
    addTemplate(data) {
      this.templates.push({
        id: Date.now(),
        ...data,
        vars: ["公司", "岗位", "亮点"],
        isDefault: false
      })
    },

    updateTemplate(id, data) {
      const template = this.templates.find(t => t.id === id)
      if (template) {
        Object.assign(template, data)
      }
    },

    deleteTemplate(id) {
      this.templates = this.templates.filter(t => t.id !== id)
      if (this.activeTemplateId === id) {
        this.activeTemplateId = this.templates[0]?.id || null
      }
    },

    setDefault(id) {
      this.templates.forEach(t => {
        t.isDefault = t.id === id
      })
    },

    setActiveTemplate(id) {
      this.activeTemplateId = id
    },

    generateGreeting(company, position, highlights) {
      const template = this.activeTemplate || this.defaultTemplate
      if (!template) return null

      return {
        boss: template.content
          .replace(/\{公司\}/g, company)
          .replace(/\{岗位\}/g, position || "该岗位")
          .replace(/\{亮点\}/g, highlights || "相关经验")
          .substring(0, 50),
        liepin: template.content
          .replace(/\{公司\}/g, `贵公司（${company}）`)
          .replace(/\{岗位\}/g, position || "相关岗位")
          .replace(/\{亮点\}/g, highlights || "相关经验")
          .substring(0, 100),
        email: `尊敬的HR，您好！

我是${highlights || "一名求职者"}，看到贵司${company}正在招聘${position || "相关岗位"}，非常感兴趣。

${highlights ? `我具备${highlights}，希望能有机会加入贵司。` : ""}

期待您的回复，谢谢！

此致
敬礼`
      }
    }
  }
})

// 分析Store
export const useAnalysisStore = defineStore("analysis", {
  state: () => ({
    currentAnalysis: null,
    history: [],
    loading: false,
    error: null
  }),

  getters: {
    latestAnalysis: (state) => state.history[0],
    hasAnalysis: (state) => !!state.currentAnalysis
  },

  actions: {
    setAnalysis(result) {
      this.currentAnalysis = {
        ...result,
        timestamp: new Date().toISOString()
      }
      this.history.unshift(this.currentAnalysis)

      // 只保留最近20条记录
      if (this.history.length > 20) {
        this.history = this.history.slice(0, 20)
      }
    },

    clearCurrent() {
      this.currentAnalysis = null
    },

    clearHistory() {
      this.history = []
      this.currentAnalysis = null
    }
  }
})

// 应用配置Store
export const useConfigStore = defineStore("config", {
  state: () => ({
    theme: "light",
    language: "zh-CN",
    apiBaseUrl: "http://localhost:8000/api",
    autoSave: true,
    notifications: {
      email: true,
      browser: false
    }
  }),

  actions: {
    setTheme(theme) {
      this.theme = theme
      document.documentElement.setAttribute("data-theme", theme)
    },

    toggleTheme() {
      this.theme = this.theme === "light" ? "dark" : "light"
      document.documentElement.setAttribute("data-theme", this.theme)
    },

    updateConfig(config) {
      Object.assign(this, config)
    }
  }
})
