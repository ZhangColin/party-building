<template>
  <div class="html-tool-view" :class="{ 'fullscreen': isFullscreen }">
    <!-- 加载中 -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p class="loading-text">加载工具中...</p>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">
        <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <h2 class="error-title">加载失败</h2>
      <p class="error-message">{{ error }}</p>
      <button class="retry-button" @click="loadToolDetail">重试</button>
      <button class="back-button" @click="goBack">返回</button>
    </div>

    <!-- HTML工具运行器 -->
    <div v-else class="tool-runner">
      <!-- 顶部工具条 -->
      <div class="toolbar">
        <div class="toolbar-title">
          <CodeBracketIcon class="w-5 h-5 text-purple-600" />
          <span>{{ toolDetail?.name }}</span>
        </div>
        <div class="toolbar-actions">
          <button 
            v-if="!isFullscreen"
            class="toolbar-btn" 
            @click="enterFullscreen"
            title="全屏"
          >
            <ArrowsPointingOutIcon class="w-4 h-4" />
            <span>全屏</span>
          </button>
          <button 
            v-else
            class="toolbar-btn" 
            @click="exitFullscreen"
            title="退出全屏"
          >
            <ArrowsPointingInIcon class="w-4 h-4" />
            <span>退出全屏</span>
          </button>
          <button class="toolbar-btn back-btn" @click="goBack">
            <ArrowLeftIcon class="w-5 h-5" />
            <span>返回</span>
          </button>
        </div>
      </div>

      <!-- HTML内容（沙箱iframe） -->
      <div class="tool-content">
        <iframe
          v-if="toolDetail?.html_url"
          ref="iframeRef"
          :src="toolDetail.html_url"
          sandbox="allow-scripts allow-forms allow-popups allow-same-origin"
          class="tool-iframe"
          @load="handleIframeLoad"
          @error="handleIframeError"
        ></iframe>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { 
  ArrowLeftIcon, 
  CodeBracketIcon, 
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon 
} from '@heroicons/vue/24/outline'
import { ApiService } from '../services/apiClient'
import type { CommonToolDetail } from '../types'

const props = defineProps<{
  toolId: string
}>()

const router = useRouter()

// 状态
const loading = ref(true)
const error = ref<string | null>(null)
const toolDetail = ref<CommonToolDetail | null>(null)
const isFullscreen = ref(false)
// const iframeRef = ref<HTMLIFrameElement | null>(null) // 未使用，但保留用于未来功能

/**
 * 加载工具详情
 */
const loadToolDetail = async () => {
  loading.value = true
  error.value = null

  try {
    const detail = await ApiService.getCommonToolDetail(props.toolId)
    
    // 验证工具类型
    if (detail.type !== 'html') {
      error.value = '此工具不是HTML工具'
      return
    }

    if (!detail.html_url) {
      error.value = '工具HTML地址无效'
      return
    }

    toolDetail.value = detail
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载工具失败，请稍后重试'
    console.error('加载HTML工具详情失败:', err)
  } finally {
    loading.value = false
  }
}

/**
 * 返回工具卡片页
 */
const goBack = () => {
  router.push('/common-tools')
}

/**
 * 进入全屏模式
 */
const enterFullscreen = async () => {
  try {
    const element = document.querySelector('.html-tool-view') as HTMLElement
    if (element && element.requestFullscreen) {
      await element.requestFullscreen()
      isFullscreen.value = true
    }
  } catch (err) {
    console.error('进入全屏失败:', err)
  }
}

/**
 * 退出全屏模式
 */
const exitFullscreen = async () => {
  try {
    if (document.fullscreenElement) {
      await document.exitFullscreen()
      isFullscreen.value = false
    }
  } catch (err) {
    console.error('退出全屏失败:', err)
  }
}

/**
 * 监听全屏状态变化
 */
const handleFullscreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement
}

/**
 * iframe加载完成
 */
const handleIframeLoad = () => {
}

/**
 * iframe加载错误
 */
const handleIframeError = () => {
  error.value = 'HTML工具加载失败'
}

// 组件挂载时加载数据
onMounted(() => {
  loadToolDetail()
  document.addEventListener('fullscreenchange', handleFullscreenChange)
})

// 组件卸载时清理
onBeforeUnmount(() => {
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  if (isFullscreen.value) {
    exitFullscreen()
  }
})
</script>

<style scoped>
.html-tool-view {
  @apply h-full w-full flex flex-col;
  background-color: theme('colors.gray.50');
}

.html-tool-view.fullscreen {
  @apply fixed inset-0 z-50;
}

/* 加载中 */
.loading-container {
  @apply flex flex-col items-center justify-center h-full gap-4;
}

.spinner {
  @apply w-12 h-12 border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin;
}

.loading-text {
  @apply text-gray-600 text-base;
}

/* 错误提示 */
.error-container {
  @apply flex flex-col items-center justify-center h-full gap-4 px-6;
}

.error-icon {
  @apply text-red-500;
}

.error-title {
  @apply text-xl font-semibold text-gray-900;
}

.error-message {
  @apply text-gray-600 text-center;
}

.retry-button,
.back-button {
  @apply mt-2 px-6 py-2 rounded-lg transition-colors;
}

.retry-button {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}

.back-button {
  @apply bg-gray-200 text-gray-700 hover:bg-gray-300;
}

/* 工具运行器 */
.tool-runner {
  @apply flex flex-col h-full;
}

/* 顶部工具条 */
.toolbar {
  @apply flex items-center gap-4 px-6 py-3 bg-white border-b border-gray-200;
  flex-shrink: 0;
}

.toolbar-btn {
  @apply flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-all;
}

.toolbar-btn:hover {
  @apply shadow-sm;
}

.back-btn {
  @apply text-gray-600 hover:text-gray-900;
}

.toolbar-title {
  @apply flex items-center gap-2 text-lg font-semibold text-gray-900 flex-1;
}

.toolbar-actions {
  @apply flex items-center gap-2;
}

.tool-content {
  @apply flex-1 overflow-hidden;
}

.tool-iframe {
  @apply w-full h-full border-0;
}

/* 响应式 */
@media (max-width: 768px) {
  .toolbar {
    @apply px-4 py-2 gap-2;
  }

  .toolbar-title {
    @apply text-base;
  }

  .toolbar-btn span {
    @apply hidden;
  }

  .toolbar-btn {
    @apply px-2 py-1.5;
  }
}
</style>
