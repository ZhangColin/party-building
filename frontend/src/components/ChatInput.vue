<template>
  <div class="chat-input">
    <textarea
      ref="textareaRef"
      v-model="inputText"
      class="input-textarea"
      :placeholder="placeholder || '输入消息...'"
      :disabled="disabled"
      rows="1"
      @keydown="handleKeyDown"
      @input="handleInput"
      @compositionstart="handleCompositionStart"
      @compositionend="handleCompositionEnd"
    ></textarea>
    <button class="send-button" :disabled="!inputText.trim() || disabled" @click="handleSend">
      发送
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'

const props = defineProps<{
  placeholder?: string
  disabled?: boolean
}>()

const emit = defineEmits<{
  send: [content: string]
}>()

const inputText = ref('')
const isComposing = ref(false) // 标记是否正在使用输入法
const textareaRef = ref<HTMLTextAreaElement | null>(null)

function handleCompositionStart() {
  // 输入法开始输入
  isComposing.value = true
}

function handleCompositionEnd() {
  // 输入法结束输入，延迟一小段时间确保状态更新
  setTimeout(() => {
    isComposing.value = false
  }, 0)
}

function handleKeyDown(event: KeyboardEvent) {
  // 如果正在使用输入法，不处理 Enter 键
  if (isComposing.value) {
    return
  }
  
  // Enter发送，Shift+Enter换行
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    // 再次检查输入法状态（防止异步问题）
    if (!isComposing.value) {
    handleSend()
    } else {
    }
  }
  // Shift+Enter 允许默认行为（换行）
}

/**
 * 调整输入框高度
 */
async function adjustTextareaHeight() {
  await nextTick()
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    const scrollHeight = textareaRef.value.scrollHeight
    // 限制最大高度为 200px
    const maxHeight = 200
    if (scrollHeight <= maxHeight) {
      textareaRef.value.style.height = `${scrollHeight}px`
    } else {
      textareaRef.value.style.height = `${maxHeight}px`
      textareaRef.value.style.overflowY = 'auto'
    }
  }
}

/**
 * 处理输入事件（自动调整高度）
 */
async function handleInput() {
  await adjustTextareaHeight()
}

// 监听输入文本变化，自动调整高度
watch(inputText, () => {
  adjustTextareaHeight()
})

function handleSend() {
  const trimmedText = inputText.value.trim()
  if (trimmedText) {
    const textToSend = trimmedText
    // 先发送，再清空输入框
    emit('send', textToSend)
    // 清空输入框
    inputText.value = ''
    // 重置输入框高度
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  } else {
  }
}
</script>

<style scoped>
.chat-input {
  @apply flex items-end gap-3;
}

.input-textarea {
  @apply flex-1 px-4 py-3 border border-gray-300 rounded-xl text-sm resize-none min-h-[44px] max-h-[200px] leading-relaxed bg-white transition-all duration-200;
  /* 层级3：交互层 - 白色背景，轻微阴影，更柔和的边框 */
  font-family: inherit;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  border-color: theme('colors.gray.300');
  overflow-y: hidden; /* 初始状态隐藏滚动条，自动调整高度 */
}

.input-textarea:hover {
  border-color: theme('colors.gray.400');
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.input-textarea:focus {
  @apply outline-none border-primary-500;
  box-shadow: 0 0 0 3px theme('colors.primary.500 / 0.1'), 0 2px 4px rgba(0, 0, 0, 0.08);
}

.input-textarea::placeholder {
  @apply text-gray-400;
}

.send-button {
  padding: 12px 24px;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  /* 党建主题：主按钮样式 */
  background: linear-gradient(135deg, #C8102E 0%, #8B0000 100%);
}

.send-button:hover:not(:disabled) {
  /* 党建主题：主按钮悬停态 */
  background: linear-gradient(135deg, #a00d25 0%, #6d0000 100%);
  box-shadow: 0 4px 12px rgba(200, 16, 46, 0.3);
  transform: translateY(-1px);
}

.send-button:active:not(:disabled) {
  transform: translateY(0);
  /* 党建主题：主按钮激活态 */
  background: linear-gradient(135deg, #8B0000 0%, #5a0000 100%);
  box-shadow: 0 2px 8px rgba(200, 16, 46, 0.2);
}

.send-button:disabled {
  @apply bg-gray-300 cursor-not-allowed opacity-60;
  box-shadow: none;
}

.input-textarea:disabled {
  @apply bg-gray-50 cursor-not-allowed opacity-60;
}

/* 平板端响应式（768px - 1023px） */
@media (min-width: 768px) and (max-width: 1023px) {
  .chat-input {
    gap: 10px;
  }
  
  .input-textarea {
    padding: 11px 15px;
    font-size: 14px;
  }
  
  .send-button {
    padding: 11px 22px;
    font-size: 14px;
  }
}

/* 移动端响应式（<768px） */
@media (max-width: 767px) {
  .chat-input {
    gap: 8px;
  }
  
  .input-textarea {
    padding: 10px 14px;
    font-size: 14px;
    min-height: 40px;
  }
  
  .send-button {
    padding: 10px 20px;
    font-size: 13px;
  }
}
</style>

