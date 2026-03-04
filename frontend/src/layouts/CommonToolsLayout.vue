<template>
  <div class="common-tools-layout">
    <!-- 顶部导航栏 -->
    <Header />
    
    <!-- 主内容区 -->
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useNavigationStore } from '../stores/navigationStore'
import Header from '../components/Header.vue'

const navigationStore = useNavigationStore()

// 页面加载时获取导航配置
onMounted(() => {
  navigationStore.loadNavigation()
})
</script>

<style scoped>
.common-tools-layout {
  @apply flex flex-col;
  height: 100%;
}

.main-content {
  @apply flex-1 flex flex-col overflow-hidden;
  height: calc(100vh - 72px);
  min-height: 0;
}

/* 平板端响应式（768px - 1023px） */
@media (min-width: 768px) and (max-width: 1023px) {
  .main-content {
    height: calc(100vh - 64px);
  }
}

/* 移动端响应式（<768px） */
@media (max-width: 767px) {
  .main-content {
    height: calc(100vh - 56px);
  }
}
</style>

