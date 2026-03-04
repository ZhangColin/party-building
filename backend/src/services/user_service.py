# -*- coding: utf-8 -*-
"""用户服务：管理用户数据"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from ..database import SessionLocal
from ..db_models import UserModel
from ..models import User


class UserService:
    """用户服务类"""
    
    def __init__(self):
        """初始化用户服务"""
        pass
    
    def _get_db(self):
        """获取数据库会话"""
        return SessionLocal()
    
    def create_user(self, username: str, password: str, nickname: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None, avatar: Optional[str] = None, is_admin: bool = False) -> User:
        """
        创建新用户
        
        Args:
            username: 用户名（必填，必须唯一）
            password: 用户密码（明文）
            nickname: 用户昵称（可选，用于显示）
            email: 用户邮箱（可选，用于登录）
            phone: 用户手机号（可选，用于登录）
            avatar: 用户头像URL（可选）
            is_admin: 是否为管理员（默认为false）
            
        Returns:
            User: 创建的用户实体
            
        Raises:
            ValueError: 用户名、邮箱或手机号已存在
        """
        # 使用User.create方法创建用户实体（密码自动加密）
        user_entity = User.create(username=username, password=password, nickname=nickname, email=email, phone=phone, avatar=avatar, is_admin=is_admin)
        
        db = self._get_db()
        try:
            # 转换为SQLAlchemy模型
            user_model = UserModel(
                user_id=user_entity.user_id,
                username=user_entity.username,
                nickname=user_entity.nickname,
                email=user_entity.email,
                phone=user_entity.phone,
                password_hash=user_entity.password_hash,
                avatar=user_entity.avatar,
                is_admin=user_entity.is_admin,
                created_at=user_entity.created_at
            )
            
            db.add(user_model)
            db.commit()
            db.refresh(user_model)
            
            # 转换回User实体
            return User(
                user_id=user_model.user_id,
                username=user_model.username,
                nickname=user_model.nickname,
                email=user_model.email,
                phone=user_model.phone,
                password_hash=user_model.password_hash,
                avatar=user_model.avatar,
                is_admin=user_model.is_admin,
                created_at=user_model.created_at
            )
        except IntegrityError as e:
            db.rollback()
            # 判断是用户名、邮箱还是手机号冲突
            if db.query(UserModel).filter(UserModel.username == username).first():
                raise ValueError("用户名已存在")
            if email and db.query(UserModel).filter(UserModel.email == email).first():
                raise ValueError("邮箱已存在")
            if phone and db.query(UserModel).filter(UserModel.phone == phone).first():
                raise ValueError("手机号已存在")
            raise ValueError("创建用户失败")
        finally:
            db.close()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        
        Args:
            email: 用户邮箱
            
        Returns:
            User: 用户实体，如果不存在返回None
        """
        db = self._get_db()
        try:
            user_model = db.query(UserModel).filter(UserModel.email == email).first()
            if user_model is None:
                return None
            
            return User(
                user_id=user_model.user_id,
                username=user_model.username,
                nickname=user_model.nickname,
                email=user_model.email,
                phone=user_model.phone,
                password_hash=user_model.password_hash,
                avatar=user_model.avatar,
                is_admin=user_model.is_admin,
                created_at=user_model.created_at
            )
        finally:
            db.close()
    
    def get_user_by_phone(self, phone: str) -> Optional[User]:
        """
        根据手机号获取用户
        
        Args:
            phone: 用户手机号
            
        Returns:
            User: 用户实体，如果不存在返回None
        """
        db = self._get_db()
        try:
            user_model = db.query(UserModel).filter(UserModel.phone == phone).first()
            if user_model is None:
                return None
            
            return User(
                user_id=user_model.user_id,
                username=user_model.username,
                nickname=user_model.nickname,
                email=user_model.email,
                phone=user_model.phone,
                password_hash=user_model.password_hash,
                avatar=user_model.avatar,
                is_admin=user_model.is_admin,
                created_at=user_model.created_at
            )
        finally:
            db.close()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            User: 用户实体，如果不存在返回None
        """
        db = self._get_db()
        try:
            user_model = db.query(UserModel).filter(UserModel.username == username).first()
            if user_model is None:
                return None
            
            return User(
                user_id=user_model.user_id,
                username=user_model.username,
                nickname=user_model.nickname,
                email=user_model.email,
                phone=user_model.phone,
                password_hash=user_model.password_hash,
                avatar=user_model.avatar,
                is_admin=user_model.is_admin,
                created_at=user_model.created_at
            )
        finally:
            db.close()
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        根据用户ID获取用户
        
        Args:
            user_id: 用户ID（UUID）
            
        Returns:
            User: 用户实体，如果不存在返回None
        """
        db = self._get_db()
        try:
            user_model = db.query(UserModel).filter(UserModel.user_id == user_id).first()
            if user_model is None:
                return None
            
            return User(
                user_id=user_model.user_id,
                username=user_model.username,
                nickname=user_model.nickname,
                email=user_model.email,
                phone=user_model.phone,
                password_hash=user_model.password_hash,
                avatar=user_model.avatar,
                is_admin=user_model.is_admin,
                created_at=user_model.created_at
            )
        finally:
            db.close()
    
    def get_all_users(self, page: int = 1, page_size: int = 20, is_admin: Optional[bool] = None) -> Tuple[List[User], int]:
        """
        获取所有用户列表（支持分页和筛选）
        
        Args:
            page: 页码（从1开始）
            page_size: 每页数量
            is_admin: 筛选管理员（true: 仅管理员，false: 仅普通用户，None: 全部）
            
        Returns:
            Tuple[List[User], int]: (用户列表, 总数)
        """
        db = self._get_db()
        try:
            # 计算偏移量
            offset = (page - 1) * page_size
            
            # 构建查询
            query = db.query(UserModel)
            
            # 筛选管理员
            if is_admin is not None:
                query = query.filter(UserModel.is_admin == is_admin)
            
            # 获取总数
            total = query.count()
            
            # 获取分页数据（按创建时间倒序）
            user_models = query.order_by(desc(UserModel.created_at)).offset(offset).limit(page_size).all()
            
            # 转换为User实体列表
            users = [
                User(
                    user_id=user_model.user_id,
                    username=user_model.username,
                    nickname=user_model.nickname,
                    email=user_model.email,
                    phone=user_model.phone,
                    password_hash=user_model.password_hash,
                    avatar=user_model.avatar,
                    is_admin=user_model.is_admin,
                    created_at=user_model.created_at
                )
                for user_model in user_models
            ]
            
            return users, total
        finally:
            db.close()
    
    def update_user(
        self, 
        user_id: str, 
        username: Optional[str] = None,
        nickname: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        is_admin: Optional[bool] = None
    ) -> Optional[User]:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            username: 用户名（可选）
            nickname: 用户昵称（可选）
            email: 用户邮箱（可选）
            phone: 用户手机号（可选）
            is_admin: 是否为管理员（可选）
            
        Returns:
            User: 更新后的用户实体，如果用户不存在返回None
            
        Raises:
            ValueError: 业务规则错误（用户名/邮箱/手机号冲突，取消最后一个管理员）
        """
        db = self._get_db()
        try:
            # 查询用户
            user_model = db.query(UserModel).filter(UserModel.user_id == user_id).first()
            if user_model is None:
                return None
            
            # 检查是否尝试取消最后一个管理员
            if is_admin is not None and not is_admin and user_model.is_admin:
                # 查询管理员总数
                admin_count = db.query(UserModel).filter(UserModel.is_admin == True).count()
                if admin_count <= 1:
                    raise ValueError("不允许取消最后一个管理员的管理员权限")
            
            # 检查用户名冲突
            if username is not None and username != user_model.username:
                existing = db.query(UserModel).filter(UserModel.username == username).first()
                if existing:
                    raise ValueError("用户名已被其他用户使用")
            
            # 检查邮箱冲突
            if email is not None and email != user_model.email:
                existing = db.query(UserModel).filter(UserModel.email == email).first()
                if existing:
                    raise ValueError("邮箱已被其他用户使用")
            
            # 检查手机号冲突
            if phone is not None and phone != user_model.phone:
                existing = db.query(UserModel).filter(UserModel.phone == phone).first()
                if existing:
                    raise ValueError("手机号已被其他用户使用")
            
            # 更新字段
            if username is not None:
                user_model.username = username
            if nickname is not None:
                user_model.nickname = nickname
            if email is not None:
                user_model.email = email
            if phone is not None:
                user_model.phone = phone
            if is_admin is not None:
                user_model.is_admin = is_admin
            
            db.commit()
            db.refresh(user_model)
            
            # 转换回User实体
            return User(
                user_id=user_model.user_id,
                username=user_model.username,
                nickname=user_model.nickname,
                email=user_model.email,
                phone=user_model.phone,
                password_hash=user_model.password_hash,
                avatar=user_model.avatar,
                is_admin=user_model.is_admin,
                created_at=user_model.created_at
            )
        except IntegrityError:
            db.rollback()
            raise ValueError("更新用户失败：数据冲突")
        finally:
            db.close()
    
    def delete_user(self, user_id: str, current_user_id: str) -> bool:
        """
        删除用户
        
        Args:
            user_id: 要删除的用户ID
            current_user_id: 当前操作的用户ID
            
        Returns:
            bool: 是否删除成功（如果用户不存在返回False）
            
        Raises:
            ValueError: 业务规则错误（删除自己，删除最后一个管理员）
        """
        db = self._get_db()
        try:
            # 检查是否删除自己
            if user_id == current_user_id:
                raise ValueError("不允许删除自己")
            
            # 查询用户
            user_model = db.query(UserModel).filter(UserModel.user_id == user_id).first()
            if user_model is None:
                return False
            
            # 检查是否删除最后一个管理员
            if user_model.is_admin:
                admin_count = db.query(UserModel).filter(UserModel.is_admin == True).count()
                if admin_count <= 1:
                    raise ValueError("不允许删除最后一个管理员")
            
            # 删除用户（会级联删除关联数据）
            db.delete(user_model)
            db.commit()
            
            return True
        finally:
            db.close()
    
    def reset_password(self, user_id: str, new_password: str) -> bool:
        """
        重置用户密码
        
        Args:
            user_id: 用户ID
            new_password: 新密码（明文）
            
        Returns:
            bool: 是否重置成功（如果用户不存在返回False）
            
        Raises:
            ValueError: 密码格式错误
        """
        if len(new_password) < 6:
            raise ValueError("密码长度不能少于6位")
        
        db = self._get_db()
        try:
            # 查询用户
            user_model = db.query(UserModel).filter(UserModel.user_id == user_id).first()
            if user_model is None:
                return False
            
            # 使用User实体的密码加密方法
            user_entity = User(
                user_id=user_model.user_id,
                username=user_model.username,
                nickname=user_model.nickname,
                email=user_model.email,
                phone=user_model.phone,
                password_hash="",  # 临时值
                avatar=user_model.avatar,
                is_admin=user_model.is_admin,
                created_at=user_model.created_at
            )
            new_password_hash = user_entity._hash_password(new_password)
            
            # 更新密码
            user_model.password_hash = new_password_hash
            db.commit()
            
            return True
        finally:
            db.close()

