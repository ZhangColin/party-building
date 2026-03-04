<template>
  <div class="modal-overlay" @click.self="handleClose">
    <div class="modal-container">
      <div class="modal-header">
        <h2 class="modal-title">创建用户</h2>
        <button @click="handleClose" class="close-button">×</button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-body">
        <!-- 用户名输入框 -->
        <div class="form-group">
          <label for="username" class="form-label">用户名 <span class="required">*</span></label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            class="form-input"
            :class="{ 'form-input-error': errors.username }"
            placeholder="请输入用户名（必填，用于登录，必须唯一）"
            @blur="validateUsername"
          />
          <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
        </div>

        <!-- 昵称输入框（可选） -->
        <div class="form-group">
          <label for="nickname" class="form-label">昵称（可选）</label>
          <input
            id="nickname"
            v-model="formData.nickname"
            type="text"
            class="form-input"
            placeholder="请输入昵称（用于显示，如未填写则使用用户名）"
          />
        </div>

        <!-- 邮箱输入框（可选） -->
        <div class="form-group">
          <label for="email" class="form-label">邮箱（可选）</label>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            class="form-input"
            :class="{ 'form-input-error': errors.email }"
            placeholder="请输入邮箱（用于登录）"
            @blur="validateEmail"
          />
          <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
        </div>

        <!-- 手机号输入框（可选） -->
        <div class="form-group">
          <label for="phone" class="form-label">手机号（可选）</label>
          <input
            id="phone"
            v-model="formData.phone"
            type="text"
            class="form-input"
            :class="{ 'form-input-error': errors.phone }"
            placeholder="请输入手机号"
            @blur="validatePhone"
          />
          <span v-if="errors.phone" class="error-message">{{ errors.phone }}</span>
        </div>

        <!-- 密码输入框 -->
        <div class="form-group">
          <label for="password" class="form-label">密码</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            class="form-input"
            :class="{ 'form-input-error': errors.password }"
            placeholder="请输入密码（至少6位）"
            @blur="validatePassword"
          />
          <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
        </div>

        <!-- 头像输入框（可选） -->
        <div class="form-group">
          <label for="avatar" class="form-label">头像URL（可选）</label>
          <input
            id="avatar"
            v-model="formData.avatar"
            type="text"
            class="form-input"
            placeholder="请输入头像URL"
          />
        </div>

        <!-- 错误提示 -->
        <div v-if="error" class="error-alert">
          {{ error }}
        </div>

        <!-- 按钮组 -->
        <div class="form-actions">
          <button type="button" @click="handleClose" class="cancel-button">
            取消
          </button>
          <button
            type="submit"
            class="submit-button"
            :disabled="loading || !isFormValid"
          >
            <span v-if="loading">创建中...</span>
            <span v-else>创建</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ApiService } from '@/services/apiClient'
import type { CreateUserRequest } from '@/types'

const emit = defineEmits<{
  close: []
  created: []
}>()

// 表单数据
const formData = ref<CreateUserRequest>({
  username: '',
  email: '',
  phone: undefined,
  password: '',
  avatar: undefined,
})

// 表单验证错误
const errors = ref<{
  username?: string
  email?: string
  phone?: string
  password?: string
}>({})

const loading = ref(false)
const error = ref<string | null>(null)

// 验证用户名
function validateUsername() {
  const username = formData.value.username.trim()
  if (!username) {
    errors.value.username = '请输入用户名'
    return false
  }
  if (username.length > 50) {
    errors.value.username = '用户名不能超过50个字符'
    return false
  }
  delete errors.value.username
  return true
}

// 验证邮箱格式（可选）
function validateEmail() {
  const email = formData.value.email?.trim()
  if (!email) {
    // 邮箱是可选的，如果为空则不验证
    delete errors.value.email
    return true
  }
  const emailRegex = /^[^@]+@[^@]+\.[^@]+$/
  if (!emailRegex.test(email)) {
    errors.value.email = '请输入正确的邮箱格式'
    return false
  }
  delete errors.value.email
  return true
}

// 验证手机号格式（可选）
function validatePhone() {
  const phone = formData.value.phone?.trim()
  if (!phone) {
    // 手机号是可选的，如果为空则不验证
    delete errors.value.phone
    return true
  }
  const phoneRegex = /^1[3-9]\d{9}$/
  if (!phoneRegex.test(phone)) {
    errors.value.phone = '请输入正确的手机号格式（11位数字，以1开头）'
    return false
  }
  delete errors.value.phone
  return true
}

// 验证密码
function validatePassword() {
  const password = formData.value.password
  if (!password) {
    errors.value.password = '请输入密码'
    return false
  }
  if (password.length < 6) {
    errors.value.password = '密码至少需要6位'
    return false
  }
  delete errors.value.password
  return true
}

// 表单是否有效
const isFormValid = computed(() => {
  return (
    formData.value.username.trim() !== '' &&
    formData.value.password.length >= 6 &&
    Object.keys(errors.value).length === 0
  )
})

// 提交创建用户
async function handleSubmit() {
  // 验证表单
  const usernameValid = validateUsername()
  const emailValid = validateEmail()
  const phoneValid = validatePhone()
  const passwordValid = validatePassword()

  if (!usernameValid || !emailValid || !phoneValid || !passwordValid) {
    return
  }

  // 清除之前的错误
  error.value = null
  loading.value = true

  try {
    await ApiService.createUser({
      username: formData.value.username.trim(),
      nickname: formData.value.nickname?.trim() || undefined,
      email: formData.value.email?.trim() || undefined,
      phone: formData.value.phone?.trim() || undefined,
      password: formData.value.password,
      avatar: formData.value.avatar?.trim() || undefined,
    })

    // 创建成功，触发created事件
    emit('created')
    
    // 重置表单
    formData.value = {
      username: '',
      nickname: undefined,
      email: undefined,
      phone: undefined,
      password: '',
      avatar: undefined,
    }
    errors.value = {}
  } catch (err) {
    error.value = err instanceof Error ? err.message : '创建用户失败'
  } finally {
    loading.value = false
  }
}

// 关闭弹窗
function handleClose() {
  emit('close')
}
</script>

<style scoped>
.modal-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50;
}

.modal-container {
  @apply bg-white rounded-lg shadow-xl w-full max-w-md mx-4;
}

.modal-header {
  @apply flex items-center justify-between px-6 py-4 border-b border-gray-200;
}

.modal-title {
  @apply text-xl font-semibold text-gray-900;
}

.close-button {
  @apply text-2xl text-gray-400 hover:text-gray-600 focus:outline-none;
}

.modal-body {
  @apply px-6 py-4 space-y-4;
}

.form-group {
  @apply space-y-2;
}

.form-label {
  @apply block text-sm font-medium text-gray-700;
}

.form-input {
  @apply w-full px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all;
}

.form-input-error {
  @apply border-error-500 focus:ring-error-500;
}

.error-message {
  @apply text-sm text-error-600;
}

.error-alert {
  @apply px-4 py-3 bg-error-50 border border-error-200 rounded-lg text-sm text-error-800;
}

.form-actions {
  @apply flex items-center justify-end gap-3 pt-4;
}

.cancel-button {
  @apply px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-all;
}

.submit-button {
  @apply px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed;
}

/* 移动端响应式 */
@media (max-width: 767px) {
  .modal-container {
    @apply mx-2;
  }

  .modal-header {
    @apply px-4 py-3;
  }

  .modal-body {
    @apply px-4 py-3;
  }
}
</style>

