<template>
  <div class="app-layout" :class="{ 'sidebar-collapsed': sidebarCollapsed, 'mobile-menu-open': mobileMenuOpen }">
    <button
      v-if="mobileMenuOpen"
      class="mobile-menu-backdrop"
      aria-label="关闭导航"
      @click="closeMobileMenu"
    ></button>
    <aside class="sidebar" :aria-hidden="isMobile && !mobileMenuOpen">
      <div class="sidebar-header">
        <div class="logo">
          <span class="logo-mark" aria-hidden="true">J3</span>
          <span class="logo-text">小林工具箱</span>
        </div>
        <button
          class="collapse-btn"
          :aria-label="sidebarCollapsed ? '展开导航' : '收起导航'"
          @click="sidebarCollapsed = !sidebarCollapsed"
        >
          <span aria-hidden="true">{{ sidebarCollapsed ? '›' : '‹' }}</span>
        </button>
        <button
          v-if="isMobile"
          class="mobile-close-btn"
          aria-label="关闭导航"
          @click="closeMobileMenu"
        >
          <span aria-hidden="true">×</span>
        </button>
      </div>

      <nav class="sidebar-nav">
        <div v-for="group in navGroups" :key="group.label" class="nav-group">
          <div class="nav-group-label">{{ group.label }}</div>
          <router-link
            v-for="item in group.items"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: isActive(item.path) }"
          >
            <span class="nav-icon" :class="item.icon" aria-hidden="true"></span>
            <span class="nav-label">{{ item.label }}</span>
            <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
          </router-link>
        </div>
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
      <button
        v-if="isMobile"
        class="mobile-menu-btn"
        aria-label="打开导航"
        :aria-expanded="mobileMenuOpen"
        @click="mobileMenuOpen = true"
      >
        <span aria-hidden="true">☰</span>
      </button>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useTheme } from '@/composables/useTheme'
import { useRoute } from 'vue-router'

const route = useRoute()
const sidebarCollapsed = ref(false)
const mobileMenuOpen = ref(false)
const viewportWidth = ref(typeof globalThis === 'undefined' ? 1440 : globalThis.innerWidth)
const isMobile = computed(() => viewportWidth.value <= 768)
const { isDark, toggleTheme } = useTheme()

const navGroups = [
  {
    label: '工作台',
    items: [
      { path: '/', label: '控制台', icon: 'dashboard' },
      { path: '/agent', label: '求职助手', icon: 'assistant' }
    ]
  },
  {
    label: '内容工具',
    items: [
      { path: '/resumes', label: '简历管理', icon: 'resume' },
      { path: '/optimize', label: '简历优化', icon: 'optimize' },
      { path: '/video-notes', label: '视频笔记', icon: 'video' }
    ]
  },
  {
    label: '分析工具',
    items: [{ path: '/decompose', label: '信息拆解', icon: 'decompose' }]
  },
  {
    label: '系统',
    items: [{ path: '/settings', label: '设置', icon: 'settings' }]
  }
]

const isActive = (path) => {
  return route.path === path || (path !== '/' && route.path.startsWith(path))
}

function closeMobileMenu() {
  mobileMenuOpen.value = false
}

function updateViewport() {
  viewportWidth.value = globalThis.innerWidth
  if (!isMobile.value) closeMobileMenu()
}

function onKeydown(event) {
  if (event.key === 'Escape') closeMobileMenu()
}

watch(() => route.path, closeMobileMenu)

onMounted(() => {
  globalThis.addEventListener('resize', updateViewport)
  globalThis.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  globalThis.removeEventListener('resize', updateViewport)
  globalThis.removeEventListener('keydown', onKeydown)
})

</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.mobile-menu-backdrop,
.mobile-menu-btn,
.mobile-close-btn {
  display: none;
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

.logo-mark {
  display: inline-grid;
  width: 28px;
  height: 28px;
  place-items: center;
  margin-right: 8px;
  border-radius: var(--radius-sm);
  background: var(--color-primary);
  color: var(--text-on-dark);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: -0.04em;
}

:root.dark .logo-text {
  color: var(--color-focus-blue);
}

.sidebar-collapsed .logo-text {
  display: none;
}

.sidebar-collapsed .logo-mark {
  margin-right: 0;
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

.nav-group + .nav-group {
  margin-top: 12px;
}

.nav-group-label {
  padding: 0 16px 8px;
  color: var(--text-subtle);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
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
  background: var(--color-info-soft);
  color: var(--color-action-blue);
  font-weight: 600;
  box-shadow: inset 3px 0 0 var(--color-action-blue);
}

:root.dark .nav-item.active {
  background: var(--color-info-soft);
  color: var(--color-focus-blue);
  box-shadow: inset 3px 0 0 var(--color-focus-blue);
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
  background: currentColor;
}

.nav-label {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  flex: 1;
}

.sidebar-collapsed .nav-label,
.sidebar-collapsed .nav-group-label {
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

.mobile-menu-btn {
  position: fixed;
  top: 12px;
  left: 12px;
  z-index: 150;
  width: 40px;
  height: 40px;
  border: 1px solid var(--border-default);
  border-radius: 8px;
  background: var(--surface-elevated);
  color: var(--text-primary);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
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
  .mobile-menu-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 250;
    border: 0;
    background: rgba(15, 23, 42, 0.38);
    cursor: pointer;
  }

  .sidebar {
    transform: translateX(-100%);
    z-index: 300;
    width: min(280px, 86vw);
    transition: transform 200ms ease, background-color 200ms ease;
  }

  .mobile-menu-open .sidebar {
    transform: translateX(0);
  }

  .mobile-menu-btn,
  .mobile-close-btn {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .mobile-close-btn {
    width: 32px;
    height: 32px;
    border: 1px solid var(--border-default);
    border-radius: 6px;
    background: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 20px;
  }
  
  .main-content {
    margin-left: 0;
  }
}
</style>


