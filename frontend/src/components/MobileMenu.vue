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
            :key="module.id"
            :class="['menu-item', { active: currentModule === module.id }]"
            @click="handleModuleClick(module.id)"
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

const route = useRoute()
const router = useRouter()

// 写死的模块数据
const modules = [
  { id: 'ai-tools', name: 'AI工具', type: 'toolset' },
  { id: 'teaching-researcher', name: '教研员', type: 'toolset' },
  { id: 'common-tools', name: '常用工具', type: 'page', path: '/common-tools' },
  { id: 'works', name: '作品展示', type: 'page', path: '/works' },
]

const currentModule = computed(() => {
  // 如果是 /modules/:moduleId 路由
  if (route.params.moduleId) {
    return route.params.moduleId as string
  }
  
  // 如果是独立页面路由，根据 path 匹配模块
  const currentPath = route.path
  const module = modules.find(m => m.type === 'page' && m.path === currentPath)
  
  if (module) {
    return module.id
  }
  
  // 默认返回 ai-tools
  return 'ai-tools'
})

const isOpen = ref(false)

function toggleMenu() {
  isOpen.value = !isOpen.value
}

function closeMenu() {
  isOpen.value = false
}

function handleModuleClick(moduleId: string) {
  const module = modules.find(m => m.id === moduleId)
  
  if (module && module.type === 'page' && module.path) {
    // page 类型模块：使用独立路径
    router.push(module.path)
  } else {
    // toolset 类型模块：使用 /modules/:moduleId
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

