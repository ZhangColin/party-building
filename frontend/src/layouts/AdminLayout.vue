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
          
          <el-sub-menu index="tools">
            <template #title>
              <el-icon><Tools /></el-icon>
              <span>工具管理</span>
            </template>
            <el-menu-item index="/admin/tool-categories">分类管理</el-menu-item>
            <el-menu-item index="/admin/common-tools">工具管理</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="works">
            <template #title>
              <el-icon><Picture /></el-icon>
              <span>作品管理</span>
            </template>
            <el-menu-item index="/admin/work-categories">分类管理</el-menu-item>
            <el-menu-item index="/admin/works">作品管理</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="courses">
            <template #title>
              <el-icon><Document /></el-icon>
              <span>课程管理</span>
            </template>
            <el-menu-item index="/admin/course-categories">目录管理</el-menu-item>
            <el-menu-item index="/admin/course-documents">文档管理</el-menu-item>
          </el-sub-menu>
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
import { User, Tools, Picture, Document } from '@element-plus/icons-vue'
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
  background-color: rgba(255, 255, 255, 0.98);
  border-bottom: 1px solid #e8e8e8;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.06);
  backdrop-filter: blur(12px);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.admin-badge {
  padding: 4px 12px;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  color: white;
  font-size: 13px;
  font-weight: 600;
  border-radius: 4px;
  letter-spacing: 0.5px;
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
  color: #666;
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
