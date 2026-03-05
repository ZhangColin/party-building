<template>
  <div class="mobile-menu">
    <button class="hamburger-button" @click="toggleMenu">
      <span class="hamburger-icon">
        <span class="line"></span>
        <span class="line"></span>
        <span class="line"></span>
      </span>
    </button>
    
    <div v-if="isOpen" class="menu-overlay" @click="closeMenu">
      <div class="menu-drawer" @click.stop>
        <div class="menu-header">
          <span class="menu-title">模块切换</span>
          <button class="close-button" @click="closeMenu">×</button>
        </div>
        <div class="menu-items">
          <button
            v-for="module in modules"
            :key="getModuleId(module)"
            :class="['menu-item', { active: currentModule === getModuleId(module) }]"
            @click="handleModuleClick(getModuleId(module))"
          >
            {{ module.name }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigationStore } from '../stores/navigationStore'
import type { NavigationModule } from '../types/navigation'

const route = useRoute()
const router = useRouter()
const navigationStore = useNavigationStore()

// 从导航配置获取模块列表（与桌面端保持一致）
const modules = computed(() => navigationStore.modules)

const currentModule = computed(() => {
  // 如果是 /modules/:moduleId 路由
  if (route.params.moduleId) {
    return route.params.moduleId as string
  }

  // 如果是独立页面路由，根据 path 匹配模块（包括子路径）
  const currentPath = route.path
  const module = modules.value.find(m =>
    m.type === 'page' && m.page_path && currentPath.startsWith(m.page_path)
  )

  if (module) {
    return getModuleId(module)
  }

  // 默认返回 party-ai
  return 'party-ai'
})

const isOpen = ref(false)

function toggleMenu() {
  isOpen.value = !isOpen.value
}

function closeMenu() {
  isOpen.value = false
}

// 辅助函数：从模块配置生成模块ID
function getModuleId(module: NavigationModule): string {
  return navigationStore.getModuleId(module)
}

function handleModuleClick(moduleId: string) {
  // 查找对应的模块配置
  const module = modules.value.find(m => getModuleId(m) === moduleId)

  if (module && module.type === 'page' && module.page_path) {
    // page 类型模块：使用 page_path 直接路由
    router.push(module.page_path)
  } else {
    // toolset 类型模块：使用 /modules/:moduleId 路由
    router.push(`/modules/${moduleId}`)
  }
  closeMenu()
}
</script>

<style scoped>
.mobile-menu {
  position: relative;
}

.hamburger-button {
  width: 40px;
  height: 40px;
  background-color: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.hamburger-icon {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 20px;
  height: 16px;
}

.line {
  width: 100%;
  height: 2px;
  background-color: #1f2937;
  border-radius: 2px;
  transition: all 0.3s;
}

.menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 200;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding-top: 56px;
}

.menu-drawer {
  width: 280px;
  background-color: #ffffff;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
  height: calc(100vh - 56px);
  display: flex;
  flex-direction: column;
}

.menu-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.menu-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.close-button {
  width: 32px;
  height: 32px;
  background-color: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 24px;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-button:hover {
  background-color: #f3f4f6;
  color: #1f2937;
}

.menu-items {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.menu-item {
  width: 100%;
  padding: 12px 16px;
  text-align: left;
  background-color: transparent;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 4px;
}

.menu-item:hover {
  background-color: #f3f4f6;
}

.menu-item.active {
  background-color: #eff6ff;
  color: #2563eb;
  font-weight: 600;
}
</style>

