<template>
  <div class="welcome-message">
    <h2 class="welcome-title">{{ welcomeTitle }}</h2>
    <div class="welcome-text markdown-body" v-html="renderedWelcomeText"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'

const props = defineProps<{
  welcomeMessage?: string
}>()

// 初始化 Markdown 渲染器
const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
  breaks: true // 支持换行
})

// 如果没有传入欢迎语，使用默认值
const welcomeTitle = '欢迎使用海创元党建 AI 智能平台'
const defaultMessage = '我是你的AI助手，可以帮助你处理各种任务。请告诉我你需要什么帮助？'

// 渲染 Markdown 格式的欢迎词
const renderedWelcomeText = computed(() => {
  const text = props.welcomeMessage || defaultMessage
  return md.render(text)
})
</script>

<style scoped>
.welcome-message {
  @apply text-center py-16 px-6 max-w-2xl mx-auto; /* 从py-12(48px)增加到py-16(64px)，更大气 */
}

.welcome-title {
  font-size: 30px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 16px;
  /* 党建主题：标题下划线样式 */
  position: relative;
  padding-bottom: 12px;
  letter-spacing: -0.5px;
}

.welcome-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%);
}

.welcome-text {
  @apply text-base text-gray-600 leading-relaxed;
  text-align: left; /* 左对齐，方便阅读列表 */
}

/* Markdown 内容样式 */
.welcome-text.markdown-body :deep(p) {
  @apply mb-4;
}

.welcome-text.markdown-body :deep(strong) {
  @apply font-semibold text-gray-900;
}

.welcome-text.markdown-body :deep(ul) {
  @apply list-none pl-0 space-y-2 mt-3;
}

.welcome-text.markdown-body :deep(li) {
  @apply text-gray-600 leading-relaxed;
}

.welcome-text.markdown-body :deep(li)::before {
  content: '✓';
  @apply mr-2 text-green-600 font-bold;
}

/* 平板端响应式（768px - 1023px） */
@media (min-width: 768px) and (max-width: 1023px) {
  .welcome-message {
    padding: 40px 20px;
  }
  
  .welcome-title {
    font-size: 26px;
  }
  
  .welcome-text {
    font-size: 15px;
  }
}

/* 移动端响应式（<768px） */
@media (max-width: 767px) {
  .welcome-message {
    padding: 32px 16px;
  }
  
  .welcome-title {
    font-size: 24px;
  }
  
  .welcome-text {
    font-size: 14px;
  }
}
</style>
