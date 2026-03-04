<template>
  <div
    class="message-item message-assistant streaming"
    data-testid="streaming-message"
  >
    <!-- 隐藏头像，保持简洁 -->
    <div class="message-avatar" style="display: none;">
      <img
        src="/images/ai-avatar.png"
        alt="AI"
        class="avatar-image"
      />
    </div>

    <div class="message-content">
      <div
        class="message-text markdown-content"
        v-html="renderedContent"
        data-testid="streaming-text"
      />
      <div class="streaming-indicator" data-testid="streaming-indicator">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { renderMarkdown } from '@/utils/markdownRenderer';

interface Props {
  content: string;
}

const props = defineProps<Props>();

const renderedContent = computed(() => {
  if (!props.content) return '';
  return renderMarkdown(props.content);
});
</script>

<style scoped>
@import '@/styles/markdown.css';

/* 继承 MessageItem 的基础样式 */
.message-item {
  display: flex;
  gap: 0;
  margin-bottom: 16px;
  animation: fadeIn 0.3s ease-in;
  position: relative;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 100%;
}

.message-text {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
  background-color: #f5f5f5;
  color: #333;
  overflow-x: auto;
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

.message-item.streaming {
  opacity: 0.9;
}

.streaming-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
  align-items: center;
}

.dot {
  width: 6px;
  height: 6px;
  background-color: #1890ff;
  border-radius: 50%;
  animation: pulse 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes pulse {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
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
</style>
