import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useClipboard } from '@/composables/useClipboard'

describe('useClipboard', () => {
  beforeEach(() => {
    vi.stubGlobal('navigator', {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined)
      }
    })
  })

  it('should copy text to clipboard', async () => {
    const { copy, copiedText } = useClipboard()

    await copy('test message')

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('test message')
    expect(copiedText.value).toBe('test message')
  })

  it('should call global toast when copy succeeds', async () => {
    const showToastSpy = vi.fn()
    vi.stubGlobal('window', {
      __showToast: showToastSpy
    })

    const { copy } = useClipboard()

    await copy('test')

    expect(showToastSpy).toHaveBeenCalledWith('已复制到剪贴板')
  })

  describe('error scenarios', () => {
    it('should handle clipboard API errors gracefully', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const mockError = new Error('Permission denied')
      vi.mocked(navigator.clipboard.writeText).mockRejectedValueOnce(mockError)

      const { copy, copiedText } = useClipboard()

      const result = await copy('test message')

      expect(result).toBe(false)
      expect(copiedText.value).toBe('')
      expect(consoleErrorSpy).toHaveBeenCalledWith('复制失败:', mockError)

      consoleErrorSpy.mockRestore()
    })

    it('should return false when clipboard API is not available', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      // 模拟不支持 clipboard API 的浏览器环境
      vi.stubGlobal('navigator', {})

      const { copy, copiedText } = useClipboard()

      const result = await copy('test message')

      expect(result).toBe(false)
      expect(copiedText.value).toBe('')
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '剪贴板 API 在当前浏览器中不可用'
      )

      consoleErrorSpy.mockRestore()

      // 恢复 navigator 以免影响其他测试
      vi.stubGlobal('navigator', {
        clipboard: {
          writeText: vi.fn().mockResolvedValue(undefined)
        }
      })
    })

    it('should return false when clipboard.writeText is not available', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      // 模拟 clipboard 对象存在但 writeText 方法不存在
      vi.stubGlobal('navigator', {
        clipboard: {}
      })

      const { copy, copiedText } = useClipboard()

      const result = await copy('test message')

      expect(result).toBe(false)
      expect(copiedText.value).toBe('')
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '剪贴板 API 在当前浏览器中不可用'
      )

      consoleErrorSpy.mockRestore()

      // 恢复 navigator 以免影响其他测试
      vi.stubGlobal('navigator', {
        clipboard: {
          writeText: vi.fn().mockResolvedValue(undefined)
        }
      })
    })
  })

  describe('integration', () => {
    it('should work when global toast is not available', async () => {
      // 模拟没有全局 toast 的情况
      vi.stubGlobal('window', {})

      const { copy } = useClipboard()

      // 应该不会抛出错误
      const result = await copy('test')

      expect(result).toBe(true)
    })
  })
})
