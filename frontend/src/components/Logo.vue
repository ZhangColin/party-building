<template>
  <div class="logo" @click="handleClick">
    <img :src="logoImage" alt="党建AI智能平台" class="logo-image" />
    <span class="logo-text">党建AI智能平台</span>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import logoImage from '@/assets/logo/logo_dark.png'

const router = useRouter()

function handleClick() {
  router.push('/modules/ai-tools')
}
</script>

<style scoped>
.logo {
  @apply flex items-center gap-2 cursor-pointer py-2 transition-opacity duration-200;
}

.logo:hover {
  @apply opacity-80;
}

.logo-image {
  @apply h-10 w-auto; /* 从h-8(32px)增加到h-10(40px) */
  object-fit: contain;
}

.logo-text {
  @apply text-lg font-semibold;
  letter-spacing: -0.5px;
  /* 党建主题：白色文字以适配红色背景 */
  color: #FFFFFF;
}

/* 平板端响应式（768px - 1023px） */
@media (min-width: 768px) and (max-width: 1023px) {
  .logo-image {
    height: 28px;
  }
  
  .logo-text {
    font-size: 17px;
  }
}

/* 移动端响应式（<768px） */
@media (max-width: 767px) {
  .logo-image {
    height: 24px;
  }
  
  .logo-text {
    font-size: 16px;
  }
}
</style>

