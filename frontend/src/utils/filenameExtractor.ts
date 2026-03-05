/**
 * 文件名提取工具
 */

/** 最大文件名长度 */
const MAX_FILENAME_LENGTH = 50

/** 默认文件名 */
const DEFAULT_FILENAME = '未命名文件'

/** 生成唯一文件名时的最大迭代次数 */
const MAX_ATTEMPTS = 1000

/**
 * 从内容或会话标题中提取默认文件名
 * @param content - Markdown 内容
 * @param sessionTitle - 会话标题
 * @returns 提取的文件名（不含扩展名）
 */
export function extractDefaultFilename(content: string, sessionTitle?: string): string {
  // 1. 尝试提取第一行 # 标题
  const titleMatch = content.match(/^#\s+(.+)$/m)
  if (titleMatch) {
    return sanitizeFilename(titleMatch[1].trim())
  }

  // 2. 使用会话标题
  if (sessionTitle) {
    return sanitizeFilename(sessionTitle)
  }

  // 3. 默认标题
  const date = new Date()
  const dateStr = date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).replace(/\//g, '-')
  return `AI回复-${dateStr}`
}

/**
 * 清理文件名中的非法字符
 * @param name - 原始文件名
 * @returns 清理后的文件名
 */
export function sanitizeFilename(name: string): string {
  // 移除 Windows/Linux 文件名非法字符
  let cleaned = name.replace(/[<>:"/\\|?*]/g, '').trim()

  // 限制长度
  if (cleaned.length > MAX_FILENAME_LENGTH) {
    cleaned = cleaned.substring(0, MAX_FILENAME_LENGTH)
  }

  // 避免空文件名
  if (!cleaned) {
    return DEFAULT_FILENAME
  }

  return cleaned
}

/**
 * 生成带数字后缀的文件名
 * @param baseFilename - 基础文件名
 * @param existingNames - 已存在的文件名列表
 * @returns 不冲突的文件名
 */
export function generateUniqueFilename(
  baseFilename: string,
  existingNames: readonly string[]
): string {
  const cleanBase = sanitizeFilename(baseFilename)

  // 如果基础名称不冲突，直接返回
  if (!existingNames.includes(cleanBase + '.md')) {
    return cleanBase
  }

  // 尝试添加数字后缀
  let counter = 1
  let newName
  do {
    if (counter > MAX_ATTEMPTS) {
      // 极端情况下使用时间戳确保唯一性
      return `${cleanBase}-${Date.now()}`
    }
    newName = `${cleanBase}(${counter})`
    counter++
  } while (existingNames.includes(newName + '.md'))

  return newName
}
