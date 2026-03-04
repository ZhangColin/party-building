# -*- coding: utf-8 -*-
"""
统一错误处理中间件

提供全局异常捕获和统一格式的错误响应
"""
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ApplicationException(Exception):
    """
    应用异常基类

    所有业务异常都应该继承此类
    """
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}

        super().__init__(self.message)


class NotFoundException(ApplicationException):
    """资源未找到异常"""
    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class ForbiddenException(ApplicationException):
    """权限不足异常"""
    def __init__(
        self,
        message: str = "Access forbidden",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class BadRequestException(ApplicationException):
    """错误请求异常"""
    def __init__(
        self,
        message: str = "Bad request",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="BAD_REQUEST",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class UnauthorizedException(ApplicationException):
    """未认证异常"""
    def __init__(
        self,
        message: str = "Authentication required",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


async def error_handler(request: Request, call_next):
    """
    全局错误处理中间件

    捕获所有异常并返回统一格式的错误响应
    """
    try:
        response = await call_next(request)
        return response

    except ApplicationException as e:
        # 应用异常
        logger.warning(f"Application error: {e.code} - {e.message}")

        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "details": e.details,
                    "path": str(request.url)
                }
            }
        )

    except Exception as e:
        # 未捕获的异常
        logger.exception(f"Unexpected error: {str(e)}")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "path": str(request.url)
                }
            }
        )
