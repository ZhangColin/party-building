/**
 * 临时文件上传 API
 */
import axios from 'axios'
import type { TempFileUploadResponse } from '@/types'

const API_BASE = '/api/v1/temp_files'

/**
 * 上传临时文件
 * @param file 要上传的文件
 * @param onProgress 上传进度回调（0-100）
 * @returns 上传响应，包含临时文件ID等信息
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
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          onProgress(progress)
        }
      }
    }
  )

  return response.data
}
