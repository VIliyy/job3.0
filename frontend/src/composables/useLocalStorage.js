/**
 * 本地自动保存 composable
 * 用于简历、J D等内容的自动保存和恢复
 */

import { ref, watch, onMounted } from 'vue'

/**
 * 创建带自动保存功能的状态
 * @param {string} key - localStorage 键名
 * @param {any} defaultValue - 默认值
 * @returns {object} { value, load, save, clear }
 */
export function useLocalStorage(key, defaultValue = null) {
  const value = ref(defaultValue)

  // 加载
  const load = () => {
    try {
      const saved = localStorage.getItem(`job3_${key}`)
      if (saved) {
        value.value = JSON.parse(saved)
      }
    } catch (e) {
      console.error(`加载 ${key} 失败:`, e)
    }
  }

  // 保存
  const save = () => {
    try {
      localStorage.setItem(`job3_${key}`, JSON.stringify(value.value))
    } catch (e) {
      console.error(`保存 ${key} 失败:`, e)
    }
  }

  // 清除
  const clear = () => {
    try {
      localStorage.removeItem(`job3_${key}`)
      value.value = defaultValue
    } catch (e) {
      console.error(`清除 ${key} 失败:`, e)
    }
  }

  // 监听变化自动保存
  watch(value, () => {
    save()
  }, { deep: true })

  // 挂载时加载
  onMounted(() => {
    load()
  })

  return {
    value,
    load,
    save,
    clear
  }
}

/**
 * 简历内容自动保存
 */
export function useResumeAutoSave() {
  const { value: resumeText, load, save, clear } = useLocalStorage('resume_text', '')
  const { value: jdText, load: loadJd, save: saveJd, clear: clearJd } = useLocalStorage('jd_text', '')

  // 初始加载
  load()
  loadJd()

  return {
    resumeText,
    jdText,
    saveResume: save,
    saveJd: saveJd,
    clearResume: clear,
    clearJd: clearJd,
    clearAll: () => {
      clear()
      clearJd()
    }
  }
}

/**
 * 用户上下文自动保存
 */
export function useContextAutoSave() {
  const { value: context, load, save, clear } = useLocalStorage('context', {
    resume: null,
    jd: null,
    target: null,
    company: null,
    position: null
  })

  const updateContext = (updates) => {
    context.value = { ...context.value, ...updates }
  }

  load()

  return {
    context,
    updateContext,
    clearContext: clear
  }
}

/**
 * 应用设置自动保存
 */
export function useSettingsAutoSave() {
  const { value: settings, load, save } = useLocalStorage('settings', {
    theme: 'light',
    autoSave: true,
    apiKey: '',
    notifications: true
  })

  load()

  return {
    settings,
    updateSettings: (updates) => {
      settings.value = { ...settings.value, ...updates }
    },
    resetSettings: () => {
      settings.value = {
        theme: 'light',
        autoSave: true,
        apiKey: '',
        notifications: true
      }
    }
  }
}
