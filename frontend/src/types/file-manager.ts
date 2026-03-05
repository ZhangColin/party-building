/**文件管理类型定义*/

/**
 * 文件类型
 */
export type FileType = 'word' | 'pdf' | 'excel' | 'markdown' | 'text' | 'image'

/**
 * 目录
 */
export interface Category {
  id: string
  name: string
  parent_id: string | null
  order: number
  created_at: string
  updated_at: string
  children?: Category[]
}

/**
 * 文档
 */
export interface Document {
  id: string
  category_id: string
  filename: string
  original_filename: string
  file_type: FileType
  file_size: number | null
  content?: string
  created_at: string
  updated_at: string
}

// ==================== 请求类型 ====================

/**
 * 创建目录请求
 */
export interface CategoryCreateRequest {
  name: string
  parent_id?: string | null
}

/**
 * 更新目录请求
 */
export interface CategoryUpdateRequest {
  name?: string
  parent_id?: string | null
}

/**
 * 创建文档请求
 */
export interface DocumentCreateRequest {
  category_id: string
  filename: string
  content: string
}

/**
 * 上传文件请求
 */
export interface DocumentUploadRequest {
  file: File
  category_id: string
}

/**
 * 更新文档内容请求
 */
export interface DocumentUpdateRequest {
  content: string
}

// ==================== 响应类型 ====================

/**
 * 目录响应
 */
export interface CategoryResponse extends Category {}

/**
 * 目录树响应
 */
export interface CategoryTreeResponse extends Category {}

/**
 * 文档上传响应
 */
export interface DocumentUploadResponse {
  id: string
  category_id: string
  filename: string
  original_filename: string
  file_type: FileType
}

/**
 * 文档响应
 */
export interface DocumentResponse extends Document {}

// ==================== UI 类型 ====================

/**
 * 文件管理视图模式
 */
export type FileViewMode = 'grid' | 'list'

/**
 * 文件管理状态
 */
export interface FileManagerState {
  currentCategory: Category | null
  categories: Category[]
  documents: Document[]
  selectedDocuments: string[]
  viewMode: FileViewMode
  loading: boolean
  searchQuery: string
}

/**
 * 文件上传进度
 */
export interface UploadProgress {
  fileName: string
  progress: number
  status: 'pending' | 'uploading' | 'success' | 'error'
  error?: string
}

/**
 * 文件操作菜单项
 */
export interface FileActionMenuItem {
  label: string
  icon: string
  action: () => void
  danger?: boolean
  disabled?: boolean
}
