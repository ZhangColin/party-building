<template>
  <div class="media-input-container">
    <div class="input-layout">
      <!-- 左侧：提示词输入区 -->
      <div class="prompt-section">
        <textarea
          ref="textareaRef"
          v-model="prompt"
          class="prompt-textarea"
          placeholder="描述你想要的画面，越详细越好..."
          rows="3"
          :disabled="disabled"
          @input="handleInput"
          @keydown="handleKeyDown"
        ></textarea>
      </div>
      
      <!-- 右侧：高级设置区 -->
      <div class="params-section">
        <div class="params-header">
          <span class="params-title">⚙️ 高级设置</span>
        </div>
        
        <div class="params-grid">
          <!-- 图片尺寸 -->
          <div class="param-item">
            <label class="param-label">尺寸</label>
            <select 
              v-model="params.size" 
              class="param-select"
              :disabled="disabled"
            >
              <option 
                v-for="option in imageSizeOptions" 
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </div>
          
          <!-- 生成数量 -->
          <div class="param-item">
            <label class="param-label">数量</label>
            <select 
              v-model="params.count" 
              class="param-select"
              :disabled="disabled"
            >
              <option 
                v-for="option in imageCountOptions" 
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </div>
          
          <!-- 生成风格 -->
          <div class="param-item">
            <label class="param-label">风格</label>
            <select 
              v-model="params.style" 
              class="param-select"
              :disabled="disabled"
            >
              <option 
                v-for="option in imageStyleOptions" 
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 发送按钮 -->
    <div class="action-bar">
      <button 
        class="send-button"
        :class="{ 'loading': loading }"
        :disabled="!canSend"
        @click="handleSend"
      >
        <span v-if="loading" class="loading-icon">⏳</span>
        <span v-else>{{ sendButtonText }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import type { MediaGenerateParams } from '../../types/media'
import {
  DEFAULT_GENERATE_PARAMS,
  IMAGE_SIZE_OPTIONS,
  IMAGE_COUNT_OPTIONS,
  IMAGE_STYLE_OPTIONS
} from '../../types/media'

const props = defineProps<{
  loading?: boolean
  disabled?: boolean
}>()

const emit = defineEmits<{
  send: [prompt: string, params: MediaGenerateParams]
}>()

const prompt = ref('')
const params = ref<MediaGenerateParams>({ ...DEFAULT_GENERATE_PARAMS })
const textareaRef = ref<HTMLTextAreaElement | null>(null)

// 选项数据
const imageSizeOptions = IMAGE_SIZE_OPTIONS
const imageCountOptions = IMAGE_COUNT_OPTIONS
const imageStyleOptions = IMAGE_STYLE_OPTIONS

// 计算属性
const canSend = computed(() => {
  return prompt.value.trim().length > 0 && !props.loading && !props.disabled
})

const sendButtonText = computed(() => {
  if (props.loading) {
    return '生成中...'
  }
  return `生成${params.value.count}张图片`
})

// 方法
function handleInput() {
  adjustTextareaHeight()
}

function handleKeyDown(event: KeyboardEvent) {
  // Ctrl/Cmd + Enter 发送
  if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
    event.preventDefault()
    handleSend()
  }
}

async function adjustTextareaHeight() {
  await nextTick()
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    const scrollHeight = textareaRef.value.scrollHeight
    const maxHeight = 200
    if (scrollHeight <= maxHeight) {
      textareaRef.value.style.height = `${scrollHeight}px`
    } else {
      textareaRef.value.style.height = `${maxHeight}px`
      textareaRef.value.style.overflowY = 'auto'
    }
  }
}

function handleSend() {
  if (!canSend.value) {
    return
  }
  
  emit('send', prompt.value, { ...params.value })
}

/**
 * 重置输入（生成失败时保留提示词，成功后可选择清空）
 */
function reset(clearPrompt: boolean = false) {
  if (clearPrompt) {
    prompt.value = ''
  }
  // 参数保持不变，方便用户调整后重试
}

// 暴露方法给父组件
defineExpose({
  reset
})
</script>

<style scoped>
.media-input-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: white;
  border-top: 1px solid #e5e7eb;
}

.input-layout {
  display: flex;
  gap: 16px;
}

/* 左侧提示词区 */
.prompt-section {
  flex: 1;
  min-width: 0;
}

.prompt-textarea {
  width: 100%;
  min-height: 80px;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.5;
  resize: none;
  transition: border-color 0.2s;
}

.prompt-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.prompt-textarea:disabled {
  background: #f3f4f6;
  cursor: not-allowed;
}

/* 右侧参数区 */
.params-section {
  width: 240px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.params-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.params-title {
  font-size: 13px;
  font-weight: 500;
  color: #6b7280;
}

.params-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.param-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.param-label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

.param-select {
  padding: 8px 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  background: white;
  cursor: pointer;
  transition: border-color 0.2s;
}

.param-select:hover:not(:disabled) {
  border-color: #9ca3af;
}

.param-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.param-select:disabled {
  background: #f3f4f6;
  cursor: not-allowed;
}

/* 发送按钮区 */
.action-bar {
  display: flex;
  justify-content: flex-end;
}

.send-button {
  padding: 10px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.send-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-button:active:not(:disabled) {
  transform: translateY(0);
}

.send-button:disabled {
  background: #d1d5db;
  cursor: not-allowed;
  transform: none;
}

.send-button.loading {
  background: #9ca3af;
}

.loading-icon {
  display: inline-block;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .input-layout {
    flex-direction: column;
  }
  
  .params-section {
    width: 100%;
  }
  
  .params-grid {
    flex-direction: row;
    flex-wrap: wrap;
  }
  
  .param-item {
    flex: 1;
    min-width: 100px;
  }
}
</style>
