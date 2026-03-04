/** 前端类型定义 - 与后端 Model 对应 */

/**
 * Agent 列表项（用于 API 响应）- 已废弃，保留以保持向后兼容
 */
export interface AgentListItem {
  agent_id: string
  name: string
  description?: string
  icon?: string
}

/**
 * Agent 列表响应 - 已废弃，保留以保持向后兼容
 */
export interface AgentListResponse {
  agents: AgentListItem[]
}

/**
 * 工具列表项（用于 API 响应）
 */
export interface ToolListItem {
  tool_id: string // 工具唯一标识符
  name: string // 工具名称
  description?: string // 工具描述
  icon?: string // 图标标识（可选）
  category: string // 分类名称
  visible: boolean // 是否在工具选择器中显示
  type: 'normal' | 'placeholder' // 工具类型
  welcome_message?: string // 欢迎语（可选，用于占位工具）
  
  // 多模态支持字段（新增）
  content_type?: 'text' | 'multimodal' // 内容类型（默认text）
  media_type?: 'image' | 'audio' | 'video' // 媒体类型（仅multimodal时有效）
}

/**
 * 分类组（用于 API 响应）
 */
export interface CategoryGroup {
  name: string // 分类名称
  icon?: string // 分类图标（可选）
  tools: ToolListItem[] // 该分类下的工具列表
}

/**
 * 工具列表响应
 */
export interface ToolListResponse {
  categories: CategoryGroup[] // 按分类组织的工具列表
}

/**
 * UI 配置值对象
 */
export interface UIConfig {
  show_preview: boolean
  preview_types: string[]
}

/**
 * 成果物值对象（不可变）
 */
export interface Artifact {
  type: string // 成果物类型，由代码块语言标识决定
  content: string // 代码块中的原始内容
  language: string // 代码块的语言标识（如 'markdown', 'html', 'svg'）
  timestamp: string // 成果物生成时间（ISO 8601 格式）
}

/**
 * 消息实体（支持文本和多模态）
 */
export interface Message {
  message_id?: string // 消息 UUID（可选，用于数据库存储）
  session_id?: string // 关联的会话ID（可选，用于数据库存储）
  role: 'user' | 'assistant' // 消息角色
  content: string // 消息内容（Markdown 格式或用户提示词）
  created_at?: string // 消息创建时间（ISO 8601 格式）
  timestamp?: string // 消息时间戳（ISO 8601 格式，可选）
  artifacts?: Artifact[] // 消息中包含的成果物列表（可选）
  error?: string // 错误信息（可选，用于显示发送失败）
  pending?: boolean // 是否正在发送（可选，用于显示加载状态）
  
  // 多模态支持字段
  media_content?: string // 多模态内容JSON字符串（图片、音频、视频等）
}

/**
 * 会话初始化响应
 */
export interface SessionInitResponse {
  session_id: string // 会话 UUID
  welcome_message: string // AI 生成的欢迎语（第一条消息）
  ui_config: UIConfig // UI 配置，如是否开启预览、预览类型等
  artifacts: Artifact[] // 欢迎语中可能包含的成果物（如代码块）
}

/**
 * 对话请求
 */
export interface ChatRequest {
  message: string // 用户输入的消息
  session_id?: string | null // 会话 UUID（可选，如果有则继续会话，没有则创建新会话）
  history?: Message[] // 历史消息列表（可选）
}

/**
 * 对话响应
 */
export interface ChatResponse {
  session_id: string // 会话 UUID。首次调用返回新创建的session_id，后续调用返回原session_id
  reply: string // AI 的文本回复内容（完整 Markdown 文本）
  artifacts: Artifact[] // 从回复中解析出的成果物列表（代码块内容）
}

/**
 * 历史对话列表项
 */
export interface ConversationListItem {
  session_id: string // 会话 UUID
  title: string // 会话标题
  updated_at: string // 最后更新时间（ISO 8601 格式）
}

/**
 * 历史对话列表响应
 */
export interface ConversationListResponse {
  conversations: ConversationListItem[] // 对话列表
}

/**
 * 会话详情响应
 */
export interface SessionDetailResponse {
  session_id: string // 会话 UUID
  tool_id: string // 工具唯一标识符
  title: string // 会话标题
  created_at: string // 创建时间（ISO 8601 格式）
  updated_at: string // 最后更新时间（ISO 8601 格式）
  messages: Message[] // 消息列表
}

/**
 * 更新会话标题请求
 */
export interface UpdateSessionRequest {
  title: string // 新的会话标题
}

/**
 * 更新会话标题响应
 */
export interface UpdateSessionResponse {
  session_id: string // 会话 UUID
  title: string // 更新后的会话标题
}

/**
 * 用户信息（用于API响应，不包含密码）
 */
export interface UserInfo {
  user_id: string // 用户唯一标识（UUID）
  username: string // 用户名（用于登录）
  nickname?: string // 用户昵称（可选，用于显示，如未填写则使用用户名）
  email?: string // 用户邮箱（可选，用于登录）
  phone?: string // 用户手机号（可选，用于登录）
  avatar?: string // 用户头像URL（可选，默认头像）
  is_admin?: boolean // 是否为管理员（可选，默认false）
}

/**
 * 登录请求
 */
export interface LoginRequest {
  account: string // 用户账号（用户名、邮箱或手机号）
  password: string // 用户密码
  remember_me: boolean // 是否记住我（影响Token有效期）
}

/**
 * 登录响应
 */
export interface LoginResponse {
  token: string // JWT Token，用于后续请求的身份验证
  user: UserInfo // 用户基本信息
  expires_in: number // Token有效期（秒），如：604800（7天）或86400（24小时）
}

/**
 * 用户列表项
 */
export interface UserListItem {
  user_id: string // 用户唯一标识（UUID）
  username: string // 用户名（用于登录）
  nickname?: string // 用户昵称（可选，用于显示，如未填写则使用用户名）
  email?: string // 用户邮箱（可选，用于登录）
  phone?: string // 用户手机号（可选，用于登录）
  avatar?: string // 用户头像URL
  is_admin?: boolean // 是否为管理员（可选，默认false）
  created_at: string // 用户创建时间（ISO 8601 格式）
}

/**
 * 用户列表响应
 */
export interface UserListResponse {
  users: UserListItem[] // 用户列表
  total: number // 用户总数
  page: number // 当前页码
  page_size: number // 每页数量
}

/**
 * 创建用户请求
 */
export interface CreateUserRequest {
  username: string // 用户名（必填，用于登录，必须唯一）
  nickname?: string // 用户昵称（可选，用于显示，如未填写则使用用户名）
  email?: string // 用户邮箱（可选，用于登录）
  phone?: string // 用户手机号（可选，用于登录）
  password: string // 用户密码
  avatar?: string // 用户头像URL（可选）
  is_admin?: boolean // 是否为管理员（可选，默认false）
}

/**
 * 创建用户响应
 */
export interface CreateUserResponse {
  user: UserListItem // 新创建的用户信息
}

/**
 * 更新用户请求
 */
export interface UpdateUserRequest {
  username?: string // 用户名（可选）
  nickname?: string // 用户昵称（可选）
  email?: string // 用户邮箱（可选）
  phone?: string // 用户手机号（可选）
  is_admin?: boolean // 是否为管理员（可选）
}

/**
 * 更新用户响应
 */
export interface UpdateUserResponse {
  user: UserListItem // 更新后的用户信息
}

/**
 * 重置密码请求
 */
export interface ResetPasswordRequest {
  new_password: string // 新密码
}

/**
 * 重置密码响应
 */
export interface ResetPasswordResponse {
  message: string // 操作结果消息
  new_password: string // 新密码（明文，用于告知用户）
}

// ==================== 常用工具模块 ====================

/**
 * 常用工具列表项（用于工具卡片页）
 */
export interface CommonToolListItem {
  id: string // 工具ID
  name: string // 工具名称
  description: string // 工具描述
  type: 'built_in' | 'html' // 工具类型
  icon?: string // 图标（可选）
  order: number // 排序字段
}

/**
 * 工具分类组（包含分类信息和工具列表）
 */
export interface ToolCategoryGroup {
  id: string // 分类ID
  name: string // 分类名称
  icon?: string // 分类图标（可选）
  order: number // 排序字段
  tools: CommonToolListItem[] // 该分类下的工具列表
}

/**
 * 常用工具分类响应
 */
export interface CommonToolCategoryResponse {
  categories: ToolCategoryGroup[] // 分类列表
}

/**
 * 常用工具详情
 */
export interface CommonToolDetail {
  id: string // 工具ID
  name: string // 工具名称
  description: string // 工具描述
  category_id: string // 分类ID
  category_name: string // 分类名称
  type: 'built_in' | 'html' // 工具类型
  icon?: string // 图标（可选）
  order: number // 排序字段
  html_url?: string // HTML工具访问URL（仅HTML工具）
  created_at: string // 创建时间（ISO 8601格式）
}

// ==================== 后台管理 - 工具管理模块 ====================

/**
 * 管理后台 - 工具列表项
 */
export interface AdminCommonToolListItem {
  id: string // 工具ID
  name: string // 工具名称
  description: string // 工具描述
  category_id: string // 所属分类ID
  category_name: string // 所属分类名称
  type: 'built_in' | 'html' // 工具类型
  icon?: string // 图标标识
  html_path?: string // HTML文件路径（仅HTML工具）
  order: number // 排序顺序
  visible: boolean // 是否可见
  created_at: string // 创建时间
  updated_at: string // 更新时间
}

/**
 * 管理后台 - 工具列表响应
 */
export interface AdminCommonToolListResponse {
  tools: AdminCommonToolListItem[] // 工具列表
  total: number // 工具总数
  page: number // 当前页码
  page_size: number // 每页数量
}

/**
 * 创建内置工具请求
 */
export interface CreateBuiltInToolRequest {
  name: string // 工具名称
  description: string // 工具描述
  category_id: string // 所属分类ID
  icon?: string // 图标标识（heroicons名称）
  order?: number // 排序顺序（默认0）
  visible?: boolean // 是否可见（默认true）
}

/**
 * 更新工具请求
 */
export interface UpdateToolRequest {
  name?: string // 工具名称
  description?: string // 工具描述
  category_id?: string // 所属分类ID
  icon?: string // 图标标识（heroicons名称）
  order?: number // 排序顺序
  visible?: boolean // 是否可见
}

/**
 * 创建/更新工具响应
 */
export interface ToolMutationResponse {
  tool: AdminCommonToolListItem // 工具信息
}

/**
 * 移动工具响应
 */
export interface MoveToolResponse {
  message: string // 操作结果消息
  tool: AdminCommonToolListItem // 移动后的工具信息
}

/**
 * 切换可见性响应
 */
export interface ToggleVisibilityResponse {
  message: string // 操作结果消息
  tool: AdminCommonToolListItem // 更新后的工具信息
}

// ==================== 后台管理 - 工具分类管理模块 ====================

/**
 * 管理后台 - 工具分类列表项
 */
export interface AdminToolCategoryListItem {
  id: string // 分类ID
  name: string // 分类名称
  icon?: string // 分类图标
  order: number // 排序顺序
  tool_count: number // 该分类下的工具数量
  created_at: string // 创建时间
  updated_at: string // 更新时间
}

/**
 * 管理后台 - 工具分类列表响应
 */
export interface AdminToolCategoryListResponse {
  categories: AdminToolCategoryListItem[] // 分类列表
}

/**
 * 创建工具分类请求
 */
export interface CreateToolCategoryRequest {
  name: string // 分类名称
  icon?: string // 分类图标（heroicons名称）
  order?: number // 排序顺序（默认0）
}

/**
 * 更新工具分类请求
 */
export interface UpdateToolCategoryRequest {
  name?: string // 分类名称
  icon?: string // 分类图标（heroicons名称）
  order?: number // 排序顺序
}

/**
 * 创建/更新分类响应
 */
export interface CategoryMutationResponse {
  category: AdminToolCategoryListItem // 分类信息
}

/**
 * 移动分类响应
 */
export interface MoveCategoryResponse {
  message: string // 操作结果消息
  category: AdminToolCategoryListItem // 移动后的分类信息
}

// ==================== 作品展示模块 ====================

/**
 * 作品列表项（用于作品卡片页）
 */
export interface WorkListItem {
  id: string // 作品ID
  name: string // 作品名称
  description: string // 作品描述
  icon?: string // 图标（可选）
  order: number // 排序字段
}

/**
 * 作品分类组（包含分类信息和作品列表）
 */
export interface WorkCategoryGroup {
  id: string // 分类ID
  name: string // 分类名称
  icon?: string // 分类图标（可选）
  order: number // 排序字段
  works: WorkListItem[] // 该分类下的作品列表
}

/**
 * 作品分类响应
 */
export interface WorkCategoryResponse {
  categories: WorkCategoryGroup[] // 分类列表
}

/**
 * 作品详情
 */
export interface WorkDetail {
  id: string // 作品ID
  name: string // 作品名称
  description: string // 作品描述
  category_id: string // 分类ID
  category_name: string // 分类名称
  icon?: string // 图标（可选）
  order: number // 排序字段
  html_url: string // HTML文件访问URL
  created_at: string // 创建时间（ISO 8601格式）
}

// ==================== 后台管理 - 作品管理模块 ====================

/**
 * 管理后台 - 作品列表项
 */
export interface AdminWorkListItem {
  id: string // 作品ID
  name: string // 作品名称
  description: string // 作品描述
  category_id: string // 所属分类ID
  category_name: string // 所属分类名称
  icon?: string // 图标标识
  html_path: string // HTML文件路径
  order: number // 排序顺序
  visible: boolean // 是否可见
  created_at: string // 创建时间
  updated_at: string // 更新时间
}

/**
 * 管理后台 - 作品列表响应
 */
export interface AdminWorkListResponse {
  works: AdminWorkListItem[] // 作品列表
  total: number // 作品总数
  page: number // 当前页码
  page_size: number // 每页数量
}

/**
 * 更新作品请求
 */
export interface UpdateWorkRequest {
  name?: string // 作品名称
  description?: string // 作品描述
  category_id?: string // 所属分类ID
  icon?: string // 图标标识（heroicons名称）
  order?: number // 排序顺序
  visible?: boolean // 是否可见
}

/**
 * 作品创建/更新响应
 */
export interface WorkMutationResponse {
  work: AdminWorkListItem // 作品信息
}

/**
 * 移动作品响应
 */
export interface MoveWorkResponse {
  message: string // 操作结果消息
  work: AdminWorkListItem // 移动后的作品信息
}

/**
 * 切换作品可见性响应
 */
export interface ToggleWorkVisibilityResponse {
  message: string // 操作结果消息
  work: AdminWorkListItem // 更新后的作品信息
}

// ==================== 后台管理 - 作品分类管理模块 ====================

/**
 * 管理后台 - 作品分类列表项
 */
export interface AdminWorkCategoryListItem {
  id: string // 分类ID
  name: string // 分类名称
  icon?: string // 分类图标
  order: number // 排序顺序
  work_count: number // 该分类下的作品数量
  created_at: string // 创建时间
  updated_at: string // 更新时间
}

/**
 * 管理后台 - 作品分类列表响应
 */
export interface AdminWorkCategoryListResponse {
  categories: AdminWorkCategoryListItem[] // 分类列表
}

/**
 * 创建作品分类请求
 */
export interface CreateWorkCategoryRequest {
  name: string // 分类名称
  icon?: string // 分类图标（heroicons名称）
  order?: number // 排序顺序（默认0）
}

/**
 * 更新作品分类请求
 */
export interface UpdateWorkCategoryRequest {
  name?: string // 分类名称
  icon?: string // 分类图标（heroicons名称）
  order?: number // 排序顺序
}

/**
 * 作品分类创建/更新响应
 */
export interface WorkCategoryMutationResponse {
  category: AdminWorkCategoryListItem // 分类信息
}

/**
 * 移动作品分类响应
 */
export interface MoveWorkCategoryResponse {
  message: string // 操作结果消息
  category: AdminWorkCategoryListItem // 移动后的分类信息
}

// ==================== 课程文档模块 ====================

/**
 * 课程目录节点（递归结构）
 */
export interface CourseCategoryNode {
  id: string // 目录ID
  name: string // 目录名称
  parent_id?: string | null // 父目录ID（根目录为null）
  order: number // 排序顺序
  children: CourseCategoryNode[] // 子目录列表
}

/**
 * 课程目录树响应
 */
export interface CourseCategoryTreeResponse {
  categories: CourseCategoryNode[] // 根目录列表
}

/**
 * 课程文档列表项（用于文档列表）
 */
export interface CourseDocumentListItem {
  id: string // 文档ID
  title: string // 文档标题
  summary: string // 文档摘要
  order: number // 排序顺序
}

/**
 * 课程文档列表响应
 */
export interface CourseDocumentListResponse {
  documents: CourseDocumentListItem[] // 文档列表
}

/**
 * 课程文档详情
 */
export interface CourseDocumentDetail {
  id: string // 文档ID
  title: string // 文档标题
  summary: string // 文档摘要
  content: string // Markdown内容
  category_id: string // 所属目录ID
  order: number // 排序顺序
  prev_doc_id?: string | null // 上一篇文档ID
  next_doc_id?: string | null // 下一篇文档ID
  created_at: string // 创建时间（ISO 8601格式）
}

// ==================== 后台管理 - 课程目录管理模块 ====================

/**
 * 管理后台 - 课程目录列表项
 */
export interface AdminCourseCategoryListItem {
  id: string // 目录ID
  name: string // 目录名称
  parent_id?: string | null // 父目录ID
  parent_name?: string | null // 父目录名称
  order: number // 排序顺序
  document_count: number // 该目录下的文档数量
  children_count: number // 子目录数量
  created_at: string // 创建时间
  updated_at: string // 更新时间
  children?: AdminCourseCategoryListItem[] // 子目录列表（树形表格使用）
}

/**
 * 管理后台 - 课程目录列表响应
 */
export interface AdminCourseCategoryListResponse {
  categories: AdminCourseCategoryListItem[] // 目录列表
}

/**
 * 创建课程目录请求
 */
export interface CreateCourseCategoryRequest {
  name: string // 目录名称
  parent_id?: string | null // 父目录ID（可选，根目录为null）
  order?: number // 排序顺序（默认0）
}

/**
 * 更新课程目录请求
 */
export interface UpdateCourseCategoryRequest {
  name?: string // 目录名称
  parent_id?: string | null // 父目录ID
  order?: number // 排序顺序
}

// ==================== 后台管理 - 课程文档管理模块 ====================

/**
 * 管理后台 - 课程文档列表项
 */
export interface AdminCourseDocumentListItem {
  id: string // 文档ID
  title: string // 文档标题
  summary: string // 文档摘要
  category_id: string // 所属目录ID
  category_name: string // 所属目录名称
  category_path: string // 所属目录完整路径
  order: number // 排序顺序
  created_at: string // 创建时间
  updated_at: string // 更新时间
}

/**
 * 管理后台 - 课程文档列表响应
 */
export interface AdminCourseDocumentListResponse {
  documents: AdminCourseDocumentListItem[] // 文档列表
  total: number // 文档总数
  page: number // 当前页码
  page_size: number // 每页数量
}

/**
 * 更新课程文档请求
 */
export interface UpdateCourseDocumentRequest {
  title?: string // 文档标题
  summary?: string // 文档摘要
  category_id?: string // 所属目录ID
  order?: number // 排序顺序
}

