/**
 * apiClient.integration.spec.ts
 * API 客户端集成测试 - 真正执行代码以提升语句覆盖率
 * 通过 mock axios 的响应而不是 mock ApiService 方法来测试
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'
import { ApiService } from '@/services/apiClient'
import apiClient from '@/services/apiClient'

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

describe('ApiService 集成测试（真实代码执行）', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    sessionStorage.clear()

    // Mock apiClient 的所有方法
    apiClient.get = vi.fn().mockResolvedValue({ data: {} })
    apiClient.post = vi.fn().mockResolvedValue({ data: {} })
    apiClient.put = vi.fn().mockResolvedValue({ data: {} })
    apiClient.patch = vi.fn().mockResolvedValue({ data: {} })
    apiClient.delete = vi.fn().mockResolvedValue({ data: {} })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('基础 API 方法 - 真实执行', () => {
    it('应该调用 getNavigationModules API', async () => {
      const mockResponse = {
        modules: [
          { id: 'ai-tools', name: 'AI工具' }
        ]
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getNavigationModules()

      expect(apiClient.get).toHaveBeenCalledWith('/navigation')
      expect(result.modules).toHaveLength(1)
    })

    it('应该调用 getTools API', async () => {
      const mockResponse = {
        categories: [
          {
            category_id: 'cat1',
            category_name: '分类1',
            tools: []
          }
        ]
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getTools()

      expect(apiClient.get).toHaveBeenCalledWith('/tools')
      expect(result.categories).toHaveLength(1)
    })

    it('应该调用 getToolsetTools API', async () => {
      const mockResponse = {
        categories: []
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getToolsetTools('ai-tools')

      expect(apiClient.get).toHaveBeenCalledWith('/toolsets/ai-tools/tools')
    })

    it('应该调用 createSession API', async () => {
      const mockResponse = {
        session_id: 'uuid-123',
        agent_id: 'test-agent'
      }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.createSession('test-agent')

      expect(apiClient.post).toHaveBeenCalledWith('/agents/test-agent/sessions')
      expect(result.session_id).toBe('uuid-123')
    })

    it('应该调用 chat API（带自定义超时）', async () => {
      const mockResponse = {
        session_id: 'uuid-123',
        message: 'AI响应'
      }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const request = { message: '用户消息' }
      const result = await ApiService.chat('test-tool', request)

      expect(apiClient.post).toHaveBeenCalledWith(
        '/tools/test-tool/chat',
        request,
        { timeout: 300000 }
      )
      expect(result.message).toBe('AI响应')
    })

    it('应该调用 getConversations API', async () => {
      const mockResponse = {
        conversations: [
          { session_id: 's1', title: '会话1' }
        ]
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getConversations('test-tool')

      expect(apiClient.get).toHaveBeenCalledWith('/tools/test-tool/conversations')
      expect(result.conversations).toHaveLength(1)
    })

    it('应该调用 getSessionDetail API', async () => {
      const mockResponse = {
        session_id: 'uuid-123',
        messages: []
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getSessionDetail('uuid-123')

      expect(apiClient.get).toHaveBeenCalledWith('/sessions/uuid-123')
    })

    it('应该调用 updateSessionTitle API', async () => {
      const mockResponse = {
        session_id: 'uuid-123',
        title: '新标题'
      }
      apiClient.patch.mockResolvedValue({ data: mockResponse })

      const request = { title: '新标题' }
      const result = await ApiService.updateSessionTitle('uuid-123', request)

      expect(apiClient.patch).toHaveBeenCalledWith('/sessions/uuid-123', request)
    })

    it('应该调用 deleteSession API', async () => {
      apiClient.delete.mockResolvedValue(undefined)

      await ApiService.deleteSession('uuid-123')

      expect(apiClient.delete).toHaveBeenCalledWith('/sessions/uuid-123')
    })
  })

  describe('认证相关 - 真实执行', () => {
    it('应该调用 login API', async () => {
      const mockResponse = {
        access_token: 'token-123',
        token_type: 'bearer',
        user: { id: 1, username: 'test', is_admin: false }
      }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const request = { username: 'test', password: '123456' }
      const result = await ApiService.login(request)

      expect(apiClient.post).toHaveBeenCalledWith('/auth/login', request)
      expect(result.access_token).toBe('token-123')
    })

    it('应该调用 getCurrentUser API', async () => {
      const mockResponse = {
        user: {
          id: 1,
          username: 'test',
          is_admin: false
        }
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getCurrentUser()

      expect(apiClient.get).toHaveBeenCalledWith('/auth/me')
      expect(result.user.username).toBe('test')
    })
  })

  describe('用户管理 - 真实执行', () => {
    it('应该调用 getUserList API（无筛选）', async () => {
      const mockResponse = {
        users: [{ id: 1, username: 'user1' }],
        total: 1,
        page: 1,
        page_size: 20
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getUserList(1, 20)

      expect(apiClient.get).toHaveBeenCalledWith('/admin/users', {
        params: { page: 1, page_size: 20 }
      })
      expect(result.total).toBe(1)
    })

    it('应该调用 getUserList API（带管理员筛选）', async () => {
      const mockResponse = {
        users: [{ id: 1, username: 'admin', is_admin: true }],
        total: 1,
        page: 1,
        page_size: 20
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getUserList(1, 20, true)

      expect(apiClient.get).toHaveBeenCalledWith('/admin/users', {
        params: { page: 1, page_size: 20, is_admin: true }
      })
    })

    it('应该调用 createUser API', async () => {
      const mockResponse = {
        user: { id: 2, username: 'newuser', is_admin: false }
      }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const request = {
        username: 'newuser',
        password: '123456',
        is_admin: false
      }
      const result = await ApiService.createUser(request)

      expect(apiClient.post).toHaveBeenCalledWith('/admin/users', request)
    })

    it('应该调用 updateUser API', async () => {
      const mockResponse = {
        user: { id: 1, username: 'updated', is_admin: false }
      }
      apiClient.put.mockResolvedValue({ data: mockResponse })

      const request = { username: 'updated' }
      const result = await ApiService.updateUser('1', request)

      expect(apiClient.put).toHaveBeenCalledWith('/admin/users/1', request)
    })

    it('应该调用 deleteUser API', async () => {
      apiClient.delete.mockResolvedValue(undefined)

      await ApiService.deleteUser('1')

      expect(apiClient.delete).toHaveBeenCalledWith('/admin/users/1')
    })

    it('应该调用 resetUserPassword API', async () => {
      const mockResponse = {
        message: '密码重置成功'
      }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const request = { new_password: 'newpass123' }
      const result = await ApiService.resetUserPassword('1', request)

      expect(apiClient.post).toHaveBeenCalledWith('/admin/users/1/reset-password', request)
    })
  })

  describe('常用工具模块 - 真实执行', () => {
    it('应该调用 getCommonToolCategories API', async () => {
      const mockResponse = {
        categories: [
          {
            category_id: 'cat1',
            category_name: '分类1',
            tools: []
          }
        ]
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getCommonToolCategories()

      expect(apiClient.get).toHaveBeenCalledWith('/common-tools/categories')
    })

    it('应该调用 getCommonToolDetail API', async () => {
      const mockResponse = {
        tool_id: 'tool1',
        name: '测试工具',
        description: '测试描述'
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getCommonToolDetail('tool1')

      expect(apiClient.get).toHaveBeenCalledWith('/common-tools/tools/tool1')
    })
  })

  describe('作品模块 - 真实执行', () => {
    it('应该调用 getWorkCategories API', async () => {
      const mockResponse = {
        categories: [
          {
            category_id: 'cat1',
            category_name: '分类1',
            works: []
          }
        ]
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getWorkCategories()

      expect(apiClient.get).toHaveBeenCalledWith('/works/categories')
    })

    it('应该调用 getWorkDetail API', async () => {
      const mockResponse = {
        work_id: 'work1',
        name: '测试作品',
        description: '作品描述'
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getWorkDetail('work1')

      expect(apiClient.get).toHaveBeenCalledWith('/works/work1')
    })
  })

  describe('课程文档模块 - 真实执行', () => {
    it('应该调用 getCourseCategories API', async () => {
      const mockResponse = {
        categories: [
          {
            category_id: 'cat1',
            name: '目录1',
            children: []
          }
        ]
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getCourseCategories()

      expect(apiClient.get).toHaveBeenCalledWith('/documents/categories')
    })

    it('应该调用 getCourseDocumentsByCategory API', async () => {
      const mockResponse = {
        documents: [
          { document_id: 'doc1', title: '文档1' }
        ]
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getCourseDocumentsByCategory('cat1')

      expect(apiClient.get).toHaveBeenCalledWith('/documents/category/cat1/documents')
    })

    it('应该调用 getCourseDocumentDetail API', async () => {
      const mockResponse = {
        document_id: 'doc1',
        title: '测试文档',
        content: '# 内容'
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getCourseDocumentDetail('doc1')

      expect(apiClient.get).toHaveBeenCalledWith('/documents/doc1')
    })
  })

  describe('后台管理 - 工具管理 - 真实执行', () => {
    it('应该调用 getAdminTools API（无筛选）', async () => {
      const mockResponse = {
        tools: [],
        total: 0,
        page: 1,
        page_size: 20
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getAdminTools(1, 20)

      expect(apiClient.get).toHaveBeenCalledWith('/admin/common-tools', {
        params: { page: 1, page_size: 20 }
      })
    })

    it('应该调用 getAdminTools API（带筛选参数）', async () => {
      const mockResponse = {
        tools: [],
        total: 0,
        page: 1,
        page_size: 20
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getAdminTools(1, 20, 'cat1', 'built_in', true)

      expect(apiClient.get).toHaveBeenCalledWith('/admin/common-tools', {
        params: { page: 1, page_size: 20, category_id: 'cat1', type: 'built_in', visible: true }
      })
    })

    it('应该调用 createBuiltInTool API', async () => {
      const mockResponse = {
        tool: { tool_id: 'tool1', name: '测试工具' }
      }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const request = {
        name: '测试工具',
        description: '描述',
        category_id: 'cat1',
        icon: 'icon',
        order: 1,
        visible: true
      }
      const result = await ApiService.createBuiltInTool(request)

      expect(apiClient.post).toHaveBeenCalledWith('/admin/common-tools/built-in', request)
    })

    it('应该调用 createHtmlTool API（FormData）', async () => {
      const mockResponse = {
        tool: { tool_id: 'tool1', name: 'HTML工具' }
      }
      apiClient.post.mockResolvedValue({ data: mockResponse })

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

      expect(apiClient.post).toHaveBeenCalledWith(
        '/admin/common-tools/html',
        expect.any(FormData),
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )
    })

    it('应该调用 updateTool API', async () => {
      const mockResponse = {
        tool: { tool_id: 'tool1', name: '更新后' }
      }
      apiClient.put.mockResolvedValue({ data: mockResponse })

      const request = { name: '更新后' }
      const result = await ApiService.updateTool('tool1', request)

      expect(apiClient.put).toHaveBeenCalledWith('/admin/common-tools/tool1', request)
    })

    it('应该调用 deleteTool API', async () => {
      apiClient.delete.mockResolvedValue(undefined)

      await ApiService.deleteTool('tool1')

      expect(apiClient.delete).toHaveBeenCalledWith('/admin/common-tools/tool1')
    })

    it('应该调用 moveToolUp API', async () => {
      const mockResponse = { message: 'success' }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.moveToolUp('tool1')

      expect(apiClient.post).toHaveBeenCalledWith('/admin/common-tools/tool1/move-up')
    })

    it('应该调用 moveToolDown API', async () => {
      const mockResponse = { message: 'success' }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.moveToolDown('tool1')

      expect(apiClient.post).toHaveBeenCalledWith('/admin/common-tools/tool1/move-down')
    })

    it('应该调用 toggleToolVisibility API', async () => {
      const mockResponse = { tool: { visible: false } }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.toggleToolVisibility('tool1')

      expect(apiClient.post).toHaveBeenCalledWith('/admin/common-tools/tool1/toggle-visibility')
    })
  })

  describe('后台管理 - 工具分类管理 - 真实执行', () => {
    it('应该调用 getAdminToolCategories API', async () => {
      const mockResponse = {
        categories: [
          { category_id: 'cat1', category_name: '分类1', order: 1 }
        ],
        total: 1
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getAdminToolCategories()

      expect(apiClient.get).toHaveBeenCalledWith('/admin/tool-categories')
    })

    it('应该调用 createToolCategory API', async () => {
      const mockResponse = {
        category: { category_id: 'cat2', category_name: '新分类' }
      }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const request = { category_name: '新分类', order: 1 }
      const result = await ApiService.createToolCategory(request)

      expect(apiClient.post).toHaveBeenCalledWith('/admin/tool-categories', request)
    })

    it('应该调用 updateToolCategory API', async () => {
      const mockResponse = {
        category: { category_id: 'cat1', category_name: '更新后' }
      }
      apiClient.put.mockResolvedValue({ data: mockResponse })

      const request = { category_name: '更新后' }
      const result = await ApiService.updateToolCategory('cat1', request)

      expect(apiClient.put).toHaveBeenCalledWith('/admin/tool-categories/cat1', request)
    })

    it('应该调用 deleteToolCategory API', async () => {
      apiClient.delete.mockResolvedValue(undefined)

      await ApiService.deleteToolCategory('cat1')

      expect(apiClient.delete).toHaveBeenCalledWith('/admin/tool-categories/cat1')
    })

    it('应该调用 moveCategoryUp API', async () => {
      const mockResponse = { message: 'success' }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.moveCategoryUp('cat1')

      expect(apiClient.post).toHaveBeenCalledWith('/admin/tool-categories/cat1/move-up')
    })

    it('应该调用 moveCategoryDown API', async () => {
      const mockResponse = { message: 'success' }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.moveCategoryDown('cat1')

      expect(apiClient.post).toHaveBeenCalledWith('/admin/tool-categories/cat1/move-down')
    })
  })

  describe('后台管理 - 作品管理 - 真实执行', () => {
    it('应该调用 getAdminWorks API（无筛选）', async () => {
      const mockResponse = {
        works: [],
        total: 0,
        page: 1,
        page_size: 20
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getAdminWorks(1, 20)

      expect(apiClient.get).toHaveBeenCalledWith('/admin/works', {
        params: { page: 1, page_size: 20 }
      })
    })

    it('应该调用 getAdminWorks API（带筛选参数）', async () => {
      const mockResponse = {
        works: [],
        total: 0,
        page: 1,
        page_size: 20
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getAdminWorks(1, 20, 'cat1', true)

      expect(apiClient.get).toHaveBeenCalledWith('/admin/works', {
        params: { page: 1, page_size: 20, category_id: 'cat1', visible: true }
      })
    })

    it('应该调用 createWork API', async () => {
      const mockResponse = {
        work: { work_id: 'work1', name: '新作品' }
      }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const file = new File(['<html></html>'], 'test.html', { type: 'text/html' })

      const result = await ApiService.createWork('新作品', '描述', 'cat1', file)

      expect(apiClient.post).toHaveBeenCalledWith(
        '/admin/works',
        expect.any(FormData),
        {
          headers: { 'Content-Type': 'multipart/form-data' },
        }
      )
    })

    it('应该调用 updateWork API', async () => {
      const mockResponse = {
        work: { work_id: 'work1', name: '更新后' }
      }
      apiClient.put.mockResolvedValue({ data: mockResponse })

      const request = { name: '更新后' }
      const result = await ApiService.updateWork('work1', request)

      expect(apiClient.put).toHaveBeenCalledWith('/admin/works/work1', request)
    })

    it('应该调用 deleteWork API', async () => {
      apiClient.delete.mockResolvedValue(undefined)

      await ApiService.deleteWork('work1')

      expect(apiClient.delete).toHaveBeenCalledWith('/admin/works/work1')
    })

    it('应该调用 moveWorkUp API', async () => {
      const mockResponse = { message: 'success' }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.moveWorkUp('work1')

      expect(apiClient.post).toHaveBeenCalledWith('/admin/works/work1/move-up')
    })

    it('应该调用 moveWorkDown API', async () => {
      const mockResponse = { message: 'success' }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.moveWorkDown('work1')

      expect(apiClient.post).toHaveBeenCalledWith('/admin/works/work1/move-down')
    })

    it('应该调用 toggleWorkVisibility API', async () => {
      const mockResponse = { work: { visible: false } }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.toggleWorkVisibility('work1')

      expect(apiClient.post).toHaveBeenCalledWith('/admin/works/work1/toggle-visibility')
    })
  })

  describe('后台管理 - 作品分类管理 - 真实执行', () => {
    it('应该调用 getAdminWorkCategories API', async () => {
      const mockResponse = {
        categories: [
          { category_id: 'cat1', category_name: '分类1', order: 1 }
        ],
        total: 1
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getAdminWorkCategories()

      expect(apiClient.get).toHaveBeenCalledWith('/admin/work-categories')
    })

    it('应该调用 createWorkCategory API', async () => {
      const mockResponse = {
        category: { category_id: 'cat2', category_name: '新分类' }
      }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const request = { category_name: '新分类', order: 1 }
      const result = await ApiService.createWorkCategory(request)

      expect(apiClient.post).toHaveBeenCalledWith('/admin/work-categories', request)
    })

    it('应该调用 updateWorkCategory API', async () => {
      const mockResponse = {
        category: { category_id: 'cat1', category_name: '更新后' }
      }
      apiClient.put.mockResolvedValue({ data: mockResponse })

      const request = { category_name: '更新后' }
      const result = await ApiService.updateWorkCategory('cat1', request)

      expect(apiClient.put).toHaveBeenCalledWith('/admin/work-categories/cat1', request)
    })

    it('应该调用 deleteWorkCategory API', async () => {
      apiClient.delete.mockResolvedValue(undefined)

      await ApiService.deleteWorkCategory('cat1')

      expect(apiClient.delete).toHaveBeenCalledWith('/admin/work-categories/cat1')
    })

    it('应该调用 moveWorkCategoryUp API', async () => {
      const mockResponse = { message: 'success' }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.moveWorkCategoryUp('cat1')

      expect(apiClient.post).toHaveBeenCalledWith('/admin/work-categories/cat1/move-up')
    })

    it('应该调用 moveWorkCategoryDown API', async () => {
      const mockResponse = { message: 'success' }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.moveWorkCategoryDown('cat1')

      expect(apiClient.post).toHaveBeenCalledWith('/admin/work-categories/cat1/move-down')
    })
  })

  describe('后台管理 - 课程目录管理 - 真实执行', () => {
    it('应该调用 getAdminCourseCategories API', async () => {
      const mockResponse = {
        categories: [
          { category_id: 'cat1', name: '目录1', order: 1 }
        ],
        total: 1
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getAdminCourseCategories()

      expect(apiClient.get).toHaveBeenCalledWith('/admin/course-categories')
    })

    it('应该调用 createCourseCategory API', async () => {
      const mockResponse = { message: '创建成功' }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const request = { name: '新目录', parent_id: null, order: 1 }
      const result = await ApiService.createCourseCategory(request)

      expect(apiClient.post).toHaveBeenCalledWith('/admin/course-categories', request)
    })

    it('应该调用 updateCourseCategory API', async () => {
      const mockResponse = { message: '更新成功' }
      apiClient.put.mockResolvedValue({ data: mockResponse })

      const request = { name: '更新后' }
      const result = await ApiService.updateCourseCategory('cat1', request)

      expect(apiClient.put).toHaveBeenCalledWith('/admin/course-categories/cat1', request)
    })

    it('应该调用 deleteCourseCategory API', async () => {
      const mockResponse = { message: '删除成功' }
      apiClient.delete.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.deleteCourseCategory('cat1')

      expect(apiClient.delete).toHaveBeenCalledWith('/admin/course-categories/cat1')
    })

    it('应该调用 moveCourseCategoryUp API', async () => {
      const mockResponse = { message: 'success' }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.moveCourseCategoryUp('cat1')

      expect(apiClient.post).toHaveBeenCalledWith('/admin/course-categories/cat1/move-up')
    })

    it('应该调用 moveCourseCategoryDown API', async () => {
      const mockResponse = { message: 'success' }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.moveCourseCategoryDown('cat1')

      expect(apiClient.post).toHaveBeenCalledWith('/admin/course-categories/cat1/move-down')
    })
  })

  describe('后台管理 - 课程文档管理 - 真实执行', () => {
    it('应该调用 getAdminCourseDocuments API（无筛选）', async () => {
      const mockResponse = {
        documents: [],
        total: 0,
        page: 1,
        page_size: 20
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getAdminCourseDocuments(1, 20)

      expect(apiClient.get).toHaveBeenCalledWith('/admin/course-documents?page=1&page_size=20')
    })

    it('应该调用 getAdminCourseDocuments API（带筛选参数）', async () => {
      const mockResponse = {
        documents: [],
        total: 0,
        page: 1,
        page_size: 20
      }
      apiClient.get.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getAdminCourseDocuments(1, 20, 'cat1')

      expect(apiClient.get).toHaveBeenCalledWith('/admin/course-documents?page=1&page_size=20&category_id=cat1')
    })

    it('应该调用 createCourseDocument API', async () => {
      const mockResponse = { message: '创建成功' }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const file = new File(['# 内容'], 'test.md', { type: 'text/markdown' })

      const result = await ApiService.createCourseDocument('标题', '摘要', 'cat1', 1, file)

      expect(apiClient.post).toHaveBeenCalledWith(
        '/admin/course-documents',
        expect.any(FormData),
        {
          headers: { 'Content-Type': 'multipart/form-data' },
        }
      )
    })

    it('应该调用 updateCourseDocument API', async () => {
      const mockResponse = { message: '更新成功' }
      apiClient.put.mockResolvedValue({ data: mockResponse })

      const request = { title: '更新后' }
      const result = await ApiService.updateCourseDocument('doc1', request)

      expect(apiClient.put).toHaveBeenCalledWith('/admin/course-documents/doc1', request)
    })

    it('应该调用 deleteCourseDocument API', async () => {
      const mockResponse = { message: '删除成功' }
      apiClient.delete.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.deleteCourseDocument('doc1')

      expect(apiClient.delete).toHaveBeenCalledWith('/admin/course-documents/doc1')
    })

    it('应该调用 moveCourseDocumentUp API', async () => {
      const mockResponse = { message: 'success' }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.moveCourseDocumentUp('doc1')

      expect(apiClient.post).toHaveBeenCalledWith('/admin/course-documents/doc1/move-up')
    })

    it('应该调用 moveCourseDocumentDown API', async () => {
      const mockResponse = { message: 'success' }
      apiClient.post.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.moveCourseDocumentDown('doc1')

      expect(apiClient.post).toHaveBeenCalledWith('/admin/course-documents/doc1/move-down')
    })
  })
})
