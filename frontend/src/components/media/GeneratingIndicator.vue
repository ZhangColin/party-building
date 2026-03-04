<template>
  <div class="generating-indicator">
    <div class="loading-container">
      <!-- 加载动画 -->
      <div class="loading-spinner">
        <div class="spinner-ring"></div>
        <div class="spinner-ring delay-1"></div>
        <div class="spinner-ring delay-2"></div>
      </div>
      
      <!-- 状态文字 -->
      <div class="status-text">
        <p class="main-text">{{ statusText }}</p>
        <p v-if="progress !== undefined" class="progress-text">
          {{ progress }}%
        </p>
      </div>
      
      <!-- 进度条 -->
      <div v-if="showProgress" class="progress-bar-container">
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: `${displayProgress}%` }"
          ></div>
        </div>
      </div>
      
      <!-- 提示信息 -->
      <p class="hint-text">{{ hintText }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  progress?: number
  estimatedTime?: number  // 预计剩余时间（秒）
  showProgress?: boolean
}>(), {
  showProgress: true
})

const statusText = computed(() => {
  if (props.progress !== undefined) {
    if (props.progress < 30) {
      return '正在理解你的描述...'
    } else if (props.progress < 70) {
      return '正在生成图片...'
    } else {
      return '即将完成...'
    }
  }
  return '正在生成中...'
})

const displayProgress = computed(() => {
  return props.progress ?? 50  // 默认显示50%
})

const hintText = computed(() => {
  if (props.estimatedTime) {
    return `预计还需 ${props.estimatedTime} 秒`
  }
  return '请稍候，这通常需要10-30秒'
})
</script>

<style scoped>
.generating-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px;
  min-height: 200px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  text-align: center;
}

/* 加载动画 */
.loading-spinner {
  position: relative;
  width: 60px;
  height: 60px;
}

.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 3px solid transparent;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
}

.spinner-ring.delay-1 {
  animation-delay: 0.15s;
  border-top-color: #764ba2;
}

.spinner-ring.delay-2 {
  animation-delay: 0.3s;
  border-top-color: #f093fb;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 状态文字 */
.status-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.main-text {
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
}

.progress-text {
  font-size: 24px;
  font-weight: 600;
  color: #667eea;
}

/* 进度条 */
.progress-bar-container {
  width: 100%;
  max-width: 300px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px;
  transition: width 0.3s ease;
}

/* 提示文字 */
.hint-text {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
}
</style>
