# -*- coding: utf-8 -*-
"""党建活动 API 路由"""
import logging
from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.models_knowledge import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    DocumentCreate, DocumentUploadResponse, DocumentResponse,
    DocumentUpdateRequest,
)
from src.services.party_activity_service import PartyActivityService
from src.database import get_async_db
from src.interfaces.auth import get_current_user
from src.models import UserInfo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/party-activities", tags=["党建活动管理"])


def get_party_activity_service(db: AsyncSession = Depends(get_async_db)) -> PartyActivityService:
    return PartyActivityService(db)


# ==================== 目录管理 ====================

@router.post("/categories", response_model=CategoryResponse, status_code=201)
async def create_category(
    request: CategoryCreate,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    service: PartyActivityService = Depends(get_party_activity_service)
):
    try:
        result = await service.create_category(request.name, request.parent_id)
        return CategoryResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/categories/tree")
async def get_category_tree(
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    service: PartyActivityService = Depends(get_party_activity_service)
):
    tree = await service.get_category_tree()
    return tree


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    request: CategoryUpdate,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    service: PartyActivityService = Depends(get_party_activity_service)
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
    service: PartyActivityService = Depends(get_party_activity_service)
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
    service: PartyActivityService = Depends(get_party_activity_service)
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
    service: PartyActivityService = Depends(get_party_activity_service),
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
    service: PartyActivityService = Depends(get_party_activity_service),
    category_id: Optional[str] = None
):
    documents = await service.get_documents(category_id)
    return documents


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    service: PartyActivityService = Depends(get_party_activity_service)
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
    service: PartyActivityService = Depends(get_party_activity_service)
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
    service: PartyActivityService = Depends(get_party_activity_service)
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
    service: PartyActivityService = Depends(get_party_activity_service)
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
