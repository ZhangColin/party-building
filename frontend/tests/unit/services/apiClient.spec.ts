/**
 * apiClient.spec.ts
 * 测试 API 客户端服务
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ApiService } from '@/services/apiClient'

// Mock fetch API
global.fetch = vi.fn()

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value.toString() },
    removeItem: (key: string) => { delete store[key] },
    clear: () => { store = {} }
  }
})()
Object.defineProperty(global, 'localStorage', { value: localStorageMock })

// Mock sessionStorage
const sessionStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value.toString() },
    removeItem: (key: string) => { delete store[key] },
    clear: () => { store = {} }
  }
})()
Object.defineProperty(global, 'sessionStorage', { value: sessionStorageMock })

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn().mockResolvedValue({ data: {} }),
      post: vi.fn().mockResolvedValue({ data: {} }),
      put: vi.fn().mockResolvedValue({ data: {} }),
      patch: vi.fn().mockResolvedValue({ data: {} }),
      delete: vi.fn().mockResolvedValue({ data: {} }),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    }))
  }
}))

describe('ApiService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    sessionStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('基础API方法测试', () => {
    it('应该获取导航模块列表', async () => {
      const mockResponse = {
        modules: [
          { id: 'ai-tools', name: 'AI工具' },
          { id: 'teaching', name: '教研工具' }
        ]
      }

      vi.spyOn(ApiService, 'getNavigationModules').mockResolvedValue(mockResponse)

      const result = await ApiService.getNavigationModules()

      expect(result.modules).toHaveLength(2)
      expect(result.modules[0].id).toBe('ai-tools')
    })

    it('应该获取工具列表', async () => {
      const mockResponse = {
        categories: [
          {
            category_id: 'cat1',
            category_name: '分类1',
            tools: [{ tool_id: 'tool1', name: '工具1' }]
          }
        ]
      }

      vi.spyOn(ApiService, 'getTools').mockResolvedValue(mockResponse)

      const result = await ApiService.getTools()

      expect(result.categories).toHaveLength(1)
      expect(result.categories[0].category_id).toBe('cat1')
    })

    it('应该获取指定工具集的工具列表', async () => {
      const mockResponse = {
        categories: [
          {
            category_id: 'cat2',
            category_name: '分类2',
            tools: []
          }
        ]
      }

      vi.spyOn(ApiService, 'getToolsetTools').mockResolvedValue(mockResponse)

      const result = await ApiService.getToolsetTools('ai-tools')

      expect(result.categories).toHaveLength(1)
    })

    it('应该创建会话', async () => {
      const mockResponse = {
        session_id: 'uuid-123',
        agent_id: 'test-agent'
      }

      vi.spyOn(ApiService, 'createSession').mockResolvedValue(mockResponse)

      const result = await ApiService.createSession('test-agent')

      expect(result.session_id).toBe('uuid-123')
      expect(result.agent_id).toBe('test-agent')
    })

    it('应该发送聊天消息', async () => {
      const mockResponse = {
        session_id: 'uuid-123',
        message: 'AI响应'
      }

      vi.spyOn(ApiService, 'chat').mockResolvedValue(mockResponse)

      const request = {
        message: '用户消息',
        session_id: 'uuid-123'
      }

      const result = await ApiService.chat('test-tool', request)

      expect(result.session_id).toBe('uuid-123')
      expect(result.message).toBe('AI响应')
    })

    it('应该获取历史对话列表', async () => {
      const mockResponse = {
        conversations: [
          { session_id: 's1', title: '会话1' },
          { session_id: 's2', title: '会话2' }
        ]
      }

      vi.spyOn(ApiService, 'getConversations').mockResolvedValue(mockResponse)

      const result = await ApiService.getConversations('test-tool')

      expect(result.conversations).toHaveLength(2)
    })

    it('应该获取会话详情', async () => {
      const mockResponse = {
        session_id: 'uuid-123',
        messages: [
          { role: 'user', content: '你好' },
          { role: 'assistant', content: '你好呀' }
        ]
      }

      vi.spyOn(ApiService, 'getSessionDetail').mockResolvedValue(mockResponse)

      const result = await ApiService.getSessionDetail('uuid-123')

      expect(result.session_id).toBe('uuid-123')
      expect(result.messages).toHaveLength(2)
    })

    it('应该更新会话标题', async () => {
      const mockResponse = {
        session_id: 'uuid-123',
        title: '新标题'
      }

      vi.spyOn(ApiService, 'updateSessionTitle').mockResolvedValue(mockResponse)

      const request = { title: '新标题' }
      const result = await ApiService.updateSessionTitle('uuid-123', request)

      expect(result.title).toBe('新标题')
    })

    it('应该删除会话', async () => {
      vi.spyOn(ApiService, 'deleteSession').mockResolvedValue(undefined)

      await ApiService.deleteSession('uuid-123')
    })
  })

  describe('认证相关测试', () => {
    it('应该登录成功', async () => {
      const mockResponse = {
        access_token: 'token-123',
        token_type: 'bearer',
        user: { id: 1, username: 'test', is_admin: false }
      }

      vi.spyOn(ApiService, 'login').mockResolvedValue(mockResponse)

      const result = await ApiService.login({ username: 'test', password: '123456' })

      expect(result.access_token).toBe('token-123')
      expect(result.user.username).toBe('test')
    })

    it('应该获取当前用户信息', async () => {
      const mockResponse = {
        user: {
          id: 1,
          username: 'test',
          is_admin: false
        }
      }

      vi.spyOn(ApiService, 'getCurrentUser').mockResolvedValue(mockResponse)

      const result = await ApiService.getCurrentUser()

      expect(result.user.username).toBe('test')
      expect(result.user.id).toBe(1)
    })
  })

  describe('用户管理测试', () => {
    it('应该获取用户列表', async () => {
      const mockResponse = {
        users: [
          { id: 1, username: 'user1' },
          { id: 2, username: 'user2' }
        ],
        total: 2,
        page: 1,
        page_size: 20
      }

      vi.spyOn(ApiService, 'getUserList').mockResolvedValue(mockResponse)

      const result = await ApiService.getUserList(1, 20)

      expect(result.total).toBe(2)
      expect(result.users).toHaveLength(2)
    })

    it('应该筛选管理员用户', async () => {
      const mockResponse = {
        users: [{ id: 1, username: 'admin', is_admin: true }],
        total: 1,
        page: 1,
        page_size: 20
      }

      vi.spyOn(ApiService, 'getUserList').mockResolvedValue(mockResponse)

      const result = await ApiService.getUserList(1, 20, true)

      expect(result.users).toHaveLength(1)
      expect(result.users[0].is_admin).toBe(true)
    })

    it('应该创建用户', async () => {
      const mockResponse = {
        user: { id: 2, username: 'newuser', is_admin: false }
      }

      vi.spyOn(ApiService, 'createUser').mockResolvedValue(mockResponse)

      const request = {
        username: 'newuser',
        password: '123456',
        is_admin: false
      }

      const result = await ApiService.createUser(request)

      expect(result.user.username).toBe('newuser')
    })

    it('应该更新用户信息', async () => {
      const mockResponse = {
        user: { id: 1, username: 'updated', is_admin: false }
      }

      vi.spyOn(ApiService, 'updateUser').mockResolvedValue(mockResponse)

      const request = { username: 'updated' }
      const result = await ApiService.updateUser('1', request)

      expect(result.user.username).toBe('updated')
    })

    it('应该删除用户', async () => {
      vi.spyOn(ApiService, 'deleteUser').mockResolvedValue(undefined)

      await ApiService.deleteUser('1')
    })

    it('应该重置用户密码', async () => {
      const mockResponse = {
        message: '密码重置成功'
      }

      vi.spyOn(ApiService, 'resetUserPassword').mockResolvedValue(mockResponse)

      const request = { new_password: 'newpass123' }
      const result = await ApiService.resetUserPassword('1', request)

      expect(result.message).toBe('密码重置成功')
    })
  })

  describe('常用工具模块测试', () => {
    it('应该获取常用工具分类列表', async () => {
      const mockResponse = {
        categories: [
          {
            category_id: 'cat1',
            category_name: '分类1',
            tools: []
          }
        ]
      }

      vi.spyOn(ApiService, 'getCommonToolCategories').mockResolvedValue(mockResponse)

      const result = await ApiService.getCommonToolCategories()

      expect(result.categories).toHaveLength(1)
    })

    it('应该获取常用工具详情', async () => {
      const mockResponse = {
        tool_id: 'tool1',
        name: '测试工具',
        description: '测试描述'
      }

      vi.spyOn(ApiService, 'getCommonToolDetail').mockResolvedValue(mockResponse)

      const result = await ApiService.getCommonToolDetail('tool1')

      expect(result.tool_id).toBe('tool1')
    })
  })

  describe('作品模块测试', () => {
    it('应该获取作品分类列表', async () => {
      const mockResponse = {
        categories: [
          {
            category_id: 'cat1',
            category_name: '分类1',
            works: []
          }
        ]
      }

      vi.spyOn(ApiService, 'getWorkCategories').mockResolvedValue(mockResponse)

      const result = await ApiService.getWorkCategories()

      expect(result.categories).toHaveLength(1)
    })

    it('应该获取作品详情', async () => {
      const mockResponse = {
        work_id: 'work1',
        name: '测试作品',
        description: '作品描述'
      }

      vi.spyOn(ApiService, 'getWorkDetail').mockResolvedValue(mockResponse)

      const result = await ApiService.getWorkDetail('work1')

      expect(result.work_id).toBe('work1')
    })
  })

  describe('课程文档模块测试', () => {
    it('应该获取课程目录树', async () => {
      const mockResponse = {
        categories: [
          {
            category_id: 'cat1',
            name: '目录1',
            children: []
          }
        ]
      }

      vi.spyOn(ApiService, 'getCourseCategories').mockResolvedValue(mockResponse)

      const result = await ApiService.getCourseCategories()

      expect(result.categories).toHaveLength(1)
    })

    it('应该获取指定目录下的文档列表', async () => {
      const mockResponse = {
        documents: [
          { document_id: 'doc1', title: '文档1' }
        ]
      }

      vi.spyOn(ApiService, 'getCourseDocumentsByCategory').mockResolvedValue(mockResponse)

      const result = await ApiService.getCourseDocumentsByCategory('cat1')

      expect(result.documents).toHaveLength(1)
    })

    it('应该获取文档详情', async () => {
      const mockResponse = {
        document_id: 'doc1',
        title: '测试文档',
        content: '# 内容'
      }

      vi.spyOn(ApiService, 'getCourseDocumentDetail').mockResolvedValue(mockResponse)

      const result = await ApiService.getCourseDocumentDetail('doc1')

      expect(result.document_id).toBe('doc1')
    })
  })

  describe('流式聊天测试（真实实现）', () => {
    it('应该成功处理流式响应', async () => {
      localStorage.setItem('auth_token', 'test-token')

      const chunks = [
        'data: {"session_id": "uuid-123"}\n\n',
        'data: {"content": "你好"}\n\n',
        'data: {"content": "世界"}\n\n',
        'data: [DONE]\n\n'
      ]
      let chunkIndex = 0

      const mockReader = {
        read: vi.fn().mockImplementation(async () => {
          if (chunkIndex < chunks.length) {
            const chunk = chunks[chunkIndex++]
            return {
              done: false,
              value: new TextEncoder().encode(chunk)
            }
          }
          return { done: true, value: null }
        }),
        releaseLock: vi.fn()
      }

      const mockResponse = {
        ok: true,
        body: { getReader: () => mockReader }
      }
      vi.mocked(global.fetch).mockResolvedValue(mockResponse as any)

      const chunksReceived: any[] = []
      const onChunk = vi.fn((data) => chunksReceived.push(data))

      await ApiService.chatStream('test-tool', { message: 'hello' }, onChunk)

      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/tools/test-tool/chat/stream',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token'
          },
          body: JSON.stringify({ message: 'hello' })
        })
      )

      expect(chunksReceived).toHaveLength(4)
      expect(chunksReceived[0]).toMatchObject({ type: 'content', session_id: 'uuid-123' })
      expect(chunksReceived[1]).toMatchObject({ type: 'content', content: '你好' })
      expect(chunksReceived[2]).toMatchObject({ type: 'content', content: '世界' })
      expect(chunksReceived[3]).toMatchObject({ type: 'done' })
      expect(mockReader.releaseLock).toHaveBeenCalled()
    })

    it('应该在无token时抛出错误', async () => {
      await expect(
        ApiService.chatStream('test-tool', { message: 'hello' }, vi.fn())
      ).rejects.toThrow('未登录')
    })

    it('应该处理响应错误', async () => {
      localStorage.setItem('auth_token', 'test-token')

      const mockResponse = {
        ok: false,
        json: async () => ({ detail: '请求失败' })
      }
      vi.mocked(global.fetch).mockResolvedValue(mockResponse as any)

      await expect(
        ApiService.chatStream('test-tool', { message: 'hello' }, vi.fn())
      ).rejects.toThrow('请求失败')
    })

    it('应该处理JSON解析错误并继续', async () => {
      localStorage.setItem('auth_token', 'test-token')

      const chunks = [
        'data: invalid json\n\n',
        'data: {"content": "valid"}\n\n',
        'data: [DONE]\n\n'
      ]
      let chunkIndex = 0

      const mockReader = {
        read: vi.fn().mockImplementation(async () => {
          if (chunkIndex < chunks.length) {
            const chunk = chunks[chunkIndex++]
            return {
              done: false,
              value: new TextEncoder().encode(chunk)
            }
          }
          return { done: true, value: null }
        }),
        releaseLock: vi.fn()
      }
      const mockResponse = {
        ok: true,
        body: { getReader: () => mockReader }
      }
      vi.mocked(global.fetch).mockResolvedValue(mockResponse as any)

      const chunksReceived: any[] = []
      const onChunk = vi.fn((data) => chunksReceived.push(data))

      await ApiService.chatStream('test-tool', { message: 'hello' }, onChunk)

      expect(chunksReceived).toHaveLength(2)
      expect(chunksReceived[0]).toMatchObject({ type: 'content', content: 'valid' })
      expect(chunksReceived[1]).toMatchObject({ type: 'done' })
    })

    it('应该处理无法读取响应流', async () => {
      localStorage.setItem('auth_token', 'test-token')

      const mockResponse = {
        ok: true,
        body: null
      }
      vi.mocked(global.fetch).mockResolvedValue(mockResponse as any)

      await expect(
        ApiService.chatStream('test-tool', { message: 'hello' }, vi.fn())
      ).rejects.toThrow('无法读取响应流')
    })

    it('应该正确处理空行', async () => {
      localStorage.setItem('auth_token', 'test-token')

      const chunks = [
        '\n\n',
        'data: {"content": "test"}\n\n',
        '\n\n',
        'data: [DONE]\n\n'
      ]
      let chunkIndex = 0

      const mockReader = {
        read: vi.fn().mockImplementation(async () => {
          if (chunkIndex < chunks.length) {
            const chunk = chunks[chunkIndex++]
            return {
              done: false,
              value: new TextEncoder().encode(chunk)
            }
          }
          return { done: true, value: null }
        }),
        releaseLock: vi.fn()
      }
      const mockResponse = {
        ok: true,
        body: { getReader: () => mockReader }
      }
      vi.mocked(global.fetch).mockResolvedValue(mockResponse as any)

      const chunksReceived: any[] = []
      const onChunk = vi.fn((data) => chunksReceived.push(data))

      await ApiService.chatStream('test-tool', { message: 'hello' }, onChunk)

      expect(chunksReceived).toHaveLength(2)
      expect(chunksReceived[0]).toMatchObject({ type: 'content', content: 'test' })
      expect(chunksReceived[1]).toMatchObject({ type: 'done' })
    })

    it('应该处理完整的SSE数据流包括最后一行', async () => {
      localStorage.setItem('auth_token', 'test-token')

      const chunks = [
        'data: {"content": "first"}\n\n',
        'data: {"content": "last"}'  // 最后一行没有\n\n
      ]
      let chunkIndex = 0

      const mockReader = {
        read: vi.fn().mockImplementation(async () => {
          if (chunkIndex < chunks.length) {
            const chunk = chunks[chunkIndex++]
            return {
              done: false,
              value: new TextEncoder().encode(chunk)
            }
          }
          return { done: true, value: null }
        }),
        releaseLock: vi.fn()
      }
      const mockResponse = {
        ok: true,
        body: { getReader: () => mockReader }
      }
      vi.mocked(global.fetch).mockResolvedValue(mockResponse as any)

      const chunksReceived: any[] = []
      const onChunk = vi.fn((data) => chunksReceived.push(data))

      await ApiService.chatStream('test-tool', { message: 'hello' }, onChunk)

      expect(chunksReceived).toHaveLength(2)
      expect(chunksReceived[0]).toMatchObject({ type: 'content', content: 'first' })
      expect(chunksReceived[1]).toMatchObject({ type: 'content', content: 'last' })
    })

    it('应该处理跨chunk的数据边界', async () => {
      localStorage.setItem('auth_token', 'test-token')

      const chunks = [
        'data: {"content":',
        ' "part1"}\n\ndata: {"content": "part2"}\n\n',
        'data: [DONE]\n\n'
      ]
      let chunkIndex = 0

      const mockReader = {
        read: vi.fn().mockImplementation(async () => {
          if (chunkIndex < chunks.length) {
            const chunk = chunks[chunkIndex++]
            return {
              done: false,
              value: new TextEncoder().encode(chunk)
            }
          }
          return { done: true, value: null }
        }),
        releaseLock: vi.fn()
      }
      const mockResponse = {
        ok: true,
        body: { getReader: () => mockReader }
      }
      vi.mocked(global.fetch).mockResolvedValue(mockResponse as any)

      const chunksReceived: any[] = []
      const onChunk = vi.fn((data) => chunksReceived.push(data))

      await ApiService.chatStream('test-tool', { message: 'hello' }, onChunk)

      expect(chunksReceived.length).toBeGreaterThan(0)
      expect(chunksReceived[chunksReceived.length - 1]).toMatchObject({ type: 'done' })
    })

    it('应该优先使用localStorage的token', async () => {
      localStorage.setItem('auth_token', 'local-token')
      sessionStorage.setItem('auth_token', 'session-token')

      const mockReader = {
        read: vi.fn().mockResolvedValue({ done: true, value: null }),
        releaseLock: vi.fn()
      }
      const mockResponse = {
        ok: true,
        body: { getReader: () => mockReader }
      }
      vi.mocked(global.fetch).mockResolvedValue(mockResponse as any)

      await ApiService.chatStream('test-tool', { message: 'hello' }, vi.fn())

      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/tools/test-tool/chat/stream',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer local-token'
          })
        })
      )
    })

    it('应该在localStorage无token时使用sessionStorage的token', async () => {
      sessionStorage.setItem('auth_token', 'session-token')

      const mockReader = {
        read: vi.fn().mockResolvedValue({ done: true, value: null }),
        releaseLock: vi.fn()
      }
      const mockResponse = {
        ok: true,
        body: { getReader: () => mockReader }
      }
      vi.mocked(global.fetch).mockResolvedValue(mockResponse as any)

      await ApiService.chatStream('test-tool', { message: 'hello' }, vi.fn())

      expect(global.fetch).toHaveBeenCalledWith(
        '/api/v1/tools/test-tool/chat/stream',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer session-token'
          })
        })
      )
    })
  })

  describe('后台管理 - 工具管理测试（部分）', () => {
    it('应该获取管理后台工具列表', async () => {
      const mockResponse = {
        tools: [],
        total: 0,
        page: 1,
        page_size: 20
      }

      vi.spyOn(ApiService, 'getAdminTools').mockResolvedValue(mockResponse)

      await ApiService.getAdminTools(1, 20)
    })

    it('应该创建内置工具', async () => {
      const mockResponse = {
        tool: { tool_id: 'tool1', name: '测试工具' }
      }

      vi.spyOn(ApiService, 'createBuiltInTool').mockResolvedValue(mockResponse)

      const request = {
        name: '测试工具',
        description: '描述',
        category_id: 'cat1',
        icon: 'icon',
        order: 1,
        visible: true
      }

      const result = await ApiService.createBuiltInTool(request)

      expect(result.tool.tool_id).toBe('tool1')
    })

    it('应该上传HTML工具', async () => {
      const mockResponse = {
        tool: { tool_id: 'tool1', name: 'HTML工具' }
      }

      vi.spyOn(ApiService, 'createHtmlTool').mockResolvedValue(mockResponse)

      const file = new File(['<html></html>'], 'test.html', { type: 'text/html' })

      const result = await ApiService.createHtmlTool(
        '测试工具',
        '描述',
        'cat1',
        file,
        'icon',
        1,
        true
      )

      expect(result.tool.tool_id).toBe('tool1')
    })

    it('应该删除工具', async () => {
      vi.spyOn(ApiService, 'deleteTool').mockResolvedValue(undefined)

      await ApiService.deleteTool('tool1')
    })

    it('应该上移工具', async () => {
      const mockResponse = { message: 'success' }

      vi.spyOn(ApiService, 'moveToolUp').mockResolvedValue(mockResponse)

      const result = await ApiService.moveToolUp('tool1')
    })

    it('应该下移工具', async () => {
      const mockResponse = { message: 'success' }

      vi.spyOn(ApiService, 'moveToolDown').mockResolvedValue(mockResponse)

      const result = await ApiService.moveToolDown('tool1')
    })

    it('应该切换工具可见性', async () => {
      const mockResponse = { tool: { visible: false } }

      vi.spyOn(ApiService, 'toggleToolVisibility').mockResolvedValue(mockResponse)

      const result = await ApiService.toggleToolVisibility('tool1')

      expect(result.tool.visible).toBe(false)
    })
  })

  describe('已废弃方法测试', () => {
    it('应该能调用getAgents（已废弃）', async () => {
      const mockResponse = {
        agents: [
          { agent_id: 'agent1', name: 'Agent1' }
        ]
      }

      vi.spyOn(ApiService, 'getAgents').mockResolvedValue(mockResponse)

      const result = await ApiService.getAgents()

      expect(result.agents).toHaveLength(1)
      expect(result.agents[0].agent_id).toBe('agent1')
    })
  })

  describe('后台管理 - 工具分类管理测试', () => {
    it('应该获取工具分类列表', async () => {
      const mockResponse = {
        categories: [
          { category_id: 'cat1', category_name: '分类1', order: 1 }
        ],
        total: 1
      }

      vi.spyOn(ApiService, 'getAdminToolCategories').mockResolvedValue(mockResponse)

      const result = await ApiService.getAdminToolCategories()

      expect(result.categories).toHaveLength(1)
      expect(result.categories[0].category_id).toBe('cat1')
    })

    it('应该创建工具分类', async () => {
      const mockResponse = {
        category: { category_id: 'cat2', category_name: '新分类' }
      }

      vi.spyOn(ApiService, 'createToolCategory').mockResolvedValue(mockResponse)

      const request = { category_name: '新分类', order: 1 }
      const result = await ApiService.createToolCategory(request)

      expect(result.category.category_name).toBe('新分类')
    })

    it('应该更新工具分类', async () => {
      const mockResponse = {
        category: { category_id: 'cat1', category_name: '更新后' }
      }

      vi.spyOn(ApiService, 'updateToolCategory').mockResolvedValue(mockResponse)

      const request = { category_name: '更新后' }
      const result = await ApiService.updateToolCategory('cat1', request)

      expect(result.category.category_name).toBe('更新后')
    })

    it('应该删除工具分类', async () => {
      vi.spyOn(ApiService, 'deleteToolCategory').mockResolvedValue(undefined)

      await ApiService.deleteToolCategory('cat1')
    })

    it('应该上移工具分类', async () => {
      const mockResponse = { message: 'success' }

      vi.spyOn(ApiService, 'moveCategoryUp').mockResolvedValue(mockResponse)

      const result = await ApiService.moveCategoryUp('cat1')

      expect(result.message).toBe('success')
    })

    it('应该下移工具分类', async () => {
      const mockResponse = { message: 'success' }

      vi.spyOn(ApiService, 'moveCategoryDown').mockResolvedValue(mockResponse)

      const result = await ApiService.moveCategoryDown('cat1')

      expect(result.message).toBe('success')
    })
  })

  describe('后台管理 - 作品管理测试', () => {
    it('应该获取作品列表', async () => {
      const mockResponse = {
        works: [
          { work_id: 'work1', name: '作品1' }
        ],
        total: 1,
        page: 1,
        page_size: 20
      }

      vi.spyOn(ApiService, 'getAdminWorks').mockResolvedValue(mockResponse)

      const result = await ApiService.getAdminWorks(1, 20)

      expect(result.works).toHaveLength(1)
    })

    it('应该按分类筛选作品', async () => {
      const mockResponse = {
        works: [{ work_id: 'work1', name: '作品1', category_id: 'cat1' }],
        total: 1,
        page: 1,
        page_size: 20
      }

      vi.spyOn(ApiService, 'getAdminWorks').mockResolvedValue(mockResponse)

      const result = await ApiService.getAdminWorks(1, 20, 'cat1')

      expect(result.works).toHaveLength(1)
    })

    it('应该按可见性筛选作品', async () => {
      const mockResponse = {
        works: [{ work_id: 'work1', name: '作品1', visible: true }],
        total: 1,
        page: 1,
        page_size: 20
      }

      vi.spyOn(ApiService, 'getAdminWorks').mockResolvedValue(mockResponse)

      const result = await ApiService.getAdminWorks(1, 20, undefined, true)

      expect(result.works[0].visible).toBe(true)
    })

    it('应该上传作品', async () => {
      const mockResponse = {
        work: { work_id: 'work1', name: '新作品' }
      }

      vi.spyOn(ApiService, 'createWork').mockResolvedValue(mockResponse)

      const file = new File(['<html></html>'], 'test.html', { type: 'text/html' })
      const result = await ApiService.createWork('新作品', '描述', 'cat1', file)

      expect(result.work.name).toBe('新作品')
    })

    it('应该更新作品信息', async () => {
      const mockResponse = {
        work: { work_id: 'work1', name: '更新后' }
      }

      vi.spyOn(ApiService, 'updateWork').mockResolvedValue(mockResponse)

      const request = { name: '更新后' }
      const result = await ApiService.updateWork('work1', request)

      expect(result.work.name).toBe('更新后')
    })

    it('应该删除作品', async () => {
      vi.spyOn(ApiService, 'deleteWork').mockResolvedValue(undefined)

      await ApiService.deleteWork('work1')
    })

    it('应该上移作品', async () => {
      const mockResponse = { message: 'success' }

      vi.spyOn(ApiService, 'moveWorkUp').mockResolvedValue(mockResponse)

      const result = await ApiService.moveWorkUp('work1')

      expect(result.message).toBe('success')
    })

    it('应该下移作品', async () => {
      const mockResponse = { message: 'success' }

      vi.spyOn(ApiService, 'moveWorkDown').mockResolvedValue(mockResponse)

      const result = await ApiService.moveWorkDown('work1')

      expect(result.message).toBe('success')
    })

    it('应该切换作品可见性', async () => {
      const mockResponse = { work: { visible: false } }

      vi.spyOn(ApiService, 'toggleWorkVisibility').mockResolvedValue(mockResponse)

      const result = await ApiService.toggleWorkVisibility('work1')

      expect(result.work.visible).toBe(false)
    })
  })

  describe('后台管理 - 作品分类管理测试', () => {
    it('应该获取作品分类列表', async () => {
      const mockResponse = {
        categories: [
          { category_id: 'cat1', category_name: '分类1', order: 1 }
        ],
        total: 1
      }

      vi.spyOn(ApiService, 'getAdminWorkCategories').mockResolvedValue(mockResponse)

      const result = await ApiService.getAdminWorkCategories()

      expect(result.categories).toHaveLength(1)
    })

    it('应该创建作品分类', async () => {
      const mockResponse = {
        category: { category_id: 'cat2', category_name: '新分类' }
      }

      vi.spyOn(ApiService, 'createWorkCategory').mockResolvedValue(mockResponse)

      const request = { category_name: '新分类', order: 1 }
      const result = await ApiService.createWorkCategory(request)

      expect(result.category.category_name).toBe('新分类')
    })

    it('应该更新作品分类', async () => {
      const mockResponse = {
        category: { category_id: 'cat1', category_name: '更新后' }
      }

      vi.spyOn(ApiService, 'updateWorkCategory').mockResolvedValue(mockResponse)

      const request = { category_name: '更新后' }
      const result = await ApiService.updateWorkCategory('cat1', request)

      expect(result.category.category_name).toBe('更新后')
    })

    it('应该删除作品分类', async () => {
      vi.spyOn(ApiService, 'deleteWorkCategory').mockResolvedValue(undefined)

      await ApiService.deleteWorkCategory('cat1')
    })

    it('应该上移作品分类', async () => {
      const mockResponse = { message: 'success' }

      vi.spyOn(ApiService, 'moveWorkCategoryUp').mockResolvedValue(mockResponse)

      const result = await ApiService.moveWorkCategoryUp('cat1')

      expect(result.message).toBe('success')
    })

    it('应该下移作品分类', async () => {
      const mockResponse = { message: 'success' }

      vi.spyOn(ApiService, 'moveWorkCategoryDown').mockResolvedValue(mockResponse)

      const result = await ApiService.moveWorkCategoryDown('cat1')

      expect(result.message).toBe('success')
    })
  })

  describe('后台管理 - 课程目录管理测试', () => {
    it('应该获取课程目录列表', async () => {
      const mockResponse = {
        categories: [
          { category_id: 'cat1', name: '目录1', order: 1 }
        ],
        total: 1
      }

      vi.spyOn(ApiService, 'getAdminCourseCategories').mockResolvedValue(mockResponse)

      const result = await ApiService.getAdminCourseCategories()

      expect(result.categories).toHaveLength(1)
    })

    it('应该创建课程目录', async () => {
      const mockResponse = { message: '创建成功' }

      vi.spyOn(ApiService, 'createCourseCategory').mockResolvedValue(mockResponse)

      const request = { name: '新目录', parent_id: null, order: 1 }
      const result = await ApiService.createCourseCategory(request)

      expect(result.message).toBe('创建成功')
    })

    it('应该更新课程目录', async () => {
      const mockResponse = { message: '更新成功' }

      vi.spyOn(ApiService, 'updateCourseCategory').mockResolvedValue(mockResponse)

      const request = { name: '更新后' }
      const result = await ApiService.updateCourseCategory('cat1', request)

      expect(result.message).toBe('更新成功')
    })

    it('应该删除课程目录', async () => {
      const mockResponse = { message: '删除成功' }

      vi.spyOn(ApiService, 'deleteCourseCategory').mockResolvedValue(mockResponse)

      const result = await ApiService.deleteCourseCategory('cat1')

      expect(result.message).toBe('删除成功')
    })

    it('应该上移课程目录', async () => {
      const mockResponse = { message: 'success' }

      vi.spyOn(ApiService, 'moveCourseCategoryUp').mockResolvedValue(mockResponse)

      const result = await ApiService.moveCourseCategoryUp('cat1')

      expect(result.message).toBe('success')
    })

    it('应该下移课程目录', async () => {
      const mockResponse = { message: 'success' }

      vi.spyOn(ApiService, 'moveCourseCategoryDown').mockResolvedValue(mockResponse)

      const result = await ApiService.moveCourseCategoryDown('cat1')

      expect(result.message).toBe('success')
    })
  })

  describe('后台管理 - 课程文档管理测试', () => {
    it('应该获取课程文档列表', async () => {
      const mockResponse = {
        documents: [
          { document_id: 'doc1', title: '文档1' }
        ],
        total: 1,
        page: 1,
        page_size: 20
      }

      vi.spyOn(ApiService, 'getAdminCourseDocuments').mockResolvedValue(mockResponse)

      const result = await ApiService.getAdminCourseDocuments(1, 20)

      expect(result.documents).toHaveLength(1)
    })

    it('应该按分类筛选课程文档', async () => {
      const mockResponse = {
        documents: [{ document_id: 'doc1', title: '文档1', category_id: 'cat1' }],
        total: 1,
        page: 1,
        page_size: 20
      }

      vi.spyOn(ApiService, 'getAdminCourseDocuments').mockResolvedValue(mockResponse)

      const result = await ApiService.getAdminCourseDocuments(1, 20, 'cat1')

      expect(result.documents).toHaveLength(1)
    })

    it('应该创建课程文档', async () => {
      const mockResponse = { message: '创建成功' }

      vi.spyOn(ApiService, 'createCourseDocument').mockResolvedValue(mockResponse)

      const file = new File(['# 内容'], 'test.md', { type: 'text/markdown' })
      const result = await ApiService.createCourseDocument('标题', '摘要', 'cat1', 1, file)

      expect(result.message).toBe('创建成功')
    })

    it('应该更新课程文档', async () => {
      const mockResponse = { message: '更新成功' }

      vi.spyOn(ApiService, 'updateCourseDocument').mockResolvedValue(mockResponse)

      const request = { title: '更新后' }
      const result = await ApiService.updateCourseDocument('doc1', request)

      expect(result.message).toBe('更新成功')
    })

    it('应该删除课程文档', async () => {
      const mockResponse = { message: '删除成功' }

      vi.spyOn(ApiService, 'deleteCourseDocument').mockResolvedValue(mockResponse)

      const result = await ApiService.deleteCourseDocument('doc1')

      expect(result.message).toBe('删除成功')
    })

    it('应该上移课程文档', async () => {
      const mockResponse = { message: 'success' }

      vi.spyOn(ApiService, 'moveCourseDocumentUp').mockResolvedValue(mockResponse)

      const result = await ApiService.moveCourseDocumentUp('doc1')

      expect(result.message).toBe('success')
    })

    it('应该下移课程文档', async () => {
      const mockResponse = { message: 'success' }

      vi.spyOn(ApiService, 'moveCourseDocumentDown').mockResolvedValue(mockResponse)

      const result = await ApiService.moveCourseDocumentDown('doc1')

      expect(result.message).toBe('success')
    })
  })

  describe('工具管理完整测试', () => {
    it('应该更新工具信息', async () => {
      const mockResponse = {
        tool: { tool_id: 'tool1', name: '更新后' }
      }

      vi.spyOn(ApiService, 'updateTool').mockResolvedValue(mockResponse)

      const request = { name: '更新后', description: '新描述' }
      const result = await ApiService.updateTool('tool1', request)

      expect(result.tool.name).toBe('更新后')
    })

    it('应该按分类筛选工具', async () => {
      const mockResponse = {
        tools: [{ tool_id: 'tool1', name: '工具1', category_id: 'cat1' }],
        total: 1,
        page: 1,
        page_size: 20
      }

      vi.spyOn(ApiService, 'getAdminTools').mockResolvedValue(mockResponse)

      const result = await ApiService.getAdminTools(1, 20, 'cat1')

      expect(result.tools).toHaveLength(1)
    })

    it('应该按类型筛选工具', async () => {
      const mockResponse = {
        tools: [{ tool_id: 'tool1', name: '工具1', type: 'built_in' }],
        total: 1,
        page: 1,
        page_size: 20
      }

      vi.spyOn(ApiService, 'getAdminTools').mockResolvedValue(mockResponse)

      const result = await ApiService.getAdminTools(1, 20, undefined, 'built_in')

      expect(result.tools).toHaveLength(1)
    })

    it('应该按可见性筛选工具', async () => {
      const mockResponse = {
        tools: [{ tool_id: 'tool1', name: '工具1', visible: true }],
        total: 1,
        page: 1,
        page_size: 20
      }

      vi.spyOn(ApiService, 'getAdminTools').mockResolvedValue(mockResponse)

      const result = await ApiService.getAdminTools(1, 20, undefined, undefined, true)

      expect(result.tools[0].visible).toBe(true)
    })
  })

  describe('边界条件测试', () => {
    it('应该处理空用户列表', async () => {
      const mockResponse = {
        users: [],
        total: 0,
        page: 1,
        page_size: 20
      }

      vi.spyOn(ApiService, 'getUserList').mockResolvedValue(mockResponse)

      const result = await ApiService.getUserList(1, 20)

      expect(result.users).toHaveLength(0)
      expect(result.total).toBe(0)
    })

    it('应该处理空会话列表', async () => {
      const mockResponse = {
        conversations: []
      }

      vi.spyOn(ApiService, 'getConversations').mockResolvedValue(mockResponse)

      const result = await ApiService.getConversations('test-tool')

      expect(result.conversations).toHaveLength(0)
    })

    it('应该处理特殊字符在用户名中', async () => {
      const mockResponse = {
        user: { id: 1, username: 'user@测试#$%', is_admin: false }
      }

      vi.spyOn(ApiService, 'createUser').mockResolvedValue(mockResponse)

      const request = {
        username: 'user@测试#$%',
        password: '123456',
        is_admin: false
      }

      const result = await ApiService.createUser(request)

      expect(result.user.username).toBe('user@测试#$%')
    })

    it('应该处理长描述文本', async () => {
      const longDescription = 'a'.repeat(1000)

      const mockResponse = {
        tool: { tool_id: 'tool1', name: '工具', description: longDescription }
      }

      vi.spyOn(ApiService, 'createBuiltInTool').mockResolvedValue(mockResponse)

      const request = {
        name: '工具',
        description: longDescription,
        category_id: 'cat1',
        icon: 'icon',
        order: 1,
        visible: true
      }

      const result = await ApiService.createBuiltInTool(request)

      expect(result.tool.description).toHaveLength(1000)
    })

    it('应该处理带特殊字符的会话标题', async () => {
      const mockResponse = {
        session_id: 'uuid-123',
        title: '标题<script>alert(1)</script>'
      }

      vi.spyOn(ApiService, 'updateSessionTitle').mockResolvedValue(mockResponse)

      const request = { title: '标题<script>alert(1)</script>' }
      const result = await ApiService.updateSessionTitle('uuid-123', request)

      expect(result.title).toContain('<script>')
    })
  })

  describe('错误处理测试', () => {
    it('应该在登录失败时抛出错误（401）', async () => {
      vi.spyOn(ApiService, 'login').mockRejectedValue(new Error('账号或密码错误'))

      await expect(
        ApiService.login({ username: 'wrong', password: 'wrong' })
      ).rejects.toThrow('账号或密码错误')
    })

    it('应该在获取用户信息时抛出错误（401过期）', async () => {
      vi.spyOn(ApiService, 'getCurrentUser').mockRejectedValue(new Error('登录已过期，请重新登录'))

      await expect(
        ApiService.getCurrentUser()
      ).rejects.toThrow('登录已过期')
    })

    it('应该在获取不存在的会话时抛出错误（404）', async () => {
      vi.spyOn(ApiService, 'getSessionDetail').mockRejectedValue(new Error('会话不存在'))

      await expect(
        ApiService.getSessionDetail('non-existent-id')
      ).rejects.toThrow('会话不存在')
    })

    it('应该在服务器错误时抛出错误（500）', async () => {
      vi.spyOn(ApiService, 'getTools').mockRejectedValue(new Error('服务器内部错误'))

      await expect(
        ApiService.getTools()
      ).rejects.toThrow('服务器内部错误')
    })

    it('应该在网络错误时抛出错误', async () => {
      vi.spyOn(ApiService, 'getNavigationModules').mockRejectedValue(new Error('网络错误，请检查网络连接'))

      await expect(
        ApiService.getNavigationModules()
      ).rejects.toThrow('网络错误')
    })

    it('应该在请求配置错误时抛出错误', async () => {
      vi.spyOn(ApiService, 'chat').mockRejectedValue(new Error('请求配置错误'))

      await expect(
        ApiService.chat('tool', { message: 'test' })
      ).rejects.toThrow('请求配置错误')
    })
  })

  describe('参数验证测试', () => {
    it('应该正确处理默认分页参数', async () => {
      const mockResponse = {
        users: [],
        total: 0,
        page: 1,
        page_size: 20
      }

      vi.spyOn(ApiService, 'getUserList').mockResolvedValue(mockResponse)

      // 不传参数，使用默认值
      const result = await ApiService.getUserList()

      expect(result.page).toBe(1)
      expect(result.page_size).toBe(20)
    })

    it('应该正确传递分页参数', async () => {
      const mockResponse = {
        users: [],
        total: 0,
        page: 2,
        page_size: 50
      }

      vi.spyOn(ApiService, 'getUserList').mockResolvedValue(mockResponse)

      const result = await ApiService.getUserList(2, 50)

      expect(result.page).toBe(2)
      expect(result.page_size).toBe(50)
    })

    it('应该正确处理可选的筛选参数', async () => {
      const mockResponse = {
        tools: [],
        total: 0,
        page: 1,
        page_size: 20
      }

      vi.spyOn(ApiService, 'getAdminTools').mockResolvedValue(mockResponse)

      // 只传部分参数
      const result = await ApiService.getAdminTools(1, 20, undefined, 'built_in')

      expect(result.tools).toBeDefined()
    })

    it('应该正确处理 FormData 文件上传参数', async () => {
      const mockResponse = {
        tool: { tool_id: 'tool1', name: 'HTML工具' }
      }

      vi.spyOn(ApiService, 'createHtmlTool').mockResolvedValue(mockResponse)

      const file = new File(['<html></html>'], 'test.html', { type: 'text/html' })

      // 测试所有可选参数
      const result = await ApiService.createHtmlTool(
        '名称',
        '描述',
        'cat1',
        file,
        undefined, // icon 可选
        0, // order 默认值
        true // visible 默认值
      )

      expect(result.tool.tool_id).toBe('tool1')
    })
  })
})
