/**
 * sessionStore 单元测试 - 工具初始化bug
 * Bug: 消息框发消息，报工具未初始化，无法发送消息
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useSessionStore } from '@/stores/sessionStore'

// Mock ApiService
vi.mock('@/services/apiClient', () => ({
  ApiService: {
    chatStream: vi.fn(),
    getSessionDetail: vi.fn(),
  },
}))

describe('sessionStore - 工具初始化测试', () => {
  beforeEach(() => {
    // 每个测试前创建新的pinia实例
    setActivePinia(createPinia())
  })

  /**
   * Bug重现场景：在没有调用initTool的情况下调用sendMessage
   * 预期：应该抛出"工具未初始化，无法发送消息"错误
   */
  it('should throw error when sendMessage is called without initTool', async () => {
    const store = useSessionStore()

    // 不调用 initTool，直接调用 sendMessage
    await expect(store.sendMessage('test message')).rejects.toThrow('工具未初始化，无法发送消息')
  })

  /**
   * 验证initTool正确设置toolId
   */
  it('should set toolId after initTool is called', () => {
    const store = useSessionStore()

    // 初始状态：toolId 应该为 null
    expect(store.toolId).toBe(null)

    // 调用 initTool
    store.initTool('test-tool-id')

    // 验证 toolId 已设置
    expect(store.toolId).toBe('test-tool-id')
  })

  /**
   * 验证initTool后sendMessage不抛出"工具未初始化"错误
   */
  it('should not throw "tool not initialized" error when sendMessage is called after initTool', async () => {
    const store = useSessionStore()

    // 先初始化工具
    store.initTool('test-tool-id')

    // 这个测试会因为没有API而失败，但不应该因为"工具未初始化"失败
    try {
      await store.sendMessage('test message')
    } catch (err) {
      // 错误不应该是"工具未初始化"
      const errorMessage = err instanceof Error ? err.message : String(err)
      expect(errorMessage).not.toContain('工具未初始化')
      // 可能是网络错误或其他错误
    }
  })

  /**
   * 验证clearSession后toolId被保留（新行为）
   * clearSession只清空会话数据，不应该清空toolId
   */
  it('should preserve toolId after clearSession is called', () => {
    const store = useSessionStore()

    // 初始化工具
    store.initTool('test-tool-id')
    expect(store.toolId).toBe('test-tool-id')

    // 清空会话
    store.clearSession()

    // 验证 toolId 被保留（这是正确的行为！）
    // 清空会话只是清空当前对话，不代表要切换工具
    expect(store.toolId).toBe('test-tool-id')
  })

  /**
   * clearSession后应该能正常发送消息（因为toolId被保留）
   */
  it('should allow sendMessage after clearSession (toolId preserved)', async () => {
    const store = useSessionStore()

    // 初始化工具
    store.initTool('test-tool-id')

    // 清空会话
    store.clearSession()

    // toolId被保留，所以应该能调用sendMessage（虽然会因为未登录而失败，但不是"工具未初始化"错误）
    try {
      await store.sendMessage('test message')
    } catch (err) {
      // 错误不应该是"工具未初始化"
      const errorMessage = err instanceof Error ? err.message : String(err)
      expect(errorMessage).not.toContain('工具未初始化')
    }
  })

  /**
   * 验证reset后toolId被清空
   */
  it('should clear toolId after reset is called', () => {
    const store = useSessionStore()

    // 初始化工具
    store.initTool('test-tool-id')
    expect(store.toolId).toBe('test-tool-id')

    // 重置
    store.reset()

    // 验证 toolId 已清空
    expect(store.toolId).toBe(null)
  })

  /**
   * Bug场景：toolId为空字符串时应该抛出错误
   */
  it('should throw error when toolId is empty string', async () => {
    const store = useSessionStore()

    // 直接设置 toolId 为空字符串（模拟API返回异常的情况）
    store.toolId = ''

    // 应该抛出"工具未初始化"错误，因为空字符串是falsy
    await expect(store.sendMessage('test message')).rejects.toThrow('工具未初始化，无法发送消息')
  })

  /**
   * 修复后的行为：initTool应该拒绝空字符串
   */
  it('should reject empty string in initTool', async () => {
    const store = useSessionStore()

    // 调用 initTool 传入空字符串
    store.initTool('')

    // 验证 toolId 保持为 null（被拒绝）
    expect(store.toolId).toBe(null)

    // 应该抛出"工具未初始化"错误
    await expect(store.sendMessage('test message')).rejects.toThrow('工具未初始化，无法发送消息')
  })

  /**
   * 验证修复：initTool应该拒绝空字符串
   */
  it('should reject empty string in initTool after fix', () => {
    const store = useSessionStore()

    // 调用 initTool 传入空字符串
    store.initTool('')

    // 修复后：toolId 应该保持为 null，或者被拒绝
    // 当前行为：toolId 会被设置为空字符串（这是bug）
    // 期望行为：initTool 应该拒绝空字符串或 null
    expect(store.toolId).not.toBe('')
    expect(store.toolId).toBe(null)
  })

  /**
   * Bug: restoreSession可能设置无效的toolId
   * 当API返回空tool_id时，restoreSession应该拒绝，避免后续sendMessage失败
   */
  describe('restoreSession - toolId验证', () => {
    it('should preserve existing toolId when API returns null tool_id', async () => {
      const store = useSessionStore()

      // 先初始化一个工具
      store.initTool('existing-tool-id')
      expect(store.toolId).toBe('existing-tool-id')

      // Mock ApiService.getSessionDetail 返回空 tool_id
      const { ApiService } = await import('@/services/apiClient')
      vi.spyOn(ApiService, 'getSessionDetail').mockResolvedValue({
        session_id: 'test-session-id',
        tool_id: null, // API返回null
        title: 'Test Session',
        messages: []
      } as any)

      // 调用 restoreSession
      try {
        await store.restoreSession('test-session-id')
      } catch (err) {
        // 可能因为API调用而失败，但不是重点
      }

      // 验证：toolId应该保持原有值，而不是被设置为null
      expect(store.toolId).toBe('existing-tool-id')
    })

    it('should preserve existing toolId when API returns empty string tool_id', async () => {
      const store = useSessionStore()

      // 先初始化一个工具
      store.initTool('existing-tool-id')
      expect(store.toolId).toBe('existing-tool-id')

      // Mock ApiService.getSessionDetail 返回空字符串 tool_id
      const { ApiService } = await import('@/services/apiClient')
      vi.spyOn(ApiService, 'getSessionDetail').mockResolvedValue({
        session_id: 'test-session-id',
        tool_id: '', // API返回空字符串
        title: 'Test Session',
        messages: []
      } as any)

      // 调用 restoreSession
      try {
        await store.restoreSession('test-session-id')
      } catch (err) {
        // 可能因为API调用而失败，但不是重点
      }

      // 验证：toolId应该保持原有值，而不是被设置为空字符串
      expect(store.toolId).toBe('existing-tool-id')
    })

    it('should update toolId when API returns valid tool_id', async () => {
      const store = useSessionStore()

      // 先初始化一个工具
      store.initTool('old-tool-id')
      expect(store.toolId).toBe('old-tool-id')

      // Mock ApiService.getSessionDetail 返回有效 tool_id
      const { ApiService } = await import('@/services/apiClient')
      vi.spyOn(ApiService, 'getSessionDetail').mockResolvedValue({
        session_id: 'test-session-id',
        tool_id: 'new-tool-id', // API返回有效tool_id
        title: 'Test Session',
        messages: []
      } as any)

      // 调用 restoreSession
      try {
        await store.restoreSession('test-session-id')
      } catch (err) {
        // 可能因为其他原因而失败，但不是重点
      }

      // 验证：toolId应该被更新为新的有效值
      expect(store.toolId).toBe('new-tool-id')
    })
  })
})

describe('sessionStore - 计算属性测试', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('hasSession 应该在设置sessionId后返回true', () => {
    const store = useSessionStore()
    expect(store.hasSession).toBe(false)

    store.sessionId = 'test-session-id'
    expect(store.hasSession).toBe(true)
  })

  it('messageCount 应该返回正确的消息数量', () => {
    const store = useSessionStore()
    expect(store.messageCount).toBe(0)

    store.messages = [
      { role: 'user', content: 'test1', created_at: new Date().toISOString() },
      { role: 'assistant', content: 'test2', created_at: new Date().toISOString() },
    ]
    expect(store.messageCount).toBe(2)
  })

  it('showPreview 应该在设置artifact后返回true', () => {
    const store = useSessionStore()
    expect(store.showPreview).toBe(false)

    store.setPreviewArtifact({
      type: 'html',
      content: '<html></html>',
      title: 'Test',
    } as any)
    expect(store.showPreview).toBe(true)
  })
})

describe('sessionStore - setPreviewArtifact测试', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('应该设置预览artifact', () => {
    const store = useSessionStore()
    const artifact = {
      type: 'html',
      content: '<html></html>',
      title: 'Test',
    } as any

    store.setPreviewArtifact(artifact)
    expect(store.currentPreviewArtifact).toEqual(artifact)
  })

  it('应该清除预览artifact', () => {
    const store = useSessionStore()
    const artifact = {
      type: 'html',
      content: '<html></html>',
      title: 'Test',
    } as any

    store.setPreviewArtifact(artifact)
    expect(store.currentPreviewArtifact).toEqual(artifact)

    store.setPreviewArtifact(null)
    expect(store.currentPreviewArtifact).toBe(null)
  })
})

describe('sessionStore - retryMessage测试', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('应该重试失败的消息', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    // 添加一个错误消息
    store.messages = [
      {
        role: 'user',
        content: 'test message',
        error: '发送失败',
        created_at: new Date().toISOString(),
      },
    ]

    // Mock成功的重试
    vi.mocked(ApiService.chatStream).mockImplementation(
      async (_toolId, _data, onChunk) => {
        onChunk({ type: 'session_id', session_id: 'new-session' })
        onChunk({ type: 'content', content: 'AI回复' })
        onChunk({ type: 'done', artifacts: [] })
      }
    )

    await store.retryMessage(0)

    // 验证错误被清除
    expect(store.messages[0].error).toBeUndefined()
  })

  it('应该忽略非用户消息', async () => {
    const store = useSessionStore()

    store.messages = [
      {
        role: 'assistant',
        content: 'AI回复',
        created_at: new Date().toISOString(),
      },
    ]

    // 不应该调用sendMessage
    const chatStreamSpy = vi.spyOn(
      await import('@/services/apiClient'),
      'ApiService',
      'chatStream'
    )

    await store.retryMessage(0)
    expect(chatStreamSpy).not.toHaveBeenCalled()
  })

  it('应该忽略没有错误的消息', async () => {
    const store = useSessionStore()

    store.messages = [
      {
        role: 'user',
        content: '正常消息',
        created_at: new Date().toISOString(),
      },
    ]

    // 不应该调用sendMessage
    const chatStreamSpy = vi.spyOn(
      await import('@/services/apiClient'),
      'ApiService',
      'chatStream'
    )

    await store.retryMessage(0)
    expect(chatStreamSpy).not.toHaveBeenCalled()
  })
})

describe('sessionStore - initTool边界情况测试', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('应该在loading时拒绝重新初始化', () => {
    const store = useSessionStore()

    store.initTool('tool1')
    store.loading = true

    store.initTool('tool2')

    // toolId不应该改变
    expect(store.toolId).toBe('tool1')
  })

  it('应该在相同toolId且messages不为空时跳过初始化', () => {
    const store = useSessionStore()

    store.initTool('tool1')
    store.messages = [
      { role: 'user', content: 'test', created_at: new Date().toISOString() },
    ]

    store.initTool('tool1')

    // messages不应该被清空
    expect(store.messages).toHaveLength(1)
  })

  it('应该在相同toolId但messages为空时重新初始化', () => {
    const store = useSessionStore()

    store.initTool('tool1')
    store.sessionId = 'old-session'

    store.initTool('tool1')

    // sessionId应该被清空
    expect(store.sessionId).toBe(null)
  })
})

describe('sessionStore - restoreSession边界情况测试', () => {
  beforeEach(async () => {
    setActivePinia(createPinia())
    const { ApiService } = await import('@/services/apiClient')
    vi.clearAllMocks()
  })

  it('应该在loading时拒绝恢复会话', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.loading = true

    // 不应该调用API
    const getSessionDetailSpy = vi.spyOn(ApiService, 'getSessionDetail')

    try {
      await store.restoreSession('test-session-id')
    } catch (err) {
      // 可能失败
    }

    // 应该返回且不调用API
    expect(getSessionDetailSpy).not.toHaveBeenCalled()
  })

  it('应该在相同session时跳过恢复', async () => {
    const store = useSessionStore()

    store.sessionId = 'test-session-id'
    store.messages = [
      { role: 'user', content: 'test', created_at: new Date().toISOString() },
    ]

    // 直接调用restoreSession，不应该调用API
    await store.restoreSession('test-session-id')

    // session ID保持不变
    expect(store.sessionId).toBe('test-session-id')
    // messages保持不变
    expect(store.messages).toHaveLength(1)
  })

  it('应该拒绝空的sessionId参数', async () => {
    const store = useSessionStore()

    // 不应该抛出错误，应该直接返回
    await expect(store.restoreSession('')).resolves.toBeUndefined()

    // session ID应该仍然是null
    expect(store.sessionId).toBe(null)
  })

  /**
   * 测试restoreSession的错误处理（第229-230行）
   */
  it('应该正确处理restoreSession的API错误', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    // Mock API错误
    vi.spyOn(ApiService, 'getSessionDetail').mockRejectedValue(
      new Error('网络错误')
    )

    // 应该抛出错误
    await expect(store.restoreSession('test-session-id')).rejects.toThrow('网络错误')

    // 验证error状态被设置
    expect(store.error).toBe('网络错误')
    // loading应该被重置
    expect(store.loading).toBe(false)
  })

  /**
   * 测试restoreSession处理非Error类型的错误（第229行false分支）
   */
  it('应该正确处理非Error类型的错误', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    // Mock非Error类型的错误（如字符串）
    vi.spyOn(ApiService, 'getSessionDetail').mockRejectedValue('字符串错误')

    // 应该抛出错误
    await expect(store.restoreSession('test-session-id')).rejects.toThrow()

    // 验证error状态被设置为默认消息（第229行fallback）
    expect(store.error).toBe('恢复会话失败')
    // loading应该被重置
    expect(store.loading).toBe(false)
  })

  /**
   * 测试restoreSession处理带artifacts的消息
   */
  it('应该正确恢复包含artifacts的消息', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    vi.spyOn(ApiService, 'getSessionDetail').mockResolvedValue({
      session_id: 'test-session-id',
      tool_id: 'test-tool',
      title: 'Test Session',
      messages: [
        {
          role: 'user',
          content: '生成一个HTML',
          timestamp: new Date().toISOString(),
        },
        {
          role: 'assistant',
          content: '这是HTML内容',
          timestamp: new Date().toISOString(),
          artifacts: [
            {
              type: 'html',
              content: '<html><body>Hello</body></html>',
              title: 'HTML成果物',
            },
          ],
        },
      ],
    } as any)

    await store.restoreSession('test-session-id')

    // 验证消息被正确恢复
    expect(store.messages).toHaveLength(2)
    expect(store.messages[1].artifacts).toHaveLength(1)
    expect(store.messages[1].artifacts![0].type).toBe('html')
  })

  /**
   * 测试restoreSession处理使用created_at而非timestamp的消息（第225行fallback）
   */
  it('应该正确处理使用created_at字段的消息', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    vi.spyOn(ApiService, 'getSessionDetail').mockResolvedValue({
      session_id: 'test-session-id',
      tool_id: 'test-tool',
      title: 'Test Session',
      messages: [
        {
          role: 'user',
          content: '测试消息',
          // 没有timestamp字段，只有created_at（第225行的fallback）
          created_at: new Date().toISOString(),
        },
      ],
    } as any)

    await store.restoreSession('test-session-id')

    // 验证消息被正确恢复，使用了created_at作为timestamp
    expect(store.messages).toHaveLength(1)
    expect(store.messages[0].timestamp).toBeDefined()
  })
})

describe('sessionStore - sendMessage详细测试', () => {
  beforeEach(async () => {
    setActivePinia(createPinia())
    const { ApiService } = await import('@/services/apiClient')
    vi.clearAllMocks()
  })

  it('应该正确处理流式响应', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    const chunks: any[] = []
    vi.mocked(ApiService.chatStream).mockImplementation(
      async (_toolId, _data, onChunk) => {
        onChunk({ type: 'session_id', session_id: 'test-session' })
        onChunk({ type: 'content', content: 'Hello' })
        onChunk({ type: 'content', content: ' World' })
        onChunk({ type: 'done', artifacts: [] })
      }
    )

    await store.sendMessage('test message')

    // 验证消息结构
    expect(store.messages).toHaveLength(2)
    expect(store.messages[0].role).toBe('user')
    expect(store.messages[0].content).toBe('test message')
    expect(store.messages[0].pending).toBe(false)

    expect(store.messages[1].role).toBe('assistant')
    expect(store.messages[1].content).toBe('Hello World')
    expect(store.messages[1].pending).toBe(false)
  })

  /**
   * 测试session_id事件没有session_id的情况（第103行false分支）
   */
  it('应该处理session_id事件没有session_id字段的情况', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    vi.mocked(ApiService.chatStream).mockImplementation(
      async (_toolId, _data, onChunk) => {
        // session_id事件但没有session_id字段
        onChunk({ type: 'session_id' })
        onChunk({ type: 'content', content: 'AI回复' })
        onChunk({ type: 'done', artifacts: [] })
      }
    )

    await store.sendMessage('test message')

    // 验证sessionId保持为null
    expect(store.sessionId).toBe(null)
  })

  /**
   * 测试content事件时AI消息不存在的边界情况（第108行false分支）
   */
  it('应该处理content时AI消息不存在的边界情况', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    vi.mocked(ApiService.chatStream).mockImplementation(
      async (_toolId, _data, onChunk) => {
        onChunk({ type: 'session_id', session_id: 'test-session' })
        // 删除AI消息
        store.messages.splice(1, 1)
        // 发送content事件，但AI消息不存在
        onChunk({ type: 'content', content: 'AI回复' })
        onChunk({ type: 'done', artifacts: [] })
      }
    )

    await store.sendMessage('test message')

    // 验证不会崩溃，AI消息不存在
    expect(store.messages).toHaveLength(1)
  })

  /**
   * 测试done事件没有artifacts字段的情况（第147行fallback）
   */
  it('应该处理done事件没有artifacts字段的情况', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    vi.mocked(ApiService.chatStream).mockImplementation(
      async (_toolId, _data, onChunk) => {
        onChunk({ type: 'session_id', session_id: 'test-session' })
        onChunk({ type: 'content', content: 'AI回复' })
        // done事件没有artifacts字段
        onChunk({ type: 'done' })
      }
    )

    await store.sendMessage('test message')

    // 验证artifacts被设置为空数组
    expect(store.messages[1].artifacts).toEqual([])
    expect(store.messages[1].pending).toBe(false)
  })

  it('应该正确处理标题生成事件', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    vi.mocked(ApiService.chatStream).mockImplementation(
      async (_toolId, _data, onChunk) => {
        onChunk({ type: 'session_id', session_id: 'test-session' })
        onChunk({ type: 'title_generated', session_id: 'new-title-session' })
        onChunk({ type: 'content', content: 'Response' })
        onChunk({ type: 'done', artifacts: [] })
      }
    )

    await store.sendMessage('test message')

    // 验证标题生成会话ID被记录
    expect(store.titleGeneratedSessionId).toBe('new-title-session')
  })

  /**
   * 测试title_generated事件没有session_id的情况（第155行false分支）
   */
  it('应该处理没有session_id的title_generated事件', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    vi.mocked(ApiService.chatStream).mockImplementation(
      async (_toolId, _data, onChunk) => {
        onChunk({ type: 'session_id', session_id: 'test-session' })
        onChunk({ type: 'title_generated' }) // 没有session_id
        onChunk({ type: 'content', content: 'Response' })
        onChunk({ type: 'done', artifacts: [] })
      }
    )

    await store.sendMessage('test message')

    // 验证不会设置titleGeneratedSessionId
    expect(store.titleGeneratedSessionId).toBe(null)
  })

  it('应该正确处理错误响应', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    vi.mocked(ApiService.chatStream).mockImplementation(
      async (_toolId, _data, onChunk) => {
        onChunk({ type: 'session_id', session_id: 'test-session' })
        onChunk({ type: 'error', error: 'API错误' })
      }
    )

    await expect(store.sendMessage('test message')).rejects.toThrow('API错误')

    // 验证用户消息被标记为错误
    expect(store.messages[0].error).toBe('API错误')
    expect(store.messages[0].pending).toBe(false)

    // AI消息应该被移除
    expect(store.messages).toHaveLength(1)
  })

  /**
   * 测试sendMessage处理非Error类型的错误（第173、175行fallback）
   */
  it('应该正确处理非Error类型的发送错误', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    // Mock抛出非Error类型的错误
    vi.mocked(ApiService.chatStream).mockImplementation(
      async () => {
        throw '字符串错误' // 非Error类型
      }
    )

    await expect(store.sendMessage('test message')).rejects.toEqual('字符串错误')

    // 验证用户消息被标记为默认错误消息（第173行fallback）
    expect(store.messages[0].error).toBe('发送消息失败')
    expect(store.error).toBe('发送消息失败')
  })

  /**
   * 测试aiMsgIndex超出数组长度的情况（第167行false分支）
   */
  it('应该处理aiMsgIndex超出数组长度的错误情况', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    let callCount = 0
    vi.mocked(ApiService.chatStream).mockImplementation(
      async () => {
        callCount++
        if (callCount === 1) {
          // 第一次调用：先添加用户消息和AI消息
          store.messages.push(
            { role: 'user', content: 'test', created_at: new Date().toISOString() },
            { role: 'assistant', content: '', created_at: new Date().toISOString() }
          )
          // 然后清空messages，模拟极端情况
          store.messages = []
        }
        throw new Error('测试错误')
      }
    )

    await expect(store.sendMessage('test')).rejects.toThrow('测试错误')

    // 验证不会因为索引越界而崩溃
    expect(store.messages).toBeDefined()
  })

  /**
   * 测试userMsgIndex超出数组长度的情况（第171行false分支）
   */
  it('应该处理userMsgIndex超出数组长度的错误情况', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    vi.mocked(ApiService.chatStream).mockImplementation(
      async () => {
        // 添加用户消息
        store.messages.push({
          role: 'user',
          content: 'test',
          created_at: new Date().toISOString()
        })
        // 立即删除用户消息，模拟极端情况
        store.messages = []
        throw new Error('测试错误')
      }
    )

    await expect(store.sendMessage('test')).rejects.toThrow('测试错误')

    // 验证不会因为索引越界而崩溃
    expect(store.messages).toHaveLength(0)
  })

  /**
   * 测试代码块重复检测逻辑（第121-128行）
   * 场景：AI在代码块中重复发送```标记
   */
  it('应该检测并清理重复的代码块标记', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    vi.mocked(ApiService.chatStream).mockImplementation(
      async (_toolId, _data, onChunk) => {
        onChunk({ type: 'session_id', session_id: 'test-session' })
        // 先发送一个代码块的开始（3个```）
        onChunk({ type: 'content', content: '这是代码块开始：\n```html\n' })
        // AI可能重复发送代码块标记（bug场景）
        // 此时currentContent中有奇数个```（3个），newContent以```html开头
        onChunk({ type: 'content', content: '```html\n<div>content</div>\n```\n' })
        onChunk({ type: 'done', artifacts: [] })
      }
    )

    await store.sendMessage('test message')

    // 验证重复的```html被清理（因为当前内容中已经有奇数个```）
    const assistantMsg = store.messages[1]
    expect(assistantMsg.content).toContain('这是代码块开始：')
    // 第二次出现的```html应该被移除
    expect(assistantMsg.content).not.toMatch(/```html\s*```html/)
  })

  /**
   * 测试新内容以代码块开头但当前内容没有```的情况（第121行fallback）
   */
  it('应该处理新内容以代码块开头但当前内容没有```的情况', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    vi.mocked(ApiService.chatStream).mockImplementation(
      async (_toolId, _data, onChunk) => {
        onChunk({ type: 'session_id', session_id: 'test-session' })
        // 当前内容没有```
        onChunk({ type: 'content', content: '这是普通文本' })
        // 新内容以代码块开头
        onChunk({ type: 'content', content: '```html\n<div>new</div>\n```\n' })
        onChunk({ type: 'done', artifacts: [] })
      }
    )

    await store.sendMessage('test message')

    // 验证代码块标记被保留（因为当前内容没有```）
    const assistantMsg = store.messages[1]
    expect(assistantMsg.content).toContain('这是普通文本```html\n<div>new</div>')
  })

  /**
   * 测试发送带历史消息的会话（第94行）
   * 场景：已有对话历史，发送新消息时应该包含历史记录
   */
  it('应该在发送消息时包含历史记录', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')
    store.sessionId = 'existing-session'

    // 添加历史消息
    store.messages = [
      { role: 'user', content: '第一条消息', created_at: new Date().toISOString() },
      { role: 'assistant', content: '第一条回复', created_at: new Date().toISOString() },
    ]

    // Mock chatStream 来捕获历史记录参数
    let capturedHistory: any[] = []
    vi.mocked(ApiService.chatStream).mockImplementation(
      async (_toolId, data, onChunk) => {
        capturedHistory = data.history || []
        onChunk({ type: 'session_id', session_id: 'test-session' })
        onChunk({ type: 'content', content: '新回复' })
        onChunk({ type: 'done', artifacts: [] })
      }
    )

    await store.sendMessage('新消息')

    // 验证历史记录被正确传递（排除刚添加的两条占位消息）
    expect(capturedHistory).toHaveLength(2)
    expect(capturedHistory[0].role).toBe('user')
    expect(capturedHistory[0].content).toBe('第一条消息')
    expect(capturedHistory[1].role).toBe('assistant')
    expect(capturedHistory[1].content).toBe('第一条回复')
  })

  /**
   * 测试代码块重复检测的分支：偶数个```时不清理（第94行和125行）
   */
  it('应该在偶数个```时保留新的代码块标记', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    vi.mocked(ApiService.chatStream).mockImplementation(
      async (_toolId, _data, onChunk) => {
        onChunk({ type: 'session_id', session_id: 'test-session' })
        // 发送完整的代码块（包含开始和结束标记，共4个```）
        onChunk({ type: 'content', content: '```html\n<div>old</div>\n```\n' })
        // 当前内容中有偶数个```（4个），新内容的```不应该被清理
        onChunk({ type: 'content', content: '```html\n<div>new</div>\n```\n' })
        onChunk({ type: 'done', artifacts: [] })
      }
    )

    await store.sendMessage('test message')

    // 验证新的代码块标记被保留
    const assistantMsg = store.messages[1]
    expect(assistantMsg.content).toContain('```html\n<div>old</div>')
    expect(assistantMsg.content).toContain('```html\n<div>new</div>')
    // 应该有两组代码块
    const codeBlockCount = (assistantMsg.content.match(/```html/g) || []).length
    expect(codeBlockCount).toBe(2)
  })

  /**
   * 测试done事件时AI消息已被删除的边界情况（第146行false分支）
   * 这是一种极端情况，可能因为某些竞态条件导致消息被删除
   */
  it('应该处理done时AI消息不存在的边界情况', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    vi.mocked(ApiService.chatStream).mockImplementation(
      async (_toolId, _data, onChunk) => {
        onChunk({ type: 'session_id', session_id: 'test-session' })
        onChunk({ type: 'content', content: 'AI回复' })
        // 在done之前删除AI消息
        store.messages.splice(1, 1)
        onChunk({ type: 'done', artifacts: [] })
      }
    )

    await store.sendMessage('test message')

    // 验证不会因为AI消息不存在而崩溃
    expect(store.messages).toBeDefined()
    // AI消息被删除，只保留用户消息
    expect(store.messages).toHaveLength(1)
  })

  /**
   * 测试done事件时用户消息已被删除的边界情况（第150行false分支）
   */
  it('应该处理done时用户消息不存在的边界情况', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    vi.mocked(ApiService.chatStream).mockImplementation(
      async (_toolId, _data, onChunk) => {
        onChunk({ type: 'session_id', session_id: 'test-session' })
        onChunk({ type: 'content', content: 'AI回复' })
        // 在done之前删除用户消息
        store.messages.splice(0, 1)
        onChunk({ type: 'done', artifacts: [] })
      }
    )

    await store.sendMessage('test message')

    // 验证不会因为用户消息不存在而崩溃
    expect(store.messages).toBeDefined()
    // 用户消息被删除，只保留AI消息
    expect(store.messages).toHaveLength(1)
  })

  /**
   * 测试用户消息和AI消息都不存在的极端情况（第150行false分支）
   */
  it('应该处理用户消息和AI消息都不存在的极端情况', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    vi.mocked(ApiService.chatStream).mockImplementation(
      async (_toolId, _data, onChunk) => {
        onChunk({ type: 'session_id', session_id: 'test-session' })
        onChunk({ type: 'content', content: 'AI回复' })
        // 删除所有消息
        store.messages = []
        onChunk({ type: 'done', artifacts: [] })
      }
    )

    await store.sendMessage('test message')

    // 验证不会崩溃
    expect(store.messages).toHaveLength(0)
  })

  /**
   * 测试未知类型的chunk事件（第158行false分支）
   */
  it('应该忽略未知类型的chunk事件', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    vi.mocked(ApiService.chatStream).mockImplementation(
      async (_toolId, _data, onChunk) => {
        onChunk({ type: 'session_id', session_id: 'test-session' })
        onChunk({ type: 'content', content: 'AI回复' })
        // 发送未知类型的chunk
        onChunk({ type: 'unknown_type' as any, data: 'some data' })
        onChunk({ type: 'done', artifacts: [] })
      }
    )

    await store.sendMessage('test message')

    // 验证不会崩溃，未知类型被忽略
    expect(store.messages).toHaveLength(2)
    expect(store.messages[1].content).toBe('AI回复')
  })

  /**
   * 测试error事件时没有error字段的情况（第160行fallback）
   */
  it('应该处理error事件没有error字段的情况', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    vi.mocked(ApiService.chatStream).mockImplementation(
      async (_toolId, _data, onChunk) => {
        onChunk({ type: 'session_id', session_id: 'test-session' })
        // error事件但没有error字段
        onChunk({ type: 'error' })
      }
    )

    await expect(store.sendMessage('test message')).rejects.toThrow('发送消息失败')

    // 验证用户消息被标记为默认错误消息
    expect(store.messages[0].error).toBe('发送消息失败')
  })

  /**
   * 测试空内容处理（第94行的分支条件）
   * 场景：currentContent或newContent为空
   */
  it('应该正确处理空内容块', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    vi.mocked(ApiService.chatStream).mockImplementation(
      async (_toolId, _data, onChunk) => {
        onChunk({ type: 'session_id', session_id: 'test-session' })
        // 发送空内容块
        onChunk({ type: 'content', content: '' })
        onChunk({ type: 'content', content: '正常内容' })
        onChunk({ type: 'done', artifacts: [] })
      }
    )

    await store.sendMessage('test message')

    // 验证空内容块不会导致错误
    expect(store.messages[1].content).toBe('正常内容')
    expect(store.messages[1].pending).toBe(false)
  })

  /**
   * 测试不匹配代码块模式的内容（第116行的else分支）
   */
  it('应该正确处理非代码块标记的内容', async () => {
    const store = useSessionStore()
    const { ApiService } = await import('@/services/apiClient')

    store.initTool('test-tool')

    vi.mocked(ApiService.chatStream).mockImplementation(
      async (_toolId, _data, onChunk) => {
        onChunk({ type: 'session_id', session_id: 'test-session' })
        // 普通文本，不以```开头
        onChunk({ type: 'content', content: '这是普通文本' })
        onChunk({ type: 'content', content: '```不是代码块开头\n' })
        onChunk({ type: 'done', artifacts: [] })
      }
    )

    await store.sendMessage('test message')

    // 验证内容被正常拼接
    const assistantMsg = store.messages[1]
    expect(assistantMsg.content).toContain('这是普通文本')
    expect(assistantMsg.content).toContain('```不是代码块开头\n')
  })
})
