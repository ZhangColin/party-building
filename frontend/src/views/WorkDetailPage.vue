<template>
  <div class="work-detail-page" :class="{ 'fullscreen': isFullscreen }">
    <!-- 加载中 -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p class="loading-text">加载作品中...</p>
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
      <button class="retry-button" @click="loadWorkDetail">重试</button>
      <button class="back-button" @click="goBack">返回</button>
    </div>

    <!-- 作品详情展示 -->
    <div v-else class="work-viewer">
      <!-- 顶部工具条 -->
      <div class="toolbar">
        <div class="toolbar-info">
          <div class="work-icon">
            <component :is="getIconComponent(workDetail?.icon)" class="w-5 h-5 text-blue-600" />
          </div>
          <div class="work-title-section">
            <h1 class="work-title">{{ workDetail?.name }}</h1>
            <p class="work-category">{{ workDetail?.category_name }}</p>
          </div>
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
      <div class="work-content">
        <iframe
          v-if="workDetail?.html_url"
          :src="workDetail.html_url"
          sandbox="allow-scripts allow-forms allow-popups allow-same-origin"
          class="work-iframe"
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
import { storeToRefs } from 'pinia'
import { 
  ArrowLeftIcon, 
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon,
  PhotoIcon,
  SparklesIcon,
  ChartBarIcon,
  StarIcon,
  CursorArrowRaysIcon,
  PresentationChartLineIcon,
} from '@heroicons/vue/24/outline'
import { useWorksStore } from '../stores/worksStore'

const props = defineProps<{
  workId: string
}>()

const router = useRouter()
const worksStore = useWorksStore()
const { currentWork: workDetail, loading, error } = storeToRefs(worksStore)

// 图标映射
const iconComponents: Record<string, any> = {
  'photo': PhotoIcon,
  'sparkles': SparklesIcon,
  'chart-bar': ChartBarIcon,
  'star': StarIcon,
  'cursor-arrow-rays': CursorArrowRaysIcon,
  'presentation-chart-line': PresentationChartLineIcon,
}

/**
 * 获取图标组件
 */
function getIconComponent(iconName?: string) {
  if (!iconName) return PhotoIcon
  return iconComponents[iconName] || PhotoIcon
}

// 全屏状态
const isFullscreen = ref(false)

/**
 * 加载作品详情
 */
const loadWorkDetail = async () => {
  await worksStore.fetchWorkDetail(props.workId)
}

/**
 * 返回作品卡片页
 */
const goBack = () => {
  router.push('/works')
}

/**
 * 进入全屏模式
 */
const enterFullscreen = async () => {
  try {
    const element = document.querySelector('.work-detail-page') as HTMLElement
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
  console.error('作品HTML加载失败')
}

// 组件挂载时加载数据
onMounted(() => {
  loadWorkDetail()
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
.work-detail-page {
  @apply h-full w-full flex flex-col;
  background-color: theme('colors.gray.50');
}

.work-detail-page.fullscreen {
  @apply fixed inset-0 z-50;
}

/* 加载中 */
.loading-container {
  @apply flex flex-col items-center justify-center h-full gap-4;
}

.spinner {
  @apply w-12 h-12 border-4 border-gray-200 border-t-blue-600 rounded-full;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
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

/* 作品查看器 */
.work-viewer {
  @apply flex flex-col h-full;
}

/* 顶部工具条 */
.toolbar {
  @apply flex items-center gap-4 px-6 py-4 bg-white border-b border-gray-200;
  flex-shrink: 0;
}

.toolbar-info {
  @apply flex items-center gap-3 flex-1 min-w-0;
}

.work-icon {
  @apply w-10 h-10 rounded-lg bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center flex-shrink-0;
  border: 1px solid rgba(59, 130, 246, 0.1);
}

.work-title-section {
  @apply flex flex-col min-w-0;
}

.work-title {
  @apply text-lg font-semibold text-gray-900 leading-tight truncate;
  letter-spacing: -0.3px;
}

.work-category {
  @apply text-sm text-gray-500 truncate;
}

.toolbar-actions {
  @apply flex items-center gap-2 flex-shrink-0;
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

.work-content {
  @apply flex-1 overflow-hidden;
}

.work-iframe {
  @apply w-full h-full border-0;
}

/* 响应式 - 移动端 */
@media (max-width: 768px) {
  .toolbar {
    @apply px-4 py-3 gap-2;
  }

  .work-icon {
    @apply w-8 h-8;
  }

  .work-icon svg {
    @apply w-4 h-4;
  }

  .work-title {
    @apply text-base;
  }

  .work-category {
    @apply text-xs;
  }

  .toolbar-btn span {
    @apply hidden;
  }

  .toolbar-btn {
    @apply px-2 py-1.5;
  }
}
</style>
