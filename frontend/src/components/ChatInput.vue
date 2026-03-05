<template>
  <div class="chat-input">
    <!-- 文件选择对话框 -->
    <FileSelectorDialog
      v-model="knowledgeDialogVisible"
      source="knowledge"
      :files="knowledgeFiles"
      :categories="knowledgeCategories"
      :loading="knowledgeLoading"
      @confirm="handleKnowledgeFilesSelected"
    />
    <FileSelectorDialog
      v-model="partyDialogVisible"
      source="party"
      :files="partyFiles"
      :categories="partyCategories"
      :loading="partyLoading"
      @confirm="handlePartyFilesSelected"
    />

    <!-- 文件操作按钮区 -->
    <div v-if="showFileButtons" class="file-actions">
      <button
        class="file-btn"
        :disabled="isAtMaxFiles || disabled"
        @click="handleUploadLocal"
        title="上传本地文件"
      >
        <CloudArrowUpIcon class="w-5 h-5" />
        <span>本地文件</span>
      </button>
      <button
        class="file-btn"
        :disabled="isAtMaxFiles || disabled"
        @click="handleSelectKnowledge"
        title="从知识库选择"
      >
        <BuildingLibraryIcon class="w-5 h-5" />
        <span>知识库</span>
      </button>
      <button
        class="file-btn"
        :disabled="isAtMaxFiles || disabled"
        @click="handleSelectParty"
        title="从党建活动选择"
      >
        <DocumentTextIcon class="w-5 h-5" />
        <span>党建活动</span>
      </button>
    </div>

    <!-- 附件展示区 -->
    <div v-if="attachments.length > 0" class="attachments-area">
      <div
        v-for="att in attachments"
        :key="att.id"
        class="attachment-tag"
        :class="{ 'error': att.status === 'error', 'uploading': att.status === 'uploading' }"
      >
        <DocumentIcon class="w-4 h-4 attachment-icon" />
        <span class="attachment-name">{{ att.name }}</span>
        <span v-if="att.status === 'uploading'" class="attachment-progress">{{ att.uploadProgress }}%</span>
        <span v-else class="attachment-size">{{ formatSize(att.size) }}</span>
        <button
          class="attachment-remove"
          @click="removeAttachment(att.id)"
          title="删除"
        >
          <XMarkIcon class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- 输入框和发送按钮 -->
    <textarea
      ref="textareaRef"
      v-model="inputText"
      class="input-textarea"
      :placeholder="placeholder || '输入消息...'"
      :disabled="disabled"
      rows="1"
      @keydown="handleKeyDown"
      @input="handleInput"
      @compositionstart="handleCompositionStart"
      @compositionend="handleCompositionEnd"
    ></textarea>
    <button
      class="send-button"
      :disabled="!canSend"
      @click="handleSend"
    >
      发送
    </button>

    <!-- 隐藏的文件输入 -->
    <input
      ref="fileInputRef"
      type="file"
      style="display: none"
      @change="handleFileSelected"
    >
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  CloudArrowUpIcon,
  BuildingLibraryIcon,
  DocumentTextIcon,
  DocumentIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'
import type { ChatAttachment } from '@/types'
import { uploadTempFile } from '@/services/tempFilesApi'
import FileSelectorDialog, { type FileItem } from './FileSelectorDialog.vue'

const props = withDefaults(
  defineProps<{
    placeholder?: string
    disabled?: boolean
    maxFiles?: number
    maxFileSize?: number
    showFileButtons?: boolean
  }>(),
  {
    maxFiles: 5,
    maxFileSize: 10 * 1024 * 1024, // 10MB
    showFileButtons: true
  }
)

const emit = defineEmits<{
  send: [content: string, attachments: ChatAttachment[]]
}>()

// 状态
const inputText = ref('')
const isComposing = ref(false) // 标记是否正在使用输入法
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)
const attachments = ref<ChatAttachment[]>([])

// 文件选择对话框状态
const knowledgeDialogVisible = ref(false)
const partyDialogVisible = ref(false)
const knowledgeFiles = ref<FileItem[]>([])
const partyFiles = ref<FileItem[]>([])
const knowledgeCategories = ref<Array<{ id: string; name: string }>>([])
const partyCategories = ref<Array<{ id: string; name: string }>>([])
const knowledgeLoading = ref(false)
const partyLoading = ref(false)

// 计算属性
const isAtMaxFiles = computed(() => attachments.value.length >= props.maxFiles)
const canSend = computed(() =>
  inputText.value.trim() && !attachments.value.some(a => a.status === 'uploading') && !props.disabled
)

// 方法
function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function handleUploadLocal() {
  fileInputRef.value?.click()
}

async function handleFileSelected(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  // 验证文件大小
  if (file.size > props.maxFileSize) {
    ElMessage.error(`文件大小超过限制（最大${formatSize(props.maxFileSize)}）`)
    return
  }

  // 添加到附件列表（上传中状态）
  const tempAttachment: ChatAttachment = {
    id: `temp-${Date.now()}`,
    name: file.name,
    type: 'temp',
    size: file.size,
    status: 'uploading',
    uploadProgress: 0
  }
  attachments.value.push(tempAttachment)

  try {
    const response = await uploadTempFile(file, (progress) => {
      // 更新上传进度
      const index = attachments.value.findIndex(a => a.id === tempAttachment.id)
      if (index !== -1) {
        const att = attachments.value[index]
        if (att) {
          att.uploadProgress = progress
        }
      }
    })

    // 更新为就绪状态
    const index = attachments.value.findIndex(a => a.id === tempAttachment.id)
    if (index !== -1) {
      const att = attachments.value[index]
      if (att) {
        attachments.value[index] = {
          ...response,
          id: response.temp_id,
          name: response.filename || response.temp_id,
          type: 'temp',
          status: 'ready'
        }
      }
    }
    ElMessage.success('文件上传成功')
  } catch (error: any) {
    const index = attachments.value.findIndex(a => a.id === tempAttachment.id)
    if (index !== -1) {
      const att = attachments.value[index]
      if (att) {
        att.status = 'error'
        att.error = error.message || '上传失败'
      }
    }
    ElMessage.error('文件上传失败')
  }

  // 清空 input
  target.value = ''
}

function removeAttachment(id: string) {
  const index = attachments.value.findIndex(a => a.id === id)
  if (index !== -1) {
    attachments.value.splice(index, 1)
  }
}

async function handleSelectKnowledge() {
  knowledgeDialogVisible.value = true
  knowledgeLoading.value = true
  try {
    // TODO: 调用知识库 API 获取文件列表
    // const response = await knowledgeApi.getDocuments()
    // knowledgeFiles.value = response.items
    // knowledgeCategories.value = response.categories
    knowledgeFiles.value = []
    knowledgeCategories.value = []
  } catch (error) {
    ElMessage.error('获取知识库文件失败')
  } finally {
    knowledgeLoading.value = false
  }
}

async function handleSelectParty() {
  partyDialogVisible.value = true
  partyLoading.value = true
  try {
    // TODO: 调用党建活动 API 获取文件列表
    // const response = await partyActivityApi.getDocuments()
    // partyFiles.value = response.items
    // partyCategories.value = response.categories
    partyFiles.value = []
    partyCategories.value = []
  } catch (error) {
    ElMessage.error('获取党建活动文件失败')
  } finally {
    partyLoading.value = false
  }
}

function handleKnowledgeFilesSelected(selectedAttachments: ChatAttachment[]) {
  // 添加选中的知识库文件到附件列表
  for (const att of selectedAttachments) {
    if (!isAtMaxFiles.value) {
      attachments.value.push(att)
    }
  }
}

function handlePartyFilesSelected(selectedAttachments: ChatAttachment[]) {
  // 添加选中的党建活动文件到附件列表
  for (const att of selectedAttachments) {
    if (!isAtMaxFiles.value) {
      attachments.value.push(att)
    }
  }
}

function handleCompositionStart() {
  isComposing.value = true
}

function handleCompositionEnd() {
  setTimeout(() => {
    isComposing.value = false
  }, 0)
}

function handleKeyDown(event: KeyboardEvent) {
  if (isComposing.value) {
    return
  }

  // Enter发送，Shift+Enter换行
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    if (!isComposing.value) {
      handleSend()
    }
  }
}

async function adjustTextareaHeight() {
  await nextTick()
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    const scrollHeight = textareaRef.value.scrollHeight
    // 限制最大高度为 200px
    const maxHeight = 200
    if (scrollHeight <= maxHeight) {
      textareaRef.value.style.height = `${scrollHeight}px`
    } else {
      textareaRef.value.style.height = `${maxHeight}px`
      textareaRef.value.style.overflowY = 'auto'
    }
  }
}

async function handleInput() {
  await adjustTextareaHeight()
}

watch(inputText, () => {
  adjustTextareaHeight()
})

function handleSend() {
  if (!canSend.value) return

  const readyAttachments = attachments.value.filter(a => a.status === 'ready')
  emit('send', inputText.value.trim(), readyAttachments)

  // 清空输入
  inputText.value = ''
  attachments.value = []
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
  }
}

// 暴露方法供测试和使用
defineExpose({
  addAttachment: (att: ChatAttachment) => {
    if (!isAtMaxFiles.value) {
      attachments.value.push(att)
    }
  },
  validateFileSize: (file: File) => {
    return {
      valid: file.size <= props.maxFileSize,
      error: file.size > props.maxFileSize
        ? `文件大小超过限制（最大${formatSize(props.maxFileSize)}）`
        : undefined
    }
  },
  attachments
})
</script>

<style scoped>
.chat-input {
  @apply flex flex-col gap-3;
}

.file-actions {
  @apply flex items-center gap-2;
}

.file-btn {
  @apply flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-200 text-gray-600 text-sm transition-all;
}

.file-btn:hover:not(:disabled) {
  @apply bg-gray-50 border-gray-300;
}

.file-btn:disabled {
  @apply opacity-50 cursor-not-allowed;
}

.attachments-area {
  @apply flex flex-wrap gap-2;
}

.attachment-tag {
  @apply flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg text-sm transition-all;
}

.attachment-tag.uploading {
  @apply bg-blue-50 text-blue-600;
}

.attachment-tag.error {
  @apply bg-red-50 text-red-600;
}

.attachment-icon {
  @apply text-gray-400 flex-shrink-0;
}

.attachment-name {
  @apply truncate max-w-[150px];
}

.attachment-size {
  @apply text-gray-400 text-xs;
}

.attachment-progress {
  @apply text-blue-600 text-xs;
}

.attachment-remove {
  @apply text-gray-400 hover:text-red-500 transition-colors cursor-pointer;
}

.input-textarea {
  @apply flex-1 px-4 py-3 border border-gray-300 rounded-xl text-sm resize-none min-h-[44px] max-h-[200px] leading-relaxed bg-white transition-all duration-200;
  font-family: inherit;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  border-color: theme('colors.gray.300');
  overflow-y: hidden;
}

.input-textarea:hover {
  border-color: theme('colors.gray.400');
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.input-textarea:focus {
  @apply outline-none border-primary-500;
  box-shadow: 0 0 0 3px theme('colors.primary.500 / 0.1'), 0 2px 4px rgba(0, 0, 0, 0.08);
}

.input-textarea::placeholder {
  @apply text-gray-400;
}

.send-button {
  padding: 12px 24px;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  background: linear-gradient(135deg, #C8102E 0%, #8B0000 100%);
}

.send-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #a00d25 0%, #6d0000 100%);
  box-shadow: 0 4px 12px rgba(200, 16, 46, 0.3);
  transform: translateY(-1px);
}

.send-button:active:not(:disabled) {
  transform: translateY(0);
  background: linear-gradient(135deg, #8B0000 0%, #5a0000 100%);
  box-shadow: 0 2px 8px rgba(200, 16, 46, 0.2);
}

.send-button:disabled {
  @apply bg-gray-300 cursor-not-allowed opacity-60;
  box-shadow: none;
}

.input-textarea:disabled {
  @apply bg-gray-50 cursor-not-allowed opacity-60;
}

/* 响应式 */
@media (min-width: 768px) and (max-width: 1023px) {
  .chat-input {
    gap: 10px;
  }

  .input-textarea {
    padding: 11px 15px;
    font-size: 14px;
  }

  .send-button {
    padding: 11px 22px;
    font-size: 14px;
  }
}

@media (max-width: 767px) {
  .chat-input {
    gap: 8px;
  }

  .input-textarea {
    padding: 10px 14px;
    font-size: 14px;
    min-height: 40px;
  }

  .send-button {
    padding: 10px 20px;
    font-size: 13px;
  }
}
</style>
