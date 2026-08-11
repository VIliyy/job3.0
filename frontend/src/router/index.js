import { createRouter, createWebHistory } from "vue-router"

const routes = [
  {
    path: "/",
    name: "Dashboard",
    component: () => import("../views/Dashboard.vue"),
    meta: { title: "控制台" }
  },
  {
    path: "/agent",
    name: "Agent",
    component: () => import("../views/Agent.vue"),
    meta: { title: "求职助手" }
  },
  {
    path: "/optimize",
    name: "Optimization",
    component: () => import("../views/Optimization.vue"),
    meta: { title: "简历优化" }
  },
  {
    path: "/resumes",
    name: "Resumes",
    component: () => import("../views/Resumes.vue"),
    meta: { title: "简历管理" }
  },
  {
    path: "/settings",
    name: "Settings",
    component: () => import("../views/Settings.vue"),
    meta: { title: "设置" }
  },
  {
    // 兼容旧入口：投递记录并入简历管理
    path: "/applications",
    redirect: "/resumes"
  },
  {
    // 未匹配路径回首页，避免空白页
    path: "/:pathMatch(.*)*",
    redirect: "/"
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由重定向（注册在路由表中，这里只处理页面标题）
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? to.meta.title + " - Job3.0" : "Job3.0"
  next()
})

export default router
