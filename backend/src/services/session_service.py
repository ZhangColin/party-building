# -*- coding: utf-8 -*-
"""会话服务：管理会话和消息"""
import uuid
from datetime import datetime
from typing import List, Optional
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models import Session as SessionDomain, Message as MessageDomain
from ..db_models import SessionModel, MessageModel, MessageRole


class SessionService:
    """会话管理服务"""
    
    def __init__(self):
        """初始化会话服务"""
        # 使用数据库的 get_db 函数
        from ..database import get_db
        self._get_db = get_db
    
    @contextmanager
    def _get_db_session(self):
        """
        获取数据库会话的上下文管理器
        确保数据库连接正确释放
        """
        db_gen = self._get_db()
        db = next(db_gen)
        try:
            yield db
        finally:
            try:
                next(db_gen, None)  # 触发生成器的 finally 块
            except StopIteration:
                pass
    
    def create_session(
        self, 
        user_id: str, 
        tool_id: str, 
        title: Optional[str] = None,
        first_message: Optional[str] = None
    ) -> SessionDomain:
        """
        创建新会话
        
        Args:
            user_id: 用户ID
            tool_id: 工具ID
            title: 会话标题（可选，如果不提供则基于 first_message 生成）
            first_message: 第一条用户消息（可选，用于自动生成标题）
            
        Returns:
            Session 领域模型实例
        """
        with self._get_db_session() as db:
            # 生成会话ID
            session_id = str(uuid.uuid4())
            
            # 生成标题
            if title is None:
                if first_message:
                    # 创建临时 Session 对象用于生成标题
                    temp_session = SessionDomain(
                        session_id=session_id,
                        user_id=user_id,
                        tool_id=tool_id,
                        title=""
                    )
                    title = temp_session.generate_title(first_message)
                else:
                    title = "新对话"
            
            # 创建数据库模型
            session_model = SessionModel(
                session_id=session_id,
                user_id=user_id,
                tool_id=tool_id,
                title=title,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.add(session_model)
            db.commit()
            db.refresh(session_model)
            
            # 转换为领域模型
            return self._to_domain_model(session_model)
    
    def get_session_by_id(self, session_id: str, user_id: Optional[str] = None) -> Optional[SessionDomain]:
        """
        根据ID获取会话
        
        Args:
            session_id: 会话ID
            user_id: 用户ID（可选，如果提供则验证会话是否属于该用户）
            
        Returns:
            Session 领域模型实例，如果不存在或不属于用户则返回 None
        """
        with self._get_db_session() as db:
            query = db.query(SessionModel).filter(SessionModel.session_id == session_id)
            
            if user_id:
                query = query.filter(SessionModel.user_id == user_id)
            
            session_model = query.first()
            
            if not session_model:
                return None
            
            return self._to_domain_model(session_model)
    
    def get_sessions_by_user_and_tool(
        self, 
        user_id: str, 
        tool_id: str
    ) -> List[SessionDomain]:
        """
        获取用户在某工具下的所有会话，按更新时间倒序
        
        Args:
            user_id: 用户ID
            tool_id: 工具ID
            
        Returns:
            会话列表（按 updated_at 倒序）
        """
        with self._get_db_session() as db:
            session_models = db.query(SessionModel).filter(
                SessionModel.user_id == user_id,
                SessionModel.tool_id == tool_id
            ).order_by(desc(SessionModel.updated_at)).all()
            
            return [self._to_domain_model(sm) for sm in session_models]
    
    def update_session_title(self, session_id: str, new_title: str, user_id: Optional[str] = None) -> Optional[SessionDomain]:
        """
        更新会话标题
        
        Args:
            session_id: 会话ID
            new_title: 新标题
            user_id: 用户ID（可选，如果提供则验证会话是否属于该用户）
            
        Returns:
            更新后的 Session 领域模型实例，如果不存在或不属于用户则返回 None
        """
        with self._get_db_session() as db:
            query = db.query(SessionModel).filter(SessionModel.session_id == session_id)
            
            if user_id:
                query = query.filter(SessionModel.user_id == user_id)
            
            session_model = query.first()
            
            if not session_model:
                return None
            
            # 更新标题和时间戳
            session_model.title = new_title
            session_model.updated_at = datetime.now()
            
            db.commit()
            db.refresh(session_model)
            
            return self._to_domain_model(session_model)
    
    def delete_session(self, session_id: str, user_id: Optional[str] = None) -> bool:
        """
        删除会话（级联删除消息和成果物）
        
        Args:
            session_id: 会话ID
            user_id: 用户ID（可选，如果提供则验证会话是否属于该用户）
            
        Returns:
            是否删除成功
        """
        with self._get_db_session() as db:
            query = db.query(SessionModel).filter(SessionModel.session_id == session_id)
            
            if user_id:
                query = query.filter(SessionModel.user_id == user_id)
            
            session_model = query.first()
            
            if not session_model:
                return False
            
            db.delete(session_model)
            db.commit()
            
            return True
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        user_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        attachments: Optional[List[dict]] = None
    ) -> MessageDomain:
        """
        添加消息到会话

        Args:
            session_id: 会话ID
            role: 消息角色（'user' 或 'assistant'）
            content: 消息内容
            user_id: 用户ID（可选，如果提供则验证会话是否属于该用户）
            created_at: 消息创建时间（可选，如果不提供则使用当前时间）
            attachments: 附件列表（可选，格式：[{"id": "...", "name": "...", "type": "temp|knowledge|party", "size": 123}]）

        Returns:
            Message 领域模型实例
        """
        import json

        with self._get_db_session() as db:
            # 验证会话存在且属于用户
            query = db.query(SessionModel).filter(SessionModel.session_id == session_id)
            if user_id:
                query = query.filter(SessionModel.user_id == user_id)

            session_model = query.first()
            if not session_model:
                raise ValueError(f"Session '{session_id}' not found")

            # 创建消息（使用传入的时间或当前时间）
            message_time = created_at if created_at is not None else datetime.now()
            message_id = str(uuid.uuid4())
            message_model = MessageModel(
                message_id=message_id,
                session_id=session_id,
                role=MessageRole(role),
                content=content,
                created_at=message_time
            )

            # 保存附件信息为 JSON 字符串
            if attachments and len(attachments) > 0:
                message_model.attachments = json.dumps(attachments, ensure_ascii=False)

            db.add(message_model)

            # 更新会话的 updated_at
            session_model.updated_at = datetime.now()

            db.commit()
            db.refresh(message_model)

            # 转换为领域模型
            return self._to_domain_model_message(message_model)
    
    def get_messages_by_session(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> List[MessageDomain]:
        """
        获取会话的所有消息，按创建时间正序
        
        Args:
            session_id: 会话ID
            user_id: 用户ID（可选，如果提供则验证会话是否属于该用户）
            
        Returns:
            消息列表（按 created_at 正序）
        """
        with self._get_db_session() as db:
            # 验证会话存在且属于用户
            query = db.query(SessionModel).filter(SessionModel.session_id == session_id)
            if user_id:
                query = query.filter(SessionModel.user_id == user_id)
            
            session_model = query.first()
            if not session_model:
                return []
            
            # 获取消息
            message_models = db.query(MessageModel).filter(
                MessageModel.session_id == session_id
            ).order_by(MessageModel.created_at).all()
            
            return [self._to_domain_model_message(mm) for mm in message_models]

    # 别名方法：为了保持API一致性，提供 get_session_messages 别名
    def get_session_messages(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> List[MessageDomain]:
        """
        获取会话的所有消息（别名方法）

        这是 get_messages_by_session 的别名，用于保持API命名一致性。
        详见 get_messages_by_session 的文档。
        """
        return self.get_messages_by_session(session_id, user_id)

    def _to_domain_model(self, session_model: SessionModel) -> SessionDomain:
        """将数据库模型转换为领域模型"""
        return SessionDomain(
            session_id=session_model.session_id,
            user_id=session_model.user_id,
            tool_id=session_model.tool_id,
            title=session_model.title,
            created_at=session_model.created_at,
            updated_at=session_model.updated_at
        )
    
    def _to_domain_model_message(self, message_model: MessageModel) -> MessageDomain:
        """将数据库模型转换为领域模型"""
        import json
        from ..models.temp_files import MessageAttachment

        # 恢复附件信息
        attachments = None
        if hasattr(message_model, 'attachments') and message_model.attachments:
            try:
                attachments_data = json.loads(message_model.attachments)
                attachments = [MessageAttachment(**a) for a in attachments_data]
            except Exception as e:
                from ..config_loader import logger
                logger.warning(f"解析附件信息失败: {e}")

        return MessageDomain(
            message_id=message_model.message_id,
            session_id=message_model.session_id,
            role=message_model.role.value,
            content=message_model.content,
            created_at=message_model.created_at,
            timestamp=message_model.created_at,  # 兼容前端
            artifacts=[],  # 成果物需要单独查询
            media_content=getattr(message_model, 'media_content', None),  # 多模态内容
            attachments=attachments  # 附件信息
        )
    
    # ==================== 多模态支持方法 ====================
    
    async def create_session_with_id(
        self, 
        session_id: str,
        user_id: str, 
        tool_id: str, 
        title: str
    ) -> SessionDomain:
        """
        创建新会话（异步版本，指定 session_id）
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
            tool_id: 工具ID
            title: 会话标题
            
        Returns:
            Session 领域模型实例
        """
        with self._get_db_session() as db:
            # 创建数据库模型
            session_model = SessionModel(
                session_id=session_id,
                user_id=user_id,
                tool_id=tool_id,
                title=title,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.add(session_model)
            db.commit()
            db.refresh(session_model)
            
            return self._to_domain_model(session_model)
    
    async def get_session(self, session_id: str) -> Optional[SessionDomain]:
        """
        获取会话（异步版本，简化接口）
        
        Args:
            session_id: 会话ID
            
        Returns:
            Session 领域模型实例
        """
        return self.get_session_by_id(session_id)
    
    async def save_message(
        self,
        message_id: str,
        session_id: str,
        role: str,
        content: str
    ) -> MessageDomain:
        """
        保存消息（文本消息）
        
        Args:
            message_id: 消息ID
            session_id: 会话ID
            role: 角色（user/assistant）
            content: 消息内容
            
        Returns:
            Message 领域模型实例
        """
        with self._get_db_session() as db:
            # 创建消息模型
            message_model = MessageModel(
                message_id=message_id,
                session_id=session_id,
                role=MessageRole(role),
                content=content,
                created_at=datetime.now()
            )
            
            db.add(message_model)
            db.commit()
            db.refresh(message_model)
            
            # 更新会话的updated_at
            session_model = db.query(SessionModel).filter(
                SessionModel.session_id == session_id
            ).first()
            if session_model:
                session_model.updated_at = datetime.now()
                db.commit()
            
            return self._to_domain_model_message(message_model)
    
    async def save_message_with_media(
        self,
        message_id: str,
        session_id: str,
        role: str,
        content: str,
        media_content: str
    ) -> MessageDomain:
        """
        保存多模态消息
        
        Args:
            message_id: 消息ID
            session_id: 会话ID
            role: 角色（user/assistant）
            content: 文本内容（可为空）
            media_content: 多模态内容JSON字符串
            
        Returns:
            Message 领域模型实例
        """
        with self._get_db_session() as db:
            # 创建消息模型
            message_model = MessageModel(
                message_id=message_id,
                session_id=session_id,
                role=MessageRole(role),
                content=content,
                created_at=datetime.now()
            )
            
            # 设置多模态内容
            message_model.media_content = media_content
            
            db.add(message_model)
            db.commit()
            db.refresh(message_model)
            
            # 更新会话的updated_at
            session_model = db.query(SessionModel).filter(
                SessionModel.session_id == session_id
            ).first()
            if session_model:
                session_model.updated_at = datetime.now()
                db.commit()
            
            return self._to_domain_model_message(message_model)
