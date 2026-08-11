<template>
  <div class="app-layout" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <span class="logo-text">Job3.0</span>
        </div>
        <button @click="sidebarCollapsed = !sidebarCollapsed" class="collapse-btn">
          <span v-if="sidebarCollapsed">+</span>
          <span v-else>-</span>
        </button>
      </div>

      <nav class="sidebar-nav">
        <router-link 
          v-for="item in navItems" 
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
        >
          <span class="nav-icon" :class="item.icon"></span>
          <span class="nav-label">{{ item.label }}</span>
          <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="theme-toggle">
          <span class="theme-label">{{ isDark ? 'Dark' : 'Light' }}</span>
          <button @click="toggleTheme" class="theme-btn">
            <span class="theme-icon" :class="isDark ? 'dark' : 'light'"></span>
          </button>
        </div>
      </div>
    </aside>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const sidebarCollapsed = ref(false)
const isDark = ref(false)

const navItems = [
  { path: '/', label: '控制台', icon: 'dashboard' },
  { path: '/optimize', label: '简历优化', icon: 'optimize' },
  { path: '/resumes', label: '简历管理', icon: 'resume' },
  { path: '/agent', label: '求职助手', icon: 'assistant' },
  { path: '/settings', label: '设置', icon: 'settings' }
]

const isActive = (path) => {
  return route.path === path || (path !== '/' && route.path.startsWith(path))
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    isDark.value = true
    document.documentElement.classList.add('dark')
  }
})
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 260px;
  background: var(--surface-elevated);
  border-right: 1px solid var(--border-default);
  display: flex;
  flex-direction: column;
  transition: width 200ms ease, background-color 200ms ease;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 200;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.04);
}

:root.dark .sidebar {
  background: var(--surface-canvas);
  border-right-color: var(--text-secondary);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.2);
}

.sidebar-collapsed .sidebar {
  width: 72px;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 20px;
  border-bottom: 1px solid var(--border-default);
}

:root.dark .sidebar-header {
  border-bottom-color: var(--text-secondary);
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-action-blue);
  letter-spacing: -0.5px;
}

:root.dark .logo-text {
  color: var(--color-focus-blue);
}

.sidebar-collapsed .logo-text {
  display: none;
}

.collapse-btn {
  width: 28px;
  height: 28px;
  border: 1px solid var(--border-default);
  border-radius: 6px;
  background: transparent;
  color: var(--text-subtle);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
  transition: all 200ms;
}

.collapse-btn:hover {
  background: var(--surface-default);
  color: var(--text-primary);
  border-color: var(--border-strong);
}

:root.dark .collapse-btn {
  border-color: var(--text-secondary);
  color: var(--text-muted);
}

:root.dark .collapse-btn:hover {
  background: var(--surface-default);
  color: var(--text-primary);
}

.sidebar-collapsed .collapse-btn {
  position: absolute;
  right: -14px;
  top: 24px;
  background: var(--surface-elevated);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

:root.dark .sidebar-collapsed .collapse-btn {
  background: var(--surface-canvas);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.sidebar-nav {
  flex: 1;
  padding: 20px 12px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 200ms;
  margin-bottom: 4px;
  position: relative;
}

.nav-item:hover {
  background: var(--surface-default);
  color: var(--text-primary);
}

:root.dark .nav-item {
  color: var(--text-secondary);
}

:root.dark .nav-item:hover {
  background: var(--surface-default);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--color-action-blue);
  color: white;
}

:root.dark .nav-item.active {
  background: var(--color-focus-blue);
}

.nav-icon {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  background: currentColor;
  opacity: 0.5;
  flex-shrink: 0;
}

.nav-item.active .nav-icon {
  opacity: 1;
  background: var(--surface-elevated);
}

.nav-label {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  flex: 1;
}

.sidebar-collapsed .nav-label {
  display: none;
}

.nav-badge {
  padding: 2px 8px;
  background: var(--color-action-blue);
  color: white;
  font-size: 11px;
  font-weight: 600;
  border-radius: 9999px;
  flex-shrink: 0;
}

.nav-item.active .nav-badge {
  background: var(--surface-elevated);
  color: var(--color-action-blue);
}

:root.dark .nav-badge {
  background: var(--color-focus-blue);
}

:root.dark .nav-item.active .nav-badge {
  background: var(--surface-elevated);
  color: var(--color-focus-blue);
}

.sidebar-collapsed .nav-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  padding: 2px 4px;
  font-size: 9px;
  min-width: 16px;
  text-align: center;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid var(--border-default);
}

:root.dark .sidebar-footer {
  border-top-color: var(--text-secondary);
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.theme-label {
  font-size: 13px;
  color: var(--text-subtle);
  font-weight: 500;
}

.sidebar-collapsed .theme-label {
  display: none;
}

.theme-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--border-default);
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 200ms;
}

.theme-btn:hover {
  background: var(--surface-default);
  border-color: var(--border-strong);
}

:root.dark .theme-btn {
  border-color: var(--text-secondary);
}

:root.dark .theme-btn:hover {
  background: var(--surface-default);
}

.theme-icon {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  transition: all 200ms;
}

.theme-icon.light {
  background: linear-gradient(135deg, var(--color-coral), var(--color-warning));
}

.theme-icon.dark {
  background: linear-gradient(135deg, var(--color-info), var(--agent-planner));
}

.main-content {
  flex: 1;
  margin-left: 260px;
  min-height: 100vh;
  background: var(--surface-default);
  transition: margin-left 200ms ease, background-color 200ms ease;
}

:root.dark .main-content {
  background: var(--color-background);
}

.sidebar-collapsed .main-content {
  margin-left: 72px;
}

@media (max-width: 1024px) {
  .sidebar {
    width: 72px;
  }
  
  .sidebar-header {
    padding: 24px 12px;
  }
  
  .logo-text,
  .nav-label,
  .theme-label {
    display: none;
  }
  
  .collapse-btn {
    display: none;
  }
  
  .nav-badge {
    position: absolute;
    top: 4px;
    right: 4px;
    padding: 2px 4px;
    font-size: 9px;
    min-width: 16px;
    text-align: center;
  }
  
  .main-content {
    margin-left: 72px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
  }
  
  .main-content {
    margin-left: 0;
  }
}
</style>
