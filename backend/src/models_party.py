# -*- coding: utf-8 -*-
"""党建业务模块 Pydantic 模型（API 请求/响应）"""
from datetime import datetime, date
from typing import List, Optional, Union
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ==================== 党员管理 ====================

class PartyMemberBase(BaseModel):
    """党员基础信息"""
    # 基本信息
    name: str = Field(..., description="姓名", min_length=1, max_length=50)
    gender: str = Field(..., description="性别", min_length=1, max_length=10)
    id_card: Optional[str] = Field(None, description="身份证号", max_length=18)
    birth_date: date = Field(..., description="出生日期")
    education: Optional[str] = Field(None, description="学历", max_length=20)
    phone: Optional[str] = Field(None, description="联系电话", max_length=20)
    email: Optional[str] = Field(None, description="邮箱", max_length=100)
    address: Optional[str] = Field(None, description="现居住地址", max_length=500)
    work_unit: Optional[str] = Field(None, description="工作单位", max_length=200)
    job_title: Optional[str] = Field(None, description="职务/职称", max_length=100)

    # 党务信息
    join_date: date = Field(..., description="入党时间")
    party_branch: str = Field(..., description="所属党支部", min_length=1, max_length=100)
    member_type: str = Field(default="正式党员", description="党员类型（正式党员/预备党员）", max_length=50)
    application_date: Optional[date] = Field(None, description="入党申请书提交时间")
    activist_date: Optional[date] = Field(None, description="确定为积极分子时间")
    candidate_date: Optional[date] = Field(None, description="确定为发展对象时间")
    provisional_date: Optional[date] = Field(None, description="接收为预备党员时间")
    full_member_date: Optional[date] = Field(None, description="转正时间")
    party_position: Optional[str] = Field(None, description="党内职务", max_length=100)
    introducer_1: Optional[str] = Field(None, description="介绍人1", max_length=50)
    introducer_2: Optional[str] = Field(None, description="介绍人2", max_length=50)

    # 流动党员
    is_mobile: bool = Field(default=False, description="是否流动党员")
    mobile_type: Optional[str] = Field(None, description="流动类型（流出/流入）", max_length=20)
    mobile_reason: Optional[str] = Field(None, description="流动原因", max_length=500)

    # 党费
    monthly_income: Optional[Decimal] = Field(None, description="月收入")
    fee_standard: Optional[Decimal] = Field(None, description="党费标准（月缴金额）")

    # 状态
    status: str = Field(default="正常", description="状态（正常/停止党籍/出党等）", max_length=20)

    # 系统字段
    branch_id: Optional[str] = Field(None, description="所属支部ID")


class PartyMemberCreate(PartyMemberBase):
    """创建党员请求"""
    # 覆盖日期字段为Union类型以支持空字符串
    application_date: Union[date, None] = Field(None, description="入党申请书提交时间")
    activist_date: Union[date, None] = Field(None, description="确定为积极分子时间")
    candidate_date: Union[date, None] = Field(None, description="确定为发展对象时间")
    provisional_date: Union[date, None] = Field(None, description="接收为预备党员时间")
    full_member_date: Union[date, None] = Field(None, description="转正时间")

    @field_validator('application_date', 'activist_date', 'candidate_date', 'provisional_date', 'full_member_date', mode='before')
    @classmethod
    def validate_empty_date_strings(cls, v):
        """将空字符串转换为None"""
        if v == "" or v is None:
            return None
        return v

    @field_validator('id_card', 'phone', 'email', 'address', 'work_unit', 'job_title',
                    'party_position', 'introducer_1', 'introducer_2', 'mobile_type', 'mobile_reason', 'branch_id')
    def validate_empty_strings(cls, v):
        """将空字符串转换为None"""
        if v == "":
            return None
        return v

    @field_validator('id_card')
    def validate_id_card(cls, v):
        """验证身份证号格式"""
        if v and len(v) != 18:
            raise ValueError('身份证号必须为18位')
        return v


class PartyMemberUpdate(BaseModel):
    """更新党员请求"""
    # 基本信息
    name: Optional[str] = Field(None, description="姓名", min_length=1, max_length=50)
    gender: Optional[str] = Field(None, description="性别", max_length=10)
    id_card: Optional[str] = Field(None, description="身份证号", max_length=18)
    birth_date: Optional[date] = Field(None, description="出生日期")
    education: Optional[str] = Field(None, description="学历", max_length=20)
    phone: Optional[str] = Field(None, description="联系电话", max_length=20)
    email: Optional[str] = Field(None, description="邮箱", max_length=100)
    address: Optional[str] = Field(None, description="现居住地址", max_length=500)
    work_unit: Optional[str] = Field(None, description="工作单位", max_length=200)
    job_title: Optional[str] = Field(None, description="职务/职称", max_length=100)

    # 党务信息
    join_date: Optional[date] = Field(None, description="入党时间")
    party_branch: Optional[str] = Field(None, description="所属党支部", max_length=100)
    member_type: Optional[str] = Field(None, description="党员类型（正式党员/预备党员）", max_length=50)
    application_date: Optional[date] = Field(None, description="入党申请书提交时间")
    activist_date: Optional[date] = Field(None, description="确定为积极分子时间")
    candidate_date: Optional[date] = Field(None, description="确定为发展对象时间")
    provisional_date: Optional[date] = Field(None, description="接收为预备党员时间")
    full_member_date: Optional[date] = Field(None, description="转正时间")
    party_position: Optional[str] = Field(None, description="党内职务", max_length=100)
    introducer_1: Optional[str] = Field(None, description="介绍人1", max_length=50)
    introducer_2: Optional[str] = Field(None, description="介绍人2", max_length=50)

    # 流动党员
    is_mobile: Optional[bool] = Field(None, description="是否流动党员")
    mobile_type: Optional[str] = Field(None, description="流动类型（流出/流入）", max_length=20)
    mobile_reason: Optional[str] = Field(None, description="流动原因", max_length=500)

    # 党费
    monthly_income: Optional[Decimal] = Field(None, description="月收入")
    fee_standard: Optional[Decimal] = Field(None, description="党费标准（月缴金额）")

    # 状态
    status: Optional[str] = Field(None, description="状态（正常/停止党籍/出党等）", max_length=20)

    # 系统字段
    branch_id: Optional[str] = Field(None, description="所属支部ID")


class PartyMemberListItem(BaseModel):
    """党员列表项"""
    member_id: str = Field(..., description="党员ID")
    name: str = Field(..., description="姓名")
    gender: str = Field(..., description="性别")
    birth_date: date = Field(..., description="出生日期")
    join_date: date = Field(..., description="入党时间")
    party_branch: str = Field(..., description="所属党支部")
    member_type: str = Field(..., description="党员类型")
    phone: Optional[str] = Field(None, description="联系电话")
    email: Optional[str] = Field(None, description="邮箱")
    status: str = Field(..., description="状态")
    created_at: datetime = Field(..., description="创建时间")

    model_config = ConfigDict(from_attributes=True)


class PartyMemberListResponse(BaseModel):
    """党员列表响应"""
    members: List[PartyMemberListItem] = Field(..., description="党员列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")


class PartyMemberDetail(PartyMemberBase):
    """党员详情"""
    member_id: str = Field(..., description="党员ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)


# ==================== 组织生活管理 ====================

class OrganizationLifeBase(BaseModel):
    """组织生活基础信息"""
    # 活动基本信息
    activity_type: str = Field(..., description="活动类型（三会一课/民主评议/主题党日等）", min_length=1, max_length=50)
    meeting_type: Optional[str] = Field(None, description="会议类型（支部党员大会/支委会/党小组会/党课）", max_length=50)
    title: str = Field(..., description="活动主题", min_length=1, max_length=200)
    activity_date: datetime = Field(..., description="活动时间")
    location: Optional[str] = Field(None, description="活动地点", max_length=200)

    # 人员信息
    host: Optional[str] = Field(None, description="主持人", max_length=50)
    recorder: Optional[str] = Field(None, description="记录人", max_length=50)
    expected_count: Optional[int] = Field(None, description="应到人数", ge=0)
    participants_count: int = Field(default=0, description="实到人数", ge=0)
    absent_members: Optional[str] = Field(None, description="缺席人员（JSON数组）")

    # 活动内容
    agenda: Optional[str] = Field(None, description="会议议程（JSON）")
    content: Optional[str] = Field(None, description="活动内容摘要")
    resolutions: Optional[str] = Field(None, description="决议事项")

    # 附件材料
    photos: Optional[str] = Field(None, description="活动照片（JSON数组）")
    attachments: Optional[str] = Field(None, description="附件材料（JSON数组）")

    # 组织者
    organizer: Optional[str] = Field(None, description="组织者", max_length=100)

    # 系统字段
    branch_id: Optional[str] = Field(None, description="所属支部ID")
    created_by: Optional[str] = Field(None, description="创建人ID")


class OrganizationLifeCreate(OrganizationLifeBase):
    """创建组织生活记录请求"""

    @field_validator('meeting_type', 'location', 'host', 'recorder', 'absent_members',
                    'agenda', 'content', 'resolutions', 'photos', 'attachments', 'organizer', 'branch_id', 'created_by')
    def validate_empty_strings(cls, v):
        """将空字符串转换为None"""
        if v == "":
            return None
        return v


class OrganizationLifeUpdate(BaseModel):
    """更新组织生活记录请求"""
    # 活动基本信息
    activity_type: Optional[str] = Field(None, description="活动类型", min_length=1, max_length=50)
    meeting_type: Optional[str] = Field(None, description="会议类型", max_length=50)
    title: Optional[str] = Field(None, description="活动主题", min_length=1, max_length=200)
    activity_date: Optional[datetime] = Field(None, description="活动时间")
    location: Optional[str] = Field(None, description="活动地点", max_length=200)

    # 人员信息
    host: Optional[str] = Field(None, description="主持人", max_length=50)
    recorder: Optional[str] = Field(None, description="记录人", max_length=50)
    expected_count: Optional[int] = Field(None, description="应到人数", ge=0)
    participants_count: Optional[int] = Field(None, description="实到人数", ge=0)
    absent_members: Optional[str] = Field(None, description="缺席人员（JSON数组）")

    # 活动内容
    agenda: Optional[str] = Field(None, description="会议议程（JSON）")
    content: Optional[str] = Field(None, description="活动内容摘要")
    resolutions: Optional[str] = Field(None, description="决议事项")

    # 附件材料
    photos: Optional[str] = Field(None, description="活动照片（JSON数组）")
    attachments: Optional[str] = Field(None, description="附件材料（JSON数组）")

    # 组织者
    organizer: Optional[str] = Field(None, description="组织者", max_length=100)

    # 系统字段
    branch_id: Optional[str] = Field(None, description="所属支部ID")


class OrganizationLifeListItem(BaseModel):
    """组织生活列表项"""
    life_id: str = Field(..., description="记录ID")
    activity_type: str = Field(..., description="活动类型")
    title: str = Field(..., description="活动主题")
    activity_date: datetime = Field(..., description="活动时间")
    location: Optional[str] = Field(None, description="活动地点")
    participants_count: int = Field(..., description="参与人数")
    organizer: Optional[str] = Field(None, description="组织者")
    created_at: datetime = Field(..., description="创建时间")

    model_config = ConfigDict(from_attributes=True)


class OrganizationLifeListResponse(BaseModel):
    """组织生活列表响应"""
    records: List[OrganizationLifeListItem] = Field(..., description="记录列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")


class OrganizationLifeDetail(OrganizationLifeBase):
    """组织生活详情"""
    life_id: str = Field(..., description="记录ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)


# ==================== 党费管理 ====================

class PartyFeeBase(BaseModel):
    """党费基础信息"""
    member_name: str = Field(..., description="党员姓名", min_length=1, max_length=50)
    amount: Decimal = Field(..., description="缴纳金额", gt=0)
    payment_date: datetime = Field(..., description="缴纳时间")
    payment_method: str = Field(default="现金", description="缴纳方式（现金/微信/支付宝/银行转账）", max_length=50)
    fee_month: str = Field(..., description="缴费月份（YYYY-MM）", pattern=r"^\d{4}-\d{2}$")
    status: str = Field(default="已缴", description="状态（已缴/欠缴）", max_length=20)
    collector: Optional[str] = Field(None, description="收款人", max_length=100)
    remark: Optional[str] = Field(None, description="备注", max_length=500)
    branch_id: Optional[str] = Field(None, description="所属支部ID")


class PartyFeeCreate(PartyFeeBase):
    """创建党费记录请求"""
    member_id: str = Field(..., description="党员ID")

    @field_validator('collector', 'remark', 'branch_id')
    def validate_empty_strings(cls, v):
        """将空字符串转换为None"""
        if v == "":
            return None
        return v


class PartyFeeUpdate(BaseModel):
    """更新党费记录请求"""
    amount: Optional[Decimal] = Field(None, description="缴纳金额", gt=0)
    payment_date: Optional[datetime] = Field(None, description="缴纳时间")
    payment_method: Optional[str] = Field(None, description="缴纳方式", max_length=50)
    fee_month: Optional[str] = Field(None, description="缴费月份（YYYY-MM）", pattern=r"^\d{4}-\d{2}$")
    status: Optional[str] = Field(None, description="状态（已缴/欠缴）", max_length=20)
    collector: Optional[str] = Field(None, description="收款人", max_length=100)
    remark: Optional[str] = Field(None, description="备注", max_length=500)
    branch_id: Optional[str] = Field(None, description="所属支部ID")


class PartyFeeListItem(BaseModel):
    """党费列表项"""
    fee_id: str = Field(..., description="记录ID")
    member_id: Optional[str] = Field(None, description="党员ID")
    member_name: str = Field(..., description="党员姓名")
    amount: Decimal = Field(..., description="缴纳金额")
    payment_date: datetime = Field(..., description="缴纳时间")
    payment_method: str = Field(..., description="缴纳方式")
    fee_month: str = Field(..., description="缴费月份")
    status: str = Field(..., description="状态")
    created_at: datetime = Field(..., description="创建时间")

    model_config = ConfigDict(from_attributes=True)


class PartyFeeListResponse(BaseModel):
    """党费列表响应"""
    fees: List[PartyFeeListItem] = Field(..., description="党费列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")


class PartyFeeDetail(PartyFeeBase):
    """党费详情"""
    fee_id: str = Field(..., description="记录ID")
    member_id: Optional[str] = Field(None, description="党员ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)


# ==================== 党费标准管理 ====================

class PartyFeeStandardBase(BaseModel):
    """党费标准基础信息"""
    member_id: str = Field(..., description="党员ID")
    monthly_income: Decimal = Field(..., description="月收入", gt=0)
    fee_amount: Decimal = Field(..., description="应缴金额", gt=0)
    effective_date: date = Field(..., description="生效日期")
    branch_id: Optional[str] = Field(None, description="所属支部ID")


class PartyFeeStandardCreate(PartyFeeStandardBase):
    """创建党费标准请求"""
    pass


class PartyFeeStandardUpdate(BaseModel):
    """更新党费标准请求"""
    monthly_income: Optional[Decimal] = Field(None, description="月收入", gt=0)
    fee_amount: Optional[Decimal] = Field(None, description="应缴金额", gt=0)
    effective_date: Optional[date] = Field(None, description="生效日期")
    branch_id: Optional[str] = Field(None, description="所属支部ID")


class PartyFeeStandardListItem(BaseModel):
    """党费标准列表项"""
    id: str = Field(..., description="标准ID")
    member_id: str = Field(..., description="党员ID")
    monthly_income: Decimal = Field(..., description="月收入")
    fee_amount: Decimal = Field(..., description="应缴金额")
    effective_date: date = Field(..., description="生效日期")
    created_at: datetime = Field(..., description="创建时间")

    model_config = ConfigDict(from_attributes=True)


class PartyFeeStandardListResponse(BaseModel):
    """党费标准列表响应"""
    standards: List[PartyFeeStandardListItem] = Field(..., description="标准列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")


class PartyFeeStandardDetail(PartyFeeStandardBase):
    """党费标准详情"""
    id: str = Field(..., description="标准ID")
    created_at: datetime = Field(..., description="创建时间")

    model_config = ConfigDict(from_attributes=True)


# ==================== 知识库管理 ====================

class KnowledgeCategoryBase(BaseModel):
    """知识库分类基础信息"""
    name: str = Field(..., description="分类名称", min_length=1, max_length=100)
    code: str = Field(..., description="分类代码", min_length=1, max_length=50)
    description: Optional[str] = Field(None, description="描述", max_length=500)
    order: int = Field(default=0, description="排序")


class KnowledgeCategoryCreate(KnowledgeCategoryBase):
    """创建知识库分类请求"""
    pass


class KnowledgeCategoryUpdate(BaseModel):
    """更新知识库分类请求"""
    name: Optional[str] = Field(None, description="分类名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="描述", max_length=500)
    order: Optional[int] = Field(None, description="排序", ge=0)


class KnowledgeCategoryListItem(BaseModel):
    """知识库分类列表项"""
    id: str = Field(..., description="分类ID")
    name: str = Field(..., description="分类名称")
    code: str = Field(..., description="分类代码")
    description: Optional[str] = Field(None, description="描述")
    order: int = Field(..., description="排序")
    document_count: int = Field(default=0, description="文档数量")
    created_at: datetime = Field(..., description="创建时间")

    model_config = ConfigDict(from_attributes=True)


class KnowledgeCategoryListResponse(BaseModel):
    """知识库分类列表响应"""
    categories: List[KnowledgeCategoryListItem] = Field(..., description="分类列表")
    total: int = Field(..., description="总数")


class KnowledgeCategoryDetail(KnowledgeCategoryBase):
    """知识库分类详情"""
    id: str = Field(..., description="分类ID")
    created_at: datetime = Field(..., description="创建时间")

    model_config = ConfigDict(from_attributes=True)


class KnowledgeDocumentBase(BaseModel):
    """知识库文档基础信息"""
    title: str = Field(..., description="文档标题", min_length=1, max_length=200)
    category: str = Field(..., description="分类代码", min_length=1, max_length=50)
    file_path: Optional[str] = Field(None, description="文件路径", max_length=500)
    file_type: Optional[str] = Field(None, description="文件类型（PDF/Word/TXT）", max_length=20)
    doc_metadata: Optional[str] = Field(None, description="元数据（JSON）- 发布时间、文号、关键词等")
    uploaded_by: Optional[str] = Field(None, description="上传者ID")


class KnowledgeDocumentCreate(KnowledgeDocumentBase):
    """上传文档请求"""
    pass


class KnowledgeDocumentUpdate(BaseModel):
    """更新文档请求"""
    title: Optional[str] = Field(None, description="文档标题", min_length=1, max_length=200)
    category: Optional[str] = Field(None, description="分类代码", max_length=50)
    file_path: Optional[str] = Field(None, description="文件路径", max_length=500)
    file_type: Optional[str] = Field(None, description="文件类型（PDF/Word/TXT）", max_length=20)
    doc_metadata: Optional[str] = Field(None, description="元数据（JSON）")


class KnowledgeDocumentListItem(BaseModel):
    """知识库文档列表项"""
    id: str = Field(..., description="文档ID")
    title: str = Field(..., description="文档标题")
    category: str = Field(..., description="分类代码")
    category_name: Optional[str] = Field(None, description="分类名称")
    file_type: Optional[str] = Field(None, description="文件类型")
    chunk_count: Optional[int] = Field(None, description="分块数量")
    created_at: datetime = Field(..., description="创建时间")

    model_config = ConfigDict(from_attributes=True)


class KnowledgeDocumentListResponse(BaseModel):
    """知识库文档列表响应"""
    documents: List[KnowledgeDocumentListItem] = Field(..., description="文档列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")


class KnowledgeDocumentDetail(KnowledgeDocumentBase):
    """知识库文档详情"""
    id: str = Field(..., description="文档ID")
    chunk_count: Optional[int] = Field(None, description="分块数量")
    vector_collection: Optional[str] = Field(None, description="向量集合名称", max_length=100)
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)


# ==================== 党建问答 ====================

class PartyQARequest(BaseModel):
    """党建问答请求"""
    question: str = Field(..., description="问题内容", min_length=1)
    session_id: Optional[str] = Field(None, description="会话ID（可选，用于多轮对话）")


class PartyQAResponse(BaseModel):
    """党建问答响应"""
    answer: str = Field(..., description="AI回答")
    sources: List[str] = Field(default_factory=list, description="知识库来源")
    session_id: str = Field(..., description="会话ID")


# ==================== 三会一课生成 ====================

class MeetingGenerateRequest(BaseModel):
    """会议文档生成请求"""
    meeting_type: str = Field(..., description="会议类型（支部党员大会/支部委员会/党小组会/党课）")
    theme: str = Field(..., description="会议主题", min_length=1)
    date: str = Field(..., description="会议日期（YYYY-MM-DD）")
    participants: Optional[List[str]] = Field(default_factory=list, description="参会人员")
    additional_requirements: Optional[str] = Field(None, description="额外要求")


class MeetingGenerateResponse(BaseModel):
    """会议文档生成响应"""
    content: str = Field(..., description="生成的会议文档内容（Markdown格式）")
    meeting_type: str = Field(..., description="会议类型")
    theme: str = Field(..., description="会议主题")
