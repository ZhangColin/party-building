/**
 * 多模态生成API封装
 */
import apiClient from './apiClient'
import type {
  MediaGenerateRequest,
  MediaGenerateResponse,
  TaskStatusResponse
} from '../types/media'

/**
 * 发起多模态内容生成
 */
export async function generateMedia(
  toolId: string,
  request: MediaGenerateRequest
): Promise<MediaGenerateResponse> {
  const response = await apiClient.post<MediaGenerateResponse>(
    `/tools/${toolId}/generate-media`,
    request
  )
  return response.data
}

/**
 * 查询任务生成状态
 */
export async function getTaskStatus(
  taskId: string
): Promise<TaskStatusResponse> {
  const response = await apiClient.get<TaskStatusResponse>(
    `/tasks/${taskId}`
  )
  return response.data
}

/**
 * 轮询任务状态直到完成或失败
 * 
 * @param taskId 任务ID
 * @param onProgress 进度回调
 * @param maxAttempts 最大轮询次数（默认60次）
 * @param interval 轮询间隔（毫秒，默认3秒）
 * @returns 最终结果
 */
export async function pollTaskStatus(
  taskId: string,
  onProgress?: (status: TaskStatusResponse) => void,
  maxAttempts: number = 60,
  interval: number = 3000
): Promise<TaskStatusResponse> {
  console.log(`开始轮询任务状态 - taskId: ${taskId}, 最大尝试次数: ${maxAttempts}`)
  
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      console.log(`轮询第 ${attempt + 1}/${maxAttempts} 次...`)
      const result = await getTaskStatus(taskId)
      console.log(`轮询结果:`, result)
      
      // 调用进度回调
      if (onProgress) {
        onProgress(result)
      }
      
      // 如果完成或失败，返回结果
      if (result.status === 'completed' || result.status === 'failed') {
        console.log(`任务${result.status}，停止轮询`)
        return result
      }
      
      console.log(`任务仍在处理中(${result.status})，${interval/1000}秒后继续轮询...`)
      
      // 等待一段时间后继续轮询
      await sleep(interval)
      
    } catch (error) {
      console.error(`轮询任务状态失败 (attempt ${attempt + 1}/${maxAttempts}):`, error)
      
      // 如果是最后一次尝试，抛出错误
      if (attempt === maxAttempts - 1) {
        throw error
      }
      
      // 否则等待后继续
      await sleep(interval)
    }
  }
  
  // 超时
  throw new Error('任务生成超时，请稍后重试')
}

/**
 * 辅助函数：延迟
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * 下载图片
 * 由于跨域限制，直接在新标签页打开图片，用户可以右键保存
 */
export async function downloadImage(url: string, filename?: string): Promise<void> {
  try {
    // 尝试通过 fetch 下载（如果支持 CORS）
    try {
      const response = await fetch(url, { mode: 'cors' })
      if (response.ok) {
        const blob = await response.blob()
        
        // 创建下载链接
        const downloadUrl = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = downloadUrl
        link.download = filename || `image_${Date.now()}.png`
        
        // 触发下载
        document.body.appendChild(link)
        link.click()
        
        // 清理
        document.body.removeChild(link)
        window.URL.revokeObjectURL(downloadUrl)
        return
      }
    } catch (fetchError) {
      console.log('直接下载失败，尝试在新窗口打开:', fetchError)
    }
    
    // 如果 fetch 失败（跨域问题），直接在新标签页打开
    window.open(url, '_blank')
    
  } catch (error) {
    console.error('下载图片失败:', error)
    throw new Error('下载失败，请重试')
  }
}

/**
 * 批量下载图片（压缩为ZIP）
 * 暂不实现，预留接口
 */
export async function downloadImagesAsZip(
  _urls: string[], 
  _zipFilename?: string
): Promise<void> {
  // TODO: 实现批量下载
  throw new Error('批量下载功能暂未实现')
}
