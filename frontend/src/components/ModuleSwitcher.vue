<template>
  <div class="module-switcher">
    <!-- 加载状态 -->
    <div v-if="navigationStore.loading" class="loading-placeholder">
      <div class="skeleton-button" v-for="i in 3" :key="i"></div>
    </div>
    
    <!-- 模块按钮 -->
    <button
      v-else
      v-for="module in modules"
      :key="getModuleId(module)"
      :class="['module-button', { active: currentModule === getModuleId(module) }]"
      @click="handleModuleClick(getModuleId(module))"
    >
      {{ module.name }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigationStore } from '../stores/navigationStore'
import type { NavigationModule } from '../types/navigation'

const route = useRoute()
const router = useRouter()
const navigationStore = useNavigationStore()

// 从导航配置获取模块列表
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

function getModuleId(module: NavigationModule) {
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
}
</script>

<style scoped>
.module-switcher {
  @apply flex items-center gap-1 p-1 rounded-xl;
  /* 党建主题：半透明白色背景以适配红色头部 */
  background-color: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(8px);
}

.module-button {
  @apply px-5 py-2 text-sm font-medium bg-transparent border-none rounded-lg cursor-pointer transition-all duration-200 whitespace-nowrap;
  /* 党建主题：白色文字 */
  color: rgba(255, 255, 255, 0.85);
}

.module-button:hover {
  /* 党建主题：hover时使用半透明白色背景 */
  background-color: rgba(255, 255, 255, 0.2);
  color: #FFFFFF;
  transform: translateY(-1px);
}

.module-button.active {
  @apply font-semibold;
  /* 党建主题：激活状态使用红色渐变背景 + 白色文字 */
  background: linear-gradient(135deg, #C8102E 0%, #8B0000 100%);
  color: #FFFFFF;
  box-shadow: 0 4px 12px rgba(200, 16, 46, 0.4), 0 2px 4px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 215, 0, 0.3);
}

.module-button:active {
  transform: translateY(0);
}

/* 加载占位符 */
.loading-placeholder {
  @apply flex gap-1;
}

.skeleton-button {
  @apply w-20 h-8 rounded-lg animate-pulse;
  /* 党建主题：骨架屏使用白色半透明 */
  background-color: rgba(255, 255, 255, 0.2);
}

/* 平板端响应式（768px - 1023px） */
@media (min-width: 768px) and (max-width: 1023px) {
  .module-switcher {
    gap: 2px;
    padding: 3px;
  }

  .module-button {
    padding: 6px 14px;
    font-size: 13px;
  }
}
</style>

