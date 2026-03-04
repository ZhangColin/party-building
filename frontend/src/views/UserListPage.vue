<template>
  <div class="user-list-page">
    <div class="page-header">
      <h1 class="page-title">用户管理</h1>
      <button @click="showCreateForm = true" class="create-button">
        创建用户
      </button>
    </div>

    <!-- 创建用户表单（弹窗） -->
    <CreateUserForm
      v-if="showCreateForm"
      @close="showCreateForm = false"
      @created="handleUserCreated"
    />

    <!-- 用户列表 -->
    <div v-if="loading" class="loading-state">
      <p>加载中...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p class="error-message">{{ error }}</p>
      <button @click="loadUsers" class="retry-button">重试</button>
    </div>

    <div v-else-if="userList.length === 0" class="empty-state">
      <p>暂无用户</p>
    </div>

    <div v-else class="user-table-container">
      <table class="user-table">
        <thead>
          <tr>
            <th>用户名</th>
            <th>昵称</th>
            <th>邮箱</th>
            <th>手机号</th>
            <th>创建时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in userList" :key="user.user_id">
            <td>{{ user.username }}</td>
            <td>{{ user.nickname || user.username }}</td>
            <td>{{ user.email || '-' }}</td>
            <td>{{ user.phone || '-' }}</td>
            <td>{{ formatDate(user.created_at) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- 分页信息 -->
      <div v-if="total > pageSize" class="pagination">
        <p class="pagination-info">
          共 {{ total }} 条，第 {{ page }} / {{ Math.ceil(total / pageSize) }} 页
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ApiService } from '@/services/apiClient'
import type { UserListItem } from '@/types'
import CreateUserForm from '@/components/CreateUserForm.vue'

const loading = ref(false)
const error = ref<string | null>(null)
const userList = ref<UserListItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const showCreateForm = ref(false)

// 加载用户列表
async function loadUsers() {
  loading.value = true
  error.value = null

  try {
    const response = await ApiService.getUserList(page.value, pageSize.value)
    userList.value = response.users
    total.value = response.total
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载用户列表失败'
  } finally {
    loading.value = false
  }
}

// 格式化日期
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 用户创建成功后的处理
function handleUserCreated() {
  showCreateForm.value = false
  loadUsers() // 重新加载用户列表
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-list-page {
  @apply max-w-6xl mx-auto px-6 py-8;
}

.page-header {
  @apply flex items-center justify-between mb-6;
}

.page-title {
  @apply text-2xl font-semibold text-gray-900;
}

.create-button {
  @apply px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all;
}

.loading-state,
.error-state,
.empty-state {
  @apply text-center py-12 text-gray-500;
}

.error-message {
  @apply text-error-600 mb-4;
}

.retry-button {
  @apply px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all;
}

.user-table-container {
  @apply bg-white rounded-lg shadow-sm overflow-hidden;
}

.user-table {
  @apply w-full border-collapse;
}

.user-table thead {
  @apply bg-gray-50;
}

.user-table th {
  @apply px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider border-b border-gray-200;
}

.user-table td {
  @apply px-6 py-4 whitespace-nowrap text-sm text-gray-900 border-b border-gray-200;
}

.user-table tbody tr:hover {
  @apply bg-gray-50;
}

.pagination {
  @apply px-6 py-4 border-t border-gray-200;
}

.pagination-info {
  @apply text-sm text-gray-600;
}

/* 移动端响应式 */
@media (max-width: 767px) {
  .user-list-page {
    @apply px-4 py-6;
  }

  .page-header {
    @apply flex-col items-start gap-4;
  }

  .create-button {
    @apply w-full;
  }

  .user-table-container {
    @apply overflow-x-auto;
  }

  .user-table {
    @apply min-w-full;
  }

  .user-table th,
  .user-table td {
    @apply px-3 py-2 text-xs;
  }
}
</style>

