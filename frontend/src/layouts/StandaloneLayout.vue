<template>
  <div class="standalone-layout">
    <!-- 顶部导航栏 -->
    <Header />

    <!-- 主内容区 - 充满整个区域 -->
    <main class="main-content">
      <slot></slot>
    </main>
  </div>
</template>

<script setup lang="ts">
import Header from '@/components/Header.vue'
</script>

<style scoped>
.standalone-layout {
  @apply flex flex-col;
  height: 100%;
  background-color: #f5f5f5;
}

.main-content {
  @apply flex-1;
  overflow: hidden;
}
</style>
