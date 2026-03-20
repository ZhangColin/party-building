/**党建活动 API 服务*/
import apiClient from './apiClient'
import type {
  CategoryCreateRequest,
  CategoryUpdateRequest,
  CategoryResponse,
  CategoryTreeResponse,
  DocumentCreateRequest,
  DocumentUpdateRequest,
  DocumentResponse,
  DocumentUploadResponse
} from '@/types/file-manager'

/**
 * 党建活动 API 基础路径
 */
const BASE_PATH = '/party-activities'

// ==================== 目录管理 ====================

/**
 * 创建目录
 */
export async function createCategory(data: CategoryCreateRequest): Promise<CategoryResponse> {
  const response = await apiClient.post<CategoryResponse>(`${BASE_PATH}/categories`, data)
  return response.data
}

/**
 * 获取目录树
 */
export async function getCategoryTree(): Promise<CategoryTreeResponse[]> {
  const response = await apiClient.get<CategoryTreeResponse[]>(`${BASE_PATH}/categories/tree`)
  return response.data
}

/**
 * 更新目录
 */
export async function updateCategory(
  categoryId: string,
  data: CategoryUpdateRequest
): Promise<CategoryResponse> {
  const response = await apiClient.put<CategoryResponse>(
    `${BASE_PATH}/categories/${categoryId}`,
    data
  )
  return response.data
}

/**
 * 删除目录
 */
export async function deleteCategory(categoryId: string): Promise<{ message: string }> {
  const response = await apiClient.delete<{ message: string }>(
    `${BASE_PATH}/categories/${categoryId}`
  )
  return response.data
}

// ==================== 文件管理 ====================

/**
 * 创建文档（新建 Markdown 文件）
 */
export async function createDocument(data: DocumentCreateRequest): Promise<DocumentResponse> {
  const response = await apiClient.post<DocumentResponse>(`${BASE_PATH}/documents`, data)
  return response.data
}

/**
 * 上传文件
 */
export async function uploadFile(
  file: File,
  categoryId: string,
  onProgress?: (progress: number) => void
): Promise<DocumentUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('category_id', categoryId)

  const response = await apiClient.post<DocumentUploadResponse>(
    `${BASE_PATH}/documents/upload`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
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
 * 获取文件列表
 */
export async function getDocuments(categoryId?: string): Promise<DocumentResponse[]> {
  const params = categoryId ? { category_id: categoryId } : {}
  const response = await apiClient.get<DocumentResponse[]>(`${BASE_PATH}/documents`, { params })
  return response.data
}

/**
 * 获取文件详情
 */
export async function getDocument(documentId: string): Promise<DocumentResponse> {
  const response = await apiClient.get<DocumentResponse>(`${BASE_PATH}/documents/${documentId}`)
  return response.data
}

/**
 * 更新文件内容
 */
export async function updateDocument(
  documentId: string,
  data: DocumentUpdateRequest
): Promise<DocumentResponse> {
  const response = await apiClient.put<DocumentResponse>(
    `${BASE_PATH}/documents/${documentId}`,
    data
  )
  return response.data
}

/**
 * 删除文件
 */
export async function deleteDocument(documentId: string): Promise<{ message: string }> {
  const response = await apiClient.delete<{ message: string }>(
    `${BASE_PATH}/documents/${documentId}`
  )
  return response.data
}

/**
 * 下载文件
 */
export async function downloadDocument(documentId: string): Promise<Blob> {
  const response = await apiClient.get(`${BASE_PATH}/documents/${documentId}/download`, {
    responseType: 'blob'
  })
  return response.data
}

/**
 * 获取文件下载 URL（用于 a 标签直接下载）
 */
export function getDownloadUrl(documentId: string): string {
  return `${BASE_PATH}/documents/${documentId}/download`
}

/**
 * 获取原文件 URL（用于预览或下载）
 */
export function getOriginalFileUrl(documentId: string): string {
  return `${BASE_PATH}/documents/${documentId}/original`
}
