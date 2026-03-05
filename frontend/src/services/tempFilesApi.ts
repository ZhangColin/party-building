/** 临时文件上传服务 */
import axios from 'axios'
import type { TempFileUploadResponse } from '@/types'

const API_BASE = '/api/v1/temp_files'

/**
 * 上传临时文件
 * @param file 要上传的文件
 * @param onProgress 上传进度回调函数（0-100）
 * @returns 上传响应结果
 */
export async function uploadTempFile(
  file: File,
  onProgress?: (progress: number) => void
): Promise<TempFileUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await axios.post<TempFileUploadResponse>(
    `${API_BASE}/upload`,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      }
    }
  )

  return response.data
}

/**
 * 删除临时文件
 * @param tempId 临时文件ID
 */
export async function deleteTempFile(tempId: string): Promise<void> {
  await axios.delete(`${API_BASE}/${tempId}`)
}
