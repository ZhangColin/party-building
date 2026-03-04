<template>
  <div class="input-area" data-testid="input-area">
    <div class="input-wrapper">
      <textarea
        ref="textareaRef"
        v-model="inputText"
        :disabled="disabled"
        :placeholder="placeholder"
        class="input-textarea"
        @keydown="handleKeyDown"
        @input="handleInput"
      ></textarea>
      <button
        :disabled="disabled || !canSend"
        class="send-button"
        :class="{ loading: loading }"
        @click="handleSend"
      >
        <span v-if="loading" class="loading-spinner"></span>
        <span>{{ loading ? '发送中...' : '发送' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'

const props = defineProps<{
  loading?: boolean
  disabled?: boolean
  placeholder?: string
}>()

const emit = defineEmits<{
  send: [content: string]
}>()

const inputText = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)

const canSend = computed(() => {
  return inputText.value.trim().length > 0
})

/**
 * 处理键盘事件
 */
function handleKeyDown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    if (canSend.value && !props.disabled) {
      handleSend()
    }
  }
}

/**
 * 处理输入事件（自动调整高度）
 */
async function handleInput() {
  await nextTick()
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    textareaRef.value.style.height = `${textareaRef.value.scrollHeight}px`
  }
}

/**
 * 处理发送
 */
function handleSend() {
  if (!canSend.value || props.disabled) {
    return
  }

  const content = inputText.value.trim()
  if (content) {
    emit('send', content)
    inputText.value = ''
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  }
}
</script>

<style scoped>
.input-area {
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
  background-color: white;
}

.input-wrapper {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
}

.input-textarea {
  flex: 1;
  min-height: 2.5rem;
  max-height: 8rem;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  resize: none;
  font-family: inherit;
  font-size: 0.875rem;
  line-height: 1.5;
  overflow-y: auto;
}

.input-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input-textarea:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
}

.send-button {
  padding: 0.75rem 1.5rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.send-button:hover:not(:disabled) {
  background-color: #2563eb;
}

.send-button:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.send-button.loading {
  position: relative;
}

.loading-spinner {
  display: inline-block;
  width: 0.875rem;
  height: 0.875rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: 0.5rem;
  vertical-align: middle;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>

