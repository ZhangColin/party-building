<template>
  <div class="conversation-list" :class="{ collapsed: isCollapsed }">
    <div v-if="!isCollapsed" class="conversation-header">
      <button class="new-conversation-btn" @click="handleNewConversation">
        + 新建对话
      </button>
    </div>
    
    <!-- 收起/展开按钮 - 在布局层级 -->
    <button 
      class="collapse-button" 
      :class="{ 'collapsed': isCollapsed }"
      @click="toggleCollapse"
    >
      <ChevronLeftIcon v-if="!isCollapsed" class="w-4 h-4" />
      <ChatBubbleLeftRightIcon v-else class="w-4 h-4" />
    </button>
    <div v-if="!isCollapsed" class="conversation-items">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <span class="loading-text">加载对话列表...</span>
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="error-state">
        <span class="error-text">{{ error }}</span>
      </div>
      
      <!-- 空状态 -->
      <div v-else-if="!conversations || conversations.length === 0" class="empty-state">
        <span class="empty-text">暂无对话</span>
      </div>
      
      <!-- 对话列表 -->
      <template v-else>
        <div
          v-for="conversation in (conversations || [])"
          :key="conversation.session_id"
        :class="['conversation-item', { active: currentConversationId === conversation.session_id }]"
        @mouseenter="hoveredSessionId = conversation.session_id"
        @mouseleave="hoveredSessionId = null"
      >
        <!-- 编辑模式 -->
        <input
          v-if="editingSessionId === conversation.session_id"
          v-model="editingTitle"
          class="conversation-title-input"
          @blur="handleSaveTitle(conversation.session_id)"
          @keyup.enter="handleSaveTitle(conversation.session_id)"
          @keyup.esc="handleCancelEdit"
          ref="(el) => { if (el) titleInputRef = el as HTMLInputElement }"
        />
        <!-- 显示模式 -->
        <div v-else class="conversation-content" @click="handleConversationClick(conversation.session_id)">
        <div class="conversation-title">{{ conversation.title }}</div>
          <div class="conversation-time">{{ formatTime(conversation.updated_at) }}</div>
        </div>
        <!-- 操作按钮（hover 时显示） -->
        <div v-if="hoveredSessionId === conversation.session_id && editingSessionId !== conversation.session_id" class="conversation-actions" @click.stop>
          <button class="action-btn edit-btn" @click="handleStartEdit(conversation)" title="编辑标题">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button class="action-btn delete-btn" @click="handleDeleteClick(conversation)" title="删除对话">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
      </template>
    </div>

    <!-- 删除确认对话框 -->
    <div v-if="deletingSession" class="delete-confirm-overlay" @click.self="handleCancelDelete">
      <div class="delete-confirm-dialog">
        <div class="delete-confirm-title">确认删除</div>
        <div class="delete-confirm-message">确定要删除对话 "{{ deletingSession.title }}" 吗？此操作不可恢复。</div>
        <div class="delete-confirm-actions">
          <button class="confirm-btn cancel-btn" @click="handleCancelDelete">取消</button>
          <button class="confirm-btn delete-confirm-btn" @click="handleConfirmDelete">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { ChevronLeftIcon, ChatBubbleLeftRightIcon } from '@heroicons/vue/24/outline'
import { ApiService } from '../services/apiClient'
import type { ConversationListItem } from '../types'

const props = defineProps<{
  toolId?: string
  collapsed?: boolean
}>()

const isCollapsed = ref(props.collapsed ?? false)

// 同步外部传入的 collapsed 状态
watch(() => props.collapsed, (newVal) => {
  if (newVal !== undefined) {
    isCollapsed.value = newVal
  }
})

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
}

const emit = defineEmits<{
  'conversation-change': [sessionId: string]
  'new-conversation': []
}>()

const conversations = ref<ConversationListItem[]>([])
const currentConversationId = ref<string | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const hoveredSessionId = ref<string | null>(null)
const editingSessionId = ref<string | null>(null)
const editingTitle = ref('')
const titleInputRef = ref<HTMLInputElement | null>(null)
const deletingSession = ref<ConversationListItem | null>(null)

// 加载历史对话列表
async function loadConversations() {
  if (!props.toolId) {
    conversations.value = []
    return
  }

  loading.value = true
  error.value = null

  try {
    const response = await ApiService.getConversations(props.toolId)
    console.log('[ConversationList] Conversations response:', response)
    if (!response || !response.conversations) {
      console.error('[ConversationList] Invalid response:', response)
      conversations.value = []
    } else {
      conversations.value = response.conversations
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载对话列表失败'
    console.error('加载对话列表失败:', err)
  } finally {
    loading.value = false
  }
}

// 监听工具切换，重新加载对话列表
watch(() => props.toolId, (newToolId) => {
  if (newToolId) {
    currentConversationId.value = null
    loadConversations()
  } else {
    conversations.value = []
  }
}, { immediate: true })

function handleConversationClick(sessionId: string) {
  currentConversationId.value = sessionId
  emit('conversation-change', sessionId)
}

function handleNewConversation() {
  currentConversationId.value = null
  emit('new-conversation')
}

// 开始编辑标题
async function handleStartEdit(conversation: ConversationListItem) {
  editingSessionId.value = conversation.session_id
  editingTitle.value = conversation.title
  await nextTick()
  titleInputRef.value?.focus()
  titleInputRef.value?.select()
}

// 保存标题
async function handleSaveTitle(sessionId: string) {
  if (editingSessionId.value !== sessionId) return
  
  const newTitle = editingTitle.value.trim()
  if (!newTitle) {
    handleCancelEdit()
    return
  }
  
  // 如果标题没有变化，直接取消编辑
  const conversation = conversations.value.find(c => c.session_id === sessionId)
  if (conversation && conversation.title === newTitle) {
    handleCancelEdit()
    return
  }
  
  try {
    await ApiService.updateSessionTitle(sessionId, { title: newTitle })
    // 更新本地列表
    if (conversation) {
      conversation.title = newTitle
    }
    editingSessionId.value = null
    editingTitle.value = ''
  } catch (err) {
    console.error('更新标题失败:', err)
    error.value = err instanceof Error ? err.message : '更新标题失败'
    // 恢复原标题
    if (conversation) {
      editingTitle.value = conversation.title
    }
  }
}

// 取消编辑
function handleCancelEdit() {
  editingSessionId.value = null
  editingTitle.value = ''
}

// 点击删除按钮
function handleDeleteClick(conversation: ConversationListItem) {
  deletingSession.value = conversation
}

// 暴露方法给父组件调用
defineExpose({
  loadConversations,
  setCurrentConversation: (sessionId: string) => {
    currentConversationId.value = sessionId
  }
})

// 取消删除
function handleCancelDelete() {
  deletingSession.value = null
}

// 确认删除
async function handleConfirmDelete() {
  if (!deletingSession.value) return
  
  const sessionId = deletingSession.value.session_id
  try {
    await ApiService.deleteSession(sessionId)
    // 从列表中移除
    conversations.value = conversations.value.filter(c => c.session_id !== sessionId)
    // 如果删除的是当前选中的会话，切换到新建对话状态
    if (currentConversationId.value === sessionId) {
      currentConversationId.value = null
      emit('new-conversation')
}
    deletingSession.value = null
  } catch (err) {
    console.error('删除会话失败:', err)
    error.value = err instanceof Error ? err.message : '删除会话失败'
    deletingSession.value = null
  }
}

/**
 * 格式化时间
 */
function formatTime(timestamp: string): string {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    // 今天：显示时间
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    })
  } else if (days === 1) {
    // 昨天
    return '昨天'
  } else if (days < 7) {
    // 一周内：显示星期
    return date.toLocaleDateString('zh-CN', { weekday: 'short' })
  } else {
    // 更早：显示日期
    return date.toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric',
    })
  }
}
</script>

<style scoped>
.conversation-list {
  @apply flex flex-col h-full border-r border-gray-200;
  /* 层级1：容器层 - 浅灰背景，右侧阴影 */
  background-color: theme('colors.gray.50');
  border-right-width: 1px;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.04);
  position: relative; /* 为按钮提供定位上下文 */
  transition: width 0.3s ease;
  width: 280px;
}

.conversation-list.collapsed {
  width: 0;
  overflow: visible; /* 允许按钮显示在容器外 */
  border-right: none;
}

/* 收起/展开按钮 - 在布局层级，不受 conversation-list overflow 影响 */
.collapse-button {
  @apply absolute w-8 h-8 bg-white border border-gray-200 rounded-full cursor-pointer flex items-center justify-center text-gray-500 z-30 transition-all duration-200;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  left: 264px; /* 展开时：conversation-list宽度280px - 按钮宽度的一半 */
  top: 85px; /* header高度(64px) + border(1px) + 间距(20px) = 85px，在新建会话按钮下面那条线下面一点 */
}

.collapse-button.collapsed {
  left: 8px; /* 收起时向左平移，与工具选择器按钮左右对齐 */
  /* top 保持 85px，只是向左平移 */
}

.collapse-button:hover {
  @apply bg-gray-50 text-gray-800;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.1);
}

.conversation-header {
  @apply p-4 border-b border-gray-200; /* 从p-3(12px)增加到p-4(16px)，更宽松 */
}

.new-conversation-btn {
  @apply w-full px-3 py-2.5 bg-primary-500 text-white border-none rounded-lg text-sm font-medium cursor-pointer transition-all duration-200;
  box-shadow: 0 2px 4px theme('colors.primary.500 / 0.25');
}

.new-conversation-btn:hover {
  @apply bg-primary-600;
  box-shadow: 0 4px 8px theme('colors.primary.500 / 0.35');
}

.new-conversation-btn:active {
  @apply scale-[0.98];
}

.conversation-items {
  @apply flex-1 overflow-y-auto p-3; /* 从p-2(8px)增加到p-3(12px)，更宽松 */
}

.conversation-item {
  @apply px-4 py-3 mb-2 rounded-lg transition-all duration-200 relative;
  /* 添加更柔和的hover效果 */
}

.conversation-item:hover {
  @apply bg-gray-100;
  transform: translateX(2px);
}

.conversation-item.active {
  @apply bg-primary-50 border-primary-600 pl-2.5;
  border-left-width: 3px;
  /* 激活状态添加更明显的视觉反馈 */
  box-shadow: inset 0 0 0 1px theme('colors.primary.100');
}

.conversation-content {
  @apply cursor-pointer;
}

.conversation-title {
  @apply text-sm font-medium text-gray-800 mb-1;
  line-height: 1.4;
}

.conversation-title-input {
  @apply w-full px-2 py-1 text-sm font-medium text-gray-800 border border-primary-500 rounded focus:outline-none focus:ring-2 focus:ring-primary-500;
  background-color: white;
}

.conversation-time {
  @apply text-xs text-gray-400;
  line-height: 1.4;
}

.conversation-actions {
  @apply absolute right-2 top-1/2 transform -translate-y-1/2 flex gap-1;
}

.action-btn {
  @apply w-6 h-6 flex items-center justify-center rounded text-gray-400 hover:text-gray-600 hover:bg-gray-200 transition-colors duration-200;
}

.action-btn.edit-btn:hover {
  @apply text-blue-600 hover:bg-blue-50;
}

.action-btn.delete-btn:hover {
  @apply text-red-600 hover:bg-red-50;
}

.delete-confirm-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50;
}

.delete-confirm-dialog {
  @apply bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4;
}

.delete-confirm-title {
  @apply text-lg font-semibold text-gray-900 mb-2;
}

.delete-confirm-message {
  @apply text-sm text-gray-600 mb-6;
}

.delete-confirm-actions {
  @apply flex justify-end gap-3;
}

.confirm-btn {
  @apply px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200;
}

.cancel-btn {
  @apply bg-gray-100 text-gray-700 hover:bg-gray-200;
}

.delete-confirm-btn {
  @apply bg-red-500 text-white hover:bg-red-600;
}

.loading-state,
.error-state,
.empty-state {
  @apply flex flex-col items-center justify-center py-8;
}

.loading-spinner {
  @apply w-6 h-6 border-[3px] border-gray-200 border-t-primary-500 rounded-full animate-spin mb-2;
}

.loading-text,
.error-text,
.empty-text {
  @apply text-sm text-gray-500;
}

.error-text {
  @apply text-red-500;
}

/* 平板端响应式（768px - 1023px） */
@media (min-width: 768px) and (max-width: 1023px) {
  .conversation-list {
    width: 200px;
  }
  
  .conversation-list.collapsed {
    width: 0;
  }
  
  .collapse-button {
    left: 184px; /* 展开时：200px - 8px */
    top: 70px; /* 平板端：header高度(52px) + border(1px) + 间距(17px) = 70px */
  }
  
  .collapse-button.collapsed {
    left: 8px; /* 收起时向左平移，与工具选择器按钮左右对齐 */
    /* top 保持 70px，只是向左平移 */
  }
  
  .collapse-button.collapsed {
    left: 8px;
  }
  
  .conversation-header {
    padding: 10px;
  }
  
  .new-conversation-btn {
    padding: 8px 10px;
    font-size: 13px;
  }
}

/* 移动端响应式（<768px） */
@media (max-width: 767px) {
  .conversation-list {
    position: absolute;
    left: 0;
    top: 0;
    width: 280px;
    height: 100%;
    z-index: 50;
    transform: translateX(-100%);
    transition: transform 0.3s;
  }
  
  .conversation-list.open {
    transform: translateX(0);
  }
}
</style>

