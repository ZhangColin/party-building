/**
 * authStore 单元测试
 * 测试认证状态管理的所有功能
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/authStore'

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString()
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
  }
})()

// Mock sessionStorage
const sessionStorageMock = (() => {
  let store: Record<string, string> = {}

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString()
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
  }
})()

// Mock ApiService
vi.mock('@/services/apiClient', () => ({
  ApiService: {
    login: vi.fn(),
    getCurrentUser: vi.fn(),
  },
}))

describe('authStore - 初始化状态测试', () => {
  beforeEach(() => {
    // 清除所有存储
    localStorageMock.clear()
    sessionStorageMock.clear()
    // 每个测试前创建新的pinia实例
    setActivePinia(createPinia())
  })

  it('应该初始化为空状态', () => {
    const store = useAuthStore()

    expect(store.token).toBe(null)
    expect(store.user).toBe(null)
    expect(store.loading).toBe(false)
    expect(store.error).toBe(null)
    expect(store.isAuthenticated).toBe(false)
  })
})

describe('authStore - restoreAuth测试', () => {
  beforeEach(() => {
    localStorageMock.clear()
    sessionStorageMock.clear()
    setActivePinia(createPinia())

    // 模拟浏览器存储
    global.localStorage = localStorageMock as any
    global.sessionStorage = sessionStorageMock as any
  })

  it('应该从localStorage恢复认证信息', () => {
    const store = useAuthStore()

    // 设置localStorage
    const testToken = 'test-token-from-local'
    const testUser = { id: 1, username: 'testuser', is_admin: false }
    localStorage.setItem('auth_token', testToken)
    localStorage.setItem('auth_user', JSON.stringify(testUser))

    // 调用restoreAuth
    store.restoreAuth()

    // 验证恢复成功
    expect(store.token).toBe(testToken)
    expect(store.user).toEqual(testUser)
    expect(store.isAuthenticated).toBe(true)
  })

  it('应该从sessionStorage恢复认证信息（当localStorage为空时）', () => {
    const store = useAuthStore()

    // 设置sessionStorage
    const testToken = 'test-token-from-session'
    const testUser = { id: 2, username: 'sessionuser', is_admin: true }
    sessionStorage.setItem('auth_token', testToken)
    sessionStorage.setItem('auth_user', JSON.stringify(testUser))

    // 调用restoreAuth
    store.restoreAuth()

    // 验证恢复成功
    expect(store.token).toBe(testToken)
    expect(store.user).toEqual(testUser)
    expect(store.isAuthenticated).toBe(true)
  })

  it('localStorage优先于sessionStorage', () => {
    const store = useAuthStore()

    // 同时设置两个存储
    const localToken = 'local-token'
    const localUser = { id: 1, username: 'localuser', is_admin: false }
    localStorage.setItem('auth_token', localToken)
    localStorage.setItem('auth_user', JSON.stringify(localUser))

    const sessionToken = 'session-token'
    const sessionUser = { id: 2, username: 'sessionuser', is_admin: true }
    sessionStorage.setItem('auth_token', sessionToken)
    sessionStorage.setItem('auth_user', JSON.stringify(sessionUser))

    // 调用restoreAuth
    store.restoreAuth()

    // 应该使用localStorage的数据
    expect(store.token).toBe(localToken)
    expect(store.user).toEqual(localUser)
  })

  it('应该处理localStorage中无效的JSON', () => {
    const store = useAuthStore()

    // 设置无效的JSON
    localStorage.setItem('auth_token', 'test-token')
    localStorage.setItem('auth_user', 'invalid-json{')

    // 调用restoreAuth（不应该抛出错误）
    expect(() => store.restoreAuth()).not.toThrow()

    // token应该被设置，但user应该是null
    expect(store.token).toBe('test-token')
    expect(store.user).toBe(null)
  })

  it('应该处理sessionStorage中无效的JSON', () => {
    const store = useAuthStore()

    // 设置无效的JSON
    sessionStorage.setItem('auth_token', 'test-token')
    sessionStorage.setItem('auth_user', 'invalid-json{')

    // 调用restoreAuth（不应该抛出错误）
    expect(() => store.restoreAuth()).not.toThrow()

    // token应该被设置，但user应该是null
    expect(store.token).toBe('test-token')
    expect(store.user).toBe(null)
  })

  it('应该跳过只有token没有user的localStorage数据', () => {
    const store = useAuthStore()

    // 只设置token（不设置user）
    localStorage.setItem('auth_token', 'test-token')

    // 调用restoreAuth
    store.restoreAuth()

    // 因为没有user，所以localStorage的token应该被忽略
    expect(store.token).toBe(null)
    expect(store.user).toBe(null)
  })

  it('应该处理空存储', () => {
    const store = useAuthStore()

    // 不设置任何存储
    store.restoreAuth()

    // 所有状态应该保持为null
    expect(store.token).toBe(null)
    expect(store.user).toBe(null)
    expect(store.isAuthenticated).toBe(false)
  })
})

describe('authStore - login测试', () => {
  beforeEach(() => {
    localStorageMock.clear()
    sessionStorageMock.clear()
    setActivePinia(createPinia())
    global.localStorage = localStorageMock as any
    global.sessionStorage = sessionStorageMock as any
  })

  it('应该成功登录并保存到localStorage（记住我）', async () => {
    const store = useAuthStore()
    const { ApiService } = await import('@/services/apiClient')

    const mockResponse = {
      token: 'new-token',
      user: { id: 1, username: 'testuser', is_admin: false },
    }
    vi.mocked(ApiService.login).mockResolvedValue(mockResponse)

    const loginRequest = {
      username: 'testuser',
      password: 'password123',
      remember_me: true,
    }

    const response = await store.login(loginRequest)

    // 验证返回值
    expect(response).toEqual(mockResponse)

    // 验证状态
    expect(store.token).toBe('new-token')
    expect(store.user).toEqual(mockResponse.user)
    expect(store.loading).toBe(false)
    expect(store.error).toBe(null)

    // 验证保存到localStorage
    expect(localStorage.getItem('auth_token')).toBe('new-token')
    expect(localStorage.getItem('auth_user')).toBe(JSON.stringify(mockResponse.user))

    // 验证sessionStorage被清除
    expect(sessionStorage.getItem('auth_token')).toBe(null)
    expect(sessionStorage.getItem('auth_user')).toBe(null)
  })

  it('应该成功登录并保存到sessionStorage（不记住我）', async () => {
    const store = useAuthStore()
    const { ApiService } = await import('@/services/apiClient')

    const mockResponse = {
      token: 'new-token',
      user: { id: 1, username: 'testuser', is_admin: false },
    }
    vi.mocked(ApiService.login).mockResolvedValue(mockResponse)

    const loginRequest = {
      username: 'testuser',
      password: 'password123',
      remember_me: false,
    }

    await store.login(loginRequest)

    // 验证保存到sessionStorage
    expect(sessionStorage.getItem('auth_token')).toBe('new-token')
    expect(sessionStorage.getItem('auth_user')).toBe(JSON.stringify(mockResponse.user))

    // 验证localStorage被清除
    expect(localStorage.getItem('auth_token')).toBe(null)
    expect(localStorage.getItem('auth_user')).toBe(null)
  })

  it('应该处理登录失败', async () => {
    const store = useAuthStore()
    const { ApiService } = await import('@/services/apiClient')

    const mockError = new Error('用户名或密码错误')
    vi.mocked(ApiService.login).mockRejectedValue(mockError)

    const loginRequest = {
      username: 'wronguser',
      password: 'wrongpassword',
      remember_me: false,
    }

    // 应该抛出错误
    await expect(store.login(loginRequest)).rejects.toThrow('用户名或密码错误')

    // 验证状态
    expect(store.token).toBe(null)
    expect(store.user).toBe(null)
    expect(store.loading).toBe(false)
    expect(store.error).toBe('用户名或密码错误')
  })

  it('应该处理非Error类型的登录失败', async () => {
    const store = useAuthStore()
    const { ApiService } = await import('@/services/apiClient')

    vi.mocked(ApiService.login).mockRejectedValue('网络错误')

    const loginRequest = {
      username: 'testuser',
      password: 'password',
      remember_me: false,
    }

    // 应该抛出错误
    await expect(store.login(loginRequest)).rejects.toEqual('网络错误')

    // 验证错误消息
    expect(store.error).toBe('登录失败')
  })

  it('登录时应该清除旧的localStorage数据（记住我）', async () => {
    const store = useAuthStore()
    const { ApiService } = await import('@/services/apiClient')

    // 先设置旧的sessionStorage数据
    sessionStorage.setItem('auth_token', 'old-session-token')
    sessionStorage.setItem('auth_user', JSON.stringify({ id: 99, username: 'old', is_admin: false }))

    const mockResponse = {
      token: 'new-token',
      user: { id: 1, username: 'testuser', is_admin: false },
    }
    vi.mocked(ApiService.login).mockResolvedValue(mockResponse)

    const loginRequest = {
      username: 'testuser',
      password: 'password',
      remember_me: true,
    }

    await store.login(loginRequest)

    // 验证sessionStorage被清除
    expect(sessionStorage.getItem('auth_token')).toBe(null)
    expect(sessionStorage.getItem('auth_user')).toBe(null)
  })

  it('登录时应该清除旧的sessionStorage数据（不记住我）', async () => {
    const store = useAuthStore()
    const { ApiService } = await import('@/services/apiClient')

    // 先设置旧的localStorage数据
    localStorage.setItem('auth_token', 'old-local-token')
    localStorage.setItem('auth_user', JSON.stringify({ id: 99, username: 'old', is_admin: false }))

    const mockResponse = {
      token: 'new-token',
      user: { id: 1, username: 'testuser', is_admin: false },
    }
    vi.mocked(ApiService.login).mockResolvedValue(mockResponse)

    const loginRequest = {
      username: 'testuser',
      password: 'password',
      remember_me: false,
    }

    await store.login(loginRequest)

    // 验证localStorage被清除
    expect(localStorage.getItem('auth_token')).toBe(null)
    expect(localStorage.getItem('auth_user')).toBe(null)
  })
})

describe('authStore - logout测试', () => {
  beforeEach(() => {
    localStorageMock.clear()
    sessionStorageMock.clear()
    setActivePinia(createPinia())
    global.localStorage = localStorageMock as any
    global.sessionStorage = sessionStorageMock as any
  })

  it('应该清除所有认证状态', () => {
    const store = useAuthStore()

    // 先设置认证状态
    store.token = 'test-token'
    store.user = { id: 1, username: 'testuser', is_admin: false }
    localStorage.setItem('auth_token', 'test-token')
    localStorage.setItem('auth_user', JSON.stringify({ id: 1, username: 'testuser', is_admin: false }))
    sessionStorage.setItem('auth_token', 'session-token')
    sessionStorage.setItem('auth_user', JSON.stringify({ id: 2, username: 'sessionuser', is_admin: true }))

    // 调用logout
    store.logout()

    // 验证状态被清除
    expect(store.token).toBe(null)
    expect(store.user).toBe(null)
    expect(store.isAuthenticated).toBe(false)

    // 验证localStorage被清除
    expect(localStorage.getItem('auth_token')).toBe(null)
    expect(localStorage.getItem('auth_user')).toBe(null)

    // 验证sessionStorage被清除
    expect(sessionStorage.getItem('auth_token')).toBe(null)
    expect(sessionStorage.getItem('auth_user')).toBe(null)
  })

  it('应该允许重复调用logout', () => {
    const store = useAuthStore()

    // 第一次logout
    store.logout()

    // 第二次logout（不应该抛出错误）
    expect(() => store.logout()).not.toThrow()

    expect(store.token).toBe(null)
    expect(store.user).toBe(null)
  })
})

describe('authStore - verifyToken测试', () => {
  beforeEach(() => {
    localStorageMock.clear()
    sessionStorageMock.clear()
    setActivePinia(createPinia())
    global.localStorage = localStorageMock as any
    global.sessionStorage = sessionStorageMock as any
  })

  it('应该在token为空时返回false', async () => {
    const store = useAuthStore()

    const result = await store.verifyToken()

    expect(result).toBe(false)
  })

  it('应该成功验证token并更新用户信息', async () => {
    const store = useAuthStore()
    const { ApiService } = await import('@/services/apiClient')

    // 设置初始token
    store.token = 'test-token'
    localStorage.setItem('auth_token', 'test-token')
    localStorage.setItem('auth_user', JSON.stringify({ id: 1, username: 'olduser', is_admin: false }))

    const updatedUser = { id: 1, username: 'updateduser', is_admin: true }
    vi.mocked(ApiService.getCurrentUser).mockResolvedValue({ user: updatedUser } as any)

    const result = await store.verifyToken()

    expect(result).toBe(true)
    expect(store.user).toEqual(updatedUser)

    // 验证localStorage中的用户信息被更新
    expect(localStorage.getItem('auth_user')).toBe(JSON.stringify(updatedUser))
  })

  it('应该成功验证token并更新sessionStorage中的用户信息', async () => {
    const store = useAuthStore()
    const { ApiService } = await import('@/services/apiClient')

    // 设置初始token在sessionStorage
    store.token = 'test-token'
    sessionStorage.setItem('auth_token', 'test-token')
    sessionStorage.setItem('auth_user', JSON.stringify({ id: 1, username: 'olduser', is_admin: false }))

    const updatedUser = { id: 1, username: 'updateduser', is_admin: true }
    vi.mocked(ApiService.getCurrentUser).mockResolvedValue({ user: updatedUser } as any)

    const result = await store.verifyToken()

    expect(result).toBe(true)
    expect(store.user).toEqual(updatedUser)

    // 验证sessionStorage中的用户信息被更新
    expect(sessionStorage.getItem('auth_user')).toBe(JSON.stringify(updatedUser))
  })

  it('应该在token不匹配时不更新存储', async () => {
    const store = useAuthStore()
    const { ApiService } = await import('@/services/apiClient')

    // 设置不同的token
    store.token = 'current-token'
    localStorage.setItem('auth_token', 'different-token')
    localStorage.setItem('auth_user', JSON.stringify({ id: 1, username: 'olduser', is_admin: false }))

    const updatedUser = { id: 1, username: 'updateduser', is_admin: true }
    vi.mocked(ApiService.getCurrentUser).mockResolvedValue({ user: updatedUser } as any)

    const result = await store.verifyToken()

    expect(result).toBe(true)
    expect(store.user).toEqual(updatedUser)

    // 验证localStorage中的用户信息没有被更新（因为token不匹配）
    expect(localStorage.getItem('auth_user')).toBe(JSON.stringify({ id: 1, username: 'olduser', is_admin: false }))
  })

  it('应该在token验证失败时清除认证状态', async () => {
    const store = useAuthStore()
    const { ApiService } = await import('@/services/apiClient')

    // 设置初始状态
    store.token = 'invalid-token'
    store.user = { id: 1, username: 'testuser', is_admin: false }
    localStorage.setItem('auth_token', 'invalid-token')
    localStorage.setItem('auth_user', JSON.stringify({ id: 1, username: 'testuser', is_admin: false }))

    // Mock验证失败
    vi.mocked(ApiService.getCurrentUser).mockRejectedValue(new Error('Token已过期'))

    const result = await store.verifyToken()

    expect(result).toBe(false)

    // 验证状态被清除（通过logout）
    expect(store.token).toBe(null)
    expect(store.user).toBe(null)
    expect(store.isAuthenticated).toBe(false)

    // 验证存储被清除
    expect(localStorage.getItem('auth_token')).toBe(null)
    expect(localStorage.getItem('auth_user')).toBe(null)
  })

  it('应该在sessionStorage有token且localStorage为空时更新sessionStorage', async () => {
    const store = useAuthStore()
    const { ApiService } = await import('@/services/apiClient')

    // 只设置sessionStorage，确保localStorage完全为空
    store.token = 'session-token'
    sessionStorage.setItem('auth_token', 'session-token')
    sessionStorage.setItem('auth_user', JSON.stringify({ id: 1, username: 'olduser', is_admin: false }))

    // 不设置localStorage，确保localStorage.getItem返回null

    const updatedUser = { id: 1, username: 'updateduser', is_admin: true }
    vi.mocked(ApiService.getCurrentUser).mockResolvedValue({ user: updatedUser } as any)

    const result = await store.verifyToken()

    expect(result).toBe(true)
    expect(store.user).toEqual(updatedUser)

    // 验证sessionStorage中的用户信息被更新（触发第117行）
    expect(sessionStorage.getItem('auth_user')).toBe(JSON.stringify(updatedUser))
    // 验证localStorage没有被修改
    expect(localStorage.getItem('auth_token')).toBe(null)
    expect(localStorage.getItem('auth_user')).toBe(null)
  })
})

describe('authStore - fetchUserInfo测试', () => {
  beforeEach(() => {
    localStorageMock.clear()
    sessionStorageMock.clear()
    setActivePinia(createPinia())
    global.localStorage = localStorageMock as any
    global.sessionStorage = sessionStorageMock as any
  })

  it('应该成功获取用户信息', async () => {
    const store = useAuthStore()
    const { ApiService } = await import('@/services/apiClient')

    store.token = 'test-token'
    localStorage.setItem('auth_token', 'test-token')

    const user = { id: 1, username: 'testuser', is_admin: false }
    vi.mocked(ApiService.getCurrentUser).mockResolvedValue({ user } as any)

    await store.fetchUserInfo()

    expect(store.user).toEqual(user)
  })

  it('应该在token为空时返回false', async () => {
    const store = useAuthStore()

    // fetchUserInfo是verifyToken的别名，应该返回false
    await expect(store.fetchUserInfo()).resolves.toBeUndefined()
  })
})

describe('authStore - 计算属性测试', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('isAuthenticated应该在有token时返回true', () => {
    const store = useAuthStore()

    expect(store.isAuthenticated).toBe(false)

    store.token = 'test-token'
    expect(store.isAuthenticated).toBe(true)
  })

  it('isAuthenticated应该在token为空字符串时返回false', () => {
    const store = useAuthStore()

    store.token = ''
    expect(store.isAuthenticated).toBe(false)
  })

  it('isAuthenticated应该在token为null时返回false', () => {
    const store = useAuthStore()

    store.token = null
    expect(store.isAuthenticated).toBe(false)
  })
})

describe('authStore - 边界情况测试', () => {
  beforeEach(() => {
    localStorageMock.clear()
    sessionStorageMock.clear()
    setActivePinia(createPinia())
    global.localStorage = localStorageMock as any
    global.sessionStorage = sessionStorageMock as any
  })

  it('应该处理restoreAuth时localStorage和sessionStorage都没有token', () => {
    const store = useAuthStore()

    localStorage.setItem('auth_user', JSON.stringify({ id: 1, username: 'user', is_admin: false }))
    sessionStorage.setItem('auth_user', JSON.stringify({ id: 2, username: 'user2', is_admin: true }))

    store.restoreAuth()

    // 应该没有token
    expect(store.token).toBe(null)
    // user应该也不被设置（因为需要同时有token和user）
    expect(store.user).toBe(null)
  })

  it('应该跳过localStorage只有token没有user的情况', () => {
    const store = useAuthStore()

    localStorage.setItem('auth_token', 'test-token')
    // 不设置auth_user

    store.restoreAuth()

    // 因为没有user，所以token应该被忽略
    expect(store.token).toBe(null)
    expect(store.user).toBe(null)
  })

  it('应该跳过sessionStorage只有token没有user的情况', () => {
    const store = useAuthStore()

    sessionStorage.setItem('auth_token', 'test-token')
    // 不设置auth_user

    store.restoreAuth()

    // 因为没有user，所以token应该被忽略
    expect(store.token).toBe(null)
    expect(store.user).toBe(null)
  })
})
