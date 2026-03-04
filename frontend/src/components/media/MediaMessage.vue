<template>
  <div class="media-message" :class="`role-${message.role}`">
    <div class="message-bubble">
      <!-- 用户消息：显示提示词 -->
      <div v-if="message.role === 'user'" class="user-message">
        <div class="message-header">
          <span class="user-label">你</span>
          <span class="message-time">{{ formattedTime }}</span>
        </div>
        <p class="message-content">{{ message.content }}</p>
      </div>
      
      <!-- AI消息：显示生成状态或图片 -->
      <div v-else class="ai-message">
        <div class="message-header">
          <span class="ai-label">AI</span>
          <span class="message-time">{{ formattedTime }}</span>
        </div>
        
        <!-- 生成中状态 -->
        <GeneratingIndicator 
          v-if="message.generation_status === 'processing'"
          :progress="message.progress"
        />
        
        <!-- 生成失败 -->
        <div v-else-if="message.generation_status === 'failed'" class="error-state">
          <div class="error-icon">⚠️</div>
          <p class="error-message">{{ message.error_message || '生成失败' }}</p>
          <button class="retry-button" @click="handleRetry">
            重试
          </button>
        </div>
        
        <!-- 生成完成：显示图片 -->
        <ImageGallery 
          v-else-if="parsedMedia"
          :images="parsedMedia.mediaUrls"
          @click-image="handleImageClick"
          @download="handleDownload"
        />
        
        <!-- 无内容 -->
        <div v-else class="empty-state">
          <p class="empty-text">暂无内容</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { MediaMessage as MediaMessageType } from '../../types/media'
import { parseMediaContent } from '../../types/media'
import GeneratingIndicator from './GeneratingIndicator.vue'
import ImageGallery from './ImageGallery.vue'

const props = defineProps<{
  message: MediaMessageType
}>()

const emit = defineEmits<{
  retry: []
  clickImage: [index: number]
  download: [url: string, index: number]
}>()

// 解析多模态内容
const parsedMedia = computed(() => {
  return parseMediaContent(props.message.media_content)
})

// 格式化时间
const formattedTime = computed(() => {
  if (!props.message.created_at) {
    return ''
  }
  
  try {
    const date = new Date(props.message.created_at)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    // 1分钟内显示"刚刚"
    if (diff < 60000) {
      return '刚刚'
    }
    
    // 1小时内显示"X分钟前"
    if (diff < 3600000) {
      return `${Math.floor(diff / 60000)}分钟前`
    }
    
    // 24小时内显示"X小时前"
    if (diff < 86400000) {
      return `${Math.floor(diff / 3600000)}小时前`
    }
    
    // 否则显示具体时间
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return ''
  }
})

function handleRetry() {
  emit('retry')
}

function handleImageClick(index: number) {
  emit('clickImage', index)
}

function handleDownload(url: string, index: number) {
  emit('download', url, index)
}
</script>

<style scoped>
.media-message {
  margin-bottom: 20px;
  display: flex;
}

.role-user {
  justify-content: flex-end;
}

.role-assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 80%;
  min-width: 200px;
}

/* 消息头部 */
.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.user-label,
.ai-label {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
}

.user-label {
  background: #667eea;
  color: white;
}

.ai-label {
  background: #f3f4f6;
  color: #1f2937;
}

.message-time {
  font-size: 12px;
  color: #9ca3af;
}

/* 用户消息内容 */
.user-message .message-content {
  background: #667eea;
  color: white;
  padding: 12px 16px;
  border-radius: 16px;
  border-top-right-radius: 4px;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* AI消息内容区 */
.ai-message {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  border-top-left-radius: 4px;
  padding: 16px;
}

/* 错误状态 */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
  text-align: center;
}

.error-icon {
  font-size: 32px;
}

.error-message {
  color: #ef4444;
  font-size: 14px;
  margin: 0;
}

.retry-button {
  padding: 8px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.retry-button:hover {
  background: #5568d3;
  transform: translateY(-1px);
}

/* 空状态 */
.empty-state {
  padding: 20px;
  text-align: center;
}

.empty-text {
  color: #9ca3af;
  font-size: 14px;
  margin: 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .message-bubble {
    max-width: 90%;
  }
}
</style>
