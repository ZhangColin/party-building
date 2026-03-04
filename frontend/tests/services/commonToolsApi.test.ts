/**
 * @vitest-environment node
 * 常用工具API测试
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import type {
  CommonToolCategoryResponse,
  CommonToolDetail,
} from '../../src/types'

// Mock axios
const { mockGet } = vi.hoisted(() => {
  return {
    mockGet: vi.fn(),
  }
})

vi.mock('axios', () => {
  return {
    default: {
      create: vi.fn(() => ({
        get: mockGet,
        post: vi.fn(),
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

describe('CommonTools API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getCommonToolCategories', () => {
    it('应该成功获取工具分类列表', async () => {
      const mockResponse: CommonToolCategoryResponse = {
        categories: [
          {
            id: 'doc-tools',
            name: '文档工具',
            icon: 'document-text',
            order: 1,
            tools: [
              {
                id: 'markdown-editor',
                name: 'Markdown编辑器',
                description: '在线编辑Markdown文档，实时预览，支持导出Word/PDF',
                type: 'built-in',
                icon: 'document-text',
                order: 1,
              },
            ],
          },
          {
            id: 'data-tools',
            name: '数据工具',
            icon: 'chart-bar',
            order: 2,
            tools: [],
          },
        ],
      }

      mockGet.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getCommonToolCategories()

      expect(result).toEqual(mockResponse)
      expect(result.categories).toHaveLength(2)
      expect(result.categories[0].id).toBe('doc-tools')
      expect(result.categories[0].tools).toHaveLength(1)
      expect(mockGet).toHaveBeenCalledWith('/common-tools/categories')
    })

    it('应该处理空分类列表', async () => {
      const mockResponse: CommonToolCategoryResponse = {
        categories: [],
      }

      mockGet.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getCommonToolCategories()

      expect(result.categories).toHaveLength(0)
      expect(mockGet).toHaveBeenCalledWith('/common-tools/categories')
    })

    it('应该处理API错误', async () => {
      mockGet.mockRejectedValue(new Error('网络错误'))

      await expect(ApiService.getCommonToolCategories()).rejects.toThrow('网络错误')
    })
  })

  describe('getCommonToolDetail', () => {
    it('应该成功获取内置工具详情', async () => {
      const mockResponse: CommonToolDetail = {
        id: 'markdown-editor',
        name: 'Markdown编辑器',
        description: '在线编辑Markdown文档，实时预览，支持导出Word/PDF',
        category_id: 'doc-tools',
        category_name: '文档工具',
        type: 'built-in',
        icon: 'document-text',
        order: 1,
        created_at: '2024-01-01T00:00:00Z',
      }

      mockGet.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getCommonToolDetail('markdown-editor')

      expect(result).toEqual(mockResponse)
      expect(result.id).toBe('markdown-editor')
      expect(result.type).toBe('built-in')
      expect(result.html_url).toBeUndefined()
      expect(mockGet).toHaveBeenCalledWith('/common-tools/tools/markdown-editor')
    })

    it('应该成功获取HTML工具详情', async () => {
      const mockResponse: CommonToolDetail = {
        id: 'html-tool',
        name: 'HTML工具',
        description: 'HTML工具描述',
        category_id: 'data-tools',
        category_name: '数据工具',
        type: 'html',
        icon: 'code',
        order: 1,
        html_url: '/static/common_tools/html/html-tool/index.html',
        created_at: '2024-01-01T00:00:00Z',
      }

      mockGet.mockResolvedValue({ data: mockResponse })

      const result = await ApiService.getCommonToolDetail('html-tool')

      expect(result).toEqual(mockResponse)
      expect(result.id).toBe('html-tool')
      expect(result.type).toBe('html')
      expect(result.html_url).toBe('/static/common_tools/html/html-tool/index.html')
      expect(mockGet).toHaveBeenCalledWith('/common-tools/tools/html-tool')
    })

    it('应该处理工具不存在的情况', async () => {
      mockGet.mockRejectedValue(new Error('工具不存在或已下线'))

      await expect(ApiService.getCommonToolDetail('non-existent')).rejects.toThrow(
        '工具不存在或已下线'
      )
    })

    it('应该处理API错误', async () => {
      mockGet.mockRejectedValue(new Error('网络错误'))

      await expect(ApiService.getCommonToolDetail('markdown-editor')).rejects.toThrow('网络错误')
    })
  })
})
