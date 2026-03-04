/** 导航状态管理 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { NavigationModule } from '../types/navigation'
import { ApiService } from '../services/apiClient'

export const useNavigationStore = defineStore('navigation', () => {
  // 状态
  const modules = ref<NavigationModule[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const currentModuleId = ref<string>('ai-tools') // 默认值
  const isLoaded = ref(false) // 标记是否已加载

  // 计算属性
  const currentModule = computed(() => {
    return modules.value.find(m => getModuleId(m) === currentModuleId.value)
  })

  const toolsetModules = computed(() => {
    return modules.value.filter(m => m.type === 'toolset')
  })

  const pageModules = computed(() => {
    return modules.value.filter(m => m.type === 'page')
  })

  // 辅助函数：从模块配置生成模块ID
  function getModuleId(module: NavigationModule): string {
    if (module.type === 'toolset' && module.config_source) {
      // 从 config_source 提取最后一部分作为 ID（如 "tools/ai_tools" -> "ai-tools"）
      const parts = module.config_source.split('/')
      return parts[parts.length - 1]?.replace(/_/g, '-') || ''
    } else if (module.type === 'page' && module.page_path) {
      // 从 page_path 提取（如 "/common-tools" -> "common-tools"）
      return module.page_path.replace(/^\//, '')
    }
    // 兜底：使用名称生成ID
    return module.name.toLowerCase().replace(/\s+/g, '-')
  }

  // Actions
  async function loadNavigation(force = false) {
    // 如果已经加载过且不强制刷新，直接返回
    if (isLoaded.value && !force) {
      return
    }

    loading.value = true
    error.value = null

    try {
      const response = await ApiService.getNavigationModules()
      modules.value = response.modules || []
      isLoaded.value = true
    } catch (err: any) {
      console.error('加载导航配置失败:', err)
      error.value = err.message || '加载导航配置失败'
      
      // 如果后端不可用，使用默认配置（向后兼容）
      modules.value = [
        {
          name: 'AI工具',
          type: 'toolset',
          config_source: 'tools/ai_tools',
          icon: '🤖',
          order: 1
        }
      ]
      isLoaded.value = true
    } finally {
      loading.value = false
    }
  }

  function setCurrentModule(moduleId: string) {
    currentModuleId.value = moduleId
  }

  // 获取工具集ID（用于API调用）
  function getToolsetId(module: NavigationModule): string | null {
    if (module.type === 'toolset' && module.config_source) {
      // 从 config_source 提取最后一部分（如 "tools/ai_tools" -> "ai_tools"）
      const parts = module.config_source.split('/')
      return parts[parts.length - 1] || null
    }
    return null
  }

  return {
    // State
    modules,
    loading,
    error,
    currentModuleId,
    isLoaded,
    
    // Getters
    currentModule,
    toolsetModules,
    pageModules,
    
    // Actions
    loadNavigation,
    setCurrentModule,
    getModuleId,
    getToolsetId
  }
})
