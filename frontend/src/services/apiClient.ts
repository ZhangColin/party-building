/** API 客户端服务 - 封装后端接口调用 */
import axios, { type AxiosInstance, type AxiosError } from 'axios'
import type {
  AgentListResponse,
  ToolListResponse,
  SessionInitResponse,
  ChatRequest,
  ChatResponse,
  ConversationListResponse,
  SessionDetailResponse,
  UpdateSessionRequest,
  UpdateSessionResponse,
  LoginRequest,
  LoginResponse,
  UserListResponse,
  CreateUserRequest,
  CreateUserResponse,
  UpdateUserRequest,
  UpdateUserResponse,
  ResetPasswordRequest,
  ResetPasswordResponse,
  UserInfo,
  CommonToolCategoryResponse,
  CommonToolDetail,
  WorkCategoryResponse,
  WorkDetail,
  AdminCommonToolListResponse,
  // AdminCommonToolListItem, // 未使用，但保留用于未来功能
  CreateBuiltInToolRequest,
  UpdateToolRequest,
  ToolMutationResponse,
  MoveToolResponse,
  ToggleVisibilityResponse,
  AdminToolCategoryListResponse,
  // AdminToolCategoryListItem, // 未使用，但保留用于未来功能
  CreateToolCategoryRequest,
  UpdateToolCategoryRequest,
  CategoryMutationResponse,
  MoveCategoryResponse,
  AdminWorkListResponse,
  // AdminWorkListItem, // 未使用，但保留用于未来功能
  UpdateWorkRequest,
  WorkMutationResponse,
  MoveWorkResponse,
  ToggleWorkVisibilityResponse,
  AdminWorkCategoryListResponse,
  // AdminWorkCategoryListItem, // 未使用，但保留用于未来功能
  CreateWorkCategoryRequest,
  UpdateWorkCategoryRequest,
  WorkCategoryMutationResponse,
  MoveWorkCategoryResponse,
  CourseCategoryTreeResponse,
  CourseDocumentListResponse,
  CourseDocumentDetail,
  AdminCourseCategoryListResponse,
  CreateCourseCategoryRequest,
  UpdateCourseCategoryRequest,
  AdminCourseDocumentListResponse,
  UpdateCourseDocumentRequest,
} from '../types'
import type { NavigationResponse } from '../types/navigation'

/**
 * API 错误响应格式
 */
export interface ApiErrorResponse {
  error_code: string
  error_message: string
  details?: Record<string, unknown>
}

/**
 * 创建 axios 实例
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 180000, // 180 秒超时（3 分钟），为长文本续写预留足够时间
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * 请求拦截器
 */
apiClient.interceptors.request.use(
  (config) => {
    // 公开接口（不需要token）
    const publicEndpoints = ['/auth/login', '/auth/register']
    const isPublicEndpoint = publicEndpoints.some(endpoint => config.url?.includes(endpoint))
    
    // 非公开接口才添加认证token
    if (!isPublicEndpoint) {
      const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器 - 统一错误处理
 */
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error: AxiosError<ApiErrorResponse | { detail?: string }>) => {
    // 统一错误处理
    if (error.response) {
      const status = error.response.status
      const errorData = error.response.data
      
      // 401 未授权：需要区分登录接口和其他接口
      if (status === 401) {
        // 检查是否是登录接口
        const isLoginRequest = error.config?.url?.includes('/auth/login')
        
        if (isLoginRequest) {
          // 登录接口的 401 错误：用户名或密码错误，显示后端返回的具体错误
          const errorMessage = 
            (errorData as { detail?: string })?.detail ||
            (errorData as ApiErrorResponse)?.error_message ||
            '账号或密码错误'
          return Promise.reject(new Error(errorMessage))
        } else {
          // 其他接口的 401 错误：Token过期或无效，清除本地认证信息并跳转到登录页
          localStorage.removeItem('auth_token')
          localStorage.removeItem('auth_user')
          sessionStorage.removeItem('auth_token')
          sessionStorage.removeItem('auth_user')
          
          // 如果不在登录页，跳转到登录页
          if (window.location.pathname !== '/login') {
            window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname)}`
          }
          
          return Promise.reject(new Error('登录已过期，请重新登录'))
        }
      }
      
      // 其他错误
      // FastAPI默认错误格式是 { detail: string }，也支持自定义格式 { error_message: string }
      const errorMessage = 
        (errorData as { detail?: string })?.detail ||
        (errorData as ApiErrorResponse)?.error_message ||
        error.message ||
        '请求失败'
      return Promise.reject(new Error(errorMessage))
    } else if (error.request) {
      // 请求已发出但没有收到响应
      return Promise.reject(new Error('网络错误，请检查网络连接'))
    } else {
      // 请求配置出错
      return Promise.reject(new Error('请求配置错误'))
    }
  }
)

/**
 * API 服务类
 */
export class ApiService {
  /**
   * 获取 Agent 列表（已废弃，请使用 getTools）
   */
  static async getAgents(): Promise<AgentListResponse> {
    const response = await apiClient.get<AgentListResponse>('/agents')
    return response.data
  }

  /**
   * 获取导航模块列表
   */
  static async getNavigationModules(): Promise<NavigationResponse> {
    const response = await apiClient.get<NavigationResponse>('/navigation')
    return response.data
  }

  /**
   * 获取工具列表（按分类组织）
   */
  static async getTools(): Promise<ToolListResponse> {
    const response = await apiClient.get<ToolListResponse>('/tools')
    return response.data
  }

  /**
   * 获取指定工具集的工具列表（按分类组织）
   * @param toolsetId 工具集ID
   */
  static async getToolsetTools(toolsetId: string): Promise<ToolListResponse> {
    const response = await apiClient.get<ToolListResponse>(`/toolsets/${toolsetId}/tools`)
    return response.data
  }

  /**
   * 创建会话
   * @param agentId Agent 唯一标识符
   */
  static async createSession(agentId: string): Promise<SessionInitResponse> {
    const response = await apiClient.post<SessionInitResponse>(
      `/agents/${agentId}/sessions`
    )
    return response.data
  }

  /**
   * 发送消息（新接口，支持延迟创建会话）
   * @param toolId 工具唯一标识符
   * @param request 对话请求（包含 session_id 可选）
   */
  static async chat(
    toolId: string,
    request: ChatRequest
  ): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>(
      `/tools/${toolId}/chat`,
      request,
      {
        timeout: 300000, // 聊天接口单独设置 300 秒超时（5 分钟），支持长文本续写
      }
    )
    return response.data
  }

  /**
   * 发送消息（流式接口，支持延迟创建会话）
   * @param toolId 工具唯一标识符
   * @param request 对话请求（包含 session_id 可选）
   * @param onChunk 接收数据块的回调函数
   */
  static async chatStream(
    toolId: string,
    request: ChatRequest,
    onChunk: (data: { type: string; session_id?: string; content?: string; artifacts?: any[]; error?: string }) => void
  ): Promise<void> {
    const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
    if (!token) {
      throw new Error('未登录')
    }

    const response = await fetch(`/api/v1/tools/${toolId}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(request)
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: '请求失败' }))
      throw new Error(error.detail || '请求失败')
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('无法读取响应流')
    }

    const decoder = new TextDecoder()
    let buffer = ''

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // 保留最后一个不完整的行

        for (const line of lines) {
          const trimmedLine = line.trim()
          if (trimmedLine.startsWith('data: ')) {
            const jsonStr = trimmedLine.slice(6).trim()

            // 处理 [DONE] 标记
            if (jsonStr === '[DONE]') {
              onChunk({ type: 'done' })
              continue
            }

            if (jsonStr) {
              try {
                const data = JSON.parse(jsonStr)
                onChunk({ type: 'content', ...data })
              } catch (e) {
                console.error('解析 SSE 数据失败:', e, trimmedLine)
              }
            }
          } else if (trimmedLine === '') {
            // 空行，跳过
            continue
          }
        }
      }

      // 处理最后一行
      const trimmedBuffer = buffer.trim()
      if (trimmedBuffer.startsWith('data: ')) {
        const jsonStr = trimmedBuffer.slice(6).trim()

        // 处理 [DONE] 标记
        if (jsonStr === '[DONE]') {
          onChunk({ type: 'done' })
        } else if (jsonStr) {
          try {
            const data = JSON.parse(jsonStr)
            onChunk({ type: 'content', ...data })
          } catch (e) {
            console.error('解析 SSE 数据失败:', e, trimmedBuffer)
          }
        }
      }
    } finally {
      reader.releaseLock()
    }
  }

  /**
   * 获取历史对话列表
   * @param toolId 工具唯一标识符
   */
  static async getConversations(toolId: string): Promise<ConversationListResponse> {
    const response = await apiClient.get<ConversationListResponse>(
      `/tools/${toolId}/conversations`
    )
    return response.data
  }

  /**
   * 获取会话详情
   * @param sessionId 会话 UUID
   */
  static async getSessionDetail(sessionId: string): Promise<SessionDetailResponse> {
    const response = await apiClient.get<SessionDetailResponse>(
      `/sessions/${sessionId}`
    )
    return response.data
  }

  /**
   * 更新会话标题
   * @param sessionId 会话 UUID
   * @param request 更新请求
   */
  static async updateSessionTitle(
    sessionId: string,
    request: UpdateSessionRequest
  ): Promise<UpdateSessionResponse> {
    const response = await apiClient.patch<UpdateSessionResponse>(
      `/sessions/${sessionId}`,
      request
    )
    return response.data
  }

  /**
   * 删除会话
   * @param sessionId 会话 UUID
   */
  static async deleteSession(sessionId: string): Promise<void> {
    await apiClient.delete(`/sessions/${sessionId}`)
  }

  /**
   * 用户登录
   * @param request 登录请求
   */
  static async login(request: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login', request)
    return response.data
  }

  /**
   * 获取当前用户信息
   */
  static async getCurrentUser(): Promise<{ user: UserInfo }> {
    const response = await apiClient.get<{ user: UserInfo }>('/auth/me')
    return response.data
  }

  /**
   * 获取用户列表
   * @param page 页码（可选，默认1）
   * @param pageSize 每页数量（可选，默认20）
   * @param isAdmin 筛选管理员（可选，true: 仅管理员，false: 仅普通用户，undefined: 全部）
   */
  static async getUserList(
    page: number = 1,
    pageSize: number = 20,
    isAdmin?: boolean
  ): Promise<UserListResponse> {
    const params: Record<string, any> = {
      page,
      page_size: pageSize,
    }
    if (isAdmin !== undefined) {
      params.is_admin = isAdmin
    }
    const response = await apiClient.get<UserListResponse>('/admin/users', { params })
    return response.data
  }

  /**
   * 创建用户
   * @param request 创建用户请求
   */
  static async createUser(request: CreateUserRequest): Promise<CreateUserResponse> {
    const response = await apiClient.post<CreateUserResponse>('/admin/users', request)
    return response.data
  }

  /**
   * 更新用户信息
   * @param userId 用户ID
   * @param request 更新用户请求
   */
  static async updateUser(userId: string, request: UpdateUserRequest): Promise<UpdateUserResponse> {
    const response = await apiClient.put<UpdateUserResponse>(`/admin/users/${userId}`, request)
    return response.data
  }

  /**
   * 删除用户
   * @param userId 用户ID
   */
  static async deleteUser(userId: string): Promise<void> {
    await apiClient.delete(`/admin/users/${userId}`)
  }

  /**
   * 重置用户密码
   * @param userId 用户ID
   * @param request 重置密码请求
   */
  static async resetUserPassword(
    userId: string,
    request: ResetPasswordRequest
  ): Promise<ResetPasswordResponse> {
    const response = await apiClient.post<ResetPasswordResponse>(
      `/admin/users/${userId}/reset-password`,
      request
    )
    return response.data
  }

  // ==================== 常用工具模块 ====================

  /**
   * 获取常用工具分类列表（包含每个分类下的工具列表）
   */
  static async getCommonToolCategories(): Promise<CommonToolCategoryResponse> {
    const response = await apiClient.get<CommonToolCategoryResponse>('/common-tools/categories')
    return response.data
  }

  /**
   * 获取常用工具详情
   * @param toolId 工具ID
   */
  static async getCommonToolDetail(toolId: string): Promise<CommonToolDetail> {
    const response = await apiClient.get<CommonToolDetail>(`/common-tools/tools/${toolId}`)
    return response.data
  }

  // ==================== 作品展示模块 ====================

  /**
   * 获取作品分类列表（包含每个分类下的作品列表）
   */
  static async getWorkCategories(): Promise<WorkCategoryResponse> {
    const response = await apiClient.get<WorkCategoryResponse>('/works/categories')
    return response.data
  }

  /**
   * 获取作品详情
   * @param workId 作品ID
   */
  static async getWorkDetail(workId: string): Promise<WorkDetail> {
    const response = await apiClient.get<WorkDetail>(`/works/${workId}`)
    return response.data
  }

  // ==================== 后台管理 - 工具管理模块 ====================

  /**
   * 获取工具列表（管理后台）
   * @param page 页码
   * @param pageSize 每页数量
   * @param categoryId 按分类ID筛选
   * @param type 按类型筛选（'built_in' | 'html'）
   * @param visible 按可见性筛选
   */
  static async getAdminTools(
    page: number = 1,
    pageSize: number = 20,
    categoryId?: string,
    type?: string,
    visible?: boolean
  ): Promise<AdminCommonToolListResponse> {
    const params: Record<string, any> = { page, page_size: pageSize }
    if (categoryId) params.category_id = categoryId
    if (type) params.type = type
    if (visible !== undefined) params.visible = visible

    const response = await apiClient.get<AdminCommonToolListResponse>('/admin/common-tools', {
      params,
    })
    return response.data
  }

  /**
   * 创建内置工具
   * @param request 创建内置工具请求
   */
  static async createBuiltInTool(request: CreateBuiltInToolRequest): Promise<ToolMutationResponse> {
    const response = await apiClient.post<ToolMutationResponse>('/admin/common-tools/built-in', request)
    return response.data
  }

  /**
   * 上传HTML工具
   * @param name 工具名称
   * @param description 工具描述
   * @param categoryId 所属分类ID
   * @param htmlFile HTML文件
   * @param icon 图标标识
   * @param order 排序顺序
   * @param visible 是否可见
   */
  static async createHtmlTool(
    name: string,
    description: string,
    categoryId: string,
    htmlFile: File,
    icon?: string,
    order: number = 0,
    visible: boolean = true
  ): Promise<ToolMutationResponse> {
    const formData = new FormData()
    formData.append('name', name)
    formData.append('description', description)
    formData.append('category_id', categoryId)
    formData.append('html_file', htmlFile)
    if (icon) formData.append('icon', icon)
    formData.append('order', order.toString())
    formData.append('visible', visible.toString())

    const response = await apiClient.post<ToolMutationResponse>('/admin/common-tools/html', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }

  /**
   * 更新工具信息
   * @param toolId 工具ID
   * @param request 更新工具请求
   */
  static async updateTool(toolId: string, request: UpdateToolRequest): Promise<ToolMutationResponse> {
    const response = await apiClient.put<ToolMutationResponse>(`/admin/common-tools/${toolId}`, request)
    return response.data
  }

  /**
   * 删除工具
   * @param toolId 工具ID
   */
  static async deleteTool(toolId: string): Promise<void> {
    await apiClient.delete(`/admin/common-tools/${toolId}`)
  }

  /**
   * 上移工具
   * @param toolId 工具ID
   */
  static async moveToolUp(toolId: string): Promise<MoveToolResponse> {
    const response = await apiClient.post<MoveToolResponse>(`/admin/common-tools/${toolId}/move-up`)
    return response.data
  }

  /**
   * 下移工具
   * @param toolId 工具ID
   */
  static async moveToolDown(toolId: string): Promise<MoveToolResponse> {
    const response = await apiClient.post<MoveToolResponse>(`/admin/common-tools/${toolId}/move-down`)
    return response.data
  }

  /**
   * 切换工具可见性
   * @param toolId 工具ID
   */
  static async toggleToolVisibility(toolId: string): Promise<ToggleVisibilityResponse> {
    const response = await apiClient.post<ToggleVisibilityResponse>(`/admin/common-tools/${toolId}/toggle-visibility`)
    return response.data
  }

  // ==================== 后台管理 - 工具分类管理模块 ====================

  /**
   * 获取工具分类列表（管理后台）
   */
  static async getAdminToolCategories(): Promise<AdminToolCategoryListResponse> {
    const response = await apiClient.get<AdminToolCategoryListResponse>('/admin/tool-categories')
    return response.data
  }

  /**
   * 创建工具分类
   * @param request 创建分类请求
   */
  static async createToolCategory(request: CreateToolCategoryRequest): Promise<CategoryMutationResponse> {
    const response = await apiClient.post<CategoryMutationResponse>('/admin/tool-categories', request)
    return response.data
  }

  /**
   * 更新工具分类
   * @param categoryId 分类ID
   * @param request 更新分类请求
   */
  static async updateToolCategory(
    categoryId: string,
    request: UpdateToolCategoryRequest
  ): Promise<CategoryMutationResponse> {
    const response = await apiClient.put<CategoryMutationResponse>(`/admin/tool-categories/${categoryId}`, request)
    return response.data
  }

  /**
   * 删除工具分类
   * @param categoryId 分类ID
   */
  static async deleteToolCategory(categoryId: string): Promise<void> {
    await apiClient.delete(`/admin/tool-categories/${categoryId}`)
  }

  /**
   * 上移分类
   * @param categoryId 分类ID
   */
  static async moveCategoryUp(categoryId: string): Promise<MoveCategoryResponse> {
    const response = await apiClient.post<MoveCategoryResponse>(`/admin/tool-categories/${categoryId}/move-up`)
    return response.data
  }

  /**
   * 下移分类
   * @param categoryId 分类ID
   */
  static async moveCategoryDown(categoryId: string): Promise<MoveCategoryResponse> {
    const response = await apiClient.post<MoveCategoryResponse>(`/admin/tool-categories/${categoryId}/move-down`)
    return response.data
  }

  // ==================== 后台管理 - 作品管理模块 ====================

  /**
   * 获取作品列表（管理后台）
   */
  static async getAdminWorks(
    page: number = 1,
    pageSize: number = 20,
    categoryId?: string,
    visible?: boolean
  ): Promise<AdminWorkListResponse> {
    const params: Record<string, any> = { page, page_size: pageSize }
    if (categoryId) params.category_id = categoryId
    if (visible !== undefined) params.visible = visible

    const response = await apiClient.get<AdminWorkListResponse>('/admin/works', { params })
    return response.data
  }

  /**
   * 上传作品
   */
  static async createWork(
    name: string,
    description: string,
    categoryId: string,
    htmlFile: File,
    icon?: string,
    order: number = 0,
    visible: boolean = true
  ): Promise<WorkMutationResponse> {
    const formData = new FormData()
    formData.append('name', name)
    formData.append('description', description)
    formData.append('category_id', categoryId)
    formData.append('html_file', htmlFile)
    if (icon) formData.append('icon', icon)
    formData.append('order', order.toString())
    formData.append('visible', visible.toString())

    const response = await apiClient.post<WorkMutationResponse>('/admin/works', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  }

  /**
   * 更新作品信息
   */
  static async updateWork(workId: string, request: UpdateWorkRequest): Promise<WorkMutationResponse> {
    const response = await apiClient.put<WorkMutationResponse>(`/admin/works/${workId}`, request)
    return response.data
  }

  /**
   * 删除作品
   */
  static async deleteWork(workId: string): Promise<void> {
    await apiClient.delete(`/admin/works/${workId}`)
  }

  /**
   * 上移作品
   */
  static async moveWorkUp(workId: string): Promise<MoveWorkResponse> {
    const response = await apiClient.post<MoveWorkResponse>(`/admin/works/${workId}/move-up`)
    return response.data
  }

  /**
   * 下移作品
   */
  static async moveWorkDown(workId: string): Promise<MoveWorkResponse> {
    const response = await apiClient.post<MoveWorkResponse>(`/admin/works/${workId}/move-down`)
    return response.data
  }

  /**
   * 切换作品可见性
   */
  static async toggleWorkVisibility(workId: string): Promise<ToggleWorkVisibilityResponse> {
    const response = await apiClient.post<ToggleWorkVisibilityResponse>(`/admin/works/${workId}/toggle-visibility`)
    return response.data
  }

  // ==================== 后台管理 - 作品分类管理模块 ====================

  /**
   * 获取作品分类列表（管理后台）
   */
  static async getAdminWorkCategories(): Promise<AdminWorkCategoryListResponse> {
    const response = await apiClient.get<AdminWorkCategoryListResponse>('/admin/work-categories')
    return response.data
  }

  /**
   * 创建作品分类
   */
  static async createWorkCategory(request: CreateWorkCategoryRequest): Promise<WorkCategoryMutationResponse> {
    const response = await apiClient.post<WorkCategoryMutationResponse>('/admin/work-categories', request)
    return response.data
  }

  /**
   * 更新作品分类
   */
  static async updateWorkCategory(
    categoryId: string,
    request: UpdateWorkCategoryRequest
  ): Promise<WorkCategoryMutationResponse> {
    const response = await apiClient.put<WorkCategoryMutationResponse>(`/admin/work-categories/${categoryId}`, request)
    return response.data
  }

  /**
   * 删除作品分类
   */
  static async deleteWorkCategory(categoryId: string): Promise<void> {
    await apiClient.delete(`/admin/work-categories/${categoryId}`)
  }

  /**
   * 上移作品分类
   */
  static async moveWorkCategoryUp(categoryId: string): Promise<MoveWorkCategoryResponse> {
    const response = await apiClient.post<MoveWorkCategoryResponse>(`/admin/work-categories/${categoryId}/move-up`)
    return response.data
  }

  /**
   * 下移作品分类
   */
  static async moveWorkCategoryDown(categoryId: string): Promise<MoveWorkCategoryResponse> {
    const response = await apiClient.post<MoveWorkCategoryResponse>(`/admin/work-categories/${categoryId}/move-down`)
    return response.data
  }

  // ==================== 课程文档模块 ====================

  /**
   * 获取课程目录树
   */
  static async getCourseCategories(): Promise<CourseCategoryTreeResponse> {
    const response = await apiClient.get<CourseCategoryTreeResponse>('/documents/categories')
    return response.data
  }

  /**
   * 获取指定目录下的文档列表
   */
  static async getCourseDocumentsByCategory(categoryId: string): Promise<CourseDocumentListResponse> {
    const response = await apiClient.get<CourseDocumentListResponse>(`/documents/category/${categoryId}/documents`)
    return response.data
  }

  /**
   * 获取文档详情
   */
  static async getCourseDocumentDetail(docId: string): Promise<CourseDocumentDetail> {
    const response = await apiClient.get<CourseDocumentDetail>(`/documents/${docId}`)
    return response.data
  }

  // ==================== 后台管理 - 课程目录管理模块 ====================

  /**
   * 获取课程目录列表（管理后台）
   */
  static async getAdminCourseCategories(): Promise<AdminCourseCategoryListResponse> {
    const response = await apiClient.get<AdminCourseCategoryListResponse>('/admin/course-categories')
    return response.data
  }

  /**
   * 创建课程目录
   */
  static async createCourseCategory(request: CreateCourseCategoryRequest): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/admin/course-categories', request)
    return response.data
  }

  /**
   * 更新课程目录
   */
  static async updateCourseCategory(
    categoryId: string,
    request: UpdateCourseCategoryRequest
  ): Promise<{ message: string }> {
    const response = await apiClient.put<{ message: string }>(`/admin/course-categories/${categoryId}`, request)
    return response.data
  }

  /**
   * 删除课程目录
   */
  static async deleteCourseCategory(categoryId: string): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(`/admin/course-categories/${categoryId}`)
    return response.data
  }

  /**
   * 上移课程目录
   */
  static async moveCourseCategoryUp(categoryId: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>(`/admin/course-categories/${categoryId}/move-up`)
    return response.data
  }

  /**
   * 下移课程目录
   */
  static async moveCourseCategoryDown(categoryId: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>(`/admin/course-categories/${categoryId}/move-down`)
    return response.data
  }

  // ==================== 后台管理 - 课程文档管理模块 ====================

  /**
   * 获取课程文档列表（管理后台）
   */
  static async getAdminCourseDocuments(
    page?: number,
    pageSize?: number,
    categoryId?: string
  ): Promise<AdminCourseDocumentListResponse> {
    const params = new URLSearchParams()
    if (page) params.append('page', page.toString())
    if (pageSize) params.append('page_size', pageSize.toString())
    if (categoryId) params.append('category_id', categoryId)

    const response = await apiClient.get<AdminCourseDocumentListResponse>(
      `/admin/course-documents?${params.toString()}`
    )
    return response.data
  }

  /**
   * 创建课程文档
   */
  static async createCourseDocument(
    title: string,
    summary: string,
    categoryId: string,
    order: number,
    markdownFile: File
  ): Promise<{ message: string }> {
    const formData = new FormData()
    formData.append('title', title)
    formData.append('summary', summary)
    formData.append('category_id', categoryId)
    formData.append('order', order.toString())
    formData.append('markdown_file', markdownFile)

    const response = await apiClient.post<{ message: string }>('/admin/course-documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  }

  /**
   * 更新课程文档
   */
  static async updateCourseDocument(
    docId: string,
    request: UpdateCourseDocumentRequest
  ): Promise<{ message: string }> {
    const response = await apiClient.put<{ message: string }>(`/admin/course-documents/${docId}`, request)
    return response.data
  }

  /**
   * 删除课程文档
   */
  static async deleteCourseDocument(docId: string): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(`/admin/course-documents/${docId}`)
    return response.data
  }

  /**
   * 上移课程文档
   */
  static async moveCourseDocumentUp(docId: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>(`/admin/course-documents/${docId}/move-up`)
    return response.data
  }

  /**
   * 下移课程文档
   */
  static async moveCourseDocumentDown(docId: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>(`/admin/course-documents/${docId}/move-down`)
    return response.data
  }
}

export default apiClient

