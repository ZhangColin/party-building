# -*- coding: utf-8 -*-
"""临时文件相关模型"""
from pydantic import BaseModel, Field
from typing import Literal


class TempFileUploadResponse(BaseModel):
    """临时文件上传响应"""

    temp_id: str = Field(..., description="临时文件唯一标识")
    filename: str = Field(..., description="原始文件名", min_length=1)
    size: int = Field(..., description="文件大小（字节）", ge=0)
    content_preview: str | None = Field(None, description="内容预览（可选）")


class AttachmentReference(BaseModel):
    """附件引用（用于聊天请求）"""

    id: str = Field(..., description="临时文件ID或文档ID")
    type: Literal["temp", "knowledge", "party"] = Field(..., description="附件类型")
    name: str = Field(..., description="附件名称")


class MessageAttachment(BaseModel):
    """消息附件（用于API响应，包含完整信息）"""

    id: str = Field(..., description="附件ID")
    name: str = Field(..., description="附件名称")
    type: Literal["temp", "knowledge", "party"] = Field(..., description="附件类型")
    size: int = Field(..., description="文件大小（字节）", ge=0)
