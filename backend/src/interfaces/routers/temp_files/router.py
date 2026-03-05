# -*- coding: utf-8 -*-
"""临时文件路由"""
import logging
from functools import lru_cache
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from src.services.temp_file_service import TempFileService
from src.models.temp_files import TempFileUploadResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# 允许的文件扩展名白名单
ALLOWED_EXTENSIONS = {
    '.txt', '.md', '.pdf', '.doc', '.docx',
    '.xls', '.xlsx', '.png', '.jpg', '.jpeg'
}


def validate_file_type(filename: str) -> bool:
    """
    验证文件类型是否在允许列表中

    Args:
        filename: 文件名

    Returns:
        bool: 是否为允许的文件类型
    """
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


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

    支持的文件类型：.txt, .md, .pdf, .doc, .docx, .xls, .xlsx, .png, .jpg, .jpeg
    """
    # 验证文件类型（在 try 块之前）
    if not validate_file_type(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型。允许的类型：{', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # 提取纯文件名，防止路径遍历攻击
    safe_filename = Path(file.filename).name

    try:
        # 读取文件内容
        content = await file.read()

        # 保存临时文件（使用安全的文件名）
        response = temp_file_service.save_file(content, safe_filename)

        logger.info(f"临时文件上传成功: {response.temp_id}, 文件名: {response.filename}")
        return response

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        # HTTPException 直接传递
        raise
    except Exception as e:
        logger.error(f"临时文件上传失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="文件上传失败")
