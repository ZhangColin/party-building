/** 导航模块类型定义 */

/**
 * 导航模块类型
 * - toolset: 工具集模块（复用AIToolsLayout的UI和功能）
 * - page: 独立页面模块（自定义页面）
 */
export type ModuleType = 'toolset' | 'page'

/**
 * 导航模块配置
 */
export interface NavigationModule {
  /** 模块显示名称 */
  name: string
  /** 模块类型 */
  type: ModuleType
  /** 配置来源（type=toolset时使用，工具集配置目录路径，如：tools/ai_tools） */
  config_source?: string
  /** 页面路径（type=page时使用，前端路由路径，如：/common-tools） */
  page_path?: string
  /** 图标标识（可选） */
  icon?: string
  /** 排序顺序（数字越小越靠前） */
  order: number
}

/**
 * 导航配置响应
 */
export interface NavigationResponse {
  /** 导航模块列表 */
  modules: NavigationModule[]
}
