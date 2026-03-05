# -*- coding: utf-8 -*-
"""临时文件相关模型"""
from pydantic import BaseModel


class TempFileUploadResponse(BaseModel):
    """临时文件上传响应"""

    temp_id: str
    filename: str
    size: int
    content_preview: str | None = None


class AttachmentReference(BaseModel):
    """附件引用（用于聊天请求）"""

    id: str  # 临时文件ID或文档ID
    type: str  # 'temp' | 'knowledge' | 'party'
    name: str
