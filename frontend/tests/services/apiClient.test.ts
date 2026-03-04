/**
 * @vitest-environment node
 * API 客户端服务测试（不需要 DOM 环境）
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import type {
  AgentListResponse,
  SessionInitResponse,
  ChatResponse,
} from '../../src/types'

// Mock axios - 使用 vi.hoisted() 确保变量在 mock 工厂函数中可用
const { mockGet, mockPost } = vi.hoisted(() => {
  return {
    mockGet: vi.fn(),
    mockPost: vi.fn(),
  }
})

vi.mock('axios', () => {
  return {
    default: {
      create: vi.fn(() => ({
        get: mockGet,
        post: mockPost,
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() },
        },
      })),
    },
  }
})

// 在 mock 之后导入
import { ApiService } from '../../src/services/apiClient'

describe('ApiService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getAgents', () => {
    it('应该成功获取 Agent 列表', async () => {
      const mockResponse: AgentListResponse = {
        agents: [
          {
            agent_id: 'prompt_wizard',
            name: 'AI 提示词向导',
            description: '通过六步引导法，帮助您打造专家级提示词',
            icon: null,
          },
        ],
      }

      mockGet.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getAgents()

      expect(result).toEqual(mockResponse)
      expect(result.agents).toHaveLength(1)
      expect(result.agents[0].agent_id).toBe('prompt_wizard')
      expect(mockGet).toHaveBeenCalledWith('/agents')
    })

    it('应该处理空列表', async () => {
      const mockResponse: AgentListResponse = {
        agents: [],
      }

      mockGet.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getAgents()

      expect(result.agents).toHaveLength(0)
      expect(mockGet).toHaveBeenCalledWith('/agents')
    })
  })

  describe('createSession', () => {
    it('应该成功创建会话', async () => {
      const mockResponse: SessionInitResponse = {
        session_id: '550e8400-e29b-41d4-a716-446655440000',
        welcome_message: '你好！我是你的提示词向导。',
        ui_config: {
          show_preview: true,
          preview_types: ['markdown', 'html', 'svg'],
        },
        artifacts: [],
      }

      mockPost.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.createSession('prompt_wizard')

      expect(result).toEqual(mockResponse)
      expect(result.session_id).toBe('550e8400-e29b-41d4-a716-446655440000')
      expect(result.welcome_message).toBe('你好！我是你的提示词向导。')
      expect(mockPost).toHaveBeenCalledWith('/agents/prompt_wizard/sessions')
    })
  })

  describe('chat', () => {
    it('应该成功发送消息并获取回复', async () => {
      const mockResponse: ChatResponse = {
        reply: '好的，我来帮你打造一个专业的提示词。',
        artifacts: [
          {
            type: 'markdown',
            content: '## [角色设定]\n你是一位专家...',
            language: 'markdown',
            timestamp: '2026-01-01T10:00:00Z',
          },
        ],
      }

      mockPost.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.chat('session-id', {
        message: '我想让 AI 帮我写文案',
        history: [],
      })

      expect(result).toEqual(mockResponse)
      expect(result.reply).toBe('好的，我来帮你打造一个专业的提示词。')
      expect(result.artifacts).toHaveLength(1)
      expect(mockPost).toHaveBeenCalledWith('/tools/session-id/chat', {
        message: '我想让 AI 帮我写文案',
        history: [],
      }, { timeout: 300000 })
    })

    it('应该正确处理包含历史消息的请求', async () => {
      const mockResponse: ChatResponse = {
        reply: '继续对话...',
        artifacts: [],
      }

      mockPost.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.chat('session-id', {
        message: '继续',
        history: [
          {
            role: 'assistant',
            content: '你好！',
          },
        ],
      })

      expect(result).toEqual(mockResponse)
      expect(mockPost).toHaveBeenCalledWith('/tools/session-id/chat', {
        message: '继续',
        history: [
          {
            role: 'assistant',
            content: '你好！',
          },
        ],
      }, { timeout: 300000 })
    })
  })
})

