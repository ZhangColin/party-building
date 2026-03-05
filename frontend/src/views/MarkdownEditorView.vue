<template>
  <div class="markdown-editor-view">
    <!-- 顶部工具条 -->
    <div class="toolbar">
      <div class="toolbar-title">
        <DocumentTextIcon class="w-5 h-5" :class="isFileMode ? 'text-red-600' : 'text-blue-600'" />
        <span>{{ editorTitle }}</span>
        <span v-if="hasUnsavedChanges" class="unsaved-indicator">未保存</span>
      </div>
      <div class="toolbar-actions">
        <!-- 文件模式显示保存按钮 -->
        <button
          v-if="isFileMode"
          class="toolbar-btn save-btn"
          :disabled="saving || !hasUnsavedChanges"
          @click="handleSave"
          title="保存文件"
        >
          <ArrowPathIcon v-if="saving" class="w-4 h-4 animate-spin" />
          <CheckIcon v-else class="w-4 h-4" />
          <span>{{ saving ? '保存中...' : '保存' }}</span>
        </button>
        <button class="toolbar-btn" @click="handleClear" title="清空内容">
          <TrashIcon class="w-4 h-4" />
          <span>清空</span>
        </button>
        <button class="toolbar-btn back-btn" @click="handleBack">
          <ArrowLeftIcon class="w-5 h-5" />
          <span>返回</span>
        </button>
      </div>
    </div>

    <!-- 编辑器容器 -->
    <div class="editor-container">
      <!-- 左侧：CodeMirror 编辑器 -->
      <div class="editor-panel" :style="{ width: `${editorWidth}%` }">
        <div ref="editorRef" class="editor-content"></div>
      </div>

      <!-- 可拖动分隔条 -->
      <div 
        class="resizer" 
        @mousedown="startResize"
        @touchstart="startResize"
      >
        <div class="resizer-line"></div>
      </div>

      <!-- 右侧：预览面板 -->
      <div class="preview-container" :style="{ width: `${100 - editorWidth}%` }">
        <PreviewPanel :artifact="previewArtifact" @close="handleClosePreview" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { EditorView, keymap, lineNumbers, highlightActiveLineGutter, highlightActiveLine } from '@codemirror/view'
import { EditorState } from '@codemirror/state'
import { defaultKeymap, history, historyKeymap } from '@codemirror/commands'
import { markdown } from '@codemirror/lang-markdown'
import { oneDark } from '@codemirror/theme-one-dark'
import { syntaxHighlighting, defaultHighlightStyle } from '@codemirror/language'
import { ArrowLeftIcon, DocumentTextIcon, TrashIcon, CheckIcon,ArrowPathIcon } from '@heroicons/vue/24/outline'
import { ElMessage } from 'element-plus'
import PreviewPanel from '../components/PreviewPanel.vue'
import type { Artifact } from '../types'
import { useKnowledgeStore } from '@/stores/knowledgeStore'
import { usePartyActivityStore } from '@/stores/partyActivityStore'

const router = useRouter()
const route = useRoute()

// ==================== 模式判断 ====================
// 文件管理模式参数
const documentId = ref<string | null>(null)
const categoryId = ref<string | null>(null)
const fileMode = ref<'knowledge' | 'party-activity' | null>(null)

// 判断是否为文件管理模式
const isFileMode = computed(() => !!fileMode.value)

// 获取当前 store
const knowledgeStore = useKnowledgeStore()
const partyActivityStore = usePartyActivityStore()

const currentStore = computed(() =>
  fileMode.value === 'knowledge' ? knowledgeStore :
  fileMode.value === 'party-activity' ? partyActivityStore :
  null
)

// 文件信息
const documentInfo = ref<{ filename: string; original_filename: string } | null>(null)
const saving = ref(false)
const hasUnsavedChanges = ref(false)

// ==================== 编辑器基础 ====================
// 编辑器引用
const editorRef = ref<HTMLElement | null>(null)
let editorView: EditorView | null = null

// 分隔条宽度（百分比）
const editorWidth = ref(50)
const isResizing = ref(false)

// 编辑器内容
const editorContent = ref('')

// 预览成果物
const previewArtifact = computed<Artifact>(() => ({
  type: 'markdown',
  content: editorContent.value,
  language: 'markdown',
  timestamp: new Date().toISOString(),
}))

// 标题
const editorTitle = computed(() => {
  if (isFileMode.value && documentInfo.value) {
    return documentInfo.value.original_filename
  }
  return 'Markdown 编辑器'
})

/**
 * 初始化 CodeMirror 编辑器
 */
const initEditor = () => {
  if (!editorRef.value) return

  const startState = EditorState.create({
    doc: editorContent.value,
    extensions: [
      lineNumbers(),
      highlightActiveLineGutter(),
      highlightActiveLine(),
      history(),
      keymap.of([...defaultKeymap, ...historyKeymap]),
      markdown(),
      syntaxHighlighting(defaultHighlightStyle),
      oneDark,
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          editorContent.value = update.state.doc.toString()
        }
      }),
      EditorView.lineWrapping, // 自动换行
    ],
  })

  editorView = new EditorView({
    state: startState,
    parent: editorRef.value,
  })
}

/**
 * 返回
 */
const handleBack = () => {
  if (hasUnsavedChanges.value) {
    if (!confirm('有未保存的更改，确定要离开吗？')) {
      return
    }
  }
  if (isFileMode.value) {
    // 文件管理模式返回到对应的文件管理页面
    const targetPath = fileMode.value === 'knowledge' ? '/knowledge' : '/party-activities'
    router.push(targetPath)
  } else {
    // 独立模式返回工具列表
    router.push('/common-tools')
  }
}

/**
 * 保存文件内容
 */
const handleSave = async () => {
  if (!isFileMode.value || !documentId.value || !currentStore.value) return

  saving.value = true
  try {
    await currentStore.value.updateDocument(documentId.value, editorContent.value)
    hasUnsavedChanges.value = false
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

/**
 * 清空编辑器内容
 */
const handleClear = () => {
  if (!editorView) return

  if (confirm('确定要清空所有内容吗？此操作不可撤销。')) {
    const transaction = editorView.state.update({
      changes: { from: 0, to: editorView.state.doc.length, insert: '' },
    })
    editorView.dispatch(transaction)
    editorContent.value = ''
    hasUnsavedChanges.value = true
  }
}

/**
 * 加载文件内容
 */
const loadDocumentContent = async () => {
  if (!documentId.value || !currentStore.value) return

  try {
    const document = await currentStore.value.loadDocument(documentId.value)
    documentInfo.value = {
      filename: document.filename,
      original_filename: document.original_filename
    }
    // 使用文件内容（包括空字符串）
    const content = document.content || ''
    editorContent.value = content
    // 更新编辑器内容
    if (editorView) {
      const transaction = editorView.state.update({
        changes: { from: 0, to: editorView.state.doc.length, insert: content },
      })
      editorView.dispatch(transaction)
    }
    // 重置未保存状态
    hasUnsavedChanges.value = false
  } catch (error) {
    console.error('加载文件失败:', error)
    ElMessage.error('加载文件失败')
  }
}

/**
 * 关闭预览（占位符，预览始终显示）
 */
const handleClosePreview = () => {
  // Markdown编辑器中预览始终显示，不关闭
}

/**
 * 开始调整大小
 */
const startResize = (e: MouseEvent | TouchEvent) => {
  isResizing.value = true
  e.preventDefault()
  
  // 添加全局监听
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopResize)
  document.addEventListener('touchmove', handleResize)
  document.addEventListener('touchend', stopResize)
  
  // 添加样式防止文本选择
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

/**
 * 调整大小中
 */
const handleResize = (e: MouseEvent | TouchEvent) => {
  if (!isResizing.value) return
  
  // 获取容器宽度
  const container = document.querySelector('.editor-container') as HTMLElement
  if (!container) return
  
  const containerRect = container.getBoundingClientRect()
  const clientX = 'touches' in e ? (e.touches[0]?.clientX ?? 0) : e.clientX
  
  // 计算新宽度（百分比）
  const newWidth = ((clientX - containerRect.left) / containerRect.width) * 100
  
  // 限制在 30% - 70% 之间
  editorWidth.value = Math.max(30, Math.min(70, newWidth))
}

/**
 * 停止调整大小
 */
const stopResize = () => {
  isResizing.value = false
  
  // 移除全局监听
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
  document.removeEventListener('touchmove', handleResize)
  document.removeEventListener('touchend', stopResize)
  
  // 恢复样式
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}

// 组件挂载时初始化编辑器
onMounted(async () => {
  // 从路由参数获取文件信息
  const docId = route.query.documentId as string | undefined
  const catId = route.query.categoryId as string | undefined
  const mode = route.query.mode as 'knowledge' | 'party-activity' | undefined

  if (docId && mode) {
    fileMode.value = mode
    documentId.value = docId
    if (catId) {
      categoryId.value = catId
    }
  }

  initEditor()

  // 如果是文件模式，加载文件内容
  if (isFileMode.value) {
    await loadDocumentContent()
  }

  // 监听 beforeunload 事件
  window.addEventListener('beforeunload', handleBeforeUnload)
})

// 组件卸载时清理
onBeforeUnmount(() => {
  if (editorView) {
    editorView.destroy()
    editorView = null
  }
  window.removeEventListener('beforeunload', handleBeforeUnload)
})

// 监听内容变化，标记未保存状态
watch(editorContent, (_newContent, oldContent) => {
  // 初始化后才开始追踪变化
  if (oldContent !== undefined) {
    hasUnsavedChanges.value = true
  }
})

/**
 * 处理页面离开前的确认
 */
const handleBeforeUnload = (e: BeforeUnloadEvent) => {
  if (hasUnsavedChanges.value) {
    e.preventDefault()
    e.returnValue = ''
  }
}

// 组件卸载时销毁编辑器
onBeforeUnmount(() => {
  if (editorView) {
    editorView.destroy()
    editorView = null
  }
})
</script>

<style scoped>
.markdown-editor-view {
  @apply h-full w-full overflow-hidden flex flex-col;
  background-color: theme('colors.gray.50');
}

/* 顶部工具条 */
.toolbar {
  @apply flex items-center gap-4 px-6 py-3 bg-white border-b border-gray-200;
  flex-shrink: 0;
}

.toolbar-btn {
  @apply flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-all;
}

.toolbar-btn:hover {
  @apply shadow-sm;
}

.back-btn {
  @apply text-gray-600 hover:text-gray-900;
}

.toolbar-title {
  @apply flex items-center gap-2 text-lg font-semibold text-gray-900 flex-1;
}

.toolbar-actions {
  @apply flex items-center gap-2;
}

/* 未保存指示器 */
.unsaved-indicator {
  @apply text-xs font-normal px-2 py-0.5 bg-orange-100 text-orange-700 rounded;
}

/* 保存按钮 */
.save-btn {
  @apply bg-red-600 text-white border-red-600 hover:bg-red-700 hover:border-red-700;
}

.save-btn:disabled {
  @apply bg-gray-300 text-gray-500 border-gray-300 cursor-not-allowed hover:bg-gray-300 hover:border-gray-300;
}

/* 编辑器容器 */
.editor-container {
  @apply flex-1 flex overflow-hidden relative;
}

/* 左侧编辑器 */
.editor-panel {
  @apply flex flex-col border-r border-gray-200 bg-white;
  min-width: 30%;
  max-width: 70%;
}

/* 可拖动分隔条 */
.resizer {
  @apply flex-shrink-0 w-1 bg-gray-200 hover:bg-blue-400 cursor-col-resize relative transition-colors;
  z-index: 10;
}

.resizer:hover .resizer-line {
  @apply opacity-100;
}

.resizer-line {
  @apply absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-1 h-12 bg-blue-500 rounded-full opacity-0 transition-opacity;
}

.editor-content {
  @apply flex-1 overflow-auto;
}

/* CodeMirror 样式覆盖 */
.editor-content :deep(.cm-editor) {
  @apply h-full;
  font-size: 14px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
}

.editor-content :deep(.cm-scroller) {
  @apply overflow-auto;
}

.editor-content :deep(.cm-content) {
  @apply p-4;
}

.editor-content :deep(.cm-line) {
  padding-left: 8px;
  padding-right: 8px;
}

/* 右侧预览 */
.preview-container {
  @apply flex flex-col bg-white;
  min-width: 30%;
  max-width: 70%;
}

/* 平板端响应式（768px - 1023px） */
@media (min-width: 768px) and (max-width: 1023px) {
  .toolbar-title {
    @apply text-base;
  }
}

/* 移动端响应式（<768px） */
@media (max-width: 767px) {
  .toolbar {
    @apply px-4 py-2 gap-2;
  }
  
  .toolbar-title {
    @apply text-sm;
  }
  
  .toolbar-btn span {
    @apply hidden;
  }
  
  .editor-container {
    @apply flex-col;
  }

  .editor-panel,
  .preview-container {
    @apply w-full;
    min-width: unset;
    max-width: unset;
    height: 50%;
  }

  .editor-panel {
    @apply border-r-0 border-b border-gray-200;
  }
  
  .resizer {
    @apply hidden;
  }
}

</style>
