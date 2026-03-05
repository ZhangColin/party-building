<template>
  <div class="chat-panel">
    <!-- 消息内容区域（可滚动） -->
    <div class="messages-area">
      <!-- 欢迎语（仅在没有消息时显示） -->
      <div v-if="messages.length === 0" class="welcome-area">
        <WelcomeMessage :welcome-message="welcomeMessage" />
      </div>
      
      <!-- 消息列表 -->
      <template v-for="(message, index) in messages" :key="`msg-${index}`">
        <!-- 用户消息 -->
        <div v-if="message.role === 'user'" class="user-message-wrapper">
          <div class="user-message">
            <div class="user-message-content">{{ message.content }}</div>
          </div>
        </div>
        
        <!-- AI 消息 -->
        <div v-else class="assistant-message-wrapper">
          <!-- 生成中状态 -->
          <div v-if="message.generation_status === 'processing'" class="loading-indicator">
            <div class="loading-typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span class="loading-text">{{ getLoadingText() }}</span>
          </div>
          
          <!-- 生成失败 -->
          <div v-else-if="message.generation_status === 'failed'" class="error-message">
            <div class="error-icon">⚠️</div>
            <div class="error-content">
              <div class="error-title">出错了</div>
              <div class="error-detail">{{ message.error_message || '生成失败，请重试' }}</div>
              <button class="error-retry-btn" @click="handleRetry(message)">重试</button>
            </div>
          </div>
          
          <!-- 生成完成：根据媒体类型显示内容 -->
          <div v-else-if="message.media_content" class="media-gallery">
            <!-- 图片 -->
            <template v-if="getMediaType(message.media_content) === 'image'">
              <div class="image-gallery">
                <div 
                  v-for="(url, idx) in parseMediaUrls(message.media_content)" 
                  :key="idx"
                  class="image-item group"
                  @click="handleImageClick(message, idx)"
                >
                  <img 
                    :src="url" 
                    :alt="`生成的图片 ${idx + 1}`" 
                    class="generated-image"
                    @load="handleImageLoad"
                  />
                  <button class="image-download-btn" @click.stop="handleDownloadImage(url, idx)">
                    下载
                  </button>
                </div>
              </div>
            </template>
            
            <!-- 音频 -->
            <template v-else-if="getMediaType(message.media_content) === 'audio'">
              <div class="audio-gallery">
                <div 
                  v-for="(url, idx) in parseMediaUrls(message.media_content)" 
                  :key="idx"
                  class="audio-item"
                >
                  <audio controls :src="url" class="generated-audio">
                    您的浏览器不支持音频播放
                  </audio>
                  <button class="media-download-btn" @click.stop="handleDownloadMedia(url, idx, 'audio')">
                    下载
                  </button>
                </div>
              </div>
            </template>
            
            <!-- 视频 -->
            <template v-else-if="getMediaType(message.media_content) === 'video'">
              <div class="video-gallery">
                <div 
                  v-for="(url, idx) in parseMediaUrls(message.media_content)" 
                  :key="idx"
                  class="video-item"
                >
                  <video controls :src="url" class="generated-video">
                    您的浏览器不支持视频播放
                  </video>
                  <button class="media-download-btn" @click.stop="handleDownloadMedia(url, idx, 'video')">
                    下载
                  </button>
                </div>
              </div>
            </template>
          </div>
        </div>
      </template>
    </div>
    
    <!-- 输入框区域（固定在底部） -->
    <div class="input-area">
      <!-- 输入框 -->
      <ChatInput 
        placeholder="描述你想要的画面..."
        @send="handleSendMessage" 
        :disabled="isGenerating" 
      />
    </div>
    
    <!-- 图片大图查看器 -->
    <ImageLightbox
      :show="showLightbox"
      :images="lightboxImages"
      :initial-index="lightboxIndex"
      @close="closeLightbox"
      @download="handleDownloadImage"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import type { MediaMessage, MediaGenerateParams, TaskStatusResponse } from '../../types/media'
import { parseMediaContent, DEFAULT_GENERATE_PARAMS } from '../../types/media'
import { generateMedia, pollTaskStatus } from '../../services/mediaApi'
import { downloadImage } from '../../services/mediaApi'
import { ApiService } from '../../services/apiClient'
import ChatInput from '../ChatInput.vue'
import ImageLightbox from './ImageLightbox.vue'
import WelcomeMessage from '../WelcomeMessage.vue'

const props = defineProps<{
  toolId: string
  toolName: string
  welcomeMessage: string
  sessionId?: string  // 外部传入的会话ID（用于加载历史会话）
}>()

const emit = defineEmits<{
  'session-created': [sessionId: string]
  'title-generated': [sessionId: string]
}>()

// 状态
const sessionId = ref<string>('')
const messages = ref<MediaMessage[]>([])
const isGenerating = ref(false)
const currentTaskId = ref<string>('')
// 使用默认参数（GLM不支持自定义这些参数）
const generateParams = ref<MediaGenerateParams>({ ...DEFAULT_GENERATE_PARAMS })

// Lightbox状态
const showLightbox = ref(false)
const lightboxImages = ref<string[]>([])
const lightboxIndex = ref(0)

// 方法
async function handleSendMessage(prompt: string) {
  await handleSend(prompt, generateParams.value)
}

async function handleSend(prompt: string, params: MediaGenerateParams) {
  console.log(`[handleSend] 开始发送 - isGenerating: ${isGenerating.value}, prompt: ${prompt}`)
  
  if (isGenerating.value || !prompt.trim()) {
    console.log(`[handleSend] 跳过发送 - isGenerating: ${isGenerating.value}, prompt empty: ${!prompt.trim()}`)
    return
  }
  
  try {
    isGenerating.value = true
    console.log(`[handleSend] 设置 isGenerating = true`)
    
    // 1. 添加用户消息到界面
    const userMessage: MediaMessage = {
      message_id: `temp_${Date.now()}`,
      role: 'user',
      content: prompt,
      created_at: new Date().toISOString()
    }
    messages.value.push(userMessage)
    
    // 2. 添加AI消息占位（生成中状态）
    const aiMessage: MediaMessage = {
      message_id: `temp_ai_${Date.now()}`,
      role: 'assistant',
      content: '',
      generation_status: 'processing',
      progress: 0
    }
    messages.value.push(aiMessage)
    
    await scrollToBottom()
    
    // 3. 调用生成API
    const response = await generateMedia(props.toolId, {
      message: prompt,
      session_id: sessionId.value || undefined,
      size: params.size,
      count: params.count,
      style: params.style
    })
    
    // 更新session_id
    const isNewSession = !sessionId.value
    if (isNewSession) {
      sessionId.value = response.session_id
      // 通知父组件会话已创建（后端会自动生成标题）
      emit('session-created', response.session_id)
      emit('title-generated', response.session_id)
    }
    
    // 更新消息ID和任务ID
    aiMessage.message_id = response.message_id
    aiMessage.task_id = response.task_id
    currentTaskId.value = response.task_id
    
    // 4. 检查是否需要轮询（同步模式直接返回结果，异步模式需要轮询）
    let result: TaskStatusResponse
    
    if (response.status === 'completed') {
      // 同步模式：后端直接返回了完成状态，不需要轮询
      console.log('同步生成完成，无需轮询')
      result = {
        task_id: response.task_id,
        status: 'completed',
        media_urls: response.media_urls,
        content_type: response.content_type,
        metadata: {}
      }
    } else {
      // 异步模式：需要轮询任务状态
      console.log(`[handleSend] 异步生成，开始轮询 - task_id: ${response.task_id}`)
      result = await pollTaskStatus(
        response.task_id,
        (status: TaskStatusResponse) => {
          // 更新进度
          console.log(`[handleSend] 轮询进度回调 - status: ${status.status}, progress: ${status.progress}`)
          aiMessage.progress = status.progress
          scrollToBottom()
        }
      )
      console.log(`[handleSend] 轮询结束 - 最终状态: ${result.status}`)
    }
    
    // 5. 处理结果
    console.log(`[handleSend] 处理结果 - status: ${result.status}, content_type: ${result.content_type}, media_urls: ${result.media_urls}`)
    
    if (result.status === 'completed') {
      // 生成成功
      const mediaContent = {
        content_type: result.content_type!,
        media_urls: result.media_urls!,
        metadata: result.metadata
      }
      
      console.log(`[handleSend] 生成成功，更新消息 - mediaContent:`, mediaContent)
      aiMessage.media_content = JSON.stringify(mediaContent)
      aiMessage.generation_status = 'completed'
      aiMessage.created_at = new Date().toISOString()
      
      await scrollToBottom()
      
    } else if (result.status === 'failed') {
      // 生成失败
      console.log(`[handleSend] 生成失败 - error: ${result.error_message}`)
      aiMessage.generation_status = 'failed'
      aiMessage.error_message = result.error_message || '生成失败，请重试'
    }
    
  } catch (error: any) {
    console.error('[handleSend] 生成失败:', error)
    
    // 更新最后一条AI消息为失败状态
    const lastAiMessage = messages.value[messages.value.length - 1]
    if (lastAiMessage && lastAiMessage.role === 'assistant') {
      lastAiMessage.generation_status = 'failed'
      lastAiMessage.error_message = error.message || '生成失败，请重试'
    }
    
  } finally {
    console.log(`[handleSend] 完成，设置 isGenerating = false`)
    isGenerating.value = false
  }
}

async function handleRetry(message: MediaMessage) {
  if (isGenerating.value) {
    return
  }
  
  // 找到对应的用户消息
  const messageIndex = messages.value.findIndex(m => m.message_id === message.message_id)
  if (messageIndex === -1 || messageIndex === 0) {
    return
  }
  
  const userMessage = messages.value[messageIndex - 1]
  if (!userMessage || userMessage.role !== 'user') {
    return
  }
  
  // 重置AI消息状态
  message.generation_status = 'processing'
  message.progress = 0
  message.error_message = undefined
  
  try {
    isGenerating.value = true
    
    await scrollToBottom()
    
    // 调用生成API
    const response = await generateMedia(props.toolId, {
      message: userMessage.content,
      session_id: sessionId.value || undefined,
      size: generateParams.value.size,
      count: generateParams.value.count,
      style: generateParams.value.style
    })
    
    // 更新任务ID
    message.task_id = response.task_id
    currentTaskId.value = response.task_id
    
    // 开始轮询
    const result = await pollTaskStatus(
      response.task_id,
      (status: TaskStatusResponse) => {
        message.progress = status.progress
      }
    )
    
    if (result.status === 'completed') {
      const mediaContent = {
        content_type: result.content_type!,
        media_urls: result.media_urls!,
        metadata: result.metadata
      }
      
      message.media_content = JSON.stringify(mediaContent)
      message.generation_status = 'completed'
      message.created_at = new Date().toISOString()
      
      await scrollToBottom()
      
    } else if (result.status === 'failed') {
      message.generation_status = 'failed'
      message.error_message = result.error_message || '生成失败，请重试'
    }
    
  } catch (error: any) {
    console.error('重试失败:', error)
    message.generation_status = 'failed'
    message.error_message = error.message || '生成失败，请重试'
  } finally {
    isGenerating.value = false
  }
}

function handleImageClick(message: MediaMessage, index: number) {
  const urls = parseMediaUrls(message.media_content)
  if (urls.length === 0) return
  
  lightboxImages.value = urls
  lightboxIndex.value = index
  showLightbox.value = true
}

async function handleDownloadImage(url: string, index: number) {
  try {
    await downloadImage(url, `generated-image-${Date.now()}-${index + 1}.png`)
  } catch (error) {
    console.error('下载失败:', error)
    alert('下载失败，请重试')
  }
}

async function handleDownloadMedia(url: string, _index: number, _type: string) {
  try {
    // 直接在新标签页打开，让浏览器处理下载
    window.open(url, '_blank')
  } catch (error) {
    console.error('下载失败:', error)
    alert('下载失败，请重试')
  }
}

function getMediaType(mediaContent?: string): string {
  if (!mediaContent) return 'unknown'
  try {
    const parsed = parseMediaContent(mediaContent)
    return parsed?.contentType || 'unknown'
  } catch {
    return 'unknown'
  }
}

function closeLightbox() {
  showLightbox.value = false
}

async function scrollToBottom() {
  await nextTick()
  const messagesArea = document.querySelector('.messages-area')
  if (messagesArea) {
    messagesArea.scrollTop = messagesArea.scrollHeight
  }
}

// 图片加载完成后滚动到底部（确保图片高度已计算）
function handleImageLoad() {
  scrollToBottom()
}

function parseMediaUrls(mediaContent?: string): string[] {
  if (!mediaContent) return []
  try {
    const parsed = parseMediaContent(mediaContent)
    return parsed?.mediaUrls || []
  } catch {
    return []
  }
}

function getLoadingText(): string {
  // 根据工具ID推断媒体类型并返回对应的加载文案
  const toolId = props.toolId.toLowerCase()
  if (toolId.includes('image') || toolId.includes('图')) {
    return 'AI 正在生成图片...'
  } else if (toolId.includes('audio') || toolId.includes('音频')) {
    return 'AI 正在生成音频...'
  } else if (toolId.includes('video') || toolId.includes('视频')) {
    return 'AI 正在生成视频...'
  } else {
    return 'AI 正在生成内容...'
  }
}

// 加载历史消息
async function loadHistoryMessages(sessionIdParam: string) {
  try {
    const response = await ApiService.getSessionDetail(sessionIdParam)
    
    // 转换为 MediaMessage 格式
    messages.value = response.messages.map(msg => ({
      message_id: msg.message_id || undefined,
      session_id: msg.session_id || undefined,
      role: msg.role,
      content: msg.content,
      media_content: msg.media_content || undefined,
      created_at: msg.created_at || msg.timestamp,
      generation_status: msg.media_content ? 'completed' : undefined
    }))
    
    sessionId.value = sessionIdParam
    await scrollToBottom()
    
  } catch (error) {
    console.error('加载历史消息失败:', error)
  }
}

// 监听外部传入的 sessionId
watch(() => props.sessionId, (newSessionId) => {
  if (newSessionId && newSessionId !== sessionId.value) {
    // 外部传入了新的会话ID，加载历史消息
    loadHistoryMessages(newSessionId)
  } else if (!newSessionId) {
    // 外部清空了会话ID，清空消息
    sessionId.value = ''
    messages.value = []
  }
}, { immediate: true })

// 生命周期
onMounted(() => {
  // 如果外部传入了 sessionId，会在 watch 中加载
})
</script>

<style scoped>
.chat-panel {
  @apply flex flex-col h-full overflow-hidden;
}

/* 消息内容区域（可滚动） - 与ChatPanel一致 */
.messages-area {
  @apply flex-1 overflow-y-auto;
  padding: 24px 32px;
  background: white;
}

/* 输入框区域（固定在底部） - 与ChatPanel一致 */
.input-area {
  @apply py-6 px-6 border-t border-gray-200 flex-shrink-0 bg-white;
  box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.04);
}


/* 欢迎语区域 */
.welcome-area {
  @apply flex items-center justify-center;
  min-height: 400px;
}

/* 用户消息样式（与ChatPanel完全一致） */
.user-message-wrapper {
  @apply flex justify-end mb-8 relative;
}

.user-message {
  @apply flex justify-end;
  min-width: 0;
}

.user-message-content {
  display: flex;
  justify-content: flex-end;
  font-size: 14px;
  line-height: 1.625;
  padding: 12px 16px;
  border-radius: 16px;
  color: white;
  /* 党建主题：用户消息气泡样式 */
  background: linear-gradient(135deg, #C8102E 0%, #8B0000 100%);
  word-break: normal;
  overflow-wrap: break-word;
  white-space: pre-line;
  width: fit-content;
  max-width: clamp(200px, 83.33%, 900px);
  display: inline-block;
  flex-shrink: 0;
}

/* AI消息样式（与ChatPanel一致） */
.assistant-message-wrapper {
  @apply w-full mb-8 relative;
}

/* 加载指示器（与ChatPanel一致） */
.loading-indicator {
  @apply flex items-center gap-3 mb-4;
}

.loading-typing {
  @apply flex gap-1;
}

.loading-typing span {
  @apply w-2 h-2 bg-gray-400 rounded-full;
  animation: typing 1.4s infinite;
}

.loading-typing span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-typing span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.loading-text {
  @apply text-sm text-gray-500;
}

/* 错误消息样式（与ChatPanel一致） */
.error-message {
  @apply flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg mb-4;
}

.error-icon {
  @apply text-2xl flex-shrink-0;
}

.error-content {
  @apply flex-1;
}

.error-title {
  @apply text-sm font-semibold text-red-800 mb-1;
}

.error-detail {
  @apply text-sm text-red-600 mb-3;
}

.error-retry-btn {
  padding: 8px 16px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  border-radius: 6px;
  transition: all 0.2s;
  /* 党建主题：主按钮样式 */
  background: linear-gradient(135deg, #C8102E 0%, #8B0000 100%);
  border: none;
  cursor: pointer;
}

/* 图片展示区域 */
.image-gallery {
  @apply grid gap-4 mb-4;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  max-width: 100%;
}

.image-item {
  @apply relative rounded-lg overflow-hidden border border-gray-200 hover:border-gray-300 transition-colors cursor-pointer;
  background: #f9fafb;
}

.generated-image {
  @apply w-full h-auto;
  display: block;
}

.image-download-btn {
  @apply absolute bottom-2 right-2 px-3 py-1.5 bg-black bg-opacity-70 text-white text-xs rounded-md opacity-0 group-hover:opacity-100 transition-opacity hover:bg-opacity-90;
}

/* 音频展示区域 */
.audio-gallery {
  @apply flex flex-col gap-4 mb-4;
  max-width: 100%;
}

.audio-item {
  @apply flex items-center gap-3 p-4 rounded-lg border border-gray-200 bg-gray-50;
}

.generated-audio {
  @apply flex-1;
  max-width: 600px;
}

/* 视频展示区域 */
.video-gallery {
  @apply grid gap-4 mb-4;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  max-width: 100%;
}

.video-item {
  @apply relative rounded-lg overflow-hidden border border-gray-200 bg-gray-50;
}

.generated-video {
  @apply w-full h-auto;
  display: block;
  max-height: 500px;
}

/* 通用下载按钮 */
.media-download-btn {
  padding: 6px 12px;
  color: white;
  font-size: 12px;
  border-radius: 6px;
  transition: all 0.2s;
  cursor: pointer;
  border: none;
  /* 党建主题：主按钮样式 */
  background: linear-gradient(135deg, #C8102E 0%, #8B0000 100%);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .image-gallery {
    @apply grid-cols-1;
  }
  
  .video-gallery {
    @apply grid-cols-1;
  }
  
  .audio-item {
    @apply flex-col items-stretch;
  }
  
  .generated-audio {
    @apply w-full max-w-full;
  }
}
</style>
