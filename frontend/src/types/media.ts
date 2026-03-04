/**
 * 多模态相关类型定义
 */

/**
 * 内容类型
 */
export type ContentType = 'image' | 'audio' | 'video'

/**
 * 生成状态
 */
export type GenerationStatus = 'pending' | 'processing' | 'completed' | 'failed'

/**
 * 图片尺寸选项
 */
export type ImageSize = '512x512' | '1024x1024' | '1024x1792' | '1792x1024'

/**
 * 生成风格选项
 */
export type ImageStyle = 'auto' | 'realistic' | 'cartoon' | 'oil_painting' | 'sketch'

/**
 * 多模态内容结构
 */
export interface MediaContent {
  content_type: ContentType
  media_urls: string[]
  metadata?: {
    size?: string
    count?: number
    style?: string
    width?: number
    height?: number
    duration?: number
    format?: string
    cost?: {
      tokens: number
      amount: number
      currency: string
    }
  }
}

/**
 * 多模态消息
 */
export interface MediaMessage {
  message_id?: string
  session_id?: string
  role: 'user' | 'assistant'
  content: string  // 用户提示词或空字符串
  media_content?: string  // JSON字符串
  created_at?: string
  
  // 前端状态字段（不存数据库）
  generation_status?: GenerationStatus
  task_id?: string
  progress?: number
  error_message?: string
}

/**
 * 媒体生成请求参数
 */
export interface MediaGenerateParams {
  size: ImageSize
  count: 1 | 2 | 3 | 4
  style: ImageStyle
}

/**
 * 媒体生成请求
 */
export interface MediaGenerateRequest {
  message: string
  session_id?: string
  size?: string
  count?: number
  style?: string
}

/**
 * 媒体生成响应
 */
export interface MediaGenerateResponse {
  session_id: string
  message_id: string
  task_id: string
  status: 'pending' | 'processing' | 'completed'  // 同步模式可以直接返回 completed
  
  // 同步模式下直接返回的字段
  media_urls?: string[]
  content_type?: ContentType
}

/**
 * 任务状态响应
 */
export interface TaskStatusResponse {
  task_id: string
  status: GenerationStatus
  progress?: number
  
  // 完成时的字段
  content_type?: ContentType
  media_urls?: string[]
  metadata?: Record<string, any>
  
  // 失败时的字段
  error_message?: string
}

/**
 * 解析后的媒体内容
 */
export interface ParsedMediaContent {
  contentType: ContentType
  mediaUrls: string[]
  metadata: Record<string, any>
}

/**
 * 解析media_content JSON字符串
 */
export function parseMediaContent(jsonString: string | undefined): ParsedMediaContent | null {
  if (!jsonString) {
    return null
  }
  
  try {
    const data: MediaContent = JSON.parse(jsonString)
    return {
      contentType: data.content_type,
      mediaUrls: data.media_urls,
      metadata: data.metadata || {}
    }
  } catch (error) {
    console.error('解析多模态内容失败:', error)
    return null
  }
}

/**
 * 生成参数默认值
 */
export const DEFAULT_GENERATE_PARAMS: MediaGenerateParams = {
  size: '1024x1024',
  count: 1,
  style: 'auto'
}

/**
 * 尺寸选项
 */
export const IMAGE_SIZE_OPTIONS: { label: string; value: ImageSize }[] = [
  { label: '正方形 (1024x1024)', value: '1024x1024' },
  { label: '小尺寸 (512x512)', value: '512x512' },
  { label: '竖版 (1024x1792)', value: '1024x1792' },
  { label: '横版 (1792x1024)', value: '1792x1024' }
]

/**
 * 数量选项
 */
export const IMAGE_COUNT_OPTIONS: { label: string; value: 1 | 2 | 3 | 4 }[] = [
  { label: '1张', value: 1 },
  { label: '2张', value: 2 },
  { label: '3张', value: 3 },
  { label: '4张', value: 4 }
]

/**
 * 风格选项
 */
export const IMAGE_STYLE_OPTIONS: { label: string; value: ImageStyle }[] = [
  { label: '自动', value: 'auto' },
  { label: '写实', value: 'realistic' },
  { label: '卡通', value: 'cartoon' },
  { label: '油画', value: 'oil_painting' },
  { label: '素描', value: 'sketch' }
]
