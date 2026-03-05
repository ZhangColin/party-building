# -*- coding: utf-8 -*-
"""临时文件路由"""
import logging
from functools import lru_cache
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from src.services.temp_file_service import TempFileService
from src.models.temp_files import TempFileUploadResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@lru_cache
def get_temp_file_service() -> TempFileService:
    """获取临时文件服务实例（单例）"""
    return TempFileService()


@router.post("/upload", response_model=TempFileUploadResponse, tags=["临时文件"])
async def upload_temp_file(
    file: UploadFile = File(...),
    temp_file_service: TempFileService = Depends(get_temp_file_service)
):
    """
    上传临时文件

    用于聊天时从本地上传的文件，消息发送后自动清理
    """
    try:
        # 读取文件内容
        content = await file.read()

        # 保存临时文件
        response = temp_file_service.save_file(content, file.filename)

        logger.info(f"临时文件上传成功: {response.temp_id}, 文件名: {response.filename}")
        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"临时文件上传失败: {e}")
        raise HTTPException(status_code=500, detail="文件上传失败")
