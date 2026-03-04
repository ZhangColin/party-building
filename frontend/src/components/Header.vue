<template>
  <header class="header">
    <!-- 左侧：Logo区域 -->
    <div class="header-left">
      <Logo />
    </div>
    
    <!-- 中间：大模块切换区域（桌面端和平板端显示） -->
    <div class="header-center">
      <ModuleSwitcher />
    </div>
    
    <!-- 移动端：汉堡菜单 -->
    <div class="header-mobile-menu">
      <MobileMenu />
    </div>
    
    <!-- 右侧：用户信息区域 -->
    <div class="header-right">
      <UserInfo />
    </div>
  </header>
</template>

<script setup lang="ts">
import Logo from './Logo.vue'
import ModuleSwitcher from './ModuleSwitcher.vue'
import UserInfo from './UserInfo.vue'
import MobileMenu from './MobileMenu.vue'
</script>

<style scoped>
.header {
  @apply flex items-center justify-between px-6 border-b sticky top-0 z-[100];
  /* 党建主题：红色渐变背景 */
  height: 72px;
  backdrop-filter: blur(12px);
  /* 使用党建红色渐变背景 */
  background: linear-gradient(135deg, #C8102E 0%, #E84D56 50%, #8B0000 100%);
  border-bottom-color: rgba(139, 0, 0, 0.2);
  box-shadow: 0 2px 8px rgba(200, 16, 46, 0.15), 0 1px 3px rgba(0, 0, 0, 0.1);
  /* 确保文字颜色为白色 */
  color: #FFFFFF;
}

.header-left,
.header-center,
.header-right,
.header-mobile-menu {
  display: flex;
  align-items: center;
}

.header-center {
  flex: 1;
  justify-content: center;
}

.header-mobile-menu {
  display: none;
}

/* 平板端响应式（768px - 1023px） */
@media (min-width: 768px) and (max-width: 1023px) {
  .header {
    padding: 0 20px;
  }
  
  .header-center {
    flex: 1;
  }
  
  .module-switcher {
    gap: 2px;
    padding: 3px;
  }
  
  .module-button {
    padding: 6px 14px;
    font-size: 13px;
  }
}

/* 移动端响应式（<768px） */
@media (max-width: 767px) {
  .header {
    padding: 0 16px;
    height: 56px;
  }
  
  .header-center {
    display: none; /* 移动端隐藏大模块切换 */
  }
  
  .header-mobile-menu {
    display: flex;
    margin-right: 8px;
  }
}
</style>

