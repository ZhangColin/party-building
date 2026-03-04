"""认证服务：JWT Token生成和验证"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import jwt, JWTError
from ..models import User


logger = logging.getLogger(__name__)


class AuthService:
    """认证服务类"""

    def __init__(self):
        """初始化认证服务"""
        # 从环境变量获取JWT密钥
        self.secret_key = os.getenv("JWT_SECRET_KEY")

        # 严格验证：生产环境必须设置密钥
        if not self.secret_key:
            raise RuntimeError(
                "JWT_SECRET_KEY environment variable is required.\n"
                "请设置环境变量 JWT_SECRET_KEY。\n"
                "生成方法: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )

        # 验证密钥强度（至少32字节）
        if len(self.secret_key) < 32:
            raise ValueError(
                f"JWT_SECRET_KEY must be at least 32 characters long. "
                f"Current length: {len(self.secret_key)}"
            )

        self.algorithm = "HS256"
    
    def generate_token(self, user: User, remember_me: bool = False) -> str:
        """
        生成JWT Token
        
        Args:
            user: 用户实体
            remember_me: 是否记住我（影响Token有效期）
            
        Returns:
            str: JWT Token字符串
        """
        # 根据remember_me决定Token有效期
        if remember_me:
            expires_in = timedelta(days=7)  # 7天
        else:
            expires_in = timedelta(hours=24)  # 24小时
        
        # 计算过期时间
        now = datetime.utcnow()
        exp = now + expires_in
        
        # 构建Token Payload
        payload = {
            "user_id": user.user_id,
            "exp": int(exp.timestamp()),  # 过期时间戳（Unix timestamp）
            "iat": int(now.timestamp())    # 签发时间戳（Unix timestamp）
        }
        
        # 生成Token
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        验证JWT Token

        Args:
            token: JWT Token字符串

        Returns:
            Dict: Token Payload（包含user_id, exp, iat），如果Token无效或过期返回None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            # Token无效或过期
            return None
    
    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """
        从Token中获取用户ID
        
        Args:
            token: JWT Token字符串
            
        Returns:
            str: 用户ID，如果Token无效返回None
        """
        payload = self.verify_token(token)
        if payload is None:
            return None
        return payload.get("user_id")

