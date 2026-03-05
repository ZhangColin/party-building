<template>
  <div
    class="message-item"
    :class="messageClass"
    data-testid="message-item"
    :data-role="message.role"
    @mouseenter="showToolbar = true"
    @mouseleave="showToolbar = false"
  >
    <!-- 隐藏头像，保持简洁 -->
    <div class="message-avatar" style="display: none;">
      <img
        :src="avatarUrl"
        :alt="message.role"
        class="avatar-image"
        data-testid="message-avatar"
      />
    </div>

    <div class="message-content">
      <div
        class="message-text"
        :class="{ 'markdown-content': message.role === 'assistant', 'user-text': message.role === 'user' }"
        v-html="renderedContent"
        data-testid="message-text"
      />
      <div class="message-footer">
        <div
          class="message-toolbar"
          :class="{ 'toolbar-visible': showToolbar }"
        >
          <button
            class="copy-button"
            @click="handleCopy"
            title="复制"
            data-testid="copy-button"
          >
            <DocumentDuplicateIcon />
          </button>
        </div>
        <div class="message-time" data-testid="message-time">
          {{ formattedTime }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { DocumentDuplicateIcon } from '@heroicons/vue/24/outline';
import { renderMarkdown } from '@/utils/markdownRenderer';
import { useClipboard } from '@/composables/useClipboard';
import type { Message } from '@/types';

interface Props {
  message: Message;
}

const props = defineProps<Props>();

const showToolbar = ref(false);
const { copy } = useClipboard();

const messageClass = computed(() => {
  return `message-${props.message.role}`;
});

const avatarUrl = computed(() => {
  return props.message.role === 'user'
    ? '/images/user-avatar.png'
    : '/images/ai-avatar.png';
});

const renderedContent = computed(() => {
  if (props.message.role === 'assistant') {
    return renderMarkdown(props.message.content);
  }
  return props.message.content;
});

const formattedTime = computed(() => {
  if (!props.message.created_at) return '';
  const date = new Date(props.message.created_at);
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  });
});

async function handleCopy() {
  await copy(props.message.content);
}
</script>

<style scoped>
@import '@/styles/markdown.css';

.message-item {
  display: flex;
  gap: 0;
  margin-bottom: 16px;
  animation: fadeIn 0.3s ease-in;
  position: relative;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.avatar-image {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  /* 默认（AI消息）使用完整宽度 */
  max-width: 100%;
}

.message-user .message-content {
  align-items: flex-end;
  /* 用户消息限制宽度 */
  max-width: 70%;
}

.message-text {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
}

.message-user .message-text {
  @apply party-message-bubble-user;
  /* 党建主题：使用全局用户消息气泡样式 */
}

.message-assistant .message-text {
  background-color: #f5f5f5;
  color: #333;
}

/* 用户消息保留原始换行 */
.user-text {
  white-space: pre-wrap;
}

/* Assistant messages use markdown-content class for rich formatting */
/* 移除 overflow-x: auto，使代码块的 sticky 定位能够相对于整个页面工作 */
.message-assistant .message-text {
  /* overflow-x: auto; - 已移除 */
}

.message-time {
  font-size: 12px;
  color: #999;
  padding: 0 4px;
}

.message-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  min-height: 20px;
}

.message-assistant .message-footer {
  flex-direction: row;
}

.message-user .message-footer {
  flex-direction: row-reverse;
}

.message-toolbar {
  display: flex;
  gap: 4px;
  /* 固定高度，避免显示时抖动 */
  height: 28px;
  min-height: 28px;
  /* 默认隐藏但保持占位 */
  visibility: hidden;
  opacity: 0;
  transition: opacity 0.2s;
}

.message-toolbar.toolbar-visible {
  visibility: visible;
  opacity: 1;
}

.copy-button {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: #999;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  padding: 0;
}

.copy-button:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #666;
}

.copy-button svg {
  width: 16px;
  height: 16px;
}
</style>
