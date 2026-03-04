<template>
  <div class="image-gallery">
    <!-- 单图显示 -->
    <div v-if="images.length === 1" class="single-image">
      <div class="image-wrapper">
        <img 
          :src="images[0]" 
          alt="生成的图片"
          class="gallery-image"
          @click="handleImageClick(0)"
        />
        <button 
          class="download-button"
          @click.stop="handleDownload(images[0], 0)"
          title="下载图片"
        >
          <svg class="download-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
        </button>
      </div>
    </div>
    
    <!-- 多图宫格显示 -->
    <div v-else class="grid-layout" :class="`grid-${gridColumns}`">
      <div 
        v-for="(imageUrl, index) in images" 
        :key="index"
        class="grid-item"
      >
        <div class="image-wrapper">
          <img 
            :src="imageUrl" 
            :alt="`生成的图片 ${index + 1}`"
            class="gallery-image"
            @click="handleImageClick(index)"
          />
          <button 
            class="download-button"
            @click.stop="handleDownload(imageUrl, index)"
            title="下载图片"
          >
            <svg class="download-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  images: string[]
}>()

const emit = defineEmits<{
  clickImage: [index: number]
  download: [url: string, index: number]
}>()

// 计算宫格列数
const gridColumns = computed(() => {
  const count = props.images.length
  if (count === 2) return 2
  if (count === 3) return 3
  if (count >= 4) return 2  // 4张图2x2布局
  return 1
})

function handleImageClick(index: number) {
  emit('clickImage', index)
}

function handleDownload(url: string | undefined, index: number) {
  if (url) {
    emit('download', url, index)
  }
}
</script>

<style scoped>
.image-gallery {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

/* 单图布局 */
.single-image {
  width: 100%;
}

/* 宫格布局 */
.grid-layout {
  display: grid;
  gap: 12px;
}

.grid-2 {
  grid-template-columns: repeat(2, 1fr);
}

.grid-3 {
  grid-template-columns: repeat(3, 1fr);
}

/* 图片容器 */
.image-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 1;  /* 保持正方形 */
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  background: #f3f4f6;
}

.image-wrapper:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.image-wrapper:hover .download-button {
  opacity: 1;
}

/* 图片 */
.gallery-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* 下载按钮 */
.download-button {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 36px;
  height: 36px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  border: none;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s;
}

.download-button:hover {
  background: rgba(0, 0, 0, 0.8);
  transform: scale(1.1);
}

.download-icon {
  width: 20px;
  height: 20px;
  color: white;
}

/* 响应式 */
@media (max-width: 768px) {
  .grid-3 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .download-button {
    opacity: 1;  /* 移动端始终显示下载按钮 */
  }
}
</style>
