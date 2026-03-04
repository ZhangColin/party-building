<template>
  <div class="coming-soon">
    <div class="coming-soon-content">
      <div class="icon-wrapper">
        <component :is="iconComponent" class="w-16 h-16 text-gray-400" />
      </div>
      <h2 class="title">{{ toolName }}</h2>
      <p class="message">{{ welcomeMessage || `敬请期待：${toolName}功能即将上线！` }}</p>
      <div class="decoration">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { SparklesIcon } from '@heroicons/vue/24/outline'

const props = defineProps<{
  toolName: string
  welcomeMessage?: string
  icon?: string
}>()

const iconComponent = computed(() => {
  // 可以根据 icon 名称返回不同的图标组件
  // 目前统一使用 SparklesIcon
  return SparklesIcon
})
</script>

<style scoped>
.coming-soon {
  @apply flex items-center justify-center h-full w-full;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.coming-soon-content {
  @apply flex flex-col items-center justify-center text-center px-8 py-12;
  max-width: 500px;
}

.icon-wrapper {
  @apply mb-6;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.title {
  @apply text-2xl font-bold text-gray-800 mb-4;
}

.message {
  @apply text-base text-gray-600 mb-8;
  line-height: 1.6;
}

.decoration {
  @apply flex gap-2;
}

.dot {
  @apply w-2 h-2 rounded-full bg-gray-400;
  animation: pulse 1.5s ease-in-out infinite;
}

.dot:nth-child(1) {
  animation-delay: 0s;
}

.dot:nth-child(2) {
  animation-delay: 0.3s;
}

.dot:nth-child(3) {
  animation-delay: 0.6s;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.4;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}
</style>

