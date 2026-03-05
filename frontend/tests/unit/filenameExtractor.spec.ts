import { describe, it, expect } from 'vitest'
import { extractDefaultFilename, sanitizeFilename, generateUniqueFilename } from '@/utils/filenameExtractor'

describe('filenameExtractor', () => {
  describe('extractDefaultFilename', () => {
    it('应该提取第一行 # 标题', () => {
      const content = '# 这是标题\n\n内容'
      expect(extractDefaultFilename(content)).toBe('这是标题')
    })

    it('应该使用会话标题作为备选', () => {
      const content = '没有标题的内容'
      expect(extractDefaultFilename(content, '会话名称')).toBe('会话名称')
    })

    it('应该使用默认日期格式', () => {
      const content = '没有标题的内容'
      const result = extractDefaultFilename(content)
      expect(result).toMatch(/^AI回复-\d{4}-\d{2}-\d{2}$/)
    })
  })

  describe('sanitizeFilename', () => {
    it('应该移除非法字符', () => {
      expect(sanitizeFilename('file<>name')).toBe('filename')
    })

    it('应该限制长度为50字符', () => {
      const longName = 'a'.repeat(100)
      expect(sanitizeFilename(longName)).toHaveLength(50)
    })

    it('应该返回未命名文件当输入为空', () => {
      expect(sanitizeFilename('   ')).toBe('未命名文件')
    })
  })

  describe('generateUniqueFilename', () => {
    it('应该返回基础名称当不冲突时', () => {
      expect(generateUniqueFilename('test', [])).toBe('test')
    })

    it('应该添加数字后缀当冲突时', () => {
      expect(generateUniqueFilename('test', ['test.md'])).toBe('test(1)')
    })

    it('应该递增数字直到找到可用名称', () => {
      expect(generateUniqueFilename('test', ['test.md', 'test(1).md'])).toBe('test(2)')
    })
  })
})
