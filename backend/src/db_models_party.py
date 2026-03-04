# -*- coding: utf-8 -*-
"""党建业务模块数据库模型（SQLAlchemy ORM）"""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Text, Integer, Numeric, ForeignKey, Index, Date, Boolean
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from .database import Base


class PartyMemberModel(Base):
    """党员信息数据库模型"""
    __tablename__ = "party_members"

    # 主键
    member_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 基本信息
    name = Column(String(50), nullable=False, comment="姓名")
    gender = Column(String(10), nullable=False, comment="性别")
    id_card = Column(String(18), nullable=True, comment="身份证号")
    birth_date = Column(Date, nullable=False, comment="出生日期")
    education = Column(String(20), nullable=True, comment="学历")
    phone = Column(String(20), nullable=True, comment="联系电话")
    email = Column(String(100), nullable=True, comment="邮箱")
    address = Column(String(500), nullable=True, comment="现居住地址")
    work_unit = Column(String(200), nullable=True, comment="工作单位")
    job_title = Column(String(100), nullable=True, comment="职务/职称")

    # 党务信息
    join_date = Column(Date, nullable=False, comment="入党时间")
    party_branch = Column(String(100), nullable=False, comment="所属党支部")
    member_type = Column(String(50), nullable=False, default="正式党员", comment="党员类型（正式党员/预备党员）")
    application_date = Column(Date, nullable=True, comment="入党申请书提交时间")
    activist_date = Column(Date, nullable=True, comment="确定为积极分子时间")
    candidate_date = Column(Date, nullable=True, comment="确定为发展对象时间")
    provisional_date = Column(Date, nullable=True, comment="接收为预备党员时间")
    full_member_date = Column(Date, nullable=True, comment="转正时间")
    party_position = Column(String(100), nullable=True, comment="党内职务")
    introducer_1 = Column(String(50), nullable=True, comment="介绍人1")
    introducer_2 = Column(String(50), nullable=True, comment="介绍人2")

    # 流动党员
    is_mobile = Column(Boolean, nullable=False, default=False, comment="是否流动党员")
    mobile_type = Column(String(20), nullable=True, comment="流动类型（流出/流入）")
    mobile_reason = Column(String(500), nullable=True, comment="流动原因")

    # 党费
    monthly_income = Column(Numeric(10, 2), nullable=True, comment="月收入")
    fee_standard = Column(Numeric(10, 2), nullable=True, comment="党费标准（月缴金额）")

    # 状态
    status = Column(String(20), nullable=False, default="正常", comment="状态（正常/停止党籍/出党等）")

    # 系统字段
    branch_id = Column(CHAR(36), nullable=True, comment="所属支部ID")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    fees = relationship("PartyFeeModel", back_populates="member", cascade="all, delete-orphan")
    fee_standards = relationship("PartyFeeStandardModel", back_populates="member", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index("idx_party_member_name", "name"),
        Index("idx_party_member_branch", "party_branch"),
        Index("idx_party_member_status", "status"),
        Index("idx_party_member_branch_id", "branch_id"),
    )


class OrganizationLifeModel(Base):
    """组织生活记录数据库模型"""
    __tablename__ = "organization_lives"

    # 主键
    life_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 活动基本信息
    activity_type = Column(String(50), nullable=False, comment="活动类型（三会一课/民主评议/主题党日等）")
    meeting_type = Column(String(50), nullable=True, comment="会议类型（支部党员大会/支委会/党小组会/党课）")
    title = Column(String(200), nullable=False, comment="活动主题")
    activity_date = Column(DateTime, nullable=False, comment="活动时间")
    location = Column(String(200), nullable=True, comment="活动地点")

    # 人员信息
    host = Column(String(50), nullable=True, comment="主持人")
    recorder = Column(String(50), nullable=True, comment="记录人")
    expected_count = Column(Integer, nullable=True, comment="应到人数")
    participants_count = Column(Integer, nullable=False, default=0, comment="实到人数")
    absent_members = Column(Text, nullable=True, comment="缺席人员（JSON）")

    # 活动内容
    agenda = Column(Text, nullable=True, comment="会议议程（JSON）")
    content = Column(Text, nullable=True, comment="活动内容摘要")
    resolutions = Column(Text, nullable=True, comment="决议事项")

    # 附件材料
    photos = Column(Text, nullable=True, comment="活动照片（JSON数组）")
    attachments = Column(Text, nullable=True, comment="附件材料（JSON数组）")

    # 组织者
    organizer = Column(String(100), nullable=True, comment="组织者")

    # 系统字段
    branch_id = Column(CHAR(36), nullable=True, comment="所属支部ID")
    created_by = Column(CHAR(36), nullable=True, comment="创建人ID")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 索引
    __table_args__ = (
        Index("idx_org_life_type", "activity_type"),
        Index("idx_org_life_date", "activity_date"),
        Index("idx_org_life_branch_id", "branch_id"),
    )


class PartyFeeModel(Base):
    """党费记录数据库模型"""
    __tablename__ = "party_fees"
    
    fee_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    member_id = Column(CHAR(36), ForeignKey("party_members.member_id", ondelete="SET NULL"), nullable=True, index=True, comment="党员ID")
    member_name = Column(String(50), nullable=False, comment="党员姓名")
    amount = Column(Numeric(10, 2), nullable=False, comment="缴纳金额")
    payment_date = Column(DateTime, nullable=False, comment="缴纳时间")
    payment_method = Column(String(50), nullable=False, default="现金", comment="缴纳方式（现金/微信/支付宝/银行转账）")
    fee_month = Column(String(7), nullable=False, comment="缴费月份（YYYY-MM）")
    status = Column(String(20), nullable=False, default="已缴", comment="状态（已缴/欠缴）")
    remark = Column(String(500), nullable=True, comment="备注")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系
    member = relationship("PartyMemberModel", back_populates="fees")
    
    # 索引
    __table_args__ = (
        Index("idx_party_fee_month", "fee_month"),
        Index("idx_party_fee_status", "status"),
        Index("idx_party_fee_member", "member_id"),
    )


class PartyFeeStandardModel(Base):
    """党费标准数据库模型"""
    __tablename__ = "party_fee_standards"

    # 主键
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 关联党员
    member_id = Column(CHAR(36), ForeignKey("party_members.member_id", ondelete="CASCADE"), nullable=False, index=True, comment="党员ID")

    # 收入和党费标准
    monthly_income = Column(Numeric(10, 2), nullable=False, comment="月收入")
    fee_amount = Column(Numeric(10, 2), nullable=False, comment="应缴金额")
    effective_date = Column(Date, nullable=False, comment="生效日期")

    # 系统字段
    branch_id = Column(CHAR(36), nullable=True, comment="所属支部ID")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")

    # 关系
    member = relationship("PartyMemberModel", back_populates="fee_standards")

    # 索引
    __table_args__ = (
        Index("idx_fee_standard_member", "member_id"),
        Index("idx_fee_standard_effective", "effective_date"),
    )


class KnowledgeCategoryModel(Base):
    """知识库分类数据库模型"""
    __tablename__ = "knowledge_categories"

    # 主键
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 分类信息
    name = Column(String(100), nullable=False, unique=True, comment="分类名称")
    code = Column(String(50), nullable=False, unique=True, comment="分类代码")
    description = Column(String(500), nullable=True, comment="描述")
    order = Column(Integer, nullable=False, default=0, comment="排序")

    # 系统字段
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")

    # 关系
    documents = relationship("KnowledgeDocumentModel", back_populates="category", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index("idx_knowledge_category_code", "code"),
        Index("idx_knowledge_category_order", "order"),
    )


class KnowledgeDocumentModel(Base):
    """知识库文档数据库模型"""
    __tablename__ = "knowledge_documents"

    # 主键
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 文档基本信息
    title = Column(String(200), nullable=False, comment="文档标题")
    category = Column(String(50), nullable=False, comment="分类代码")

    # 文件信息
    file_path = Column(String(500), nullable=True, comment="文件路径")
    file_type = Column(String(20), nullable=True, comment="文件类型（PDF/Word/TXT）")

    # 向量化信息
    chunk_count = Column(Integer, nullable=True, comment="分块数量")
    vector_collection = Column(String(100), nullable=True, comment="向量集合名称")

    # 元数据
    doc_metadata = Column(Text, nullable=True, comment="元数据（JSON）- 发布时间、文号、关键词等")

    # 系统字段
    uploaded_by = Column(CHAR(36), nullable=True, comment="上传者ID")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    category_rel = relationship("KnowledgeCategoryModel", back_populates="documents", foreign_keys=[category], primaryjoin="KnowledgeDocumentModel.category == KnowledgeCategoryModel.code")

    # 索引
    __table_args__ = (
        Index("idx_knowledge_doc_category", "category"),
        Index("idx_knowledge_doc_title", "title"),
        Index("idx_knowledge_doc_type", "file_type"),
    )
