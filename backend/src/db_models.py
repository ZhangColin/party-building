"""SQLAlchemy ORM 数据模型"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Enum, ForeignKey, Index, Integer, Boolean
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from .database import Base
import enum


class UserModel(Base):
    """用户数据库模型（SQLAlchemy ORM）"""
    __tablename__ = "users"
    
    user_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    nickname = Column(String(50), nullable=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone = Column(String(11), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    avatar = Column(String(500), nullable=True)
    is_admin = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # 关系
    sessions = relationship("SessionModel", back_populates="user", cascade="all, delete-orphan")


class MessageRole(enum.Enum):
    """消息角色枚举"""
    user = "user"
    assistant = "assistant"


class SessionModel(Base):
    """会话数据库模型（SQLAlchemy ORM）"""
    __tablename__ = "sessions"
    
    session_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    tool_id = Column(String(50), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, index=True)
    
    # 关系
    user = relationship("UserModel", back_populates="sessions")
    messages = relationship("MessageModel", back_populates="session", cascade="all, delete-orphan", order_by="MessageModel.created_at")
    
    # 联合索引
    __table_args__ = (
        Index("idx_user_tool", "user_id", "tool_id"),
    )


class MessageModel(Base):
    """消息数据库模型（SQLAlchemy ORM）"""
    __tablename__ = "messages"
    
    message_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(CHAR(36), ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now, index=True)
    
    # 多模态支持字段（新增）
    media_content = Column(Text, nullable=True, comment="多模态内容JSON字符串")
    
    # 关系
    session = relationship("SessionModel", back_populates="messages")
    artifacts = relationship("ArtifactModel", back_populates="message", cascade="all, delete-orphan")


class ArtifactModel(Base):
    """成果物数据库模型（SQLAlchemy ORM）"""
    __tablename__ = "artifacts"
    
    artifact_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(CHAR(36), ForeignKey("messages.message_id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # 关系
    message = relationship("MessageModel", back_populates="artifacts")


class CommonToolType(enum.Enum):
    """常用工具类型枚举"""
    built_in = "built_in"
    html = "html"


class ToolCategoryModel(Base):
    """工具分类数据库模型（SQLAlchemy ORM）"""
    __tablename__ = "tool_categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), nullable=False, unique=True)
    icon = Column(String(50), nullable=True)
    order = Column(Integer, nullable=False, default=0, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    tools = relationship("CommonToolModel", back_populates="category", cascade="all, delete-orphan")


class CommonToolModel(Base):
    """常用工具数据库模型（SQLAlchemy ORM）"""
    __tablename__ = "common_tools"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(String(200), nullable=False)
    category_id = Column(String(36), ForeignKey("tool_categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    type = Column(Enum(CommonToolType), nullable=False)
    icon = Column(String(50), nullable=True)
    html_path = Column(String(255), nullable=True)
    order = Column(Integer, nullable=False, default=0)
    visible = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    category = relationship("ToolCategoryModel", back_populates="tools")
    
    # 联合索引（按分类和排序查询）
    __table_args__ = (
        Index("idx_common_tool_category_order", "category_id", "order"),
    )


class WorkCategoryModel(Base):
    """作品分类数据库模型（SQLAlchemy ORM）"""
    __tablename__ = "work_categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), nullable=False, unique=True)
    icon = Column(String(50), nullable=True)
    order = Column(Integer, nullable=False, default=0, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    works = relationship("WorkModel", back_populates="category", cascade="all, delete-orphan")


class WorkModel(Base):
    """作品数据库模型（SQLAlchemy ORM）"""
    __tablename__ = "works"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(String(200), nullable=False)
    category_id = Column(String(36), ForeignKey("work_categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    icon = Column(String(50), nullable=True)
    html_path = Column(String(255), nullable=False)
    order = Column(Integer, nullable=False, default=0)
    visible = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    category = relationship("WorkCategoryModel", back_populates="works")
    
    # 联合索引（按分类和排序查询）
    __table_args__ = (
        Index("idx_work_category_order", "category_id", "order"),
    )


class CourseCategoryModel(Base):
    """文档目录数据库模型（SQLAlchemy ORM）"""
    __tablename__ = "course_categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    parent_id = Column(String(36), ForeignKey("course_categories.id", ondelete="RESTRICT"), nullable=True, index=True)
    order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    children = relationship("CourseCategoryModel", back_populates="parent", remote_side="CourseCategoryModel.id")
    parent = relationship("CourseCategoryModel", back_populates="children", remote_side="CourseCategoryModel.parent_id")
    documents = relationship("CourseDocumentModel", back_populates="category", cascade="all, delete-orphan")
    
    # 联合索引（按父目录和排序查询）
    __table_args__ = (
        Index("idx_course_category_parent_order", "parent_id", "order"),
    )


class CourseDocumentModel(Base):
    """文档数据库模型（SQLAlchemy ORM）"""
    __tablename__ = "course_documents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    summary = Column(String(500), nullable=False)
    file_path = Column(String(255), nullable=False)
    category_id = Column(String(36), ForeignKey("course_categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    category = relationship("CourseCategoryModel", back_populates="documents")
    
    # 联合索引（按分类和排序查询）
    __table_args__ = (
        Index("idx_course_document_category_order", "category_id", "order"),
    )


# ==================== 党建业务模块 ====================
# 导入党建业务模块模型（用于Alembic迁移检测）
from .db_models_party import (
    PartyMemberModel,
    OrganizationLifeModel,
    PartyFeeModel,
    PartyFeeStandardModel,
    KnowledgeCategoryModel,
    KnowledgeDocumentModel,
)
