<template>
  <div class="admin-layout">
    <!-- 顶部栏 -->
    <el-header class="admin-header">
      <div class="header-left">
        <Logo />
        <span class="admin-badge">管理后台</span>
      </div>
      <div class="header-right">
        <el-button type="primary" link @click="goToHome">返回前台</el-button>
        <el-divider direction="vertical" />
        <span class="user-info">{{ userInfo?.nickname || userInfo?.username }}</span>
        <el-button type="primary" link @click="handleLogout">退出</el-button>
      </div>
    </el-header>

    <el-container class="admin-main-container">
      <!-- 侧边栏导航 -->
      <el-aside width="200px" class="admin-aside">
        <el-menu
          :default-active="currentRoute"
          class="admin-menu"
          router
        >
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>

          <el-menu-item index="/admin/party-members">
            <el-icon><User /></el-icon>
            <span>党员管理</span>
          </el-menu-item>

          <el-menu-item index="/admin/organization-life">
            <el-icon><Calendar /></el-icon>
            <span>组织生活</span>
          </el-menu-item>

          <el-menu-item index="/admin/party-fees">
            <el-icon><Coin /></el-icon>
            <span>党费管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-main class="admin-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Calendar, Coin } from '@element-plus/icons-vue'
import Logo from '../components/Logo.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const userInfo = computed(() => authStore.user)
const currentRoute = computed(() => route.path)

/**
 * 返回前台
 */
const goToHome = () => {
  router.push('/')
}

/**
 * 退出登录
 */
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch {
    // 用户取消
  }
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f0f2f5;
}

/* 顶部栏 */
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  /* 党建主题：红色渐变背景 */
  background: linear-gradient(135deg, #C8102E 0%, #E84D56 50%, #8B0000 100%);
  border-bottom: 1px solid rgba(139, 0, 0, 0.2);
  box-shadow: 0 2px 8px rgba(200, 16, 46, 0.15), 0 1px 3px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(12px);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.admin-badge {
  padding: 4px 12px;
  /* 党建主题：红色渐变背景 */
  background: linear-gradient(135deg, #8B0000 0%, #C8102E 100%);
  color: white;
  font-size: 13px;
  font-weight: 600;
  border-radius: 4px;
  letter-spacing: 0.5px;
  /* 添加金色边框装饰 */
  border: 1px solid rgba(255, 215, 0, 0.3);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-right :deep(.el-divider--vertical) {
  height: 1.5em;
  margin: 0;
}

.user-info {
  font-size: 14px;
  color: #FFFFFF;
}

/* 党建主题：按钮样式覆盖 */
.header-right :deep(.el-button--primary.is-link) {
  /* 默认状态：白色文字 */
  color: #FFFFFF;
  background-color: transparent;
  border: none;
}

.header-right :deep(.el-button--primary.is-link:hover) {
  /* hover状态：金色文字 */
  color: #FFD700;
  background-color: transparent;
  border: none;
}

.header-right :deep(.el-button--primary.is-link:focus) {
  /* focus状态：金色文字 */
  color: #FFD700;
  background-color: transparent;
  border: none;
}

/* 主容器 */
.admin-main-container {
  flex: 1;
  overflow: hidden;
}

/* 侧边栏 */
.admin-aside {
  background-color: #fff;
  border-right: 1px solid #e8e8e8;
  overflow-y: auto;
}

.admin-menu {
  border-right: none;
  height: 100%;
}

/* 主内容区 */
.admin-content {
  padding: 24px;
  overflow-y: auto;
  background-color: #f0f2f5;
}
</style>
