<template>
  <StandaloneLayout>
    <FileManagementLayout
        ref="fileManagementRef"
        :categories="store.categoryTree"
        :current-category="store.currentCategory"
        :documents="store.documents"
        :selected-ids="selectedIdsSet"
        :view-mode="store.viewMode"
        :search-query="store.searchQuery"
        :is-party-theme="false"
        sidebar-title="知识目录"
        @category-click="handleCategoryClick"
        @file-click="handleFileClick"
        @file-open="handleOpenFile"
        @file-edit="handleEditFile"
        @file-download="handleDownloadFile"
        @file-rename="handleRenameFile"
        @file-delete="handleDeleteFile"
        @file-upload="handleUploadFile"
        @file-create="handleCreateFile"
        @category-add="handleAddCategory"
        @category-rename="handleRenameCategory"
        @category-delete="handleDeleteCategory"
        @toggle-file-select="store.toggleDocumentSelection"
        @select-all-files="store.selectAllDocuments"
        @clear-selection="store.clearSelection"
        @batch-download="handleBatchDownload"
        @batch-delete="handleBatchDelete"
        @view-mode-change="store.setViewMode"
        @search-query-change="store.setSearchQuery"
      />
  </StandaloneLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import StandaloneLayout from '@/layouts/StandaloneLayout.vue'
import FileManagementLayout from '@/layouts/FileManagementLayout.vue'
import { useKnowledgeStore } from '@/stores/knowledgeStore'
import type { Category, Document } from '@/types/file-manager'

const router = useRouter()
const store = useKnowledgeStore()

const uploadingFiles = ref<Map<string, number>>(new Map())
const fileManagementRef = ref<InstanceType<typeof FileManagementLayout> | null>(null)

// 选中的文件 ID（Set 类型用于组件）
const selectedIdsSet = computed(() => new Set(store.selectedDocuments))

// 初始化
onMounted(async () => {
  await Promise.all([
    store.loadCategoryTree(),
    store.loadDocuments()
  ])
})

// 目录操作
const handleCategoryClick = async (category: Category | null) => {
  store.setCurrentCategory(category)
  if (category) {
    await store.loadDocuments(category.id)
  } else {
    await store.loadDocuments()
  }
}

const handleAddCategory = async (parentId: string | null) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入目录名称', '新建目录', {
      confirmButtonText: '创建',
      cancelButtonText: '取消',
      inputPattern: /^.{1,100}$/,
      inputErrorMessage: '目录名称长度为 1-100 个字符'
    })
    await store.createCategory({ name: value, parent_id: parentId })
    ElMessage.success('目录创建成功')
    // 如果是子目录，展开父节点
    if (parentId) {
      fileManagementRef.value?.expandCategoryNode(parentId)
    }
  } catch {
    // 用户取消
  }
}

const handleRenameCategory = async (category: Category) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入新的目录名称', '重命名目录', {
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputValue: category.name,
      inputPattern: /^.{1,100}$/,
      inputErrorMessage: '目录名称长度为 1-100 个字符'
    })
    await store.updateCategory(category.id, { name: value })
    ElMessage.success('目录重命名成功')
  } catch {
    // 用户取消
  }
}

const handleDeleteCategory = async (category: Category) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除目录"${category.name}"吗？此操作不可撤销。`,
      '删除目录',
      {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消'
      }
    )
    await store.deleteCategory(category.id)
    ElMessage.success('目录删除成功')
  } catch {
    // 用户取消
  }
}

// 文件操作
const handleFileClick = (document: Document) => {
  // 单击文件时的处理（可以预览或选中）
  console.log('File clicked:', document)
}

const handleOpenFile = async (document: Document) => {
  // 跳转到编辑器查看
  router.push({
    path: '/markdown-editor',
    query: {
      documentId: document.id,
      categoryId: document.category_id,
      mode: 'knowledge',
      readonly: 'true'
    }
  })
}

const handleEditFile = async (document: Document) => {
  router.push({
    path: '/markdown-editor',
    query: {
      documentId: document.id,
      categoryId: document.category_id,
      mode: 'knowledge'
    }
  })
}

const handleDownloadFile = async (document: Document) => {
  try {
    const blob = await store.downloadDocument(document.id)
    const url = URL.createObjectURL(blob)
    const a = window.document.createElement('a')
    a.href = url
    a.download = document.original_filename
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('文件下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('文件下载失败')
  }
}

const handleRenameFile = async (document: Document) => {
  try {
    await ElMessageBox.prompt('请输入新的文件名（不含扩展名）', '重命名文件', {
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputValue: document.original_filename.replace(/\.[^/.]+$/, ''),
      inputPattern: /^[^<>:"/\\|?*]+$/,
      inputErrorMessage: '文件名不能包含特殊字符'
    })

    // 这里需要调用重命名 API（当前后端暂不支持，可以提示）
    ElMessage.info('文件重命名功能将在后续版本支持')
  } catch {
    // 用户取消
  }
}

const handleDeleteFile = async (document: Document) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文件"${document.original_filename}"吗？此操作不可撤销。`,
      '删除文件',
      {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消'
      }
    )
    await store.deleteDocument(document.id)
    ElMessage.success('文件删除成功')
  } catch {
    // 用户取消
  }
}

const handleUploadFile = async (file: File, categoryId: string) => {
  try {
    await store.uploadFile(file, categoryId, (progress) => {
      // 更新上传进度
      uploadingFiles.value.set(file.name, progress)
    })
    uploadingFiles.value.delete(file.name)
    ElMessage.success('文件上传成功')
  } catch (error: any) {
    uploadingFiles.value.delete(file.name)
    ElMessage.error(error.message || '文件上传失败')
  }
}

const handleCreateFile = async (data: { categoryId: string; filename: string; content: string }) => {
  try {
    const document = await store.createDocument({
      category_id: data.categoryId,
      filename: data.filename,
      content: data.content
    })
    ElMessage.success('文件创建成功')
    // 跳转到编辑器
    router.push({
      path: '/markdown-editor',
      query: {
        documentId: document.id,
        categoryId: document.category_id,
        mode: 'knowledge'
      }
    })
  } catch (error: any) {
    ElMessage.error(error.message || '文件创建失败')
  }
}

// 批量操作
const handleBatchDownload = async () => {
  ElMessage.info('批量下载功能将在后续版本支持')
}

const handleBatchDelete = async () => {
  try {
    for (const id of store.selectedDocuments) {
      await store.deleteDocument(id)
    }
    store.clearSelection()
    ElMessage.success(`成功删除 ${store.selectedDocuments.length} 个文件`)
  } catch (error: any) {
    ElMessage.error(error.message || '批量删除失败')
  }
}
</script>

<style scoped>
</style>
