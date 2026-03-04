<template>
  <div class="media-chat-area" :class="{ 'conversation-collapsed': conversationListCollapsed }">
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
    
    <!-- 中间：媒体聊天区域 -->
    <div class="media-chat-panel">
      <MediaChatInterface
        :tool-id="toolId"
        :tool-name="toolName"
        :welcome-message="welcomeMessage"
        :session-id="currentSessionId ?? undefined"
        @session-created="handleSessionCreated"
        @title-generated="handleTitleGenerated"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import ConversationList from './ConversationList.vue'
import MediaChatInterface from './media/MediaChatInterface.vue'

const props = defineProps<{
  toolId: string
  toolName: string
  welcomeMessage: string
}>()

const currentSessionId = ref<string | null>(null)
const conversationListCollapsed = ref(false)
const conversationListRef = ref<InstanceType<typeof ConversationList> | null>(null)

// 监听工具切换，清空当前会话
watch(() => props.toolId, () => {
  currentSessionId.value = null
})

function handleConversationChange(sessionId: string) {
  currentSessionId.value = sessionId
}

function handleNewConversation() {
  currentSessionId.value = null
}

function handleSessionCreated(sessionId: string) {
  currentSessionId.value = sessionId
}

async function handleTitleGenerated(sessionId: string) {
  // 标题生成完成，刷新会话列表
  if (conversationListRef.value) {
    await conversationListRef.value.loadConversations()
    // 设置为当前选中的会话
    conversationListRef.value.setCurrentConversation(sessionId)
  }
}
</script>

<style scoped>
.media-chat-area {
  @apply flex h-full overflow-hidden bg-white;
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.04);
  position: relative;
}

.media-chat-panel {
  flex: 1;
  min-width: 0;
  transition: padding-left 0.3s ease;
  position: relative;
  overflow: hidden;
  background: #f9fafb;
}

/* 当历史列表收起时，增加左边距 */
.media-chat-area.conversation-collapsed .media-chat-panel {
  padding-left: 60px;
}

/* 平板端响应式（768px - 1023px） */
@media (min-width: 768px) and (max-width: 1023px) {
  .media-chat-area.conversation-collapsed .media-chat-panel {
    padding-left: 50px;
  }
}

/* 移动端响应式（<768px） */
@media (max-width: 767px) {
  .conversation-list {
    width: 280px;
  }
  
  .media-chat-area.conversation-collapsed .media-chat-panel {
    padding-left: 40px;
  }
}
</style>
