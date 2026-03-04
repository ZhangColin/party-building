# -*- coding: utf-8 -*-
"""作品展示服务：管理作品和分类数据"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import asc
from ..database import SessionLocal
from ..db_models import WorkCategoryModel, WorkModel
from ..models import (
    WorkListItem, 
    WorkCategoryGroup, WorkCategoryResponse, WorkDetail,
    AdminWorkListItem, AdminWorkListResponse,
    UpdateWorkRequest,
    AdminWorkCategoryListItem, AdminWorkCategoryListResponse,
    CreateWorkCategoryRequest, UpdateWorkCategoryRequest
)
import uuid
from datetime import datetime


class WorkService:
    """作品展示服务类"""
    
    def __init__(self):
        """初始化作品展示服务"""
        pass
    
    def _get_db(self):
        """获取数据库会话"""
        return SessionLocal()
    
    def get_categories_with_works(self) -> WorkCategoryResponse:
        """
        获取所有作品分类及其下的作品列表
        
        Returns:
            WorkCategoryResponse: 分类列表响应，包含每个分类及其作品
            
        Notes:
            - 只返回 visible=True 的作品
            - 分类按 order 字段升序排列
            - 每个分类下的作品按 order 字段升序排列
            - 如果某个分类下没有可见作品，则不返回该分类
        """
        db = self._get_db()
        try:
            # 查询所有分类（按order排序）
            categories = db.query(WorkCategoryModel).order_by(asc(WorkCategoryModel.order)).all()
            
            # 构建分类组列表
            category_groups = []
            
            for category in categories:
                # 查询该分类下的可见作品（按order排序）
                works = db.query(WorkModel).filter(
                    WorkModel.category_id == category.id,
                    WorkModel.visible == True
                ).order_by(asc(WorkModel.order)).all()
                
                # 只有该分类下有可见作品时，才添加到结果中
                if works:
                    work_items = [
                        WorkListItem(
                            id=work.id,
                            name=work.name,
                            description=work.description,
                            icon=work.icon,
                            order=work.order
                        )
                        for work in works
                    ]
                    
                    category_groups.append(
                        WorkCategoryGroup(
                            id=category.id,
                            name=category.name,
                            icon=category.icon,
                            order=category.order,
                            works=work_items
                        )
                    )
            
            return WorkCategoryResponse(categories=category_groups)
            
        finally:
            db.close()
    
    def get_work_detail(self, work_id: str) -> Optional[WorkDetail]:
        """
        获取作品详情
        
        Args:
            work_id: 作品ID
            
        Returns:
            WorkDetail: 作品详情，如果作品不存在或不可见则返回None
            
        Notes:
            - 只能查询 visible=True 的作品
            - html_path 会被转换为完整的访问URL
        """
        db = self._get_db()
        try:
            # 查询作品及其分类
            work = db.query(WorkModel).filter(
                WorkModel.id == work_id,
                WorkModel.visible == True
            ).first()
            
            if not work:
                return None
            
            # 获取分类信息
            category = db.query(WorkCategoryModel).filter(
                WorkCategoryModel.id == work.category_id
            ).first()
            
            # 生成HTML访问URL
            html_url = f"/static/{work.html_path}"
            
            # 构建响应
            return WorkDetail(
                id=work.id,
                name=work.name,
                description=work.description,
                category_id=work.category_id,
                category_name=category.name if category else "",
                icon=work.icon,
                order=work.order,
                html_url=html_url,
                created_at=work.created_at
            )
            
        finally:
            db.close()
    
    # ==================== 后台管理方法 ====================
    
    def get_all_works_admin(
        self,
        page: int = 1,
        page_size: int = 20,
        category_id: Optional[str] = None,
        visible: Optional[bool] = None
    ) -> AdminWorkListResponse:
        """获取所有作品列表（管理后台）"""
        db = self._get_db()
        try:
            page_size = min(page_size, 100)
            query = db.query(WorkModel)
            
            if category_id:
                query = query.filter(WorkModel.category_id == category_id)
            if visible is not None:
                query = query.filter(WorkModel.visible == visible)
            
            total = query.count()
            works = query.order_by(
                asc(WorkModel.category_id),
                asc(WorkModel.order)
            ).offset((page - 1) * page_size).limit(page_size).all()
            
            work_items = []
            for work in works:
                category = db.query(WorkCategoryModel).filter(
                    WorkCategoryModel.id == work.category_id
                ).first()
                
                work_items.append(AdminWorkListItem(
                    id=work.id,
                    name=work.name,
                    description=work.description,
                    category_id=work.category_id,
                    category_name=category.name if category else "未分类",
                    icon=work.icon,
                    html_path=work.html_path,
                    order=work.order,
                    visible=work.visible,
                    created_at=work.created_at,
                    updated_at=work.updated_at
                ))
            
            return AdminWorkListResponse(
                works=work_items,
                total=total,
                page=page,
                page_size=page_size
            )
        finally:
            db.close()
    
    def create_work(
        self,
        name: str,
        description: str,
        category_id: str,
        html_path: str,
        icon: Optional[str] = None,
        order: int = 0,
        visible: bool = True
    ) -> AdminWorkListItem:
        """创建作品"""
        db = self._get_db()
        try:
            category = db.query(WorkCategoryModel).filter(
                WorkCategoryModel.id == category_id
            ).first()
            if not category:
                raise ValueError(f"分类不存在: {category_id}")
            
            work = WorkModel(
                id=str(uuid.uuid4()),
                name=name,
                description=description,
                category_id=category_id,
                icon=icon,
                html_path=html_path,
                order=order,
                visible=visible,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.add(work)
            db.commit()
            db.refresh(work)
            
            return AdminWorkListItem(
                id=work.id,
                name=work.name,
                description=work.description,
                category_id=work.category_id,
                category_name=category.name,
                icon=work.icon,
                html_path=work.html_path,
                order=work.order,
                visible=work.visible,
                created_at=work.created_at,
                updated_at=work.updated_at
            )
        finally:
            db.close()
    
    def update_work(self, work_id: str, request: UpdateWorkRequest) -> AdminWorkListItem:
        """更新作品信息"""
        db = self._get_db()
        try:
            work = db.query(WorkModel).filter(WorkModel.id == work_id).first()
            if not work:
                raise ValueError(f"作品不存在: {work_id}")
            
            if request.category_id and request.category_id != work.category_id:
                category = db.query(WorkCategoryModel).filter(
                    WorkCategoryModel.id == request.category_id
                ).first()
                if not category:
                    raise ValueError(f"分类不存在: {request.category_id}")
                work.category_id = request.category_id
            
            if request.name is not None:
                work.name = request.name
            if request.description is not None:
                work.description = request.description
            if request.icon is not None:
                work.icon = request.icon
            if request.order is not None:
                work.order = request.order
            if request.visible is not None:
                work.visible = request.visible
            
            work.updated_at = datetime.now()
            db.commit()
            db.refresh(work)
            
            category = db.query(WorkCategoryModel).filter(
                WorkCategoryModel.id == work.category_id
            ).first()
            
            return AdminWorkListItem(
                id=work.id,
                name=work.name,
                description=work.description,
                category_id=work.category_id,
                category_name=category.name if category else "未分类",
                icon=work.icon,
                html_path=work.html_path,
                order=work.order,
                visible=work.visible,
                created_at=work.created_at,
                updated_at=work.updated_at
            )
        finally:
            db.close()
    
    def delete_work(self, work_id: str) -> str:
        """删除作品，返回html_path用于删除文件"""
        db = self._get_db()
        try:
            work = db.query(WorkModel).filter(WorkModel.id == work_id).first()
            if not work:
                raise ValueError(f"作品不存在: {work_id}")
            
            html_path = work.html_path
            db.delete(work)
            db.commit()
            return html_path
        finally:
            db.close()
    
    def move_work_up(self, work_id: str) -> AdminWorkListItem:
        """上移作品"""
        db = self._get_db()
        try:
            work = db.query(WorkModel).filter(WorkModel.id == work_id).first()
            if not work:
                raise ValueError(f"作品不存在: {work_id}")
            
            prev_work = db.query(WorkModel).filter(
                WorkModel.category_id == work.category_id,
                WorkModel.order < work.order
            ).order_by(WorkModel.order.desc()).first()
            
            if not prev_work:
                raise ValueError("已经是第一个作品，无法上移")
            
            work.order, prev_work.order = prev_work.order, work.order
            work.updated_at = datetime.now()
            prev_work.updated_at = datetime.now()
            db.commit()
            db.refresh(work)
            
            category = db.query(WorkCategoryModel).filter(
                WorkCategoryModel.id == work.category_id
            ).first()
            
            return AdminWorkListItem(
                id=work.id,
                name=work.name,
                description=work.description,
                category_id=work.category_id,
                category_name=category.name if category else "未分类",
                icon=work.icon,
                html_path=work.html_path,
                order=work.order,
                visible=work.visible,
                created_at=work.created_at,
                updated_at=work.updated_at
            )
        finally:
            db.close()
    
    def move_work_down(self, work_id: str) -> AdminWorkListItem:
        """下移作品"""
        db = self._get_db()
        try:
            work = db.query(WorkModel).filter(WorkModel.id == work_id).first()
            if not work:
                raise ValueError(f"作品不存在: {work_id}")
            
            next_work = db.query(WorkModel).filter(
                WorkModel.category_id == work.category_id,
                WorkModel.order > work.order
            ).order_by(WorkModel.order.asc()).first()
            
            if not next_work:
                raise ValueError("已经是最后一个作品，无法下移")
            
            work.order, next_work.order = next_work.order, work.order
            work.updated_at = datetime.now()
            next_work.updated_at = datetime.now()
            db.commit()
            db.refresh(work)
            
            category = db.query(WorkCategoryModel).filter(
                WorkCategoryModel.id == work.category_id
            ).first()
            
            return AdminWorkListItem(
                id=work.id,
                name=work.name,
                description=work.description,
                category_id=work.category_id,
                category_name=category.name if category else "未分类",
                icon=work.icon,
                html_path=work.html_path,
                order=work.order,
                visible=work.visible,
                created_at=work.created_at,
                updated_at=work.updated_at
            )
        finally:
            db.close()
    
    def toggle_work_visibility(self, work_id: str) -> Tuple[AdminWorkListItem, str]:
        """切换作品可见性"""
        db = self._get_db()
        try:
            work = db.query(WorkModel).filter(WorkModel.id == work_id).first()
            if not work:
                raise ValueError(f"作品不存在: {work_id}")
            
            work.visible = not work.visible
            work.updated_at = datetime.now()
            db.commit()
            db.refresh(work)
            
            category = db.query(WorkCategoryModel).filter(
                WorkCategoryModel.id == work.category_id
            ).first()
            
            message = "作品已显示" if work.visible else "作品已隐藏"
            
            return (
                AdminWorkListItem(
                    id=work.id,
                    name=work.name,
                    description=work.description,
                    category_id=work.category_id,
                    category_name=category.name if category else "未分类",
                    icon=work.icon,
                    html_path=work.html_path,
                    order=work.order,
                    visible=work.visible,
                    created_at=work.created_at,
                    updated_at=work.updated_at
                ),
                message
            )
        finally:
            db.close()
    
    # ==================== 作品分类管理方法 ====================
    
    def get_all_categories_admin(self) -> AdminWorkCategoryListResponse:
        """获取所有作品分类列表（管理后台）"""
        db = self._get_db()
        try:
            categories = db.query(WorkCategoryModel).order_by(asc(WorkCategoryModel.order)).all()
            
            category_items = []
            for category in categories:
                work_count = db.query(WorkModel).filter(
                    WorkModel.category_id == category.id
                ).count()
                
                category_items.append(AdminWorkCategoryListItem(
                    id=category.id,
                    name=category.name,
                    icon=category.icon,
                    order=category.order,
                    work_count=work_count,
                    created_at=category.created_at,
                    updated_at=category.updated_at
                ))
            
            return AdminWorkCategoryListResponse(categories=category_items)
        finally:
            db.close()
    
    def create_category(self, request: CreateWorkCategoryRequest) -> AdminWorkCategoryListItem:
        """创建作品分类"""
        db = self._get_db()
        try:
            existing = db.query(WorkCategoryModel).filter(
                WorkCategoryModel.name == request.name
            ).first()
            if existing:
                raise ValueError(f"分类名称已存在: {request.name}")
            
            category = WorkCategoryModel(
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
            
            return AdminWorkCategoryListItem(
                id=category.id,
                name=category.name,
                icon=category.icon,
                order=category.order,
                work_count=0,
                created_at=category.created_at,
                updated_at=category.updated_at
            )
        finally:
            db.close()
    
    def update_category(self, category_id: str, request: UpdateWorkCategoryRequest) -> AdminWorkCategoryListItem:
        """更新作品分类"""
        db = self._get_db()
        try:
            category = db.query(WorkCategoryModel).filter(
                WorkCategoryModel.id == category_id
            ).first()
            if not category:
                raise ValueError(f"分类不存在: {category_id}")
            
            if request.name and request.name != category.name:
                existing = db.query(WorkCategoryModel).filter(
                    WorkCategoryModel.name == request.name
                ).first()
                if existing:
                    raise ValueError(f"分类名称已被使用: {request.name}")
                category.name = request.name
            
            if request.icon is not None:
                category.icon = request.icon
            if request.order is not None:
                category.order = request.order
            
            category.updated_at = datetime.now()
            db.commit()
            db.refresh(category)
            
            work_count = db.query(WorkModel).filter(
                WorkModel.category_id == category.id
            ).count()
            
            return AdminWorkCategoryListItem(
                id=category.id,
                name=category.name,
                icon=category.icon,
                order=category.order,
                work_count=work_count,
                created_at=category.created_at,
                updated_at=category.updated_at
            )
        finally:
            db.close()
    
    def delete_category(self, category_id: str) -> None:
        """删除作品分类"""
        db = self._get_db()
        try:
            category = db.query(WorkCategoryModel).filter(
                WorkCategoryModel.id == category_id
            ).first()
            if not category:
                raise ValueError(f"分类不存在: {category_id}")
            
            work_count = db.query(WorkModel).filter(
                WorkModel.category_id == category_id
            ).count()
            if work_count > 0:
                raise ValueError(f"分类下还有{work_count}个作品，无法删除")
            
            db.delete(category)
            db.commit()
        finally:
            db.close()
    
    def move_category_up(self, category_id: str) -> AdminWorkCategoryListItem:
        """上移分类"""
        db = self._get_db()
        try:
            category = db.query(WorkCategoryModel).filter(
                WorkCategoryModel.id == category_id
            ).first()
            if not category:
                raise ValueError(f"分类不存在: {category_id}")
            
            prev_category = db.query(WorkCategoryModel).filter(
                WorkCategoryModel.order < category.order
            ).order_by(WorkCategoryModel.order.desc()).first()
            
            if not prev_category:
                raise ValueError("已经是第一个分类，无法上移")
            
            category.order, prev_category.order = prev_category.order, category.order
            category.updated_at = datetime.now()
            prev_category.updated_at = datetime.now()
            db.commit()
            db.refresh(category)
            
            work_count = db.query(WorkModel).filter(
                WorkModel.category_id == category.id
            ).count()
            
            return AdminWorkCategoryListItem(
                id=category.id,
                name=category.name,
                icon=category.icon,
                order=category.order,
                work_count=work_count,
                created_at=category.created_at,
                updated_at=category.updated_at
            )
        finally:
            db.close()
    
    def move_category_down(self, category_id: str) -> AdminWorkCategoryListItem:
        """下移分类"""
        db = self._get_db()
        try:
            category = db.query(WorkCategoryModel).filter(
                WorkCategoryModel.id == category_id
            ).first()
            if not category:
                raise ValueError(f"分类不存在: {category_id}")
            
            next_category = db.query(WorkCategoryModel).filter(
                WorkCategoryModel.order > category.order
            ).order_by(WorkCategoryModel.order.asc()).first()
            
            if not next_category:
                raise ValueError("已经是最后一个分类，无法下移")
            
            category.order, next_category.order = next_category.order, category.order
            category.updated_at = datetime.now()
            next_category.updated_at = datetime.now()
            db.commit()
            db.refresh(category)
            
            work_count = db.query(WorkModel).filter(
                WorkModel.category_id == category.id
            ).count()
            
            return AdminWorkCategoryListItem(
                id=category.id,
                name=category.name,
                icon=category.icon,
                order=category.order,
                work_count=work_count,
                created_at=category.created_at,
                updated_at=category.updated_at
            )
        finally:
            db.close()
