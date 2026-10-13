// 全局共享主题状态：AppLayout 与控制台等页面共用同一 isDark，避免重复实现导致状态不同步
import { ref } from 'vue'

const savedTheme = typeof localStorage !== 'undefined' ? localStorage.getItem('theme') : null
const isDark = ref(savedTheme === 'dark')

function applyTheme() {
  if (typeof document !== 'undefined') {
    document.documentElement.classList.toggle('dark', isDark.value)
  }
}

// 模块加载时立即应用一次，避免页面闪烁
applyTheme()

export function useTheme() {
  const toggleTheme = () => {
    isDark.value = !isDark.value
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
    }
    applyTheme()
  }
  return { isDark, toggleTheme }
}

export default useTheme