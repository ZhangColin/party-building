# -*- coding: utf-8 -*-
"""知识库 API 路由"""
import logging
from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.models_knowledge import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    DocumentCreate, DocumentUploadResponse, DocumentResponse,
    DocumentUpdateRequest, BatchDocumentRequest, BatchDocumentResponse,
)
from src.services.knowledge_service import KnowledgeService
from src.database import get_async_db
from src.interfaces.auth import get_current_user
from src.models import UserInfo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/knowledge", tags=["知识库管理"])


def get_knowledge_service(db: AsyncSession = Depends(get_async_db)) -> KnowledgeService:
    return KnowledgeService(db)


# ==================== 目录管理 ====================

@router.post("/categories", response_model=CategoryResponse, status_code=201)
async def create_category(
    request: CategoryCreate,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    service: KnowledgeService = Depends(get_knowledge_service)
):
    try:
        result = await service.create_category(request.name, request.parent_id)
        return CategoryResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/categories/tree")
async def get_category_tree(
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    service: KnowledgeService = Depends(get_knowledge_service)
):
    tree = await service.get_category_tree()
    return tree


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    request: CategoryUpdate,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    service: KnowledgeService = Depends(get_knowledge_service)
):
    try:
        result = await service.update_category(category_id, request.name, request.parent_id)
        return CategoryResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="目录不存在")


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: str,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    service: KnowledgeService = Depends(get_knowledge_service)
):
    try:
        await service.delete_category(category_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=404, detail="目录不存在")
    return {"message": "删除成功"}


# ==================== 文件管理 ====================

@router.post("/documents", response_model=DocumentResponse, status_code=201)
async def create_document(
    request: DocumentCreate,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    service: KnowledgeService = Depends(get_knowledge_service)
):
    """新建 Markdown 文件"""
    try:
        result = await service.create_document(
            category_id=request.category_id,
            filename=request.filename,
            content=request.content,
            uploaded_by=current_user.user_id
        )
        return DocumentResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/documents/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_file(
    file: UploadFile,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    service: KnowledgeService = Depends(get_knowledge_service),
    category_id: str = Form(...)
):
    """上传文件"""
    try:
        content = await file.read()
        result = await service.upload_file(
            file_content=content,
            filename=file.filename,
            category_id=category_id,
            uploaded_by=current_user.user_id
        )
        return DocumentUploadResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/documents")
async def get_documents(
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    service: KnowledgeService = Depends(get_knowledge_service),
    category_id: Optional[str] = None
):
    documents = await service.get_documents(category_id)
    return documents


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    service: KnowledgeService = Depends(get_knowledge_service)
):
    try:
        document = await service.get_document(document_id)
        return DocumentResponse(**document)
    except ValueError:
        raise HTTPException(status_code=404, detail="文件不存在")


@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    request: DocumentUpdateRequest,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    service: KnowledgeService = Depends(get_knowledge_service)
):
    try:
        document = await service.update_document(document_id, request.content)
        return DocumentResponse(**document)
    except ValueError:
        raise HTTPException(status_code=400, detail="更新失败")
    except Exception:
        raise HTTPException(status_code=404, detail="文件不存在")


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    service: KnowledgeService = Depends(get_knowledge_service)
):
    try:
        await service.delete_document(document_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="文件不存在")
    return {"message": "删除成功"}


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    service: KnowledgeService = Depends(get_knowledge_service)
):
    """下载文件（Markdown 格式）"""
    try:
        document = await service.get_document(document_id)
        from pathlib import Path
        return FileResponse(
            path=Path(document["markdown_path"]),
            filename=document["original_filename"],
            media_type="text/markdown"
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="文件不存在")


@router.post("/documents/batch", response_model=BatchDocumentResponse, tags=["知识库"])
async def batch_get_documents(
    request: BatchDocumentRequest,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """批量获取文档内容"""
    try:
        documents = await service.batch_get_documents(request.document_ids)
        return BatchDocumentResponse(documents=documents)
    except Exception as e:
        logger.error(f"批量获取文档失败: {e}")
        raise HTTPException(status_code=500, detail="获取文档内容失败")


@router.get("/documents/{document_id}/original")
async def get_original_file(
    document_id: str,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    service: KnowledgeService = Depends(get_knowledge_service)
):
    """获取原文件（用于预览或下载）"""
    try:
        from pathlib import Path
        document = await service.get_document_with_paths(document_id)

        original_path = document.get("original_path")
        if not original_path or not Path(original_path).exists():
            raise HTTPException(status_code=404, detail="原文件不存在")

        # 根据文件扩展名确定媒体类型（用于浏览器预览）
        def get_media_type(filename: str, file_type: str) -> str:
            if file_type == "pdf":
                return "application/pdf"
            elif file_type == "image":
                # 根据扩展名返回正确的图片类型
                ext = Path(filename).suffix.lower()
                mime_types = {
                    ".png": "image/png",
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".gif": "image/gif",
                    ".webp": "image/webp",
                    ".svg": "image/svg+xml"
                }
                return mime_types.get(ext, "image/jpeg")
            elif file_type == "word":
                return "application/msword"
            elif file_type == "excel":
                return "application/vnd.ms-excel"
            elif file_type == "text":
                return "text/plain"
            return "application/octet-stream"

        media_type = get_media_type(document["original_filename"], document.get("file_type", ""))

        # 使用 inline 让浏览器尝试预览而不是下载
        return FileResponse(
            path=Path(original_path),
            filename=document["original_filename"],
            media_type=media_type,
            headers={"Content-Disposition": f"inline; filename=\"{document['original_filename']}\""}
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="文件不存在")
    except HTTPException:
        raise
