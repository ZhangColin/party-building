<template>
  <div class="chat-input-wrapper" data-testid="chat-input-wrapper">
    <textarea
      ref="textareaRef"
      v-model="inputContent"
      class="chat-input"
      placeholder="输入消息..."
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
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

interface Props {
  disabled?: boolean;
  isLoading?: boolean;
  maxLength?: number;
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  isLoading: false,
  maxLength: 2000,
});

const emit = defineEmits<{
  send: [content: string];
}>();

const inputContent = ref('');
const textareaRef = ref<HTMLTextAreaElement>();
// 标记是否正在使用输入法组合（中文输入法等）
const isComposing = ref(false);

const canSend = computed(() => {
  return !props.disabled && !props.isLoading && inputContent.value.trim().length > 0;
});

const handleInput = () => {
  // 自动调整高度
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto';
    textareaRef.value.style.height = Math.min(textareaRef.value.scrollHeight, 200) + 'px';
  }

  // 限制长度
  if (inputContent.value.length > props.maxLength) {
    inputContent.value = inputContent.value.slice(0, props.maxLength);
  }
};

const handleKeydown = (event: KeyboardEvent) => {
  // Enter发送，Shift+Enter换行
  // 重要：在输入法组合期间，Enter不应该发送消息（而是用来选择候选词）
  if (event.key === 'Enter' && !event.shiftKey && !isComposing.value) {
    event.preventDefault();
    handleSend();
  }
};

// 输入法组合开始
const handleCompositionStart = () => {
  isComposing.value = true;
};

// 输入法组合结束
const handleCompositionEnd = () => {
  isComposing.value = false;
};

const handleSend = () => {
  const content = inputContent.value.trim();
  if (content && canSend.value) {
    emit('send', content);
    inputContent.value = '';

    // 重置高度
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto';
    }
  }
};

// 聚焦输入框
const focus = () => {
  textareaRef.value?.focus();
};

defineExpose({
  focus,
});
</script>

<style scoped>
.chat-input-wrapper {
  display: flex;
  gap: 8px;
  padding: 12px;
  background-color: #fff;
  border-top: 1px solid #e0e0e0;
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
  border-color: #1890ff;
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
  @apply party-btn-primary;
  /* 党建主题：使用全局主按钮样式 */
}

.send-button:hover:not(:disabled) {
  @apply party-btn-primary-hover;
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

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
