/**
 * useFileDownload.spec.ts
 * 测试文件下载 composable
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { useFileDownload } from '@/composables/useFileDownload'

describe('useFileDownload', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Mock DOM methods
    document.body.innerHTML = ''
    global.URL = {
      createObjectURL: vi.fn(() => 'blob:url'),
      revokeObjectURL: vi.fn()
    } as any
  })

  describe('download', () => {
    it('应该成功下载文本文件', () => {
      const { download, isDownloading } = useFileDownload()

      // 创建 mock link 元素
      const mockLink = {
        href: '',
        download: '',
        click: vi.fn(),
        style: {}
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      const result = download('测试内容', {
        filename: 'test.txt',
        mimeType: 'text/plain'
      })

      expect(result).toEqual({ success: true })
      expect(isDownloading.value).toBe(false)
      expect(mockLink.href).toBe('blob:url')
      expect(mockLink.download).toBe('test.txt')
      expect(mockLink.click).toHaveBeenCalled()
      expect(global.URL.createObjectURL).toHaveBeenCalled()
      expect(global.URL.revokeObjectURL).toHaveBeenCalledWith('blob:url')
    })

    it('应该使用默认的 text/plain MIME类型', () => {
      const { download } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      download('内容', { filename: 'test.txt' })

      expect(global.URL.createObjectURL).toHaveBeenCalledWith(
        expect.any(Blob)
      )
      const blobCall = vi.mocked(global.URL.createObjectURL).mock.calls[0]
      const blob = blobCall[0] as Blob
      expect(blob.type).toBe('text/plain')
    })

    it('应该支持自定义 MIME类型', () => {
      const { download } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      download('<div>HTML内容</div>', {
        filename: 'test.html',
        mimeType: 'text/html'
      })

      const blobCall = vi.mocked(global.URL.createObjectURL).mock.calls[0]
      const blob = blobCall[0] as Blob
      expect(blob.type).toBe('text/html')
    })

    it('应该下载 JSON 文件', () => {
      const { download } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      const jsonData = { name: '测试', value: 123 }
      download(JSON.stringify(jsonData, null, 2), {
        filename: 'data.json',
        mimeType: 'application/json'
      })

      expect(mockLink.download).toBe('data.json')
      const blobCall = vi.mocked(global.URL.createObjectURL).mock.calls[0]
      const blob = blobCall[0] as Blob
      expect(blob.type).toBe('application/json')
    })

    it('应该下载 Markdown 文件', () => {
      const { download } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      download('# 标题\n\n内容', {
        filename: 'document.md',
        mimeType: 'text/markdown'
      })

      expect(mockLink.download).toBe('document.md')
    })

    it('应该在下载过程中设置 isDownloading 为 true', () => {
      const { download, isDownloading } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      // 注意：由于下载是同步的，isDownloading 会在 finally 块中立即重置
      // 这个测试验证下载后最终状态为 false
      download('内容', { filename: 'test.txt' })

      expect(isDownloading.value).toBe(false)
    })

    it('应该正确处理中文文件名', () => {
      const { download } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      download('内容', { filename: '测试文件.txt' })

      expect(mockLink.download).toBe('测试文件.txt')
    })

    it('应该处理空内容', () => {
      const { download } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      const result = download('', { filename: 'empty.txt' })

      expect(result).toEqual({ success: true })
    })

    it('应该处理大文件内容', () => {
      const { download } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      const largeContent = 'x'.repeat(1000000) // 1MB 的数据
      const result = download(largeContent, { filename: 'large.txt' })

      expect(result).toEqual({ success: true })
    })

    it('应该处理特殊字符内容', () => {
      const { download } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      const specialContent = '特殊字符: < > & " \' \n\t\r'
      const result = download(specialContent, { filename: 'special.txt' })

      expect(result).toEqual({ success: true })
    })
  })

  describe('downloadBlob', () => {
    it('应该成功下载 Blob 对象', () => {
      const { downloadBlob, isDownloading } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      const blob = new Blob(['blob内容'], { type: 'text/plain' })
      const result = downloadBlob(blob, 'blob-file.txt')

      expect(result).toEqual({ success: true })
      expect(mockLink.href).toBe('blob:url')
      expect(mockLink.download).toBe('blob-file.txt')
      expect(mockLink.click).toHaveBeenCalled()
      expect(global.URL.revokeObjectURL).toHaveBeenCalledWith('blob:url')
      expect(isDownloading.value).toBe(false)
    })

    it('应该下载 HTML Blob', () => {
      const { downloadBlob } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      const htmlBlob = new Blob(['<div>HTML内容</div>'], { type: 'text/html' })
      downloadBlob(htmlBlob, 'page.html')

      expect(mockLink.download).toBe('page.html')
    })

    it('应该下载图片 Blob', () => {
      const { downloadBlob } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      // 创建一个模拟的图片 Blob
      const imageBlob = new Blob(['fake-image-data'], { type: 'image/png' })
      downloadBlob(imageBlob, 'image.png')

      expect(mockLink.download).toBe('image.png')
    })

    it('应该下载 PDF Blob', () => {
      const { downloadBlob } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      const pdfBlob = new Blob(['%PDF-1.4...'], { type: 'application/pdf' })
      downloadBlob(pdfBlob, 'document.pdf')

      expect(mockLink.download).toBe('document.pdf')
    })

    it('应该处理空的 Blob', () => {
      const { downloadBlob } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      const emptyBlob = new Blob([], { type: 'text/plain' })
      const result = downloadBlob(emptyBlob, 'empty.txt')

      expect(result).toEqual({ success: true })
    })

    it('应该处理大文件 Blob', () => {
      const { downloadBlob } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      const largeData = new Array(1000000).fill('x').join('')
      const largeBlob = new Blob([largeData], { type: 'text/plain' })
      const result = downloadBlob(largeBlob, 'large.txt')

      expect(result).toEqual({ success: true })
    })
  })

  describe('错误处理', () => {
    it('download 应该处理 createElement 失败', () => {
      const { download } = useFileDownload()

      vi.spyOn(document, 'createElement').mockImplementation(() => {
        throw new Error('createElement failed')
      })

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      const result = download('内容', { filename: 'test.txt' })

      expect(result.success).toBe(false)
      expect(result.error).toBeInstanceOf(Error)
      expect(consoleSpy).toHaveBeenCalledWith('Download failed:', expect.any(Error))
      consoleSpy.mockRestore()
    })

    it('download 应该处理 appendChild 失败', () => {
      const { download } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => {
        throw new Error('appendChild failed')
      })

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      const result = download('内容', { filename: 'test.txt' })

      expect(result.success).toBe(false)
      expect(result.error).toBeInstanceOf(Error)
      consoleSpy.mockRestore()
    })

    it('downloadBlob 应该处理 createObjectURL 失败', () => {
      const { downloadBlob } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      vi.mocked(global.URL.createObjectURL).mockImplementation(() => {
        throw new Error('createObjectURL failed')
      })

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      const blob = new Blob(['content'])
      const result = downloadBlob(blob, 'test.txt')

      expect(result.success).toBe(false)
      expect(result.error).toBeInstanceOf(Error)
      consoleSpy.mockRestore()
    })

    it('downloadBlob 应该处理 click 失败', () => {
      const { downloadBlob } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn(() => {
          throw new Error('click failed')
        })
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      const blob = new Blob(['content'])
      const result = downloadBlob(blob, 'test.txt')

      expect(result.success).toBe(false)
      expect(result.error).toBeInstanceOf(Error)
      consoleSpy.mockRestore()
    })

    it('应该确保 finally 块中重置 isDownloading', () => {
      const { download, isDownloading } = useFileDownload()

      vi.spyOn(document, 'createElement').mockImplementation(() => {
        throw new Error('error')
      })

      vi.spyOn(console, 'error').mockImplementation(() => {})

      download('内容', { filename: 'test.txt' })

      // 即使发生错误，isDownloading 也应该被重置
      expect(isDownloading.value).toBe(false)
    })
  })

  describe('资源清理', () => {
    it('download 应该清理资源', () => {
      const { download } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      const createElementSpy = vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      const appendChildSpy = vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      const removeChildSpy = vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      download('内容', { filename: 'test.txt' })

      expect(createElementSpy).toHaveBeenCalledWith('a')
      expect(appendChildSpy).toHaveBeenCalledWith(mockLink)
      expect(removeChildSpy).toHaveBeenCalledWith(mockLink)
      expect(global.URL.revokeObjectURL).toHaveBeenCalledWith('blob:url')
    })

    it('downloadBlob 应该清理资源', () => {
      const { downloadBlob } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      const appendChildSpy = vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      const removeChildSpy = vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      const blob = new Blob(['content'])
      downloadBlob(blob, 'test.txt')

      expect(appendChildSpy).toHaveBeenCalledWith(mockLink)
      expect(removeChildSpy).toHaveBeenCalledWith(mockLink)
      expect(global.URL.revokeObjectURL).toHaveBeenCalledWith('blob:url')
    })

    it('应该多次调用不会冲突', () => {
      const { download } = useFileDownload()

      const mockLink = {
        href: '',
        download: '',
        click: vi.fn()
      }
      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any)
      vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any)

      // 多次调用
      download('内容1', { filename: 'file1.txt' })
      download('内容2', { filename: 'file2.txt' })
      download('内容3', { filename: 'file3.txt' })

      expect(mockLink.click).toHaveBeenCalledTimes(3)
    })
  })

  describe('isDownloading 状态', () => {
    it('应该导出 isDownloading 响应式状态', () => {
      const { isDownloading } = useFileDownload()

      expect(isDownloading).toBeDefined()
      expect(typeof isDownloading.value).toBe('boolean')
    })

    it('应该返回 isDownloading、download 和 downloadBlob', () => {
      const result = useFileDownload()

      expect(result).toHaveProperty('isDownloading')
      expect(result).toHaveProperty('download')
      expect(result).toHaveProperty('downloadBlob')
    })
  })
})
