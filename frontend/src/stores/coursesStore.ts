/** Courses Store - 管理课程文档状态 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ApiService } from '../services/apiClient'
import type {
  CourseCategoryNode,
  CourseDocumentListItem,
  CourseDocumentDetail,
} from '../types'

export const useCoursesStore = defineStore('courses', () => {
  // 状态
  const categoryTree = ref<CourseCategoryNode[]>([])
  const currentCategoryId = ref<string | null>(null)
  const documents = ref<CourseDocumentListItem[]>([])
  const currentDocument = ref<CourseDocumentDetail | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const hasCategories = computed(() => categoryTree.value.length > 0)
  const hasDocuments = computed(() => documents.value.length > 0)
  const currentCategoryName = computed(() => {
    if (!currentCategoryId.value) return null
    const category = findCategoryById(currentCategoryId.value, categoryTree.value)
    return category?.name || null
  })

  /**
   * 递归查找目录
   * @param id 目录ID
   * @param categories 目录列表
   */
  function findCategoryById(
    id: string,
    categories: CourseCategoryNode[]
  ): CourseCategoryNode | null {
    for (const category of categories) {
      if (category.id === id) {
        return category
      }
      if (category.children && category.children.length > 0) {
        const found = findCategoryById(id, category.children)
        if (found) return found
      }
    }
    return null
  }

  /**
   * 获取目录树
   */
  async function fetchCategoryTree() {
    loading.value = true
    error.value = null
    try {
      const response = await ApiService.getCourseCategories()
      categoryTree.value = response.categories
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取目录树失败'
      categoryTree.value = []
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取指定目录下的文档列表
   * @param categoryId 目录ID
   */
  async function fetchDocumentsByCategory(categoryId: string) {
    currentCategoryId.value = categoryId
    loading.value = true
    error.value = null
    try {
      const response = await ApiService.getCourseDocumentsByCategory(categoryId)
      documents.value = response.documents
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取文档列表失败'
      documents.value = []
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取文档详情
   * @param docId 文档ID
   */
  async function fetchDocumentDetail(docId: string) {
    loading.value = true
    error.value = null
    try {
      const detail = await ApiService.getCourseDocumentDetail(docId)
      currentDocument.value = detail
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取文档详情失败'
      currentDocument.value = null
    } finally {
      loading.value = false
    }
  }

  /**
   * 设置当前选中的目录
   * @param categoryId 目录ID
   */
  function setCurrentCategory(categoryId: string | null) {
    currentCategoryId.value = categoryId
  }

  /**
   * 清空文档列表
   */
  function clearDocuments() {
    documents.value = []
  }

  /**
   * 重置状态
   */
  function reset() {
    categoryTree.value = []
    currentCategoryId.value = null
    documents.value = []
    currentDocument.value = null
    loading.value = false
    error.value = null
  }

  return {
    // 状态
    categoryTree,
    currentCategoryId,
    documents,
    currentDocument,
    loading,
    error,
    // 计算属性
    hasCategories,
    hasDocuments,
    currentCategoryName,
    // 方法
    fetchCategoryTree,
    fetchDocumentsByCategory,
    fetchDocumentDetail,
    setCurrentCategory,
    clearDocuments,
    findCategoryById,
    reset,
  }
})

