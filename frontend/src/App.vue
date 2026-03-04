<template>
  <div class="app-container">
    <RouterView />
    <ToastNotification
      :show="toast.show"
      :message="toast.message"
    />
  </div>
</template>

<script setup lang="ts">
import { reactive, onUnmounted } from 'vue'
import { RouterView } from 'vue-router'
import ToastNotification from '@/components/ToastNotification.vue'

const toast = reactive({
  show: false,
  message: ''
})

// Track active toast timers for cleanup
const activeTimers: Set<number> = new Set()

// 暴露给全局使用
window.__showToast = (message: string) => {
  toast.message = message
  toast.show = true
  const timerId = window.setTimeout(() => {
    toast.show = false
    activeTimers.delete(timerId)
  }, 2000)
  activeTimers.add(timerId)
}

// Clean up any pending timers when component unmounts
onUnmounted(() => {
  activeTimers.forEach((timerId) => {
    clearTimeout(timerId)
  })
  activeTimers.clear()
})
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body {
  height: 100%;
  margin: 0;
  padding: 0;
}

#app {
  height: 100%;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.5;
  color: theme('colors.gray.800');
  /* 层级0：页面主背景 - 极浅灰，带微妙渐变，避免纯白刺眼 */
  background: linear-gradient(to bottom, theme('colors.gray.50') 0%, theme('colors.gray.100') 100%);
}

.app-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>
