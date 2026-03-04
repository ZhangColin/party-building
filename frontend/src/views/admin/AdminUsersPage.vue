<template>
  <div class="admin-users-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>用户管理</h3>
          <el-button type="primary" @click="handleCreate">创建用户</el-button>
        </div>
      </template>

      <!-- 筛选器 -->
      <div class="filter-bar">
        <el-select
          v-model="filterIsAdmin"
          placeholder="筛选管理员"
          clearable
          @change="handleFilterChange"
          style="width: 150px"
        >
          <el-option label="全部用户" :value="undefined" />
          <el-option label="仅管理员" :value="true" />
          <el-option label="仅普通用户" :value="false" />
        </el-select>
      </div>

      <!-- 用户列表表格 -->
      <el-table
        :data="users"
        v-loading="loading"
        style="width: 100%; margin-top: 16px"
      >
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="nickname" label="昵称" width="150">
          <template #default="{ row }">
            {{ row.nickname || row.username }}
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" width="200">
          <template #default="{ row }">
            {{ row.email || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="120">
          <template #default="{ row }">
            {{ row.phone || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="is_admin" label="管理员" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_admin" type="primary">是</el-tag>
            <el-tag v-else type="info">否</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" @click="handleResetPassword(row)">重置密码</el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row)"
              :disabled="row.user_id === currentUserId"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
        style="margin-top: 16px; justify-content: flex-end"
      />
    </el-card>

    <!-- 创建用户对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="创建新用户"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="createForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="createForm.nickname" placeholder="请输入昵称（可选）" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="createForm.email" placeholder="请输入邮箱（可选）" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="createForm.phone" placeholder="请输入手机号（可选）" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="createForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="管理员">
          <el-checkbox v-model="createForm.is_admin">设置为管理员</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateSubmit" :loading="submitting">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑用户对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑用户"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="editForm.nickname" placeholder="请输入昵称（可选）" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" placeholder="请输入邮箱（可选）" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="editForm.phone" placeholder="请输入手机号（可选）" />
        </el-form-item>
        <el-form-item label="管理员">
          <el-checkbox v-model="editForm.is_admin">设置为管理员</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEditSubmit" :loading="submitting">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog
      v-model="resetPasswordDialogVisible"
      title="重置密码"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="resetPasswordFormRef"
        :model="resetPasswordForm"
        :rules="resetPasswordRules"
        label-width="100px"
      >
        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="resetPasswordForm.new_password"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetPasswordDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleResetPasswordSubmit"
          :loading="submitting"
        >
          确认
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { ApiService } from '../../services/apiClient'
import type {
  UserListItem,
  CreateUserRequest,
  UpdateUserRequest,
  ResetPasswordRequest,
} from '../../types'
import { useAuthStore } from '../../stores/authStore'

const authStore = useAuthStore()

// 当前用户ID
const currentUserId = computed(() => authStore.user?.user_id)

// 用户列表数据
const users = ref<UserListItem[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

// 筛选器
const filterIsAdmin = ref<boolean | undefined>(undefined)

// 创建用户对话框
const createDialogVisible = ref(false)
const createFormRef = ref<FormInstance>()
const createForm = reactive<CreateUserRequest>({
  username: '',
  nickname: '',
  email: '',
  phone: '',
  password: '',
  is_admin: false,
})

// 编辑用户对话框
const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editForm = reactive<UpdateUserRequest & { user_id?: string }>({
  username: '',
  nickname: '',
  email: '',
  phone: '',
  is_admin: false,
})

// 重置密码对话框
const resetPasswordDialogVisible = ref(false)
const resetPasswordFormRef = ref<FormInstance>()
const resetPasswordForm = reactive<ResetPasswordRequest & { user_id?: string }>({
  new_password: '',
})

// 提交状态
const submitting = ref(false)

// 表单验证规则
const createRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 1, max: 50, message: '用户名长度为1-50个字符', trigger: 'blur' },
  ],
  email: [
    {
      pattern: /^[^@]+@[^@]+\.[^@]+$/,
      message: '请输入正确的邮箱格式',
      trigger: 'blur',
    },
  ],
  phone: [
    {
      pattern: /^1[3-9]\d{9}$/,
      message: '请输入正确的手机号格式',
      trigger: 'blur',
    },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
}

const editRules: FormRules = {
  username: [
    { min: 1, max: 50, message: '用户名长度为1-50个字符', trigger: 'blur' },
  ],
  email: [
    {
      pattern: /^[^@]+@[^@]+\.[^@]+$/,
      message: '请输入正确的邮箱格式',
      trigger: 'blur',
    },
  ],
  phone: [
    {
      pattern: /^1[3-9]\d{9}$/,
      message: '请输入正确的手机号格式',
      trigger: 'blur',
    },
  ],
}

const resetPasswordRules: FormRules = {
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
}

/**
 * 格式化日期
 */
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

/**
 * 加载用户列表
 */
async function loadUsers() {
  loading.value = true
  try {
    const response = await ApiService.getUserList(
      currentPage.value,
      pageSize.value,
      filterIsAdmin.value
    )
    users.value = response.users
    total.value = response.total
  } catch (error: any) {
    ElMessage.error(error.message || '加载用户列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 筛选变化
 */
function handleFilterChange() {
  currentPage.value = 1
  loadUsers()
}

/**
 * 页码变化
 */
function handlePageChange() {
  loadUsers()
}

/**
 * 每页数量变化
 */
function handleSizeChange() {
  currentPage.value = 1
  loadUsers()
}

/**
 * 创建用户
 */
function handleCreate() {
  // 重置表单
  Object.assign(createForm, {
    username: '',
    nickname: '',
    email: '',
    phone: '',
    password: '',
    is_admin: false,
  })
  createFormRef.value?.clearValidate()
  createDialogVisible.value = true
}

/**
 * 提交创建用户
 */
async function handleCreateSubmit() {
  if (!createFormRef.value) return

  await createFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      await ApiService.createUser(createForm)
      ElMessage.success('创建用户成功')
      createDialogVisible.value = false
      loadUsers()
    } catch (error: any) {
      ElMessage.error(error.message || '创建用户失败')
    } finally {
      submitting.value = false
    }
  })
}

/**
 * 编辑用户
 */
function handleEdit(user: UserListItem) {
  Object.assign(editForm, {
    user_id: user.user_id,
    username: user.username,
    nickname: user.nickname || '',
    email: user.email || '',
    phone: user.phone || '',
    is_admin: user.is_admin || false,
  })
  editFormRef.value?.clearValidate()
  editDialogVisible.value = true
}

/**
 * 提交编辑用户
 */
async function handleEditSubmit() {
  if (!editFormRef.value || !editForm.user_id) return

  await editFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const { user_id, ...requestData } = editForm
      await ApiService.updateUser(user_id!, requestData)
      ElMessage.success('更新用户成功')
      editDialogVisible.value = false
      loadUsers()
      
      // 如果编辑的是当前用户，刷新用户信息
      if (user_id === currentUserId.value) {
        await authStore.fetchUserInfo()
      }
    } catch (error: any) {
      ElMessage.error(error.message || '更新用户失败')
    } finally {
      submitting.value = false
    }
  })
}

/**
 * 删除用户
 */
async function handleDelete(user: UserListItem) {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 ${user.username} 吗？删除后无法恢复。`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value = true
    try {
      await ApiService.deleteUser(user.user_id)
      ElMessage.success('删除用户成功')
      loadUsers()
    } catch (error: any) {
      ElMessage.error(error.message || '删除用户失败')
    } finally {
      loading.value = false
    }
  } catch {
    // 用户取消
  }
}

/**
 * 重置密码
 */
function handleResetPassword(user: UserListItem) {
  Object.assign(resetPasswordForm, {
    user_id: user.user_id,
    new_password: '',
  })
  resetPasswordFormRef.value?.clearValidate()
  resetPasswordDialogVisible.value = true
}

/**
 * 提交重置密码
 */
async function handleResetPasswordSubmit() {
  if (!resetPasswordFormRef.value || !resetPasswordForm.user_id) return

  await resetPasswordFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const { user_id, ...requestData } = resetPasswordForm
      const response = await ApiService.resetUserPassword(user_id!, requestData)
      
      // 显示新密码
      await ElMessageBox.alert(
        `密码已重置为：${response.new_password}\n\n请将新密码告知用户。`,
        '重置密码成功',
        {
          confirmButtonText: '我知道了',
          type: 'success',
        }
      )
      
      resetPasswordDialogVisible.value = false
    } catch (error: any) {
      ElMessage.error(error.message || '重置密码失败')
    } finally {
      submitting.value = false
    }
  })
}

// 组件挂载时加载数据
onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.admin-users-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.filter-bar {
  display: flex;
  gap: 12px;
}
</style>
