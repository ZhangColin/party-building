/**
 * 剪贴板 composable
 * 提供剪贴板复制功能，包含成功提示
 */
import { ref } from 'vue'

export function useClipboard() {
  const copiedText = ref<string>('')

  /**
   * 检查剪贴板 API 是否可用
   */
  function isClipboardAvailable(): boolean {
    return (
      typeof navigator !== 'undefined' &&
      'clipboard' in navigator &&
      'writeText' in navigator.clipboard
    )
  }

  /**
   * 复制文本到剪贴板
   * @param text 要复制的文本
   * @returns 复制是否成功
   */
  async function copy(text: string): Promise<boolean> {
    // 浏览器兼容性检查
    if (!isClipboardAvailable()) {
      console.error('剪贴板 API 在当前浏览器中不可用')
      return false
    }

    try {
      await navigator.clipboard.writeText(text)
      copiedText.value = text

      // 使用全局 Toast
      const showToast = (window as any).__showToast
      if (showToast) {
        showToast('已复制到剪贴板')
      }

      return true
    } catch (error) {
      console.error('复制失败:', error)
      return false
    }
  }

  return {
    copy,
    copiedText
  }
}
