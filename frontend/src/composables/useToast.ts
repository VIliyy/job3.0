/**
 * Toast 通知组件 - JavaScript 版本
 */

import { ref } from 'vue'

// Toast 类型
export type ToastType = "success" | "error" | "warning" | "info"

export interface Toast {
  id: number
  type: ToastType
  message: string
  duration?: number
}

// Toast 状态
const toasts = ref<Toast[]>([])
let toastId = 0

// Toast API
export const toast = {
  success(message: string, duration = 3000) {
    return this.show("success", message, duration)
  },
  
  error(message: string, duration = 5000) {
    return this.show("error", message, duration)
  },
  
  warning(message: string, duration = 4000) {
    return this.show("warning", message, duration)
  },
  
  info(message: string, duration = 3000) {
    return this.show("info", message, duration)
  },
  
  show(type: ToastType, message: string, duration = 3000) {
    const id = ++toastId
    toasts.value.push({ id, type, message, duration })
    
    if (duration > 0) {
      setTimeout(() => {
        this.dismiss(id)
      }, duration)
    }
    
    return id
  },
  
  dismiss(id: number) {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index !== -1) {
      toasts.value.splice(index, 1)
    }
  },
  
  clear() {
    toasts.value = []
  }
}

// Composable
export function useToast() {
  const getIcon = (type: ToastType): string => {
    switch (type) {
      case "success": return "check"
      case "error": return "close"
      case "warning": return "warning"
      case "info": return "info"
      default: return "info"
    }
  }
  
  return {
    toast,
    toasts,
    getIcon
  }
}
