/** 会话存储工具 - 管理 localStorage 中的会话数据 */
import type { Message } from '../types'

const STORAGE_PREFIX = 'agent_session_'

/**
 * 获取存储 key
 */
function getStorageKey(agentId: string): string {
  return `${STORAGE_PREFIX}${agentId}`
}

/**
 * 会话存储数据结构
 */
export interface SessionStorageData {
  sessionId: string
  agentId: string
  messages: Message[]
  createdAt: string
  updatedAt: string
}

/**
 * 保存会话到 localStorage
 */
export function saveSession(
  agentId: string,
  sessionId: string,
  messages: Message[]
): void {
  try {
    const data: SessionStorageData = {
      sessionId,
      agentId,
      messages,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    const key = getStorageKey(agentId)
    localStorage.setItem(key, JSON.stringify(data))
  } catch (error) {
    console.error('保存会话失败:', error)
    // 如果存储失败（如存储空间已满），不抛出错误，静默处理
  }
}

/**
 * 更新会话消息（追加新消息）
 */
export function updateSession(agentId: string, messages: Message[]): void {
  try {
    const key = getStorageKey(agentId)
    const existingData = localStorage.getItem(key)
    
    if (existingData) {
      const data: SessionStorageData = JSON.parse(existingData)
      data.messages = messages
      data.updatedAt = new Date().toISOString()
      localStorage.setItem(key, JSON.stringify(data))
    } else {
      // 如果不存在，创建新会话（这种情况不应该发生，但为了健壮性处理）
    }
  } catch (error) {
    console.error('更新会话失败:', error)
  }
}

/**
 * 从 localStorage 恢复会话
 */
export function restoreSession(agentId: string): SessionStorageData | null {
  try {
    const key = getStorageKey(agentId)
    const data = localStorage.getItem(key)
    
    if (!data) {
      return null
    }
    
    const sessionData: SessionStorageData = JSON.parse(data)
    
    // 验证数据完整性
    if (
      !sessionData.sessionId ||
      !sessionData.agentId ||
      !Array.isArray(sessionData.messages)
    ) {
      localStorage.removeItem(key)
      return null
    }
    
    return sessionData
  } catch (error) {
    console.error('恢复会话失败:', error)
    // 如果解析失败，清除损坏的数据
    const key = getStorageKey(agentId)
    localStorage.removeItem(key)
    return null
  }
}

/**
 * 删除会话
 */
export function deleteSession(agentId: string): void {
  try {
    const key = getStorageKey(agentId)
    localStorage.removeItem(key)
  } catch (error) {
    console.error('删除会话失败:', error)
  }
}

/**
 * 清除所有会话
 */
export function clearAllSessions(): void {
  try {
    const keys = Object.keys(localStorage)
    keys.forEach((key) => {
      if (key.startsWith(STORAGE_PREFIX)) {
        localStorage.removeItem(key)
      }
    })
  } catch (error) {
    console.error('清除所有会话失败:', error)
  }
}

