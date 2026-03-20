# -*- coding: utf-8 -*-
<template>
  <el-dialog
    v-model="visible"
    :title="dialogTitle"
    width="80%"
    top="5vh"
    :close-on-click-modal="false"
    @close="handleClose"
    class="file-preview-dialog"
  >
    <div class="preview-container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-icon class="is-loading"><Loading /></el-icon>
        <p>加载中...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-state">
        <el-icon><Warning /></el-icon>
        <p>{{ error }}</p>
        <el-button type="primary" @click="handleDownload">下载文件</el-button>
      </div>

      <!-- PDF 预览 -->
      <div v-else-if="document?.file_type === 'pdf'" class="pdf-preview">
        <iframe
          :src="previewUrl"
          class="preview-iframe"
          @load="handleLoad"
          @error="handleError"
        />
      </div>

      <!-- 图片预览 -->
      <div v-else-if="document?.file_type === 'image'" class="image-preview">
        <img
          :src="previewUrl"
          :alt="document?.original_filename"
          class="preview-image"
          @load="handleLoad"
          @error="handleImageError"
        />
      </div>

      <!-- 不支持预览的文件类型 -->
      <div v-else class="unsupported-preview">
        <el-icon class="file-icon"><Document /></el-icon>
        <p class="file-name">{{ document?.original_filename }}</p>
        <p class="hint">此文件类型不支持在线预览</p>
        <el-button type="primary" @click="handleDownload">下载文件</el-button>
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button v-if="canDownload" type="primary" @click="handleDownload">下载</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Loading, Warning, Document } from '@element-plus/icons-vue'
import type { Document as DocumentType, FileType } from '@/types/file-manager'

interface Props {
  modelValue: boolean
  document: DocumentType | null
  originalFileUrl: string
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const loading = ref(false)
const error = ref('')

// 可以预览的文件类型
const previewableTypes: FileType[] = ['pdf', 'image']

const canPreview = computed(() =>
  props.document && previewableTypes.includes(props.document.file_type)
)

const canDownload = computed(() => props.document !== null)

const dialogTitle = computed(() => {
  if (!props.document) return '文件预览'
  return `预览：${props.document.original_filename}`
})

// 获取完整的预览 URL（包含 API 基础路径）
const previewUrl = computed(() => {
  if (!props.document || !props.originalFileUrl) return ''

  // originalFileUrl 应该是完整路径（如 /api/v1/knowledge/documents/xxx/original）
  // 添加时间戳避免缓存
  const url = `${props.originalFileUrl}?t=${Date.now()}`
  console.log('previewUrl computed:', url)
  return url
})

// 监听弹窗打开，重置状态并开始加载
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    loading.value = true
    error.value = ''
  }
})

const handleLoad = () => {
  loading.value = false
}

const handleError = () => {
  loading.value = false
  error.value = '文件加载失败，请稍后重试或下载查看'
}

const handleImageError = () => {
  loading.value = false
  error.value = '图片加载失败，请稍后重试或下载查看'
}

const handleClose = () => {
  visible.value = false
}

const handleDownload = () => {
  if (props.originalFileUrl) {
    // 获取完整的下载 URL
    const apiBase = import.meta.env.VITE_API_BASE_URL || '/api/v1'
    const url = props.originalFileUrl.startsWith('/') ? props.originalFileUrl : `/${props.originalFileUrl}`
    const fullUrl = url.startsWith('/api') ? url : `${apiBase}${url}`

    // 创建下载链接
    const link = document.createElement('a')
    link.href = fullUrl
    link.download = props.document?.original_filename || 'download'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}
</script>

<style scoped>
.file-preview-dialog {
  --el-dialog-border-radius: 12px;
}

.preview-container {
  min-height: 500px;
  max-height: 75vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.loading-state .el-icon {
  font-size: 32px;
}

/* 错误状态 */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  padding: 24px;
  text-align: center;
}

.error-state .el-icon {
  font-size: 48px;
  color: var(--el-color-warning);
}

/* PDF 预览 */
.pdf-preview {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-iframe {
  width: 100%;
  height: 70vh;
  border: none;
  border-radius: 8px;
  background: #f5f5f5;
}

/* 图片预览 */
.image-preview {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border-radius: 8px;
  padding: 16px;
}

.preview-image {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
}

/* 不支持预览 */
.unsupported-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 32px;
  text-align: center;
}

.unsupported-preview .file-icon {
  font-size: 64px;
  color: var(--el-text-color-placeholder);
}

.unsupported-preview .file-name {
  font-size: 16px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin: 0;
}

.unsupported-preview .hint {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin: 0;
}
</style>
