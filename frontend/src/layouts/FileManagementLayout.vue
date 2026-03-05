# -*- coding: utf-8 -*-
<template>
  <div class="file-management-layout" :class="{ 'party-theme': isPartyTheme }">
    <!-- 顶部工具栏 -->
    <div class="layout-header">
      <!-- 操作区 -->
      <div class="header-actions">
        <!-- 搜索框 -->
        <el-input
          v-model="searchQuery"
          placeholder="搜索文件..."
          :prefix-icon="Search"
          clearable
          class="search-input"
          size="default"
        />

        <!-- 视图切换 -->
        <div class="view-toggle">
          <button
            class="toggle-btn"
            :class="{ active: viewMode === 'grid' }"
            @click="setViewMode('grid')"
            title="网格视图"
          >
            <Squares2X2Icon class="w-5 h-5" />
          </button>
          <button
            class="toggle-btn"
            :class="{ active: viewMode === 'list' }"
            @click="setViewMode('list')"
            title="列表视图"
          >
            <ListBulletIcon class="w-5 h-5" />
          </button>
        </div>

        <!-- 上传按钮 -->
        <el-button
          type="primary"
          :class="isPartyTheme ? 'party-btn-primary' : ''"
          @click="handleUpload"
        >
          <CloudArrowUpIcon class="w-5 h-5" />
          <span>上传文件</span>
        </el-button>

        <!-- 新建文件按钮 -->
        <el-button @click="handleCreateFile">
          <DocumentPlusIcon class="w-5 h-5" />
          <span>新建文件</span>
        </el-button>

        <!-- 批量操作（选中时显示） -->
        <div v-if="selectedCount > 0" class="batch-actions">
          <span class="selected-count">已选 {{ selectedCount }} 项</span>
          <el-button size="small" @click="handleBatchDownload">下载</el-button>
          <el-button size="small" type="danger" @click="handleBatchDelete">删除</el-button>
          <el-button size="small" link @click="handleClearSelection">取消选择</el-button>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="layout-content">
      <!-- 左侧目录树 -->
      <div class="layout-sidebar">
        <CategoryTree
          ref="categoryTreeRef"
          :categories="categories"
          :current-category-id="currentCategory?.id || null"
          :title="sidebarTitle"
          :is-party-theme="isPartyTheme"
          :height="sidebarHeight"
          @select="handleCategorySelect"
          @add="handleAddCategory"
          @rename="handleRenameCategory"
          @delete="handleDeleteCategory"
        />
      </div>

      <!-- 右侧文件列表 -->
      <div class="layout-main">
        <!-- 网格视图 -->
        <div v-if="viewMode === 'grid'" class="file-grid-view">
          <FileCard
            v-for="document in displayedDocuments"
            :key="document.id"
            :document="document"
            :is-selected="selectedIds.has(document.id)"
            :is-party-theme="isPartyTheme"
            @click="handleFileClick"
            @toggle-select="handleToggleSelect"
            @open="handleOpenFile"
            @edit="handleEditFile"
            @download="handleDownloadFile"
            @rename="handleRenameFile"
            @delete="handleDeleteFile"
          />
          <div v-if="displayedDocuments.length === 0" class="empty-state">
            <DocumentIcon class="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p class="text-gray-500">{{ currentCategory ? '此目录暂无文件' : '请选择一个目录查看文件' }}</p>
            <el-button v-if="currentCategory" type="primary" @click="handleCreateFile">
              创建第一个文件
            </el-button>
          </div>
        </div>

        <!-- 列表视图 -->
        <FileList
          v-else
          :documents="displayedDocuments"
          :selected-ids="selectedIds"
          :is-party-theme="isPartyTheme"
          @click="handleFileClick"
          @toggle-select="handleToggleSelect"
          @select-all="handleSelectAll"
          @clear-selection="handleClearSelection"
          @open="handleOpenFile"
          @edit="handleEditFile"
          @download="handleDownloadFile"
          @rename="handleRenameFile"
          @delete="handleDeleteFile"
        />
      </div>
    </div>

    <!-- 上传对话框 -->
    <UploadDialog
      v-model="uploadDialogVisible"
      :categories="flatCategories"
      :default-category-id="currentCategory?.id || null"
      :is-party-theme="isPartyTheme"
      @confirm="handleUploadConfirm"
    />

    <!-- 新建文件对话框 -->
    <CreateFileDialog
      v-model="createFileDialogVisible"
      :categories="flatCategories"
      :default-category-id="currentCategory?.id || null"
      :is-party-theme="isPartyTheme"
      @confirm="handleCreateFileConfirm"
    />

    <!-- 目录编辑对话框 -->
    <CategoryEditDialog
      v-model="categoryEditDialogVisible"
      :category="editingCategory"
      :categories="flatCategories"
      :is-party-theme="isPartyTheme"
      @confirm="handleCategoryEditConfirm"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import {
  Squares2X2Icon,
  ListBulletIcon,
  CloudArrowUpIcon,
  DocumentPlusIcon,
  DocumentIcon
} from '@heroicons/vue/24/outline'
import CategoryTree from '@/components/file-manager/CategoryTree.vue'
import FileCard from '@/components/file-manager/FileCard.vue'
import FileList from '@/components/file-manager/FileList.vue'
import UploadDialog from '@/components/file-manager/UploadDialog.vue'
import CreateFileDialog from '@/components/file-manager/CreateFileDialog.vue'
import CategoryEditDialog from '@/components/file-manager/CategoryEditDialog.vue'
import type { Category, Document, FileViewMode } from '@/types/file-manager'

interface Props {
  categories: Category[]
  currentCategory: Category | null
  documents: Document[]
  selectedIds: Set<string>
  viewMode: FileViewMode
  searchQuery: string
  isPartyTheme?: boolean
  sidebarTitle?: string
}

interface Emits {
  (e: 'categoryClick', category: Category | null): void
  (e: 'fileClick', document: Document): void
  (e: 'fileOpen', document: Document): void
  (e: 'fileEdit', document: Document): void
  (e: 'fileDownload', document: Document): void
  (e: 'fileRename', document: Document): void
  (e: 'fileDelete', document: Document): void
  (e: 'fileUpload', file: File, categoryId: string): void
  (e: 'fileCreate', data: { categoryId: string; filename: string; content?: string }): void
  (e: 'categoryAdd', parentId: string | null): void
  (e: 'categoryRename', category: Category): void
  (e: 'categoryDelete', category: Category): void
  (e: 'toggleFileSelect', documentId: string): void
  (e: 'selectAllFiles'): void
  (e: 'clearSelection'): void
  (e: 'batchDownload', documentIds: string[]): void
  (e: 'batchDelete', documentIds: string[]): void
  (e: 'viewModeChange', mode: FileViewMode): void
  (e: 'searchQueryChange', query: string): void
}

const props = withDefaults(defineProps<Props>(), {
  isPartyTheme: false,
  sidebarTitle: '目录'
})

const emit = defineEmits<Emits>()

// 对话框状态
const uploadDialogVisible = ref(false)
const createFileDialogVisible = ref(false)
const categoryEditDialogVisible = ref(false)
const editingCategory = ref<Category | null>(null)

// 组件引用
const categoryTreeRef = ref<InstanceType<typeof CategoryTree> | null>(null)

// 侧边栏高度
const sidebarHeight = ref(600)

// 扁平化的目录列表
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
  return flatten(props.categories)
})

// 选中的文件数量
const selectedCount = computed(() => props.selectedIds.size)

// 显示的文件列表
const displayedDocuments = computed(() => {
  let docs = props.documents

  // 按目录筛选
  if (props.currentCategory) {
    docs = docs.filter(d => d.category_id === props.currentCategory!.id)
  }

  // 搜索筛选
  if (props.searchQuery.trim()) {
    const query = props.searchQuery.toLowerCase()
    docs = docs.filter(d =>
      d.original_filename.toLowerCase().includes(query)
    )
  }

  return docs
})

// 事件处理
const handleCategorySelect = (category: Category) => emit('categoryClick', category)

const handleFileClick = (document: Document) => emit('fileClick', document)

const handleToggleSelect = (documentId: string) => emit('toggleFileSelect', documentId)

const handleSelectAll = () => emit('selectAllFiles')

const handleClearSelection = () => emit('clearSelection')

const handleOpenFile = (document: Document) => emit('fileOpen', document)

const handleEditFile = (document: Document) => emit('fileEdit', document)

const handleDownloadFile = (document: Document) => emit('fileDownload', document)

const handleRenameFile = (document: Document) => emit('fileRename', document)

const handleDeleteFile = (document: Document) => emit('fileDelete', document)

const handleUpload = () => {
  uploadDialogVisible.value = true
}

const handleCreateFile = () => {
  createFileDialogVisible.value = true
}

const handleUploadConfirm = async (data: { file: File; categoryId: string }) => {
  emit('fileUpload', data.file, data.categoryId)
}

const handleCreateFileConfirm = async (data: { categoryId: string; filename: string; content?: string }) => {
  emit('fileCreate', data)
}

const setViewMode = (mode: FileViewMode) => emit('viewModeChange', mode)

const searchQuery = computed({
  get: () => props.searchQuery,
  set: (value) => emit('searchQueryChange', value)
})

// 批量操作
const handleBatchDownload = () => {
  emit('batchDownload', Array.from(props.selectedIds))
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedCount.value} 个文件吗？此操作不可撤销。`,
      '批量删除',
      {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }
    )
    emit('batchDelete', Array.from(props.selectedIds))
  } catch {
    // 用户取消
  }
}

// 目录操作
const handleAddCategory = (parentId: string | null) => emit('categoryAdd', parentId)

const handleRenameCategory = (category: Category) => {
  editingCategory.value = category
  categoryEditDialogVisible.value = true
  emit('categoryRename', category)
}

const handleDeleteCategory = (category: Category) => emit('categoryDelete', category)

const handleCategoryEditConfirm = (_data: { categoryId?: string; name: string; parentId?: string | null }) => {
  categoryEditDialogVisible.value = false
  editingCategory.value = null
  // 由父组件处理实际的更新操作
}

// 初始化
onMounted(() => {
  // 计算侧边栏高度
  const updateHeight = () => {
    sidebarHeight.value = window.innerHeight - 200
  }
  updateHeight()
  window.addEventListener('resize', updateHeight)
})

// 暴露方法给父组件
defineExpose({
  expandCategoryNode: (nodeId: string) => {
    categoryTreeRef.value?.expandNode(nodeId)
  }
})
</script>

<style scoped>
.file-management-layout {
  @apply h-full flex flex-col bg-gray-50;
}

/* 顶部工具栏 */
.layout-header {
  @apply bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-3 flex-shrink-0;
}

.header-actions {
  @apply flex items-center gap-3;
}

.search-input {
  @apply w-64;
}

.view-toggle {
  @apply flex items-center bg-gray-100 rounded-lg p-1;
}

.toggle-btn {
  @apply p-2 text-gray-500 hover:text-gray-700 rounded-md transition-all;
}

.toggle-btn.active {
  @apply bg-white text-red-600 shadow-sm;
}

.toggle-btn.party-theme.active {
  @apply bg-white text-red-600;
}

.batch-actions {
  @apply flex items-center gap-2 pl-4 border-l border-gray-200;
}

.selected-count {
  @apply text-sm text-gray-600 mr-2;
}

/* 主内容区 */
.layout-content {
  @apply flex-1 flex overflow-hidden;
}

/* 侧边栏 */
.layout-sidebar {
  @apply w-64 flex-shrink-0 border-r border-gray-200 bg-white overflow-y-auto;
}

/* 主内容 */
.layout-main {
  @apply flex-1 overflow-y-auto p-6;
}

/* 网格视图 */
.file-grid-view {
  @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4;
}

.empty-state {
  @apply flex flex-col items-center justify-center py-16 col-span-full;
}

/* 响应式 */
@media (max-width: 1024px) {
  .layout-sidebar {
    @apply hidden;
  }
}
</style>
