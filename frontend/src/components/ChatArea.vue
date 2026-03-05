<template>
  <div class="chat-area" :class="{ 'with-preview': showPreview, 'conversation-collapsed': conversationListCollapsed }">
    <!-- 左侧：历史对话列表 -->
    <ConversationList 
      ref="conversationListRef"
      :tool-id="toolId"
      :collapsed="conversationListCollapsed"
      class="conversation-list" 
      :class="{ collapsed: conversationListCollapsed }"
      @conversation-change="handleConversationChange"
      @new-conversation="handleNewConversation"
    />
    
    
    <!-- 中间：当前对话区域 -->
    <ChatPanel
      ref="chatPanelRef"
      :tool-id="toolId"
      :messages="sessionStore.messages"
      :welcome-message="welcomeMessage"
      :session-id="currentSessionId ?? undefined"
      :conversation-collapsed="conversationListCollapsed"
      :error="sessionStore.error ?? undefined"
      :is-loading="sessionStore.loading"
      class="chat-panel"
      :style="showPreview ? { width: chatPanelWidth + 'px' } : {}"
      @send="handleSendMessage"
      @retry="handleRetry"
      @preview="openPreview"
    />
    
    <!-- 可拖拽的分隔条 -->
    <div 
      v-if="showPreview"
      class="resizer"
      @mousedown="startResize"
    >
      <div class="resizer-handle"></div>
    </div>
    
    <!-- 右侧：预览区域 -->
    <PreviewPanel
      v-if="showPreview"
      :artifact="currentArtifact"
      class="preview-panel"
      @close-preview="closePreview"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import ConversationList from './ConversationList.vue'
import ChatPanel from './ChatPanel.vue'
import PreviewPanel from './PreviewPanel.vue'
import { useSessionStore } from '../stores/sessionStore'
import type { Artifact, AttachmentReference } from '../types'

const props = defineProps<{
  toolId?: string
  welcomeMessage?: string
}>()

const sessionStore = useSessionStore()
const currentSessionId = ref<string | null>(null)
const showPreview = ref(false)
const currentArtifact = ref<Artifact | null>(null)
const conversationListCollapsed = ref(false)
const conversationListRef = ref<InstanceType<typeof ConversationList> | null>(null)
const chatPanelRef = ref<InstanceType<typeof ChatPanel> | null>(null)

// 拖拽相关
const chatPanelWidth = ref<number>(0)
const isResizing = ref(false)
const containerWidth = ref<number>(0)

// function toggleConversationList() {
//   conversationListCollapsed.value = !conversationListCollapsed.value
// }

// 监听工具切换，清空当前会话
watch(() => props.toolId, (newToolId) => {
  console.log('[ChatArea] toolId changed to:', newToolId)
  if (newToolId) {
    currentSessionId.value = null
    showPreview.value = false
    currentArtifact.value = null
    sessionStore.initTool(newToolId)
  }
}, { immediate: true })

// 监听 sessionStore 的 sessionId 变化（新会话创建）
watch(() => sessionStore.sessionId, async (newId, oldId) => {
  if (newId && !oldId) {
    // 新会话创建了
    console.log('检测到新会话创建:', newId)
    // 更新当前会话ID（但不刷新列表，等待标题生成完成）
    currentSessionId.value = newId
  }
})

// 监听标题生成完成，然后刷新会话列表
watch(() => sessionStore.titleGeneratedSessionId, async (generatedSessionId) => {
  if (generatedSessionId && conversationListRef.value) {
    console.log('检测到标题生成完成，刷新会话列表:', generatedSessionId)
    // 刷新会话列表
    await conversationListRef.value.loadConversations()
    // 设置为当前选中的会话
    conversationListRef.value.setCurrentConversation(generatedSessionId)
    // 清除标记，避免重复刷新
    sessionStore.titleGeneratedSessionId = null
  }
})

function handleConversationChange(sessionId: string) {
  currentSessionId.value = sessionId
  showPreview.value = false
  currentArtifact.value = null
}

function handleNewConversation() {
  currentSessionId.value = null
  showPreview.value = false
  currentArtifact.value = null
  sessionStore.clearSession()
}

async function handleSendMessage(content: string, attachments?: AttachmentReference[]) {
  console.log('[ChatArea] handleSendMessage called with:', content, 'attachments:', attachments)

  // 安全检查：如果toolId为空，尝试从props重新初始化
  if (!sessionStore.toolId && props.toolId) {
    console.warn('[ChatArea] toolId is empty, re-initializing with props.toolId:', props.toolId)
    sessionStore.initTool(props.toolId)
  }

  // 双重检查：如果还是无法初始化toolId，抛出明确的错误
  if (!sessionStore.toolId) {
    const errorMsg = '无法发送消息：工具未初始化。请选择一个工具后重试。'
    console.error('[ChatArea]', errorMsg, {
      sessionStoreToolId: sessionStore.toolId,
      propsToolId: props.toolId
    })
    sessionStore.error = errorMsg
    throw new Error(errorMsg)
  }

  try {
    await sessionStore.sendMessage(content, attachments)
    console.log('[ChatArea] Message sent successfully')
  } catch (err) {
    console.error('[ChatArea] Failed to send message:', err)
    // 如果是"工具未初始化"错误，提供更友好的提示
    if (err instanceof Error && err.message.includes('工具未初始化')) {
      sessionStore.error = '工具初始化失败，请刷新页面重试'
    }
    // 错误已记录到 sessionStore.error，由 ChatPanel 显示给用户
  }
}

async function handleRetry() {
  console.log('[ChatArea] Retry requested')
  // Clear the error and let the user resend
  sessionStore.error = null
}

function openPreview(artifact: Artifact) {
  currentArtifact.value = artifact
  showPreview.value = true
  // 打开预览时，初始化聊天面板宽度为 1/3
  updateContainerWidth()
  chatPanelWidth.value = containerWidth.value / 3
}

function closePreview() {
  showPreview.value = false
  currentArtifact.value = null
}

// 拖拽调整宽度
function startResize(e: MouseEvent) {
  isResizing.value = true
  e.preventDefault()
  
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopResize)
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

function handleResize(e: MouseEvent) {
  if (!isResizing.value) return
  
  const chatArea = document.querySelector('.chat-area') as HTMLElement
  if (!chatArea) return
  
  const rect = chatArea.getBoundingClientRect()
  const conversationList = document.querySelector('.conversation-list') as HTMLElement
  const conversationListWidth = conversationList?.offsetWidth || 0
  
  // 计算新的聊天面板宽度（相对于容器左边）
  let newWidth = e.clientX - rect.left - conversationListWidth
  
  // 限制最小和最大宽度
  const minChatWidth = 300 // 最小 300px
  const maxChatWidth = containerWidth.value - 400 // 至少给预览区留 400px
  
  newWidth = Math.max(minChatWidth, Math.min(newWidth, maxChatWidth))
  
  chatPanelWidth.value = newWidth
}

function stopResize() {
  isResizing.value = false
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}

function updateContainerWidth() {
  const chatArea = document.querySelector('.chat-area') as HTMLElement
  if (chatArea) {
    const conversationList = document.querySelector('.conversation-list') as HTMLElement
    const conversationListWidth = conversationList?.offsetWidth || 0
    containerWidth.value = chatArea.offsetWidth - conversationListWidth
  }
}

// 监听窗口大小变化
onMounted(() => {
  window.addEventListener('resize', updateContainerWidth)
  updateContainerWidth()

  // 监听代码块预览事件
  window.addEventListener('codeblock-preview', handleCodeBlockPreview as EventListener)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateContainerWidth)
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)

  // 移除代码块预览事件监听
  window.removeEventListener('codeblock-preview', handleCodeBlockPreview as EventListener)
})

// 处理代码块预览事件
function handleCodeBlockPreview(event: Event) {
  const customEvent = event as CustomEvent<{ artifact: Artifact }>
  console.log('[ChatArea] 收到代码块预览事件:', customEvent.detail.artifact)
  openPreview(customEvent.detail.artifact)
}

// 监听工具切换或会话切换，关闭预览
watch(() => props.toolId, () => {
  showPreview.value = false
  currentArtifact.value = null
})

watch(() => currentSessionId.value, () => {
  showPreview.value = false
  currentArtifact.value = null
})

// 监听流式输出，自动滚动到底部
watch(() => sessionStore.messages.length, async () => {
  // 消息数量变化时滚动（新消息添加）
  await nextTick()
  chatPanelRef.value?.scrollToBottom()
}, { flush: 'post' })

// 监听最后一条消息的内容变化（流式输出）
watch(() => {
  const messages = sessionStore.messages
  if (messages.length === 0) return ''
  const lastMsg = messages[messages.length - 1]
  return lastMsg?.content || ''
}, async () => {
  // 最后一条消息内容变化时滚动（流式输出）
  await nextTick()
  chatPanelRef.value?.scrollToBottom()
}, { flush: 'post' })
</script>

<style scoped>
.chat-area {
  @apply flex h-full overflow-hidden bg-white;
  /* 层级2：内容层 - 白色背景，轻微阴影 */
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.04);
  position: relative;
}

.chat-panel {
  flex: 1;
  min-width: 0;
  transition: padding-left 0.3s ease;
  /* 层级2：内容层 - 白色背景 */
  position: relative;
  overflow: hidden;
}

/* 当显示预览时，聊天面板不使用 flex，而是固定宽度 */
.chat-area.with-preview .chat-panel {
  flex: 0 0 auto;
}

/* 当历史列表收起时，增加左边距，避免图标压到文字 */
.chat-area.conversation-collapsed .chat-panel :deep(.messages-area) {
  padding-left: 80px !important;
}

.chat-area.conversation-collapsed .chat-panel :deep(.input-area) {
  padding-left: 80px !important;
}

/* 可拖拽的分隔条 */
.resizer {
  @apply flex-shrink-0 bg-gray-200 cursor-col-resize relative;
  width: 4px;
  transition: background-color 0.2s;
  z-index: 10;
}

.resizer:hover {
  @apply bg-primary-400;
}

.resizer-handle {
  @apply absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-gray-400 rounded-full;
  width: 4px;
  height: 40px;
  pointer-events: none;
  transition: background-color 0.2s;
}

.resizer:hover .resizer-handle {
  @apply bg-primary-500;
}

/* 预览面板：flex 布局 */
.preview-panel {
  @apply flex flex-col bg-white overflow-hidden;
  flex: 1;
  min-width: 400px;
  /* 层级2：内容层 - 白色背景 */
}


/* 平板端响应式（768px - 1023px） */
@media (min-width: 768px) and (max-width: 1023px) {
  .preview-panel {
    min-width: 350px;
  }
  
  .resizer {
    width: 3px;
  }
}

/* 移动端响应式（<768px） */
@media (max-width: 767px) {
  .conversation-list {
    width: 280px;
  }
  
  /* 移动端：隐藏聊天面板，预览全屏 */
  .chat-area.with-preview .chat-panel {
    display: none;
  }
  
  .chat-area.with-preview .resizer {
    display: none;
  }
  
  .preview-panel {
    flex: 1;
    min-width: 100%;
  }
}
</style>

