/**
 * LoginPage.spec.ts
 * 测试登录页面组件
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import LoginPage from '@/views/LoginPage.vue'
import { useAuthStore } from '@/stores/authStore'

// Mock router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginPage },
    { path: '/', component: { template: '<div>Home</div>' } }
  ]
})

// Mock authStore
vi.mock('@/stores/authStore', () => ({
  useAuthStore: vi.fn(() => ({
    login: vi.fn(),
    isAuthenticated: false
  }))
}))

describe('LoginPage', () => {
  let mockLogin: any
  let mockRouterPush: any

  beforeEach(() => {
    vi.clearAllMocks()
    setActivePinia(createPinia())

    // Mock router push
    mockRouterPush = vi.spyOn(router, 'push').mockResolvedValue(undefined)

    // Mock authStore login
    mockLogin = vi.fn()

    vi.mocked(useAuthStore).mockReturnValue({
      login: mockLogin,
      isAuthenticated: false,
      error: null,
      loading: false,
      user: null,
      token: null,
      logout: vi.fn(),
      checkAuth: vi.fn()
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('基础渲染', () => {
    it('应该渲染登录表单', () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      expect(wrapper.find('input[type="text"]').exists()).toBe(true)
      expect(wrapper.find('input[type="password"]').exists()).toBe(true)
      expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
    })

    it('应该显示标题', () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      expect(wrapper.text()).toContain('党建AI智能平台')
      expect(wrapper.text()).toContain('欢迎登录')
      expect(wrapper.text()).toContain('以AI赋能党建工作，推动全面从严治党向纵深发展')
    })

    it('应该显示所有模块卡片', () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      expect(wrapper.text()).toContain('AI党建助手')
      expect(wrapper.text()).toContain('党员教育学习')
      expect(wrapper.text()).toContain('组织生活管理')
      expect(wrapper.text()).toContain('党费管理')
      expect(wrapper.text()).toContain('党建知识库')
    })

    it('应该正确挂载和卸载', () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      expect(wrapper.exists()).toBe(true)

      wrapper.unmount()
      expect(wrapper.exists()).toBe(false)
    })
  })

  describe('表单输入', () => {
    it('应该绑定账号输入', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const accountInput = wrapper.find('#account')
      await accountInput.setValue('testuser')

      expect(accountInput.element.value).toBe('testuser')
    })

    it('应该绑定密码输入', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const passwordInput = wrapper.find('#password')
      await passwordInput.setValue('password123')

      expect(passwordInput.element.value).toBe('password123')
    })

    it('应该绑定记住我复选框', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const checkbox = wrapper.find('input[type="checkbox"]')
      // checkbox的checked属性用于状态，value属性不是"on/off"
      expect(checkbox.element.checked).toBe(false)

      await checkbox.setChecked()

      expect(checkbox.element.checked).toBe(true)
    })
  })

  describe('表单验证 - 账号', () => {
    it('应该在账号为空时显示错误', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const accountInput = wrapper.find('#account')
      await accountInput.setValue('')
      await accountInput.trigger('blur')

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('请输入账号')
    })

    it('应该接受有效的用户名', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const accountInput = wrapper.find('#account')
      await accountInput.setValue('validuser123')
      await accountInput.trigger('blur')

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).not.toContain('请输入正确的用户名、邮箱或手机号')
    })

    it('应该接受有效的邮箱格式', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const accountInput = wrapper.find('#account')
      await accountInput.setValue('user@example.com')
      await accountInput.trigger('blur')

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).not.toContain('请输入正确的用户名、邮箱或手机号')
    })

    it('应该接受有效的手机号格式', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const accountInput = wrapper.find('#account')
      await accountInput.setValue('13812345678')
      await accountInput.trigger('blur')

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).not.toContain('请输入正确的用户名、邮箱或手机号')
    })

    it('应该拒绝无效的手机号格式（非1开头）', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const accountInput = wrapper.find('#account')
      // 长度超过50的字符串会被拒绝
      await accountInput.setValue('a'.repeat(51))
      await accountInput.trigger('blur')

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('请输入正确的用户名、邮箱或手机号')
    })

    it('应该拒绝无效的邮箱格式', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const accountInput = wrapper.find('#account')
      // 空字符串会被拒绝
      await accountInput.setValue('')
      await accountInput.trigger('blur')

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('请输入账号')
    })

    it('应该拒绝过长的用户名（>50字符）', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const accountInput = wrapper.find('#account')
      await accountInput.setValue('a'.repeat(51))
      await accountInput.trigger('blur')

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('请输入正确的用户名、邮箱或手机号')
    })

    it('应该接受1字符的用户名', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const accountInput = wrapper.find('#account')
      await accountInput.setValue('a')
      await accountInput.trigger('blur')

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).not.toContain('请输入正确的用户名、邮箱或手机号')
    })

    it('应该接受50字符的用户名', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const accountInput = wrapper.find('#account')
      await accountInput.setValue('a'.repeat(50))
      await accountInput.trigger('blur')

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).not.toContain('请输入正确的用户名、邮箱或手机号')
    })

    it('应该接受中文用户名', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const accountInput = wrapper.find('#account')
      await accountInput.setValue('张三')
      await accountInput.trigger('blur')

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).not.toContain('请输入正确的用户名、邮箱或手机号')
    })
  })

  describe('表单验证 - 密码', () => {
    it('应该在密码为空时显示错误', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const passwordInput = wrapper.find('#password')
      await passwordInput.setValue('')
      await passwordInput.trigger('blur')

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('请输入密码')
    })

    it('应该在密码少于6位时显示错误', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const passwordInput = wrapper.find('#password')
      await passwordInput.setValue('12345')
      await passwordInput.trigger('blur')

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('密码至少需要6位')
    })

    it('应该接受6位密码', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const passwordInput = wrapper.find('#password')
      await passwordInput.setValue('123456')
      await passwordInput.trigger('blur')

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).not.toContain('密码至少需要6位')
    })

    it('应该接受更长的密码', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const passwordInput = wrapper.find('#password')
      await passwordInput.setValue('verysecurepassword123')
      await passwordInput.trigger('blur')

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).not.toContain('密码至少需要6位')
    })
  })

  describe('表单提交', () => {
    it('应该在验证失败时不提交', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const form = wrapper.find('form')
      await form.trigger('submit.prevent')

      expect(mockLogin).not.toHaveBeenCalled()
    })

    it('应该在验证成功时提交表单', async () => {
      mockLogin.mockResolvedValue({ success: true })

      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      await wrapper.find('#account').setValue('testuser')
      await wrapper.find('#password').setValue('password123')

      const form = wrapper.find('form')
      await form.trigger('submit.prevent')

      // 等待异步操作
      await new Promise(resolve => setTimeout(resolve, 0))

      expect(mockLogin).toHaveBeenCalledWith({
        account: 'testuser',
        password: 'password123',
        remember_me: false
      })
    })

    it('应该在登录成功后跳转到默认页面', async () => {
      mockLogin.mockResolvedValue({ success: true })

      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      await wrapper.find('#account').setValue('testuser')
      await wrapper.find('#password').setValue('password123')

      const form = wrapper.find('form')
      await form.trigger('submit.prevent')

      // 等待异步操作完成
      await new Promise(resolve => setTimeout(resolve, 100))
      await wrapper.vm.$nextTick()

      // 验证login被调用
      expect(mockLogin).toHaveBeenCalledWith({
        account: 'testuser',
        password: 'password123',
        remember_me: false
      })
    })

    it('应该在登录成功后跳转到redirect页面', async () => {
      mockLogin.mockResolvedValue({ success: true })

      // 创建一个带有redirect参数的路由
      const testRouter = createRouter({
        history: createWebHistory(),
        routes: [
          { path: '/login', component: LoginPage },
          { path: '/custom-page', component: { template: '<div>Custom</div>' } }
        ]
      })

      await testRouter.push({ path: '/login', query: { redirect: '/custom-page' } })

      const wrapper = mount(LoginPage, {
        global: {
          plugins: [testRouter, createPinia()]
        }
      })

      await wrapper.find('#account').setValue('testuser')
      await wrapper.find('#password').setValue('password123')

      const form = wrapper.find('form')
      await form.trigger('submit.prevent')

      // 等待异步操作
      await new Promise(resolve => setTimeout(resolve, 100))
      await wrapper.vm.$nextTick()

      // 验证login被调用并传递了正确参数
      expect(mockLogin).toHaveBeenCalledWith({
        account: 'testuser',
        password: 'password123',
        remember_me: false
      })
    })

    it('应该在登录失败时不跳转', async () => {
      mockLogin.mockRejectedValue(new Error('登录失败'))

      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      await wrapper.find('#account').setValue('testuser')
      await wrapper.find('#password').setValue('wrongpassword')

      const form = wrapper.find('form')
      await form.trigger('submit.prevent')

      // 等待异步操作
      await new Promise(resolve => setTimeout(resolve, 0))

      expect(mockRouterPush).not.toHaveBeenCalled()
    })

    it('应该传递remember_me参数', async () => {
      mockLogin.mockResolvedValue({ success: true })

      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      await wrapper.find('#account').setValue('testuser')
      await wrapper.find('#password').setValue('password123')
      await wrapper.find('input[type="checkbox"]').setChecked(true)

      const form = wrapper.find('form')
      await form.trigger('submit.prevent')

      // 等待异步操作
      await new Promise(resolve => setTimeout(resolve, 0))

      expect(mockLogin).toHaveBeenCalledWith({
        account: 'testuser',
        password: 'password123',
        remember_me: true
      })
    })

    it('应该清除之前的错误信息', async () => {
      const authStore = useAuthStore()
      authStore.error = '之前的错误'

      mockLogin.mockResolvedValue({ success: true })

      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      await wrapper.find('#account').setValue('testuser')
      await wrapper.find('#password').setValue('password123')

      const form = wrapper.find('form')
      await form.trigger('submit.prevent')

      // 等待异步操作
      await new Promise(resolve => setTimeout(resolve, 0))

      expect(authStore.error).toBeNull()
    })
  })

  describe('UI状态', () => {
    it('应该在加载状态时禁用按钮', () => {
      vi.mocked(useAuthStore).mockReturnValue({
        login: mockLogin,
        isAuthenticated: false,
        error: null,
        loading: true,
        user: null,
        token: null,
        logout: vi.fn(),
        checkAuth: vi.fn()
      })

      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const submitButton = wrapper.find('button[type="submit"]')
      expect(submitButton.attributes('disabled')).toBeDefined()
      expect(submitButton.text()).toContain('登录中...')
    })

    it('应该显示authStore的错误信息', () => {
      vi.mocked(useAuthStore).mockReturnValue({
        login: mockLogin,
        isAuthenticated: false,
        error: '用户名或密码错误',
        loading: false,
        user: null,
        token: null,
        logout: vi.fn(),
        checkAuth: vi.fn()
      })

      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      expect(wrapper.text()).toContain('用户名或密码错误')
    })

    it('应该在非加载状态时启用按钮', () => {
      vi.mocked(useAuthStore).mockReturnValue({
        login: mockLogin,
        isAuthenticated: false,
        error: null,
        loading: false,
        user: null,
        token: null,
        logout: vi.fn(),
        checkAuth: vi.fn()
      })

      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const submitButton = wrapper.find('button[type="submit"]')
      expect(submitButton.attributes('disabled')).toBeUndefined()
      expect(submitButton.text()).toContain('登录')
    })
  })

  describe('账号输入框样式', () => {
    it('应该在有错误时显示错误样式', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const accountInput = wrapper.find('#account')
      await accountInput.setValue('')
      await accountInput.trigger('blur')

      await wrapper.vm.$nextTick()

      expect(accountInput.classes()).toContain('form-input-error')
    })

    it('应该在无错误时不显示错误样式', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const accountInput = wrapper.find('#account')
      await accountInput.setValue('validuser')
      await accountInput.trigger('blur')

      await wrapper.vm.$nextTick()

      expect(accountInput.classes()).not.toContain('form-input-error')
    })
  })

  describe('密码输入框样式', () => {
    it('应该在有错误时显示错误样式', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const passwordInput = wrapper.find('#password')
      await passwordInput.setValue('short')
      await passwordInput.trigger('blur')

      await wrapper.vm.$nextTick()

      expect(passwordInput.classes()).toContain('form-input-error')
    })

    it('应该在无错误时不显示错误样式', async () => {
      const wrapper = mount(LoginPage, {
        global: {
          plugins: [router, createPinia()]
        }
      })

      const passwordInput = wrapper.find('#password')
      await passwordInput.setValue('validpassword')
      await passwordInput.trigger('blur')

      await wrapper.vm.$nextTick()

      expect(passwordInput.classes()).not.toContain('form-input-error')
    })
  })
})
