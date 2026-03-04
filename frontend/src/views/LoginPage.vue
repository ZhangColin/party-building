<template>
  <div class="login-page">
    <!-- 左侧：平台介绍 -->
    <div class="intro-section">
      <div class="intro-content">
        <!-- Logo和平台名称 -->
        <div class="intro-header">
          <img src="@/assets/logo/logo.png" alt="党建AI智能平台" class="intro-logo" />
          <h1 class="intro-title">党建AI智能平台</h1>
        </div>

        <!-- 平台介绍 -->
        <div class="intro-modules">
          <div class="modules-grid">
            <!-- 模块1: AI党建助手 - 横跨两列 -->
            <div class="module-card module-card-featured">
              <div class="module-header">
                <div class="module-icon">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                  </svg>
                </div>
                <h3 class="module-title">AI党建助手</h3>
              </div>
              <p class="module-desc">智能党建服务平台，提供党员教育、组织管理、党费缴纳等全方位服务</p>
            </div>

            <!-- 模块2: 党员教育学习 -->
            <div class="module-card">
              <div class="module-header">
                <div class="module-icon">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222" />
                  </svg>
                </div>
                <h3 class="module-title">党员教育学习</h3>
              </div>
              <p class="module-desc">在线学习党史党章，提升党员理论素养</p>
            </div>

            <!-- 模块3: 组织生活管理 -->
            <div class="module-card">
              <div class="module-header">
                <div class="module-icon">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 class="module-title">组织生活管理</h3>
              </div>
              <p class="module-desc">三会一课智能化，主题党日活动管理</p>
            </div>

            <!-- 模块4: 党费管理 -->
            <div class="module-card">
              <div class="module-header">
                <div class="module-icon">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <h3 class="module-title">党费管理</h3>
              </div>
              <p class="module-desc">在线缴纳党费，明细查询透明公开</p>
            </div>

            <!-- 模块5: 党建知识库 -->
            <div class="module-card">
              <div class="module-header">
                <div class="module-icon">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <h3 class="module-title">党建知识库</h3>
              </div>
              <p class="module-desc">党的理论文献，政策法规智能检索</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧：登录区域 -->
    <div class="login-section">
      <div class="login-container">
        <div class="login-header">
          <h2 class="login-title">欢迎登录</h2>
          <p class="login-subtitle">以AI赋能党建工作，推动全面从严治党向纵深发展</p>
        </div>

        <!-- 登录表单 -->
        <form @submit.prevent="handleSubmit" class="login-form">
          <!-- 账号输入框 -->
          <div class="form-group">
            <label for="account" class="form-label">账号</label>
            <input
              id="account"
              v-model="formData.account"
              type="text"
              class="form-input"
              :class="{ 'form-input-error': errors.account }"
              placeholder="请输入用户名、邮箱或手机号"
              @blur="validateAccount"
            />
            <span v-if="errors.account" class="error-message">{{ errors.account }}</span>
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
              placeholder="请输入密码"
              @blur="validatePassword"
            />
            <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
          </div>

          <!-- 记住我 -->
          <div class="form-group">
            <label class="checkbox-label">
              <input
                v-model="formData.remember_me"
                type="checkbox"
                class="checkbox-input"
              />
              <span class="checkbox-text">记住我</span>
            </label>
          </div>

          <!-- 错误提示 -->
          <div v-if="authStore.error" class="error-alert">
            {{ authStore.error }}
          </div>

          <!-- 登录按钮 -->
          <button
            type="submit"
            class="login-button"
            :disabled="authStore.loading"
          >
            <span v-if="authStore.loading">登录中...</span>
            <span v-else>登录</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import type { LoginRequest } from '@/types'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 表单数据
const formData = ref<LoginRequest>({
  account: '',
  password: '',
  remember_me: false,
})

// 表单验证错误
const errors = ref<{
  account?: string
  password?: string
}>({})

// 验证账号格式（用户名、邮箱或手机号）
function validateAccount() {
  const account = formData.value.account.trim()
  if (!account) {
    errors.value.account = '请输入账号'
    return false
  }
  
  // 邮箱格式：^[^@]+@[^@]+\.[^@]+$
  const emailRegex = /^[^@]+@[^@]+\.[^@]+$/
  // 手机号格式：^1[3-9]\d{9}$
  const phoneRegex = /^1[3-9]\d{9}$/
  // 用户名格式：1-50个字符，允许字母、数字、下划线、中文字符等（更宽松）
  // 只要不是邮箱格式和手机号格式，就认为是用户名
  const isEmail = emailRegex.test(account)
  const isPhone = phoneRegex.test(account)
  const isUsername = !isEmail && !isPhone && account.length >= 1 && account.length <= 50
  
  if (!isEmail && !isPhone && !isUsername) {
    errors.value.account = '请输入正确的用户名、邮箱或手机号'
    return false
  }
  
  delete errors.value.account
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

// 表单是否有效（虽然当前未使用，但保留用于未来功能）
// const isFormValid = computed(() => {
//   return (
//     formData.value.account.trim() !== '' &&
//     formData.value.password.length >= 6 &&
//     Object.keys(errors.value).length === 0
//   )
// })

// 提交登录
async function handleSubmit() {
  // 验证表单
  const accountValid = validateAccount()
  const passwordValid = validatePassword()
  
  if (!accountValid || !passwordValid) {
    return
  }

  // 清除之前的错误
  authStore.error = null

  try {
    await authStore.login({
      account: formData.value.account.trim(),
      password: formData.value.password,
      remember_me: formData.value.remember_me,
    })

    // 登录成功，跳转到原访问页面或首页
    const redirect = route.query.redirect as string | undefined
    router.push(redirect || '/modules/ai-tools')
  } catch (err) {
    // 错误已在authStore中处理
    console.error('登录失败:', err)
  }
}
</script>

<style scoped>
/* ========== 页面布局 ========== */
.login-page {
  @apply min-h-screen flex;
}

/* ========== 左侧：平台介绍 ========== */
.intro-section {
  @apply flex-1 flex items-center justify-center px-8 py-12;
  background: linear-gradient(135deg, #C8102E 0%, #E84D56 50%, #8B0000 100%);
  position: relative;
  overflow: hidden;
}

.intro-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.3;
}

.intro-content {
  @apply relative z-10 w-full max-w-2xl;
}

.intro-header {
  @apply text-center mb-12;
}

.intro-logo {
  @apply h-16 w-auto mx-auto mb-4;
  object-fit: contain;
  filter: brightness(0) invert(1);
}

.intro-title {
  @apply text-3xl font-bold text-white mb-2;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.intro-modules {
  @apply w-full;
}

.modules-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-4;
}

.module-card {
  @apply bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-5 transition-all duration-300 hover:bg-white hover:bg-opacity-15 hover:transform hover:scale-105;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.module-card-featured {
  @apply md:col-span-2;
}

.module-header {
  @apply flex items-center gap-3 mb-3;
}

.module-icon {
  @apply flex-shrink-0 w-10 h-10 rounded-lg bg-white bg-opacity-20 flex items-center justify-center text-white;
}

.module-card-featured .module-icon {
  @apply w-12 h-12;
}

.module-title {
  @apply text-base font-semibold text-white flex-1;
}

.module-card-featured .module-title {
  @apply text-lg;
}

.module-desc {
  @apply text-sm text-white text-opacity-90 leading-relaxed;
}

/* ========== 右侧：登录区域 ========== */
.login-section {
  @apply w-full md:w-[480px] lg:w-[520px] flex items-center justify-center px-8 py-12 bg-gray-50;
}

.login-container {
  @apply w-full max-w-md;
}

.login-header {
  @apply text-center mb-8;
}

.login-title {
  @apply text-3xl font-bold text-gray-900 mb-2;
}

.login-subtitle {
  @apply text-sm text-gray-600;
}

.login-form {
  @apply space-y-5;
}

.form-group {
  @apply space-y-2;
}

.form-label {
  @apply block text-sm font-medium text-gray-700;
}

.form-input {
  @apply w-full px-4 py-3 border border-gray-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all;
}

.form-input-error {
  @apply border-error-500 focus:ring-error-500;
}

.error-message {
  @apply text-sm text-error-600;
}

.checkbox-label {
  @apply flex items-center cursor-pointer;
}

.checkbox-input {
  @apply w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 cursor-pointer;
}

.checkbox-text {
  @apply ml-2 text-sm text-gray-700;
}

.error-alert {
  @apply px-4 py-3 bg-error-50 border border-error-200 rounded-lg text-sm text-error-800;
}

.login-button {
  @apply w-full px-4 py-3.5 text-white rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm hover:shadow-md;
  background-color: var(--el-color-primary);
}

.login-button:hover {
  background-color: var(--el-color-primary-dark-2);
}

.login-button:focus-visible {
  background-color: var(--el-color-primary-dark-2);
  box-shadow: 0 0 0 3px var(--el-color-primary-light-7);
}

/* ========== 响应式设计 ========== */

/* 平板端 (768px - 1023px) */
@media (min-width: 768px) and (max-width: 1023px) {
  .intro-section {
    @apply px-6 py-10;
  }

  .intro-logo {
    @apply h-14;
  }

  .intro-title {
    @apply text-2xl;
  }

  .modules-grid {
    @apply gap-3;
  }

  .module-card {
    @apply p-4;
  }

  .module-header {
    @apply gap-2 mb-2;
  }

  .module-icon {
    @apply w-9 h-9;
  }

  .module-card-featured .module-icon {
    @apply w-10 h-10;
  }

  .module-title {
    @apply text-sm;
  }

  .module-card-featured .module-title {
    @apply text-base;
  }

  .module-desc {
    @apply text-xs;
  }

  .login-section {
    @apply w-[420px];
  }
}

/* 移动端 (<768px) - 垂直堆叠 */
@media (max-width: 767px) {
  .login-page {
    @apply flex-col;
  }

  .intro-section {
    @apply px-6 py-8;
    min-height: auto;
  }

  .intro-header {
    @apply mb-6;
  }

  .intro-logo {
    @apply h-12;
  }

  .intro-title {
    @apply text-xl;
  }

  .modules-grid {
    @apply gap-3;
  }

  .module-card {
    @apply p-4;
  }

  .module-header {
    @apply gap-2 mb-2;
  }

  .module-icon {
    @apply w-9 h-9;
  }

  .module-card-featured .module-icon {
    @apply w-10 h-10;
  }

  .module-title {
    @apply text-sm;
  }

  .module-card-featured .module-title {
    @apply text-base;
  }

  .module-desc {
    @apply text-xs;
  }

  .login-section {
    @apply w-full px-6 py-8;
  }

  .login-title {
    @apply text-2xl;
  }

  .login-subtitle {
    @apply text-xs;
  }
}

/* 超小屏幕 (<375px) */
@media (max-width: 374px) {
  .intro-section {
    @apply px-4 py-6;
  }

  .intro-logo {
    @apply h-10;
  }

  .intro-title {
    @apply text-lg;
  }

  .modules-grid {
    @apply gap-2;
  }

  .module-card {
    @apply p-3;
  }

  .module-header {
    @apply gap-2 mb-2;
  }

  .module-icon {
    @apply w-8 h-8;
  }

  .module-card-featured .module-icon {
    @apply w-9 h-9;
  }

  .module-title {
    @apply text-xs;
  }

  .module-desc {
    @apply text-xs;
  }

  .login-section {
    @apply px-4 py-6;
  }

  .login-title {
    @apply text-xl;
  }
}
</style>

