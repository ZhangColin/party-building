<template>
  <div class="chat-input-container" data-testid="chat-input-container">
    <!-- 附件展示区 -->
    <div v-if="attachments.length > 0" class="attachments-area">
      <TransitionGroup name="attachment">
        <div
          v-for="attachment in attachments"
          :key="attachment.id"
          class="attachment-tag"
          :class="{ 'attachment-error': attachment.status === 'error' }"
        >
          <DocumentIcon class="attachment-icon" />
          <span class="attachment-name">{{ attachment.name }}</span>
          <span class="attachment-size">({{ formatFileSize(attachment.size) }})</span>
          <button
            class="attachment-remove"
            @click="removeAttachment(attachment.id)"
            :disabled="attachment.status === 'uploading'"
            :title="attachment.status === 'uploading' ? '上传中...' : '移除'"
          >
            <XMarkIcon v-if="attachment.status !== 'uploading'" class="w-4 h-4" />
            <div v-else class="upload-spinner"></div>
          </button>
          <span v-if="attachment.status === 'uploading'" class="attachment-progress">
            上传中 {{ attachment.uploadProgress }}%
          </span>
          <span v-if="attachment.status === 'error'" class="attachment-error-text">
            {{ attachment.error || '上传失败' }}
          </span>
        </div>
      </TransitionGroup>
    </div>

    <!-- 文件操作按钮区 -->
    <div v-if="showFileButtons" class="file-actions">
      <button
        class="file-action-btn"
        @click="triggerFileInput"
        :disabled="disabled || isLoading || !canAddMoreFiles"
        title="上传本地文件"
      >
        <CloudArrowUpIcon class="w-5 h-5" />
        <span>本地文件</span>
      </button>
      <button
        class="file-action-btn"
        @click="$emit('openKnowledge')"
        :disabled="disabled || isLoading"
        title="从知识库选择"
      >
        <BookOpenIcon class="w-5 h-5" />
        <span>知识库</span>
      </button>
      <button
        class="file-action-btn"
        @click="$emit('openPartyActivity')"
        :disabled="disabled || isLoading"
        title="从党建活动选择"
      >
        <CalendarIcon class="w-5 h-5" />
        <span>党建活动</span>
      </button>
      <input
        ref="fileInputRef"
        type="file"
        class="hidden-file-input"
        @change="handleFileSelect"
        accept=".txt,.md,.json,.csv,.pdf,.doc,.docx,.xls,.xlsx"
        multiple
      />
    </div>

    <!-- 输入区域 -->
    <div class="chat-input-wrapper" data-testid="chat-input-wrapper">
      <textarea
        ref="textareaRef"
        v-model="inputContent"
        class="chat-input"
        :placeholder="placeholder"
        rows="1"
        :disabled="disabled"
        @keydown="handleKeydown"
        @input="handleInput"
        @compositionstart="handleCompositionStart"
        @compositionend="handleCompositionEnd"
        data-testid="chat-input"
      />
      <button
        class="send-button"
        :disabled="!canSend"
        @click="handleSend"
        data-testid="send-button"
        title="发送 (Enter)"
      >
        <svg
          v-if="!isLoading"
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <line x1="22" y1="2" x2="11" y2="13"></line>
          <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
        </svg>
        <div v-else class="loading-spinner" data-testid="loading-spinner"></div>
      </button>
    </div>

    <!-- 文件限制提示 -->
    <div v-if="fileError" class="file-error">
      {{ fileError }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import {
  DocumentIcon,
  XMarkIcon,
  CloudArrowUpIcon,
  BookOpenIcon,
  CalendarIcon
} from '@heroicons/vue/24/outline';
import { uploadTempFile } from '@/services/tempFilesApi';
import type { ChatAttachment, AttachmentReference } from '@/types';

interface Props {
  disabled?: boolean;
  isLoading?: boolean;
  maxLength?: number;
  placeholder?: string;
  maxFiles?: number;
  maxFileSize?: number; // 字节
  showFileButtons?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  isLoading: false,
  maxLength: 2000,
  placeholder: '输入消息...',
  maxFiles: 5,
  maxFileSize: 10 * 1024 * 1024, // 10MB
  showFileButtons: true,
});

const emit = defineEmits<{
  send: [content: string, attachments: AttachmentReference[]];
  openKnowledge: [];
  openPartyActivity: [];
}>();

const inputContent = ref('');
const textareaRef = ref<HTMLTextAreaElement>();
const fileInputRef = ref<HTMLInputElement>();
const isComposing = ref(false);
const attachments = ref<ChatAttachment[]>([]);
const fileError = ref('');

const canSend = computed(() => {
  return !props.disabled && !props.isLoading && (inputContent.value.trim().length > 0 || hasReadyAttachments.value);
});

const hasReadyAttachments = computed(() => {
  return attachments.value.some(att => att.status === 'ready');
});

const canAddMoreFiles = computed(() => {
  return attachments.value.filter(att => att.status !== 'error').length < props.maxFiles;
});

const handleInput = () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto';
    textareaRef.value.style.height = Math.min(textareaRef.value.scrollHeight, 200) + 'px';
  }

  if (inputContent.value.length > props.maxLength) {
    inputContent.value = inputContent.value.slice(0, props.maxLength);
  }
};

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey && !isComposing.value) {
    event.preventDefault();
    handleSend();
  }
};

const handleCompositionStart = () => {
  isComposing.value = true;
};

const handleCompositionEnd = () => {
  isComposing.value = false;
};

/**
 * 触发文件选择
 */
const triggerFileInput = () => {
  fileInputRef.value?.click();
};

/**
 * 处理文件选择
 */
const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const files = Array.from(target.files || []);

  if (files.length === 0) {
    return;
  }

  // 清空 input，允许重复选择同一文件
  target.value = '';

  // 验证文件数量
  const currentFileCount = attachments.value.filter(att => att.status !== 'error').length;
  if (currentFileCount + files.length > props.maxFiles) {
    fileError.value = `最多只能上传 ${props.maxFiles} 个文件`;
    setTimeout(() => { fileError.value = ''; }, 3000);
    return;
  }

  // 验证并上传每个文件
  for (const file of files) {
    if (file.size > props.maxFileSize) {
      fileError.value = `文件 "${file.name}" 超过大小限制 (${formatFileSize(props.maxFileSize)})`;
      setTimeout(() => { fileError.value = ''; }, 3000);
      continue;
    }

    await uploadFile(file);
  }
};

/**
 * 上传单个文件
 */
const uploadFile = async (file: File) => {
  const attachmentId = `temp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

  // 添加待上传附件
  attachments.value.push({
    id: attachmentId,
    name: file.name,
    type: 'temp',
    size: file.size,
    status: 'uploading',
    uploadProgress: 0
  });

  try {
    // 调用上传 API
    const response = await uploadTempFile(file, (progress) => {
      const attachment = attachments.value.find(att => att.id === attachmentId);
      if (attachment) {
        attachment.uploadProgress = progress;
      }
    });

    // 更新为就绪状态
    const attachment = attachments.value.find(att => att.id === attachmentId);
    if (attachment) {
      attachment.id = response.temp_id;
      attachment.status = 'ready';
      attachment.uploadProgress = 100;
    }
  } catch (error) {
    // 更新为错误状态
    const attachment = attachments.value.find(att => att.id === attachmentId);
    if (attachment) {
      attachment.status = 'error';
      attachment.error = error instanceof Error ? error.message : '上传失败';
    }
  }
};

/**
 * 移除附件
 */
const removeAttachment = (attachmentId: string) => {
  const index = attachments.value.findIndex(att => att.id === attachmentId);
  if (index !== -1) {
    attachments.value.splice(index, 1);
  }
};

/**
 * 格式化文件大小
 */
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

/**
 * 获取附件类型标签
 */
const getAttachmentTypeLabel = (type: 'temp' | 'knowledge' | 'party'): string => {
  const labels = {
    temp: '本地文件',
    knowledge: '知识库',
    party: '党建活动'
  };
  return labels[type];
};

const handleSend = () => {
  const content = inputContent.value.trim();
  const readyAttachments = attachments.value
    .filter(att => att.status === 'ready')
    .map(att => ({
      id: att.id,
      type: att.type,
      name: att.name
    } as AttachmentReference));

  if ((content || readyAttachments.length > 0) && canSend.value) {
    emit('send', content, readyAttachments);
    inputContent.value = '';
    attachments.value = [];

    // 重置高度
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto';
    }
  }
};

const focus = () => {
  textareaRef.value?.focus();
};

/**
 * 添加外部附件（从知识库或党建活动选择）
 */
const addAttachment = (attachment: ChatAttachment) => {
  if (!canAddMoreFiles.value) {
    fileError.value = `最多只能上传 ${props.maxFiles} 个文件`;
    setTimeout(() => { fileError.value = ''; }, 3000);
    return;
  }
  attachments.value.push(attachment);
};

defineExpose({
  focus,
  addAttachment,
  attachments
});
</script>

<style scoped>
.chat-input-container {
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border-top: 1px solid #e0e0e0;
}

.attachments-area {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px 12px 0;
}

.attachment-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 13px;
  transition: all 0.2s;
}

.attachment-tag.attachment-error {
  border-color: #ff4d4f;
  background-color: #fff2f0;
}

.attachment-icon {
  width: 16px;
  height: 16px;
  color: #666;
  flex-shrink: 0;
}

.attachment-name {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attachment-size {
  color: #999;
  font-size: 12px;
}

.attachment-remove {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: none;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  color: #999;
  transition: all 0.2s;
  flex-shrink: 0;
}

.attachment-remove:hover:not(:disabled) {
  background-color: #ff4d4f;
  color: white;
}

.attachment-remove:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.upload-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid #999;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.attachment-progress {
  color: #1890ff;
  font-size: 12px;
}

.attachment-error-text {
  color: #ff4d4f;
  font-size: 12px;
}

.file-actions {
  display: flex;
  gap: 8px;
  padding: 12px 12px 8px;
  flex-wrap: wrap;
}

.file-action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1px solid #d0d0d0;
  border-radius: 6px;
  background-color: white;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.file-action-btn:hover:not(:disabled) {
  border-color: #C8102E;
  color: #C8102E;
  background-color: #fff5f5;
}

.file-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.hidden-file-input {
  display: none;
}

.chat-input-wrapper {
  display: flex;
  gap: 8px;
  padding: 8px 12px 12px;
}

.chat-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #d0d0d0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  outline: none;
  transition: border-color 0.2s;
  min-height: 40px;
  max-height: 200px;
  overflow-y: auto;
}

.chat-input:focus {
  border-color: #C8102E;
  box-shadow: 0 0 0 2px rgba(200, 16, 46, 0.1);
}

.chat-input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.chat-input::placeholder {
  color: #999;
}

.send-button {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: linear-gradient(135deg, #C8102E 0%, #8B0000 100%);
  color: white;
}

.send-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #a00d25 0%, #6d0000 100%);
  box-shadow: 0 4px 12px rgba(200, 16, 46, 0.3);
  transform: scale(1.05);
}

.send-button:disabled {
  background-color: #d0d0d0;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #fff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.file-error {
  padding: 8px 12px;
  color: #ff4d4f;
  font-size: 13px;
  background-color: #fff2f0;
  border-top: 1px solid #ffccc7;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.attachment-enter-active,
.attachment-leave-active {
  transition: all 0.2s ease;
}

.attachment-enter-from {
  opacity: 0;
  transform: scale(0.8);
}

.attachment-leave-to {
  opacity: 0;
  transform: scale(0.8);
}
</style>
