<template>
  <div class="chat-panel" data-testid="chat-panel">
    <MessageList
      ref="messageListRef"
      :messages="messages"
      :streaming-content="streamingContent"
      :auto-scroll="autoScroll"
    />

    <Transition name="fade">
      <div v-if="error" class="error-message" role="alert" aria-live="assertive" data-testid="error-message">
        <svg class="error-icon" role="img" aria-label="警告" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 9V13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <circle cx="12" cy="17" r="1" fill="currentColor"/>
          <path d="M12 2L2.5 11.5V20C2.5 20.8284 3.17157 21.5 4 21.5H20C20.8284 21.5 21.5 20.8284 21.5 20V11.5L12 2Z" stroke="currentColor" stroke-width="2"/>
        </svg>
        <div class="error-content">
          <div class="error-title">出错了</div>
          <div class="error-detail">{{ error }}</div>
          <button class="retry-button" @click="handleRetry" data-testid="retry-button">
            重试
          </button>
        </div>
      </div>
    </Transition>

    <ChatInput
      ref="chatInputRef"
      :disabled="disabled"
      :is-loading="isLoading"
      :show-file-buttons="showFileButtons"
      @send="handleSend"
      @open-knowledge="handleOpenKnowledge"
      @open-party-activity="handleOpenPartyActivity"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import MessageList from './chat/MessageList.vue';
import ChatInput from './chat/ChatInput.vue';
import { useSessionStore } from '../stores/sessionStore';
import type { Message } from '@/types';
import type { AttachmentReference } from '@/types';

interface Props {
  toolId?: string;
  welcomeMessage?: string;
  sessionId?: string;
  conversationCollapsed?: boolean;
  messages?: Message[];
  streamingContent?: string;
  disabled?: boolean;
  isLoading?: boolean;
  autoScroll?: boolean;
  error?: string;
  showFileButtons?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  messages: () => [],
  streamingContent: '',
  disabled: false,
  isLoading: false,
  autoScroll: true,
  showFileButtons: true,
});

const emit = defineEmits<{
  send: [content: string, attachments: AttachmentReference[]];
  retry: [];
  openKnowledge: [];
  openPartyActivity: [];
}>();

const sessionStore = useSessionStore();
const messageListRef = ref<InstanceType<typeof MessageList>>();
const chatInputRef = ref<InstanceType<typeof ChatInput>>();

// 初始化工具
watch(() => props.toolId, (newToolId) => {
  if (newToolId) {
    sessionStore.initTool(newToolId);
  }
}, { immediate: true });

// 恢复会话 - 当 sessionId prop 变化时
watch(() => props.sessionId, async (newSessionId) => {
  if (newSessionId) {
    // 如果正在流式输出，跳过 restoreSession（避免替换数组导致引用失效）
    if (sessionStore.loading) {
      return;
    }
    try {
      await sessionStore.restoreSession(newSessionId);
      // 恢复会话后，滚动到底部
      messageListRef.value?.scrollToBottom();
    } catch (err) {
      console.error('[ChatPanel] Failed to restore session:', err);
    }
  }
}, { immediate: true });

const handleSend = (content: string, attachments: AttachmentReference[]) => {
  emit('send', content, attachments);
};

const handleRetry = () => {
  emit('retry');
};

const handleOpenKnowledge = () => {
  emit('openKnowledge');
};

const handleOpenPartyActivity = () => {
  emit('openPartyActivity');
};

// 聚焦输入框
const focusInput = () => {
  chatInputRef.value?.focus();
};

// 滚动到底部
const scrollToBottom = () => {
  messageListRef.value?.scrollToBottom();
};

defineExpose({
  focusInput,
  scrollToBottom,
});
</script>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #f5f5f5;
}

.error-message {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  margin: 16px;
}

.error-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  color: #dc2626;
}

.error-content {
  flex: 1;
}

.error-title {
  font-size: 14px;
  font-weight: 600;
  color: #991b1b;
  margin-bottom: 4px;
}

.error-detail {
  font-size: 14px;
  color: #b91c1c;
  margin-bottom: 12px;
}

.retry-button {
  padding: 8px 16px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.retry-button:hover {
  background: #dc2626;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
