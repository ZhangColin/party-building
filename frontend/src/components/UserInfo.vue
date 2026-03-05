<template>
  <div v-if="authStore.isAuthenticated && authStore.user" class="user-info">
    <div class="user-avatar" @click="toggleDropdown">
      <span class="avatar-text">{{ userInitial }}</span>
    </div>
    <span class="user-name cursor-pointer hover:text-primary-600 transition-colors" @click="toggleDropdown">{{ displayName }}</span>
    
    <!-- 下拉菜单 -->
    <div v-if="showDropdown" class="dropdown-menu">
      <div class="dropdown-item user-info-item">
        <div class="user-info-name">{{ displayName }}</div>
        <div v-if="authStore.user.email" class="user-info-email">{{ authStore.user.email }}</div>
      </div>
      <div class="dropdown-divider"></div>
      <!-- 管理后台入口（仅管理员可见） -->
      <button v-if="authStore.user.is_admin" @click="goToAdmin" class="dropdown-item admin-button">
        管理后台
      </button>
      <div v-if="authStore.user.is_admin" class="dropdown-divider"></div>
      <button @click="handleLogout" class="dropdown-item logout-button">
        退出
      </button>
    </div>
  </div>
  <div v-else class="user-info">
    <span class="user-name">未登录</span>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()
const showDropdown = ref(false)

// 显示名称：优先使用昵称，如未填写则使用用户名
const displayName = computed(() => {
  if (authStore.user) {
    return authStore.user.nickname || authStore.user.username
  }
  return ''
})

const userInitial = computed(() => {
  if (authStore.user) {
    // 优先使用昵称的首字母，如未填写则使用用户名的首字母
    const name = authStore.user.nickname || authStore.user.username
    if (name) {
      return name.charAt(0).toUpperCase()
    }
  }
  return 'U'
})

// 切换下拉菜单
function toggleDropdown() {
  showDropdown.value = !showDropdown.value
}

// 点击外部关闭下拉菜单
function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (!target.closest('.user-info')) {
    showDropdown.value = false
  }
}

// 进入管理后台
function goToAdmin() {
  showDropdown.value = false
  router.push('/admin')
}

// 登出
function handleLogout() {
  authStore.logout()
  showDropdown.value = false
  router.push('/login')
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.user-info {
  @apply flex items-center gap-3 relative;
}

.user-avatar {
  @apply w-9 h-9 rounded-full flex items-center justify-center cursor-pointer transition-all duration-200;
  /* 党建主题：红色渐变背景 */
  background: linear-gradient(135deg, #C8102E 0%, #E84D56 100%);
  border: 2px solid rgba(255, 215, 0, 0.3); /* 金色边框装饰 */
  box-shadow: 0 2px 4px rgba(200, 16, 46, 0.3);
}

.user-avatar:hover {
  @apply scale-105;
  border-color: rgba(255, 215, 0, 0.6); /* 悬停时金色边框更明显 */
  box-shadow: 0 4px 8px rgba(200, 16, 46, 0.4), 0 0 8px rgba(255, 215, 0, 0.3); /* 金色光晕 */
}

.avatar-text {
  @apply text-white text-sm font-semibold;
}

.user-name {
  @apply text-sm text-gray-900 font-medium;
}

/* 平板端响应式（768px - 1023px） */
@media (min-width: 768px) and (max-width: 1023px) {
  .user-info {
    gap: 10px;
  }
  
  .user-avatar {
    width: 34px;
    height: 34px;
  }
  
  .avatar-text {
    font-size: 13px;
  }
  
  .user-name {
    font-size: 13px;
  }
}

/* 下拉菜单 */
.dropdown-menu {
  @apply absolute top-full right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50;
}

.dropdown-item {
  @apply block w-full text-left px-4 py-2 text-sm transition-colors party-menu-item;
  /* 党建主题：使用全局菜单项样式 */
}

.user-info-item {
  @apply cursor-default;
}

.user-info-name {
  @apply font-medium text-gray-900;
}

.user-info-email {
  @apply text-xs text-gray-500 mt-1;
}

.dropdown-divider {
  @apply border-t border-gray-200 my-1;
}

.admin-button {
  @apply text-primary-600 hover:bg-primary-50 cursor-pointer;
}

.logout-button {
  @apply text-error-600 hover:bg-error-50 cursor-pointer;
}

/* 移动端响应式（<768px） */
@media (max-width: 767px) {
  .user-name {
    display: none; /* 移动端只显示头像 */
  }
  
  .user-avatar {
    width: 32px;
    height: 32px;
  }
  
  .avatar-text {
    font-size: 12px;
  }
  
  .dropdown-menu {
    @apply right-0 w-48;
  }
}
</style>

