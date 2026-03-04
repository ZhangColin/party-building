/** Works Store - 管理作品展示状态 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ApiService } from '../services/apiClient'
import type { WorkCategoryGroup, WorkDetail } from '../types'

export const useWorksStore = defineStore('works', () => {
  // 状态
  const categories = ref<WorkCategoryGroup[]>([])
  const currentWork = ref<WorkDetail | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const hasCategories = computed(() => categories.value.length > 0)
  const totalWorks = computed(() => {
    return categories.value.reduce((sum, category) => sum + category.works.length, 0)
  })

  /**
   * 获取作品分类列表
   */
  async function fetchCategories() {
    loading.value = true
    error.value = null
    try {
      const response = await ApiService.getWorkCategories()
      categories.value = response.categories
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取作品列表失败'
      categories.value = []
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取作品详情
   * @param workId 作品ID
   */
  async function fetchWorkDetail(workId: string) {
    loading.value = true
    error.value = null
    try {
      const detail = await ApiService.getWorkDetail(workId)
      currentWork.value = detail
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取作品详情失败'
      currentWork.value = null
    } finally {
      loading.value = false
    }
  }

  /**
   * 根据 work_id 获取作品（从已加载的分类列表中查找）
   */
  function getWorkById(workId: string) {
    for (const category of categories.value) {
      const work = category.works.find((w) => w.id === workId)
      if (work) {
        return work
      }
    }
    return null
  }

  /**
   * 重置状态
   */
  function reset() {
    categories.value = []
    currentWork.value = null
    loading.value = false
    error.value = null
  }

  return {
    // 状态
    categories,
    currentWork,
    loading,
    error,
    // 计算属性
    hasCategories,
    totalWorks,
    // 方法
    fetchCategories,
    fetchWorkDetail,
    getWorkById,
    reset,
  }
})
