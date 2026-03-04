<template>
  <div class="main-layout">
    <!-- 顶部导航栏 -->
    <Header />
    
    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 加载中状态 -->
      <div v-if="navigationStore.loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p class="loading-text">加载中...</p>
      </div>
      
      <!-- 根据导航配置动态渲染模块 -->
      <component v-else :is="currentComponent" v-bind="currentComponentProps" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useNavigationStore } from '../stores/navigationStore'
import Header from '../components/Header.vue'
import AIToolsLayout from './AIToolsLayout.vue'
import ToolsetModuleLayout from './ToolsetModuleLayout.vue'
import CommonToolsLayout from './CommonToolsLayout.vue'
import WorksLayout from './WorksLayout.vue'

const route = useRoute()
const navigationStore = useNavigationStore()

const moduleId = computed(() => route.params.moduleId as string)

// 根据 moduleId 找到对应的导航模块
const currentModule = computed(() => {
  return navigationStore.modules.find(m => 
    navigationStore.getModuleId(m) === moduleId.value
  )
})

// 根据模块类型动态选择组件
const currentComponent = computed(() => {
  if (!currentModule.value) {
    // 兜底：使用 AIToolsLayout
    return AIToolsLayout
  }

  if (currentModule.value.type === 'toolset') {
    // 工具集模块：使用 ToolsetModuleLayout
    return ToolsetModuleLayout
  } else if (currentModule.value.type === 'page') {
    // 独立页面模块：根据 page_path 选择组件
    if (moduleId.value === 'common-tools') {
      return CommonToolsLayout
    } else if (moduleId.value === 'works') {
      return WorksLayout
    }
  }

  // 兜底：使用 AIToolsLayout
  return AIToolsLayout
})

// 根据模块类型传递不同的 props
const currentComponentProps = computed(() => {
  if (!currentModule.value) {
    return {}
  }

  if (currentModule.value.type === 'toolset') {
    // 工具集模块：传递 toolsetId
    const toolsetId = navigationStore.getToolsetId(currentModule.value)
    return toolsetId ? { toolsetId } : {}
  }

  return {}
})

// 页面加载时获取导航配置（如果还没加载）
onMounted(async () => {
  if (!navigationStore.isLoaded) {
    await navigationStore.loadNavigation()
  }
})

// 监听路由变化，更新当前模块
watch(moduleId, (newId) => {
  navigationStore.setCurrentModule(newId)
}, { immediate: true })
</script>

<style scoped>
.main-layout {
  @apply flex flex-col;
  height: 100%;
  /* 层级0：背景层 - 继承App的背景 */
}

.main-content {
  @apply flex-1 flex flex-col overflow-hidden;
  height: calc(100vh - 72px);
  min-height: 0; /* 允许 flex 子元素收缩 */
}

/* 加载状态 */
.loading-container {
  @apply flex flex-col items-center justify-center h-full gap-4;
}

.loading-spinner {
  @apply w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  @apply text-gray-600 text-sm;
}

/* 平板端响应式（768px - 1023px） */
@media (min-width: 768px) and (max-width: 1023px) {
  .main-content {
    height: calc(100vh - 64px);
  }
}

/* 移动端响应式（<768px） */
@media (max-width: 767px) {
  .main-content {
    height: calc(100vh - 56px);
  }
}
</style>

