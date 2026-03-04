/** 认证状态管理 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ApiService } from '../services/apiClient'
import type { LoginRequest, UserInfo } from '../types'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref<string | null>(null)
  const user = ref<UserInfo | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)

  /**
   * 从存储中恢复Token和用户信息
   */
  function restoreAuth() {
    // 优先从localStorage读取（记住我）
    const storedToken = localStorage.getItem('auth_token')
    const storedUser = localStorage.getItem('auth_user')
    
    if (storedToken && storedUser) {
      token.value = storedToken
      try {
        user.value = JSON.parse(storedUser)
      } catch {
        user.value = null
      }
      return
    }
    
    // 如果没有，从sessionStorage读取（未记住我）
    const sessionToken = sessionStorage.getItem('auth_token')
    const sessionUser = sessionStorage.getItem('auth_user')
    
    if (sessionToken && sessionUser) {
      token.value = sessionToken
      try {
        user.value = JSON.parse(sessionUser)
      } catch {
        user.value = null
      }
    }
  }

  /**
   * 用户登录
   */
  async function login(request: LoginRequest) {
    loading.value = true
    error.value = null

    try {
      const response = await ApiService.login(request)
      
      // 保存Token和用户信息
      token.value = response.token
      user.value = response.user
      
      // 根据"记住我"选择存储方式
      if (request.remember_me) {
        localStorage.setItem('auth_token', response.token)
        localStorage.setItem('auth_user', JSON.stringify(response.user))
        // 清除sessionStorage中的旧数据
        sessionStorage.removeItem('auth_token')
        sessionStorage.removeItem('auth_user')
      } else {
        sessionStorage.setItem('auth_token', response.token)
        sessionStorage.setItem('auth_user', JSON.stringify(response.user))
        // 清除localStorage中的旧数据
        localStorage.removeItem('auth_token')
        localStorage.removeItem('auth_user')
      }
      
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : '登录失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 用户登出
   */
  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
    sessionStorage.removeItem('auth_token')
    sessionStorage.removeItem('auth_user')
  }

  /**
   * 验证Token是否有效
   * 调用后端API验证Token，如果有效则更新用户信息
   */
  async function verifyToken() {
    if (!token.value) {
      return false
    }

    try {
      const response = await ApiService.getCurrentUser()
      // Token有效，更新用户信息
      user.value = response.user
      // 更新存储中的用户信息
      const storedToken = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
      if (storedToken === token.value) {
        if (localStorage.getItem('auth_token')) {
          localStorage.setItem('auth_user', JSON.stringify(response.user))
        } else if (sessionStorage.getItem('auth_token')) {
          sessionStorage.setItem('auth_user', JSON.stringify(response.user))
        }
      }
      return true
    } catch (err) {
      // Token无效或过期，清除认证状态
      logout()
      return false
    }
  }

  /**
   * 获取用户信息（别名，用于路由守卫）
   */
  async function fetchUserInfo() {
    await verifyToken()
  }

  /**
   * 初始化：从存储中恢复认证状态
   */
  restoreAuth()

  return {
    // 状态
    token,
    user,
    loading,
    error,
    // 计算属性
    isAuthenticated,
    // 方法
    login,
    logout,
    restoreAuth,
    verifyToken,
    fetchUserInfo,
  }
})

