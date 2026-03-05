/**知识库状态管理*/
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Category,
  Document,
  CategoryCreateRequest,
  CategoryUpdateRequest,
  DocumentCreateRequest,
  FileViewMode
} from '@/types/file-manager'
import * as knowledgeApi from '@/services/knowledgeApi'

export const useKnowledgeStore = defineStore('knowledge', () => {
  // ==================== 状态 ====================
  const categories = ref<Category[]>([])
  const documents = ref<Document[]>([])
  const currentCategory = ref<Category | null>(null)
  const selectedDocuments = ref<string[]>([])
  const viewMode = ref<FileViewMode>('grid')
  const loading = ref(false)
  const searchQuery = ref('')

  // ==================== 计算属性 ====================
  const currentDocuments = computed(() => {
    let docs = documents.value

    // 按目录筛选
    if (currentCategory.value) {
      docs = docs.filter(d => d.category_id === currentCategory.value!.id)
    }

    // 搜索筛选
    if (searchQuery.value.trim()) {
      const query = searchQuery.value.toLowerCase()
      docs = docs.filter(d =>
        d.original_filename.toLowerCase().includes(query)
      )
    }

    return docs
  })

  const categoryTree = computed(() => categories.value)

  const flatCategories = computed(() => {
    const flatten = (cats: Category[]): Category[] => {
      const result: Category[] = []
      for (const cat of cats) {
        result.push(cat)
        if (cat.children?.length) {
          result.push(...flatten(cat.children))
        }
      }
      return result
    }
    return flatten(categories.value)
  })

  // ==================== 目录操作 ====================
  async function loadCategoryTree() {
    loading.value = true
    try {
      categories.value = await knowledgeApi.getCategoryTree()
    } finally {
      loading.value = false
    }
  }

  async function createCategory(data: CategoryCreateRequest) {
    const category = await knowledgeApi.createCategory(data)
    await loadCategoryTree()
    return category
  }

  async function updateCategory(categoryId: string, data: CategoryUpdateRequest) {
    await knowledgeApi.updateCategory(categoryId, data)
    await loadCategoryTree()
  }

  async function deleteCategory(categoryId: string) {
    await knowledgeApi.deleteCategory(categoryId)
    if (currentCategory.value?.id === categoryId) {
      currentCategory.value = null
    }
    await loadCategoryTree()
  }

  function setCurrentCategory(category: Category | null) {
    currentCategory.value = category
    selectedDocuments.value = []
  }

  // ==================== 文件操作 ====================
  async function loadDocuments(categoryId?: string) {
    loading.value = true
    try {
      documents.value = await knowledgeApi.getDocuments(categoryId)
    } finally {
      loading.value = false
    }
  }

  async function createDocument(data: DocumentCreateRequest) {
    const document = await knowledgeApi.createDocument(data)
    await loadDocuments(currentCategory.value?.id)
    return document
  }

  async function uploadFile(
    file: File,
    categoryId: string,
    onProgress?: (progress: number) => void
  ) {
    const result = await knowledgeApi.uploadFile(file, categoryId, onProgress)
    await loadDocuments(categoryId)
    return result
  }

  async function loadDocument(documentId: string) {
    return await knowledgeApi.getDocument(documentId)
  }

  async function updateDocument(documentId: string, content: string) {
    const document = await knowledgeApi.updateDocument(documentId, { content })
    const index = documents.value.findIndex(d => d.id === documentId)
    if (index !== -1) {
      documents.value[index] = document
    }
    return document
  }

  async function deleteDocument(documentId: string) {
    await knowledgeApi.deleteDocument(documentId)
    documents.value = documents.value.filter(d => d.id !== documentId)
    selectedDocuments.value = selectedDocuments.value.filter(id => id !== documentId)
  }

  async function downloadDocument(documentId: string) {
    return await knowledgeApi.downloadDocument(documentId)
  }

  // ==================== 批量操作 ====================
  function toggleDocumentSelection(documentId: string) {
    const index = selectedDocuments.value.indexOf(documentId)
    if (index === -1) {
      selectedDocuments.value.push(documentId)
    } else {
      selectedDocuments.value.splice(index, 1)
    }
  }

  function selectAllDocuments() {
    selectedDocuments.value = currentDocuments.value.map(d => d.id)
  }

  function clearSelection() {
    selectedDocuments.value = []
  }

  // ==================== 视图操作 ====================
  function setViewMode(mode: FileViewMode) {
    viewMode.value = mode
  }

  function toggleViewMode() {
    viewMode.value = viewMode.value === 'grid' ? 'list' : 'grid'
  }

  function setSearchQuery(query: string) {
    searchQuery.value = query
  }

  // ==================== 工具函数 ====================
  function getCategoryById(id: string): Category | undefined {
    return flatCategories.value.find(c => c.id === id)
  }

  function getCategoryPath(category: Category): Category[] {
    const path: Category[] = [category]
    let current = category
    while (current.parent_id) {
      const parent = getCategoryById(current.parent_id)
      if (parent) {
        path.unshift(parent)
        current = parent
      } else {
        break
      }
    }
    return path
  }

  return {
    // 状态
    categories,
    documents,
    currentCategory,
    selectedDocuments,
    viewMode,
    loading,
    searchQuery,

    // 计算属性
    currentDocuments,
    categoryTree,
    flatCategories,

    // 目录操作
    loadCategoryTree,
    createCategory,
    updateCategory,
    deleteCategory,
    setCurrentCategory,

    // 文件操作
    loadDocuments,
    createDocument,
    uploadFile,
    loadDocument,
    updateDocument,
    deleteDocument,
    downloadDocument,

    // 批量操作
    toggleDocumentSelection,
    selectAllDocuments,
    clearSelection,

    // 视图操作
    setViewMode,
    toggleViewMode,
    setSearchQuery,

    // 工具函数
    getCategoryById,
    getCategoryPath
  }
})
