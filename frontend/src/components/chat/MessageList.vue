<template>
  <div
    ref="scrollContainer"
    class="message-list"
    data-testid="message-list"
  >
    <MessageItem
      v-for="(message, index) in messages"
      :key="message.message_id || index"
      :message="message"
      data-testid="message-item"
    />

    <StreamingMessage
      v-if="streamingContent"
      :content="streamingContent"
      data-testid="streaming-message-wrapper"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onUnmounted, onMounted } from 'vue';
import MessageItem from './MessageItem.vue';
import StreamingMessage from './StreamingMessage.vue';
import type { Message } from '@/types';

interface Props {
  messages: Message[];
  streamingContent?: string;
  autoScroll?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  streamingContent: '',
  autoScroll: true,
});

const scrollContainer = ref<HTMLElement>();
let scrollFrameId: number | null = null;

// 距离底部多少像素内认为是"在底部"
const NEAR_BOTTOM_THRESHOLD = 100;

// 检查是否在底部（或接近底部）
const isNearBottom = (): boolean => {
  if (!scrollContainer.value) return true;
  const container = scrollContainer.value;
  const distanceToBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
  return distanceToBottom <= NEAR_BOTTOM_THRESHOLD;
};

// 自动滚动到底部（带节流）
const scrollToBottom = async () => {
  // 如果已经有待处理的滚动请求，取消它
  if (scrollFrameId !== null) {
    cancelAnimationFrame(scrollFrameId);
  }

  // 使用 requestAnimationFrame 节流滚动操作
  scrollFrameId = requestAnimationFrame(() => {
    nextTick(() => {
      if (scrollContainer.value && props.autoScroll) {
        // 只有当用户在底部附近时才自动滚动
        if (isNearBottom()) {
          scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight;
        }
      }
      scrollFrameId = null;
    });
  });
};

// 监听消息变化，自动滚动
watch(
  () => props.messages.length,
  async () => {
    await scrollToBottom();
  },
  { flush: 'post' }
);

// 监听流式内容变化
watch(
  () => props.streamingContent,
  async () => {
    await scrollToBottom();
  },
  { flush: 'post' }
);

// 监听滚动事件（用于检测用户手动滚动）
const handleScroll = () => {
  // 这里可以添加额外的逻辑，比如记录用户滚动状态
  // 当前实现只需要在 scrollToBottom 中检查 isNearBottom()
};

// 组件挂载时添加滚动监听
onMounted(() => {
  if (scrollContainer.value) {
    scrollContainer.value.addEventListener('scroll', handleScroll, { passive: true });
  }
});

// 组件卸载时清理
onUnmounted(() => {
  if (scrollFrameId !== null) {
    cancelAnimationFrame(scrollFrameId);
  }
  if (scrollContainer.value) {
    scrollContainer.value.removeEventListener('scroll', handleScroll);
  }
});

// 暴露方法供外部调用
defineExpose({
  scrollToBottom,
  isNearBottom,
});
</script>

<style scoped>
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 0;
}

/* 滚动条样式 */
.message-list::-webkit-scrollbar {
  width: 6px;
}

.message-list::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.message-list::-webkit-scrollbar-thumb {
  background: #d1d1d1;
  border-radius: 3px;
}

.message-list::-webkit-scrollbar-thumb:hover {
  background: #b1b1b1;
}
</style>
