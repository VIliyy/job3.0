/**
 * Job3.0 前端应用入口
 */

import { createApp } from "vue"
import { createPinia } from "pinia"
import App from "./App.vue"
import router from "./router"

// 导入样式
import "./assets/styles/variables.css"
import "./assets/styles/base.css"
import "./assets/styles/animations.css"

// 创建Vue应用
const app = createApp(App)

// 创建并使用Pinia
const pinia = createPinia()
app.use(pinia)

// 使用路由
app.use(router)

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error("Global error:", err)
  console.error("Component:", instance)
  console.error("Info:", info)
}

// 挂载应用
app.mount("#app")
