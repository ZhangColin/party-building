/** 党建业务模块类型定义 */

// ==================== 党员管理 ====================

/**
 * 党员列表项
 */
export interface PartyMemberListItem {
  member_id: string // 党员ID
  name: string // 姓名
  gender: string // 性别
  birth_date: string // 出生日期 (ISO 8601 格式)
  join_date: string // 入党时间 (ISO 8601 格式)
  party_branch: string // 所属党支部
  member_type: string // 党员类型（正式党员/预备党员）
  phone?: string // 联系电话
  email?: string // 邮箱
  status: string // 状态（正常/停止党籍/出党等）
  fee_standard?: string // 党费标准（月缴金额）
  created_at: string // 创建时间 (ISO 8601 格式)
}

/**
 * 党员列表响应
 */
export interface PartyMemberListResponse {
  members: PartyMemberListItem[] // 党员列表
  total: number // 总数
  page: number // 当前页码
  page_size: number // 每页数量
}

/**
 * 党员详情
 */
export interface PartyMemberDetail {
  member_id: string // 党员ID
  // 基本信息
  name: string // 姓名
  gender: string // 性别
  id_card?: string // 身份证号
  birth_date: string // 出生日期
  education?: string // 学历
  phone?: string // 联系电话
  email?: string // 邮箱
  address?: string // 现居住地址
  work_unit?: string // 工作单位
  job_title?: string // 职务/职称

  // 党务信息
  join_date: string // 入党时间
  party_branch: string // 所属党支部
  member_type: string // 党员类型（正式党员/预备党员）
  application_date?: string // 入党申请书提交时间
  activist_date?: string // 确定为积极分子时间
  candidate_date?: string // 确定为发展对象时间
  provisional_date?: string // 接收为预备党员时间
  full_member_date?: string // 转正时间
  party_position?: string // 党内职务
  introducer_1?: string // 介绍人1
  introducer_2?: string // 介绍人2

  // 流动党员
  is_mobile: boolean // 是否流动党员
  mobile_type?: string // 流动类型（流出/流入）
  mobile_reason?: string // 流动原因

  // 党费
  monthly_income?: string // 月收入
  fee_standard?: string // 党费标准（月缴金额）

  // 状态
  status: string // 状态（正常/停止党籍/出党等）

  // 系统字段
  branch_id?: string // 所属支部ID
  created_at: string // 创建时间
  updated_at: string // 更新时间
}

/**
 * 创建党员请求
 */
export interface PartyMemberCreateRequest {
  // 基本信息
  name: string // 姓名
  gender: string // 性别
  id_card?: string // 身份证号
  birth_date: string // 出生日期
  education?: string // 学历
  phone?: string // 联系电话
  email?: string // 邮箱
  address?: string // 现居住地址
  work_unit?: string // 工作单位
  job_title?: string // 职务/职称

  // 党务信息
  join_date: string // 入党时间
  party_branch: string // 所属党支部
  member_type?: string // 党员类型（默认正式党员）
  application_date?: string // 入党申请书提交时间
  activist_date?: string // 确定为积极分子时间
  candidate_date?: string // 确定为发展对象时间
  provisional_date?: string // 接收为预备党员时间
  full_member_date?: string // 转正时间
  party_position?: string // 党内职务
  introducer_1?: string // 介绍人1
  introducer_2?: string // 介绍人2

  // 流动党员
  is_mobile?: boolean // 是否流动党员
  mobile_type?: string // 流动类型（流出/流入）
  mobile_reason?: string // 流动原因

  // 党费
  monthly_income?: string // 月收入
  fee_standard?: string // 党费标准（月缴金额）

  // 状态
  status?: string // 状态（默认正常）

  // 系统字段
  branch_id?: string // 所属支部ID
}

/**
 * 更新党员请求
 */
export interface PartyMemberUpdateRequest {
  // 基本信息
  name?: string // 姓名
  gender?: string // 性别
  id_card?: string // 身份证号
  birth_date?: string // 出生日期
  education?: string // 学历
  phone?: string // 联系电话
  email?: string // 邮箱
  address?: string // 现居住地址
  work_unit?: string // 工作单位
  job_title?: string // 职务/职称

  // 党务信息
  join_date?: string // 入党时间
  party_branch?: string // 所属党支部
  member_type?: string // 党员类型（正式党员/预备党员）
  application_date?: string // 入党申请书提交时间
  activist_date?: string // 确定为积极分子时间
  candidate_date?: string // 确定为发展对象时间
  provisional_date?: string // 接收为预备党员时间
  full_member_date?: string // 转正时间
  party_position?: string // 党内职务
  introducer_1?: string // 介绍人1
  introducer_2?: string // 介绍人2

  // 流动党员
  is_mobile?: boolean // 是否流动党员
  mobile_type?: string // 流动类型（流出/流入）
  mobile_reason?: string // 流动原因

  // 党费
  monthly_income?: string // 月收入
  fee_standard?: string // 党费标准（月缴金额）

  // 状态
  status?: string // 状态（正常/停止党籍/出党等）

  // 系统字段
  branch_id?: string // 所属支部ID
}

/**
 * 批量导入党员响应
 */
export interface PartyMemberBatchImportResponse {
  success_count: number // 成功导入数量
  total_count: number // 总数量
  errors: string[] // 失败原因列表
}

// ==================== 组织生活管理 ====================

/**
 * 组织生活列表项
 */
export interface OrganizationLifeListItem {
  life_id: string // 记录ID
  activity_type: string // 活动类型（三会一课/民主评议/主题党日等）
  title: string // 活动主题
  activity_date: string // 活动时间 (ISO 8601 格式)
  location?: string // 活动地点
  participants_count: number // 实到人数
  organizer?: string // 组织者
  created_at: string // 创建时间
}

/**
 * 组织生活列表响应
 */
export interface OrganizationLifeListResponse {
  records: OrganizationLifeListItem[] // 记录列表
  total: number // 总数
  page: number // 当前页码
  page_size: number // 每页数量
}

/**
 * 组织生活详情
 */
export interface OrganizationLifeDetail {
  life_id: string // 记录ID

  // 活动基本信息
  activity_type: string // 活动类型
  meeting_type?: string // 会议类型
  title: string // 活动主题
  activity_date: string // 活动时间
  location?: string // 活动地点

  // 人员信息
  host?: string // 主持人
  recorder?: string // 记录人
  expected_count?: number // 应到人数
  participants_count: number // 实到人数
  absent_members?: string // 缺席人员（JSON字符串）

  // 活动内容
  agenda?: string // 会议议程（JSON字符串）
  content?: string // 活动内容摘要
  resolutions?: string // 决议事项

  // 附件材料
  photos?: string // 活动照片（JSON数组字符串）
  attachments?: string // 附件材料（JSON数组字符串）

  // 组织者
  organizer?: string // 组织者

  // 系统字段
  branch_id?: string // 所属支部ID
  created_by?: string // 创建人ID
  created_at: string // 创建时间
  updated_at: string // 更新时间
}

/**
 * 创建组织生活请求
 */
export interface OrganizationLifeCreateRequest {
  // 活动基本信息
  activity_type: string // 活动类型
  meeting_type?: string // 会议类型
  title: string // 活动主题
  activity_date: string // 活动时间
  location?: string // 活动地点

  // 人员信息
  host?: string // 主持人
  recorder?: string // 记录人
  expected_count?: number // 应到人数
  participants_count?: number // 实到人数
  absent_members?: string // 缺席人员（JSON字符串）

  // 活动内容
  agenda?: string // 会议议程（JSON字符串）
  content?: string // 活动内容摘要
  resolutions?: string // 决议事项

  // 附件材料
  photos?: string // 活动照片（JSON数组字符串）
  attachments?: string // 附件材料（JSON数组字符串）

  // 组织者
  organizer?: string // 组织者

  // 系统字段
  branch_id?: string // 所属支部ID
}

/**
 * 更新组织生活请求
 */
export interface OrganizationLifeUpdateRequest {
  // 活动基本信息
  activity_type?: string // 活动类型
  meeting_type?: string // 会议类型
  title?: string // 活动主题
  activity_date?: string // 活动时间
  location?: string // 活动地点

  // 人员信息
  host?: string // 主持人
  recorder?: string // 记录人
  expected_count?: number // 应到人数
  participants_count?: number // 实到人数
  absent_members?: string // 缺席人员

  // 活动内容
  agenda?: string // 会议议程
  content?: string // 活动内容摘要
  resolutions?: string // 决议事项

  // 附件材料
  photos?: string // 活动照片
  attachments?: string // 附件材料

  // 组织者
  organizer?: string // 组织者

  // 系统字段
  branch_id?: string // 所属支部ID
}

// ==================== 党费管理 ====================

/**
 * 党费记录列表项
 */
export interface PartyFeeListItem {
  fee_id: string // 记录ID
  member_id?: string // 党员ID
  member_name: string // 党员姓名
  amount: number // 缴纳金额
  payment_date: string // 缴纳时间 (ISO 8601 格式)
  payment_method: string // 缴纳方式
  fee_month: string // 缴费月份（YYYY-MM）
  status: string // 状态（已缴/欠缴）
  collector?: string // 收款人
  created_at: string // 创建时间
}

/**
 * 党费记录列表响应
 */
export interface PartyFeeListResponse {
  fees: PartyFeeListItem[] // 党费记录列表
  total: number // 总数
  page: number // 当前页码
  page_size: number // 每页数量
}

/**
 * 党费记录详情
 */
export interface PartyFeeDetail {
  fee_id: string // 记录ID
  member_id?: string // 党员ID
  member_name: string // 党员姓名
  amount: number // 缴纳金额
  payment_date: string // 缴纳时间
  payment_method: string // 缴纳方式（现金/微信/支付宝/银行转账）
  fee_month: string // 缴费月份（YYYY-MM）
  status: string // 状态（已缴/欠缴）
  collector?: string // 收款人
  branch_id?: string // 所属支部ID
  remark?: string // 备注
  created_at: string // 创建时间
  updated_at: string // 更新时间
}

/**
 * 创建党费记录请求
 */
export interface PartyFeeCreateRequest {
  member_id?: string // 党员ID
  member_name: string // 党员姓名
  amount: number // 缴纳金额
  payment_date: string // 缴纳时间
  payment_method?: string // 缴纳方式（默认现金）
  fee_month: string // 缴费月份（YYYY-MM）
  status?: string // 状态（默认已缴）
  collector?: string // 收款人
  branch_id?: string // 所属支部ID
  remark?: string // 备注
}

/**
 * 更新党费记录请求
 */
export interface PartyFeeUpdateRequest {
  member_id?: string // 党员ID
  member_name?: string // 党员姓名
  amount?: number // 缴纳金额
  payment_date?: string // 缴纳时间
  payment_method?: string // 缴纳方式
  fee_month?: string // 缴费月份
  status?: string // 状态
  collector?: string // 收款人
  branch_id?: string // 所属支部ID
  remark?: string // 备注
}
