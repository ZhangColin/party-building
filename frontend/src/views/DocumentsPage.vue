<template>
  <div class="documents-page">
    <!-- 左侧：目录树 -->
    <aside class="category-sidebar">
      <div class="sidebar-header">
        <h2 class="sidebar-title">课程目录</h2>
      </div>
      <div class="sidebar-content">
        <!-- 加载中 -->
        <div v-if="loading && !hasCategories" class="loading-container">
          <div class="spinner"></div>
          <p class="loading-text">加载中...</p>
        </div>

        <!-- 错误提示 -->
        <div v-else-if="error && !hasCategories" class="error-container">
          <p class="error-message">{{ error }}</p>
          <button class="retry-button" @click="loadCategoryTree">重试</button>
        </div>

        <!-- 目录树 -->
        <div v-else-if="hasCategories" class="category-tree">
          <CategoryTreeNode
            v-for="category in categoryTree"
            :key="category.id"
            :node="category"
            :selectedId="currentCategoryId"
            @select="handleCategorySelect"
          />
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <DocumentTextIcon class="w-12 h-12 text-gray-300" />
          <p class="empty-text">暂无课程目录</p>
        </div>
      </div>
    </aside>

    <!-- 中间：文档列表 -->
    <div class="documents-list">
      <div class="list-header">
        <h2 class="list-title">
          {{ currentCategoryName || '请选择目录' }}
        </h2>
      </div>
      <div class="list-content">
        <!-- 加载中 -->
        <div v-if="loading && currentCategoryId" class="loading-container">
          <div class="spinner"></div>
          <p class="loading-text">加载中...</p>
        </div>

        <!-- 文档列表 -->
        <div v-else-if="hasDocuments" class="document-items">
          <div
            v-for="(doc, index) in documents"
            :key="doc.id"
            class="document-item"
            :class="{ active: currentDocument?.id === doc.id }"
            @click="handleDocumentSelect(doc.id)"
          >
            <div class="document-index">{{ index + 1 }}</div>
            <div class="document-info">
              <h3 class="document-title">{{ doc.title }}</h3>
              <p class="document-summary">{{ doc.summary }}</p>
            </div>
          </div>
        </div>

        <!-- 提示：选择目录 -->
        <div v-else-if="!currentCategoryId" class="hint-container">
          <FolderOpenIcon class="w-16 h-16 text-gray-300" />
          <p class="hint-text">请从左侧选择一个目录</p>
        </div>

        <!-- 空状态：该目录下无文档 -->
        <div v-else class="empty-state">
          <DocumentIcon class="w-16 h-16 text-gray-300" />
          <p class="empty-text">该目录下暂无文档</p>
        </div>
      </div>
    </div>

    <!-- 右侧：文档预览 -->
    <div class="document-preview">
      <div class="preview-header">
        <h2 class="preview-title">
          {{ currentDocument?.title || '文档预览' }}
        </h2>
        <!-- 工具栏：导航和下载 -->
        <div v-if="currentDocument" class="preview-toolbar">
          <!-- 导航按钮 -->
          <div class="preview-nav">
            <button
              class="nav-button"
              :disabled="!currentDocument.prev_doc_id"
              @click="navigateToPrevDoc"
              title="上一篇"
            >
              <ChevronLeftIcon class="w-5 h-5" />
            </button>
            <button
              class="nav-button"
              :disabled="!currentDocument.next_doc_id"
              @click="navigateToNextDoc"
              title="下一篇"
            >
              <ChevronRightIcon class="w-5 h-5" />
            </button>
          </div>
          <!-- 下载按钮 -->
          <div class="download-actions">
            <button class="action-button" @click="handleDownloadMarkdown" title="下载 Markdown">
              <ArrowDownTrayIcon class="w-4 h-4" />
              <span>Markdown</span>
            </button>
            <button class="action-button" @click="handleDownloadWord" :disabled="isDownloadingWord" title="下载 Word">
              <ArrowDownTrayIcon class="w-4 h-4" />
              <span>{{ isDownloadingWord ? '转换中...' : 'Word' }}</span>
            </button>
            <button class="action-button" @click="handleDownloadPDF" :disabled="isDownloadingPDF" title="下载 PDF">
              <ArrowDownTrayIcon class="w-4 h-4" />
              <span>{{ isDownloadingPDF ? '生成中...' : 'PDF' }}</span>
            </button>
          </div>
        </div>
      </div>
      <div class="preview-content">
        <!-- 加载中 -->
        <div v-if="loading && currentDocument" class="loading-container">
          <div class="spinner"></div>
          <p class="loading-text">加载中...</p>
        </div>

        <!-- 文档内容渲染 -->
        <div v-else-if="currentDocument" class="markdown-content" v-html="renderedContent"></div>

        <!-- 提示：选择文档 -->
        <div v-else class="hint-container">
          <DocumentTextIcon class="w-16 h-16 text-gray-300" />
          <p class="hint-text">请从中间栏选择一个文档</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import { storeToRefs } from 'pinia'
import {
  DocumentTextIcon,
  FolderOpenIcon,
  DocumentIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ArrowDownTrayIcon,
} from '@heroicons/vue/24/outline'
import { useCoursesStore } from '../stores/coursesStore'
import CategoryTreeNode from '../components/CategoryTreeNode.vue'
import { renderMarkdown } from '../utils/markdownRenderer'
import html2pdf from 'html2pdf.js'

const coursesStore = useCoursesStore()
const {
  categoryTree,
  currentCategoryId,
  documents,
  currentDocument,
  loading,
  error,
  hasCategories,
  hasDocuments,
  currentCategoryName,
} = storeToRefs(coursesStore)

// 下载状态
const isDownloadingWord = ref(false)
const isDownloadingPDF = ref(false)

// 渲染Markdown内容
const renderedContent = computed(() => {
  if (!currentDocument.value?.content) return ''
  return renderMarkdown(currentDocument.value.content)
})

/**
 * 加载目录树
 */
const loadCategoryTree = async () => {
  await coursesStore.fetchCategoryTree()
}

/**
 * 处理目录选择
 */
const handleCategorySelect = async (categoryId: string) => {
  coursesStore.setCurrentCategory(categoryId)
  await coursesStore.fetchDocumentsByCategory(categoryId)
}

/**
 * 处理文档选择
 */
const handleDocumentSelect = async (docId: string) => {
  await coursesStore.fetchDocumentDetail(docId)
}

/**
 * 导航到上一篇文档
 */
const navigateToPrevDoc = async () => {
  if (currentDocument.value?.prev_doc_id) {
    await handleDocumentSelect(currentDocument.value.prev_doc_id)
  }
}

/**
 * 导航到下一篇文档
 */
const navigateToNextDoc = async () => {
  if (currentDocument.value?.next_doc_id) {
    await handleDocumentSelect(currentDocument.value.next_doc_id)
  }
}

/**
 * 下载Markdown
 */
const handleDownloadMarkdown = () => {
  if (!currentDocument.value) return
  
  const blob = new Blob([currentDocument.value.content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${currentDocument.value.title}.md`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/**
 * 下载Word
 */
const handleDownloadWord = async () => {
  if (!currentDocument.value || isDownloadingWord.value) return
  
  isDownloadingWord.value = true
  try {
    const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
    const response = await fetch('/api/v1/convert/markdown-to-word', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        content: currentDocument.value.content,
        filename: currentDocument.value.title,
      }),
    })
    
    if (!response.ok) {
      throw new Error('Word转换失败')
    }
    
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${currentDocument.value.title}.docx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Word转换失败:', error)
    alert('Word转换失败，请稍后重试')
  } finally {
    isDownloadingWord.value = false
  }
}

/**
 * 下载PDF
 */
const handleDownloadPDF = async () => {
  if (!currentDocument.value || isDownloadingPDF.value) return
  
  isDownloadingPDF.value = true
  try {
    const element = document.querySelector('.markdown-content')
    if (!element) {
      throw new Error('未找到内容元素')
    }
    
    const opt = {
      margin: 10,
      filename: `${currentDocument.value.title}.pdf`,
      image: { type: 'jpeg' as const, quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' as const },
    }
    
    await html2pdf().set(opt).from(element as HTMLElement).save()
  } catch (error) {
    console.error('PDF生成失败:', error)
    alert('PDF生成失败，请稍后重试')
  } finally {
    isDownloadingPDF.value = false
  }
}

// 组件挂载时加载目录树
onMounted(() => {
  loadCategoryTree()
})
</script>

<style scoped>
.documents-page {
  @apply h-full w-full flex;
  background-color: theme('colors.gray.50');
}

/* 左侧：目录树 */
.category-sidebar {
  @apply flex flex-col border-r border-gray-200 bg-white;
  width: 280px;
  flex-shrink: 0;
}

.sidebar-header {
  @apply px-4 py-3 border-b border-gray-200;
}

.sidebar-title {
  @apply text-base font-semibold text-gray-900;
}

.sidebar-content {
  @apply flex-1 overflow-y-auto p-2;
}

.category-tree {
  @apply space-y-1;
}

/* 中间：文档列表 */
.documents-list {
  @apply flex flex-col border-r border-gray-200 bg-white;
  width: 360px;
  flex-shrink: 0;
}

.list-header {
  @apply px-4 py-3 border-b border-gray-200;
}

.list-title {
  @apply text-base font-semibold text-gray-900 truncate;
}

.list-content {
  @apply flex-1 overflow-y-auto;
}

.document-items {
  @apply divide-y divide-gray-100;
}

.document-item {
  @apply flex gap-3 px-4 py-3 cursor-pointer hover:bg-gray-50 transition-colors;
}

.document-item.active {
  @apply bg-blue-50 hover:bg-blue-100;
}

.document-index {
  @apply flex-shrink-0 w-6 h-6 flex items-center justify-center rounded-full bg-gray-100 text-xs font-medium text-gray-600;
}

.document-item.active .document-index {
  @apply bg-blue-500 text-white;
}

.document-info {
  @apply flex-1 min-w-0;
}

.document-title {
  @apply text-sm font-medium text-gray-900 truncate;
}

.document-summary {
  @apply text-xs text-gray-500 mt-1 line-clamp-2;
}

/* 右侧：文档预览 */
.document-preview {
  @apply flex-1 flex flex-col bg-white min-w-0;
}

.preview-header {
  @apply px-6 py-3 border-b border-gray-200 flex items-center justify-between;
}

.preview-title {
  @apply text-base font-semibold text-gray-900 truncate flex-1;
}

.preview-toolbar {
  @apply flex gap-4 ml-4 items-center;
}

.preview-nav {
  @apply flex gap-2;
}

.download-actions {
  @apply flex gap-2 border-l border-gray-200 pl-4;
}

.action-button {
  @apply flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors disabled:opacity-30 disabled:cursor-not-allowed;
}

.action-button:not(:disabled):hover {
  @apply bg-gray-100;
}

.nav-button {
  @apply p-1.5 rounded hover:bg-gray-100 transition-colors disabled:opacity-30 disabled:cursor-not-allowed;
}

.nav-button:not(:disabled):hover {
  @apply bg-gray-100;
}

.preview-content {
  @apply flex-1 overflow-y-auto;
}

.markdown-content {
  @apply px-6 py-4;
}

/* Markdown样式 */
.markdown-content :deep(h1) {
  @apply text-3xl font-bold mt-6 mb-4 pb-2 border-b border-gray-200;
}

.markdown-content :deep(h2) {
  @apply text-2xl font-bold mt-5 mb-3;
}

.markdown-content :deep(h3) {
  @apply text-xl font-semibold mt-4 mb-2;
}

.markdown-content :deep(p) {
  @apply my-3 leading-7;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  @apply my-3 ml-6;
}

.markdown-content :deep(li) {
  @apply my-1 leading-7;
}

.markdown-content :deep(code) {
  @apply bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono;
}

.markdown-content :deep(pre) {
  @apply bg-gray-50 border border-gray-200 rounded p-4 my-4 overflow-x-auto;
}

.markdown-content :deep(pre code) {
  @apply bg-transparent p-0;
}

.markdown-content :deep(blockquote) {
  @apply border-l-4 border-blue-500 pl-4 my-4 text-gray-600 italic;
}

.markdown-content :deep(a) {
  @apply text-blue-600 hover:text-blue-800 underline;
}

.markdown-content :deep(table) {
  @apply w-full my-4 border-collapse;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  @apply border border-gray-300 px-4 py-2;
}

.markdown-content :deep(th) {
  @apply bg-gray-50 font-semibold;
}

/* 共用样式 */
.loading-container {
  @apply flex flex-col items-center justify-center h-full gap-4 py-12;
}

.spinner {
  @apply w-10 h-10 border-4 border-gray-200 border-t-blue-500 rounded-full;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  @apply text-gray-500 text-sm;
}

.error-container {
  @apply flex flex-col items-center gap-3 py-12 px-4;
}

.error-message {
  @apply text-red-600 text-sm text-center;
}

.retry-button {
  @apply px-3 py-1.5 text-sm font-medium text-blue-600 hover:text-blue-700 bg-blue-50 hover:bg-blue-100 rounded transition-colors;
}

.empty-state,
.hint-container {
  @apply flex flex-col items-center justify-center h-full gap-3 py-12 px-4;
}

.empty-text,
.hint-text {
  @apply text-gray-400 text-sm;
}
</style>

