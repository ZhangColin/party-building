# -*- coding: utf-8 -*-
"""常用工具服务：管理常用工具和分类数据"""
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import asc
from ..database import SessionLocal
from ..db_models import ToolCategoryModel, CommonToolModel, CommonToolType
from ..models import (
    CommonToolListItem, 
    ToolCategoryGroup, CommonToolCategoryResponse, CommonToolDetail,
    AdminCommonToolListItem, AdminCommonToolListResponse,
    AdminToolCategoryListItem, AdminToolCategoryListResponse,
    CreateBuiltInToolRequest, UpdateToolRequest,
    CreateToolCategoryRequest, UpdateToolCategoryRequest
)
import uuid
from datetime import datetime


class CommonToolService:
    """常用工具服务类"""
    
    def __init__(self):
        """初始化常用工具服务"""
        pass
    
    def _get_db(self):
        """获取数据库会话"""
        return SessionLocal()
    
    def get_categories_with_tools(self) -> CommonToolCategoryResponse:
        """
        获取所有工具分类及其下的工具列表
        
        Returns:
            CommonToolCategoryResponse: 分类列表响应，包含每个分类及其工具
            
        Notes:
            - 只返回 visible=True 的工具
            - 分类按 order 字段升序排列
            - 每个分类下的工具按 order 字段升序排列
            - 如果某个分类下没有可见工具，则不返回该分类
        """
        db = self._get_db()
        try:
            # 查询所有分类（按order排序）
            categories = db.query(ToolCategoryModel).order_by(asc(ToolCategoryModel.order)).all()
            
            # 构建分类组列表
            category_groups = []
            
            for category in categories:
                # 查询该分类下的可见工具（按order排序）
                tools = db.query(CommonToolModel).filter(
                    CommonToolModel.category_id == category.id,
                    CommonToolModel.visible == True
                ).order_by(asc(CommonToolModel.order)).all()
                
                # 只有该分类下有可见工具时，才添加到结果中
                if tools:
                    tool_items = [
                        CommonToolListItem(
                            id=tool.id,
                            name=tool.name,
                            description=tool.description,
                            type=tool.type.value,  # Enum转字符串
                            icon=tool.icon,
                            order=tool.order
                        )
                        for tool in tools
                    ]
                    
                    category_groups.append(
                        ToolCategoryGroup(
                            id=category.id,
                            name=category.name,
                            icon=category.icon,
                            order=category.order,
                            tools=tool_items
                        )
                    )
            
            return CommonToolCategoryResponse(categories=category_groups)
            
        finally:
            db.close()
    
    def get_tool_detail(self, tool_id: str) -> Optional[CommonToolDetail]:
        """
        获取工具详情
        
        Args:
            tool_id: 工具ID
            
        Returns:
            CommonToolDetail: 工具详情，如果工具不存在或不可见则返回None
            
        Notes:
            - 只能查询 visible=True 的工具
            - HTML工具的 html_path 会被转换为完整的访问URL
        """
        db = self._get_db()
        try:
            # 查询工具及其分类
            tool = db.query(CommonToolModel).filter(
                CommonToolModel.id == tool_id,
                CommonToolModel.visible == True
            ).first()
            
            if not tool:
                return None
            
            # 获取分类信息
            category = db.query(ToolCategoryModel).filter(
                ToolCategoryModel.id == tool.category_id
            ).first()
            
            # 生成HTML访问URL（如果是HTML工具）
            html_url = None
            if tool.type.value == "html" and tool.html_path:
                html_url = f"/static/{tool.html_path}"
            
            return CommonToolDetail(
                id=tool.id,
                name=tool.name,
                description=tool.description,
                category_id=tool.category_id,
                category_name=category.name if category else "未分类",
                type=tool.type.value,  # Enum转字符串
                icon=tool.icon,
                order=tool.order,
                html_url=html_url,
                created_at=tool.created_at
            )
            
        finally:
            db.close()
    
    # ==================== 后台管理方法 ====================
    
    def get_all_tools_admin(
        self,
        page: int = 1,
        page_size: int = 20,
        category_id: Optional[str] = None,
        tool_type: Optional[str] = None,
        visible: Optional[bool] = None
    ) -> AdminCommonToolListResponse:
        """
        获取所有工具列表（管理后台）
        
        Args:
            page: 页码（默认1）
            page_size: 每页数量（默认20，最大100）
            category_id: 按分类ID筛选（可选）
            tool_type: 按类型筛选（'built_in' | 'html'）
            visible: 按可见性筛选（true | false）
            
        Returns:
            AdminCommonToolListResponse: 工具列表响应
        """
        db = self._get_db()
        try:
            # 限制page_size最大值
            page_size = min(page_size, 100)
            
            # 构建查询
            query = db.query(CommonToolModel)
            
            # 应用筛选条件
            if category_id:
                query = query.filter(CommonToolModel.category_id == category_id)
            if tool_type:
                query = query.filter(CommonToolModel.type == CommonToolType[tool_type])
            if visible is not None:
                query = query.filter(CommonToolModel.visible == visible)
            
            # 获取总数
            total = query.count()
            
            # 分页和排序
            tools = query.order_by(
                asc(CommonToolModel.category_id),
                asc(CommonToolModel.order)
            ).offset((page - 1) * page_size).limit(page_size).all()
            
            # 构建响应
            tool_items = []
            for tool in tools:
                # 获取分类名称
                category = db.query(ToolCategoryModel).filter(
                    ToolCategoryModel.id == tool.category_id
                ).first()
                
                tool_items.append(AdminCommonToolListItem(
                    id=tool.id,
                    name=tool.name,
                    description=tool.description,
                    category_id=tool.category_id,
                    category_name=category.name if category else "未分类",
                    type=tool.type.value,
                    icon=tool.icon,
                    html_path=tool.html_path,
                    order=tool.order,
                    visible=tool.visible,
                    created_at=tool.created_at,
                    updated_at=tool.updated_at
                ))
            
            return AdminCommonToolListResponse(
                tools=tool_items,
                total=total,
                page=page,
                page_size=page_size
            )
            
        finally:
            db.close()
    
    def create_built_in_tool(self, request: CreateBuiltInToolRequest) -> AdminCommonToolListItem:
        """
        创建内置工具
        
        Args:
            request: 创建内置工具请求
            
        Returns:
            AdminCommonToolListItem: 新创建的工具信息
            
        Raises:
            ValueError: 分类不存在
        """
        db = self._get_db()
        try:
            # 验证分类是否存在
            category = db.query(ToolCategoryModel).filter(
                ToolCategoryModel.id == request.category_id
            ).first()
            if not category:
                raise ValueError(f"分类不存在: {request.category_id}")
            
            # 创建工具
            tool = CommonToolModel(
                id=str(uuid.uuid4()),
                name=request.name,
                description=request.description,
                category_id=request.category_id,
                type=CommonToolType.built_in,
                icon=request.icon,
                html_path=None,
                order=request.order,
                visible=request.visible,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.add(tool)
            db.commit()
            db.refresh(tool)
            
            return AdminCommonToolListItem(
                id=tool.id,
                name=tool.name,
                description=tool.description,
                category_id=tool.category_id,
                category_name=category.name,
                type=tool.type.value,
                icon=tool.icon,
                html_path=tool.html_path,
                order=tool.order,
                visible=tool.visible,
                created_at=tool.created_at,
                updated_at=tool.updated_at
            )
            
        finally:
            db.close()
    
    def create_html_tool(
        self,
        name: str,
        description: str,
        category_id: str,
        html_path: str,
        icon: Optional[str] = None,
        order: int = 0,
        visible: bool = True
    ) -> AdminCommonToolListItem:
        """
        创建HTML工具
        
        Args:
            name: 工具名称
            description: 工具描述
            category_id: 所属分类ID
            html_path: HTML文件路径（相对于static目录）
            icon: 图标标识
            order: 排序顺序
            visible: 是否可见
            
        Returns:
            AdminCommonToolListItem: 新创建的工具信息
            
        Raises:
            ValueError: 分类不存在
        """
        db = self._get_db()
        try:
            # 验证分类是否存在
            category = db.query(ToolCategoryModel).filter(
                ToolCategoryModel.id == category_id
            ).first()
            if not category:
                raise ValueError(f"分类不存在: {category_id}")
            
            # 创建工具
            tool = CommonToolModel(
                id=str(uuid.uuid4()),
                name=name,
                description=description,
                category_id=category_id,
                type=CommonToolType.html,
                icon=icon,
                html_path=html_path,
                order=order,
                visible=visible,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.add(tool)
            db.commit()
            db.refresh(tool)
            
            return AdminCommonToolListItem(
                id=tool.id,
                name=tool.name,
                description=tool.description,
                category_id=tool.category_id,
                category_name=category.name,
                type=tool.type.value,
                icon=tool.icon,
                html_path=tool.html_path,
                order=tool.order,
                visible=tool.visible,
                created_at=tool.created_at,
                updated_at=tool.updated_at
            )
            
        finally:
            db.close()
    
    def update_tool(self, tool_id: str, request: UpdateToolRequest) -> AdminCommonToolListItem:
        """
        更新工具信息
        
        Args:
            tool_id: 工具ID
            request: 更新工具请求
            
        Returns:
            AdminCommonToolListItem: 更新后的工具信息
            
        Raises:
            ValueError: 工具不存在或分类不存在
        """
        db = self._get_db()
        try:
            # 查询工具
            tool = db.query(CommonToolModel).filter(CommonToolModel.id == tool_id).first()
            if not tool:
                raise ValueError(f"工具不存在: {tool_id}")
            
            # 如果更新分类，验证分类是否存在
            if request.category_id and request.category_id != tool.category_id:
                category = db.query(ToolCategoryModel).filter(
                    ToolCategoryModel.id == request.category_id
                ).first()
                if not category:
                    raise ValueError(f"分类不存在: {request.category_id}")
                tool.category_id = request.category_id
            
            # 更新字段
            if request.name is not None:
                tool.name = request.name
            if request.description is not None:
                tool.description = request.description
            if request.icon is not None:
                tool.icon = request.icon
            if request.order is not None:
                tool.order = request.order
            if request.visible is not None:
                tool.visible = request.visible
            
            tool.updated_at = datetime.now()
            
            db.commit()
            db.refresh(tool)
            
            # 获取分类名称
            category = db.query(ToolCategoryModel).filter(
                ToolCategoryModel.id == tool.category_id
            ).first()
            
            return AdminCommonToolListItem(
                id=tool.id,
                name=tool.name,
                description=tool.description,
                category_id=tool.category_id,
                category_name=category.name if category else "未分类",
                type=tool.type.value,
                icon=tool.icon,
                html_path=tool.html_path,
                order=tool.order,
                visible=tool.visible,
                created_at=tool.created_at,
                updated_at=tool.updated_at
            )
            
        finally:
            db.close()
    
    def delete_tool(self, tool_id: str) -> None:
        """
        删除工具
        
        Args:
            tool_id: 工具ID
            
        Raises:
            ValueError: 工具不存在
            
        Returns:
            html_path: HTML文件路径（如果是HTML工具），用于调用方删除文件
        """
        db = self._get_db()
        try:
            # 查询工具
            tool = db.query(CommonToolModel).filter(CommonToolModel.id == tool_id).first()
            if not tool:
                raise ValueError(f"工具不存在: {tool_id}")
            
            html_path = tool.html_path if tool.type == CommonToolType.html else None
            
            # 删除工具
            db.delete(tool)
            db.commit()
            
            return html_path
            
        finally:
            db.close()
    
    def move_tool_up(self, tool_id: str) -> AdminCommonToolListItem:
        """
        上移工具（与上一个工具交换order值）
        
        Args:
            tool_id: 工具ID
            
        Returns:
            AdminCommonToolListItem: 移动后的工具信息
            
        Raises:
            ValueError: 工具不存在或已经是第一个
        """
        db = self._get_db()
        try:
            # 查询当前工具
            tool = db.query(CommonToolModel).filter(CommonToolModel.id == tool_id).first()
            if not tool:
                raise ValueError(f"工具不存在: {tool_id}")
            
            # 查询同分类下order值更小的第一个工具
            prev_tool = db.query(CommonToolModel).filter(
                CommonToolModel.category_id == tool.category_id,
                CommonToolModel.order < tool.order
            ).order_by(CommonToolModel.order.desc()).first()
            
            if not prev_tool:
                raise ValueError("已经是第一个工具，无法上移")
            
            # 交换order值
            tool.order, prev_tool.order = prev_tool.order, tool.order
            tool.updated_at = datetime.now()
            prev_tool.updated_at = datetime.now()
            
            db.commit()
            db.refresh(tool)
            
            # 获取分类名称
            category = db.query(ToolCategoryModel).filter(
                ToolCategoryModel.id == tool.category_id
            ).first()
            
            return AdminCommonToolListItem(
                id=tool.id,
                name=tool.name,
                description=tool.description,
                category_id=tool.category_id,
                category_name=category.name if category else "未分类",
                type=tool.type.value,
                icon=tool.icon,
                html_path=tool.html_path,
                order=tool.order,
                visible=tool.visible,
                created_at=tool.created_at,
                updated_at=tool.updated_at
            )
            
        finally:
            db.close()
    
    def move_tool_down(self, tool_id: str) -> AdminCommonToolListItem:
        """
        下移工具（与下一个工具交换order值）
        
        Args:
            tool_id: 工具ID
            
        Returns:
            AdminCommonToolListItem: 移动后的工具信息
            
        Raises:
            ValueError: 工具不存在或已经是最后一个
        """
        db = self._get_db()
        try:
            # 查询当前工具
            tool = db.query(CommonToolModel).filter(CommonToolModel.id == tool_id).first()
            if not tool:
                raise ValueError(f"工具不存在: {tool_id}")
            
            # 查询同分类下order值更大的第一个工具
            next_tool = db.query(CommonToolModel).filter(
                CommonToolModel.category_id == tool.category_id,
                CommonToolModel.order > tool.order
            ).order_by(CommonToolModel.order.asc()).first()
            
            if not next_tool:
                raise ValueError("已经是最后一个工具，无法下移")
            
            # 交换order值
            tool.order, next_tool.order = next_tool.order, tool.order
            tool.updated_at = datetime.now()
            next_tool.updated_at = datetime.now()
            
            db.commit()
            db.refresh(tool)
            
            # 获取分类名称
            category = db.query(ToolCategoryModel).filter(
                ToolCategoryModel.id == tool.category_id
            ).first()
            
            return AdminCommonToolListItem(
                id=tool.id,
                name=tool.name,
                description=tool.description,
                category_id=tool.category_id,
                category_name=category.name if category else "未分类",
                type=tool.type.value,
                icon=tool.icon,
                html_path=tool.html_path,
                order=tool.order,
                visible=tool.visible,
                created_at=tool.created_at,
                updated_at=tool.updated_at
            )
            
        finally:
            db.close()
    
    def toggle_tool_visibility(self, tool_id: str) -> Tuple[AdminCommonToolListItem, str]:
        """
        切换工具可见性
        
        Args:
            tool_id: 工具ID
            
        Returns:
            Tuple[AdminCommonToolListItem, str]: (更新后的工具信息, 操作消息)
            
        Raises:
            ValueError: 工具不存在
        """
        db = self._get_db()
        try:
            # 查询工具
            tool = db.query(CommonToolModel).filter(CommonToolModel.id == tool_id).first()
            if not tool:
                raise ValueError(f"工具不存在: {tool_id}")
            
            # 切换可见性
            tool.visible = not tool.visible
            tool.updated_at = datetime.now()
            
            db.commit()
            db.refresh(tool)
            
            # 获取分类名称
            category = db.query(ToolCategoryModel).filter(
                ToolCategoryModel.id == tool.category_id
            ).first()
            
            message = "工具已显示" if tool.visible else "工具已隐藏"
            
            return (
                AdminCommonToolListItem(
                    id=tool.id,
                    name=tool.name,
                    description=tool.description,
                    category_id=tool.category_id,
                    category_name=category.name if category else "未分类",
                    type=tool.type.value,
                    icon=tool.icon,
                    html_path=tool.html_path,
                    order=tool.order,
                    visible=tool.visible,
                    created_at=tool.created_at,
                    updated_at=tool.updated_at
                ),
                message
            )
            
        finally:
            db.close()
    
    # ==================== 工具分类管理方法 ====================
    
    def get_all_categories_admin(self) -> AdminToolCategoryListResponse:
        """
        获取所有工具分类列表（管理后台）
        
        Returns:
            AdminToolCategoryListResponse: 分类列表响应（包含工具数量统计）
        """
        db = self._get_db()
        try:
            # 查询所有分类（按order排序）
            categories = db.query(ToolCategoryModel).order_by(asc(ToolCategoryModel.order)).all()
            
            # 构建分类列表
            category_items = []
            for category in categories:
                # 统计该分类下的工具数量（包括隐藏的工具）
                tool_count = db.query(CommonToolModel).filter(
                    CommonToolModel.category_id == category.id
                ).count()
                
                category_items.append(AdminToolCategoryListItem(
                    id=category.id,
                    name=category.name,
                    icon=category.icon,
                    order=category.order,
                    tool_count=tool_count,
                    created_at=category.created_at,
                    updated_at=category.updated_at
                ))
            
            return AdminToolCategoryListResponse(categories=category_items)
            
        finally:
            db.close()
    
    def create_category(self, request: CreateToolCategoryRequest) -> AdminToolCategoryListItem:
        """
        创建工具分类
        
        Args:
            request: 创建分类请求
            
        Returns:
            AdminToolCategoryListItem: 新创建的分类信息
            
        Raises:
            ValueError: 分类名称已存在
        """
        db = self._get_db()
        try:
            # 检查分类名称是否已存在
            existing = db.query(ToolCategoryModel).filter(
                ToolCategoryModel.name == request.name
            ).first()
            if existing:
                raise ValueError(f"分类名称已存在: {request.name}")
            
            # 创建分类
            category = ToolCategoryModel(
                id=str(uuid.uuid4()),
                name=request.name,
                icon=request.icon,
                order=request.order,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.add(category)
            db.commit()
            db.refresh(category)
            
            return AdminToolCategoryListItem(
                id=category.id,
                name=category.name,
                icon=category.icon,
                order=category.order,
                tool_count=0,
                created_at=category.created_at,
                updated_at=category.updated_at
            )
            
        finally:
            db.close()
    
    def update_category(self, category_id: str, request: UpdateToolCategoryRequest) -> AdminToolCategoryListItem:
        """
        更新工具分类
        
        Args:
            category_id: 分类ID
            request: 更新分类请求
            
        Returns:
            AdminToolCategoryListItem: 更新后的分类信息
            
        Raises:
            ValueError: 分类不存在或分类名称已被使用
        """
        db = self._get_db()
        try:
            # 查询分类
            category = db.query(ToolCategoryModel).filter(
                ToolCategoryModel.id == category_id
            ).first()
            if not category:
                raise ValueError(f"分类不存在: {category_id}")
            
            # 如果更新名称，检查名称是否已被使用
            if request.name and request.name != category.name:
                existing = db.query(ToolCategoryModel).filter(
                    ToolCategoryModel.name == request.name
                ).first()
                if existing:
                    raise ValueError(f"分类名称已被使用: {request.name}")
                category.name = request.name
            
            # 更新其他字段
            if request.icon is not None:
                category.icon = request.icon
            if request.order is not None:
                category.order = request.order
            
            category.updated_at = datetime.now()
            
            db.commit()
            db.refresh(category)
            
            # 统计工具数量
            tool_count = db.query(CommonToolModel).filter(
                CommonToolModel.category_id == category.id
            ).count()
            
            return AdminToolCategoryListItem(
                id=category.id,
                name=category.name,
                icon=category.icon,
                order=category.order,
                tool_count=tool_count,
                created_at=category.created_at,
                updated_at=category.updated_at
            )
            
        finally:
            db.close()
    
    def delete_category(self, category_id: str) -> None:
        """
        删除工具分类
        
        Args:
            category_id: 分类ID
            
        Raises:
            ValueError: 分类不存在或分类下还有工具
        """
        db = self._get_db()
        try:
            # 查询分类
            category = db.query(ToolCategoryModel).filter(
                ToolCategoryModel.id == category_id
            ).first()
            if not category:
                raise ValueError(f"分类不存在: {category_id}")
            
            # 检查分类下是否还有工具
            tool_count = db.query(CommonToolModel).filter(
                CommonToolModel.category_id == category_id
            ).count()
            if tool_count > 0:
                raise ValueError(f"分类下还有{tool_count}个工具，无法删除")
            
            # 删除分类
            db.delete(category)
            db.commit()
            
        finally:
            db.close()
    
    def move_category_up(self, category_id: str) -> AdminToolCategoryListItem:
        """
        上移分类（与上一个分类交换order值）
        
        Args:
            category_id: 分类ID
            
        Returns:
            AdminToolCategoryListItem: 移动后的分类信息
            
        Raises:
            ValueError: 分类不存在或已经是第一个
        """
        db = self._get_db()
        try:
            # 查询当前分类
            category = db.query(ToolCategoryModel).filter(
                ToolCategoryModel.id == category_id
            ).first()
            if not category:
                raise ValueError(f"分类不存在: {category_id}")
            
            # 查询order值更小的第一个分类
            prev_category = db.query(ToolCategoryModel).filter(
                ToolCategoryModel.order < category.order
            ).order_by(ToolCategoryModel.order.desc()).first()
            
            if not prev_category:
                raise ValueError("已经是第一个分类，无法上移")
            
            # 交换order值
            category.order, prev_category.order = prev_category.order, category.order
            category.updated_at = datetime.now()
            prev_category.updated_at = datetime.now()
            
            db.commit()
            db.refresh(category)
            
            # 统计工具数量
            tool_count = db.query(CommonToolModel).filter(
                CommonToolModel.category_id == category.id
            ).count()
            
            return AdminToolCategoryListItem(
                id=category.id,
                name=category.name,
                icon=category.icon,
                order=category.order,
                tool_count=tool_count,
                created_at=category.created_at,
                updated_at=category.updated_at
            )
            
        finally:
            db.close()
    
    def move_category_down(self, category_id: str) -> AdminToolCategoryListItem:
        """
        下移分类（与下一个分类交换order值）
        
        Args:
            category_id: 分类ID
            
        Returns:
            AdminToolCategoryListItem: 移动后的分类信息
            
        Raises:
            ValueError: 分类不存在或已经是最后一个
        """
        db = self._get_db()
        try:
            # 查询当前分类
            category = db.query(ToolCategoryModel).filter(
                ToolCategoryModel.id == category_id
            ).first()
            if not category:
                raise ValueError(f"分类不存在: {category_id}")
            
            # 查询order值更大的第一个分类
            next_category = db.query(ToolCategoryModel).filter(
                ToolCategoryModel.order > category.order
            ).order_by(ToolCategoryModel.order.asc()).first()
            
            if not next_category:
                raise ValueError("已经是最后一个分类，无法下移")
            
            # 交换order值
            category.order, next_category.order = next_category.order, category.order
            category.updated_at = datetime.now()
            next_category.updated_at = datetime.now()
            
            db.commit()
            db.refresh(category)
            
            # 统计工具数量
            tool_count = db.query(CommonToolModel).filter(
                CommonToolModel.category_id == category.id
            ).count()
            
            return AdminToolCategoryListItem(
                id=category.id,
                name=category.name,
                icon=category.icon,
                order=category.order,
                tool_count=tool_count,
                created_at=category.created_at,
                updated_at=category.updated_at
            )
            
        finally:
            db.close()
