# -*- coding: utf-8 -*-
"""知识库 API 数据模型"""
from pydantic import BaseModel, Field
from typing import Optional, List


class CategoryCreate(BaseModel):
    """创建目录请求"""
    name: str = Field(..., min_length=1, max_length=100)
    parent_id: Optional[str] = None


class CategoryUpdate(BaseModel):
    """更新目录请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    parent_id: Optional[str] = None


class CategoryResponse(BaseModel):
    """目录响应"""
    id: str
    name: str
    parent_id: Optional[str]
    order: int
    created_at: str
    updated_at: str


class CategoryTreeResponse(BaseModel):
    """目录树响应"""
    id: str
    name: str
    parent_id: Optional[str]
    children: List['CategoryTreeResponse'] = []


CategoryTreeResponse.model_rebuild()


class DocumentCreate(BaseModel):
    """创建文档请求"""
    category_id: str
    filename: str
    content: str


class DocumentUploadResponse(BaseModel):
    """文件上传响应"""
    id: str
    category_id: str
    filename: str
    original_filename: str
    file_type: str


class DocumentResponse(BaseModel):
    """文件响应"""
    id: str
    category_id: str
    filename: str
    original_filename: str
    file_type: str
    content: Optional[str] = None
    created_at: str
    updated_at: str


class DocumentUpdateRequest(BaseModel):
    """更新文件内容请求"""
    content: str


class BatchDocumentRequest(BaseModel):
    """批量获取文档请求"""
    document_ids: List[str]


class BatchDocumentResponse(BaseModel):
    """批量获取文档响应"""
    documents: List[dict]
