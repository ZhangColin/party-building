<template>
  <Teleport to="body">
    <Transition name="lightbox-fade">
      <div 
        v-if="show" 
        class="lightbox-overlay"
        @click="handleOverlayClick"
        @keydown.esc="handleClose"
        @keydown.left="handlePrevious"
        @keydown.right="handleNext"
        tabindex="0"
        ref="overlayRef"
      >
        <div class="lightbox-container">
          <!-- 关闭按钮 -->
          <button class="lightbox-close" @click="handleClose" title="关闭 (Esc)">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          
          <!-- 下载按钮 -->
          <button class="lightbox-download" @click="handleDownloadCurrent" title="下载图片">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </button>
          
          <!-- 左箭头（多图时显示） -->
          <button 
            v-if="canShowPrevious"
            class="lightbox-nav lightbox-prev"
            @click.stop="handlePrevious"
            title="上一张 (←)"
          >
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          
          <!-- 图片 -->
          <div class="lightbox-image-container" @click.stop>
            <img 
              :src="currentImageUrl" 
              :alt="`图片 ${currentIndex + 1}`"
              class="lightbox-image"
            />
          </div>
          
          <!-- 右箭头（多图时显示） -->
          <button 
            v-if="canShowNext"
            class="lightbox-nav lightbox-next"
            @click.stop="handleNext"
            title="下一张 (→)"
          >
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
          
          <!-- 图片计数（多图时显示） -->
          <div v-if="images.length > 1" class="lightbox-counter">
            {{ currentIndex + 1 }} / {{ images.length }}
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  show: boolean
  images: string[]
  initialIndex?: number
}>()

const emit = defineEmits<{
  close: []
  download: [url: string, index: number]
}>()

const currentIndex = ref(props.initialIndex || 0)
const overlayRef = ref<HTMLDivElement | null>(null)

// 计算属性
const currentImageUrl = computed(() => {
  return props.images[currentIndex.value] || ''
})

const canShowPrevious = computed(() => {
  return props.images.length > 1 && currentIndex.value > 0
})

const canShowNext = computed(() => {
  return props.images.length > 1 && currentIndex.value < props.images.length - 1
})

// 方法
function handleClose() {
  emit('close')
}

function handleOverlayClick(event: MouseEvent) {
  // 点击背景关闭
  if (event.target === event.currentTarget) {
    handleClose()
  }
}

function handlePrevious() {
  if (canShowPrevious.value) {
    currentIndex.value--
  }
}

function handleNext() {
  if (canShowNext.value) {
    currentIndex.value++
  }
}

function handleDownloadCurrent() {
  emit('download', currentImageUrl.value, currentIndex.value)
}

// 监听show变化，自动聚焦以支持键盘事件
watch(() => props.show, (newShow) => {
  if (newShow) {
    nextTick(() => {
      overlayRef.value?.focus()
    })
  }
})

// 监听initialIndex变化
watch(() => props.initialIndex, (newIndex) => {
  if (newIndex !== undefined) {
    currentIndex.value = newIndex
  }
})

// 阻止背景滚动
onMounted(() => {
  if (props.show) {
    document.body.style.overflow = 'hidden'
  }
})

onUnmounted(() => {
  document.body.style.overflow = ''
})

watch(() => props.show, (newShow) => {
  if (newShow) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

function nextTick(callback: () => void) {
  setTimeout(callback, 0)
}
</script>

<style scoped>
.lightbox-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  outline: none;
}

.lightbox-container {
  position: relative;
  width: 90vw;
  height: 90vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 图片容器 */
.lightbox-image-container {
  max-width: 100%;
  max-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lightbox-image {
  max-width: 100%;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

/* 控制按钮 */
.lightbox-close,
.lightbox-download {
  position: absolute;
  top: 20px;
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  color: white;
}

.lightbox-close {
  right: 20px;
}

.lightbox-download {
  right: 80px;
}

.lightbox-close:hover,
.lightbox-download:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.lightbox-close svg,
.lightbox-download svg {
  width: 24px;
  height: 24px;
}

.download-icon {
  width: 20px;
  height: 20px;
}

/* 导航按钮 */
.lightbox-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  color: white;
}

.lightbox-prev {
  left: 20px;
}

.lightbox-next {
  right: 20px;
}

.lightbox-nav:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-50%) scale(1.1);
}

.lightbox-nav svg {
  width: 28px;
  height: 28px;
}

/* 图片计数器 */
.lightbox-counter {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  color: white;
  font-size: 14px;
  font-weight: 500;
}

/* 过渡动画 */
.lightbox-fade-enter-active,
.lightbox-fade-leave-active {
  transition: opacity 0.3s;
}

.lightbox-fade-enter-from,
.lightbox-fade-leave-to {
  opacity: 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .lightbox-close,
  .lightbox-download {
    top: 10px;
    width: 40px;
    height: 40px;
  }
  
  .lightbox-close {
    right: 10px;
  }
  
  .lightbox-download {
    right: 60px;
  }
  
  .lightbox-nav {
    width: 44px;
    height: 44px;
  }
  
  .lightbox-prev {
    left: 10px;
  }
  
  .lightbox-next {
    right: 10px;
  }
}
</style>
