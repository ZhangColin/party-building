# -*- coding: utf-8 -*-
"""课程文档服务：管理文档目录和文档内容"""
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from pathlib import Path
import uuid
from datetime import datetime
import shutil
import os

from ..database import SessionLocal
from ..db_models import CourseCategoryModel, CourseDocumentModel
from ..models import (
    CourseCategoryNode, CourseCategoryTreeResponse,
    CourseDocumentListItem, CourseDocumentListResponse,
    CourseDocumentDetail,
    AdminCourseCategoryListItem, AdminCourseCategoryListResponse,
    CreateCourseCategoryRequest, UpdateCourseCategoryRequest,
    AdminCourseDocumentListItem, AdminCourseDocumentListResponse,
    UpdateCourseDocumentRequest
)


class CourseService:
    """课程文档服务类"""
    
    def __init__(self):
        """初始化课程文档服务"""
        # 文档存储根目录
        self.storage_root = Path(__file__).parent.parent.parent / "static" / "course_docs"
        self.storage_root.mkdir(parents=True, exist_ok=True)
    
    def _get_db(self):
        """获取数据库会话"""
        return SessionLocal()
    
    def _get_category_path(self, db: Session, category_id: str) -> str:
        """
        获取目录的完整路径
        
        Args:
            db: 数据库会话
            category_id: 目录ID
            
        Returns:
            完整路径字符串（如: AI基础知识 > 什么是AI）
        """
        path_parts = []
        current_id = category_id
        
        # 向上遍历找到所有父目录
        while current_id:
            category = db.query(CourseCategoryModel).filter(
                CourseCategoryModel.id == current_id
            ).first()
            
            if not category:
                break
                
            path_parts.insert(0, category.name)
            current_id = category.parent_id
        
        return " > ".join(path_parts) if path_parts else "未知"
    
    # ========== 目录管理方法 ==========
    
    def _build_category_tree(self, categories: List[CourseCategoryModel], parent_id: Optional[str] = None) -> List[CourseCategoryNode]:
        """
        递归构建目录树
        
        Args:
            categories: 所有目录列表
            parent_id: 父目录ID（None表示根目录）
            
        Returns:
            目录节点列表
        """
        result = []
        
        # 筛选当前层级的目录
        current_level = [c for c in categories if c.parent_id == parent_id]
        
        # 按 order 排序
        current_level.sort(key=lambda x: x.order)
        
        for category in current_level:
            # 递归构建子目录
            children = self._build_category_tree(categories, category.id)
            
            result.append(CourseCategoryNode(
                id=category.id,
                name=category.name,
                parent_id=category.parent_id,
                order=category.order,
                children=children
            ))
        
        return result
    
    def get_category_tree(self) -> CourseCategoryTreeResponse:
        """
        获取目录树结构
        
        Returns:
            目录树响应
        """
        db = self._get_db()
        try:
            # 查询所有目录
            categories = db.query(CourseCategoryModel).all()
            
            # 构建树结构
            tree = self._build_category_tree(categories, parent_id=None)
            
            return CourseCategoryTreeResponse(categories=tree)
            
        finally:
            db.close()
    
    def get_admin_categories(self) -> AdminCourseCategoryListResponse:
        """
        获取所有目录列表（管理后台，扁平结构）
        
        Returns:
            目录列表响应
        """
        db = self._get_db()
        try:
            # 查询所有目录（按层级和order排序）
            categories = db.query(CourseCategoryModel).order_by(
                asc(CourseCategoryModel.parent_id),
                asc(CourseCategoryModel.order)
            ).all()
            
            result = []
            for category in categories:
                # 获取父目录名称
                parent_name = None
                if category.parent_id:
                    parent = db.query(CourseCategoryModel).filter(
                        CourseCategoryModel.id == category.parent_id
                    ).first()
                    if parent:
                        parent_name = parent.name
                
                # 统计文档数
                document_count = db.query(CourseDocumentModel).filter(
                    CourseDocumentModel.category_id == category.id
                ).count()
                
                # 统计子目录数
                children_count = db.query(CourseCategoryModel).filter(
                    CourseCategoryModel.parent_id == category.id
                ).count()
                
                result.append(AdminCourseCategoryListItem(
                    id=category.id,
                    name=category.name,
                    parent_id=category.parent_id,
                    parent_name=parent_name,
                    order=category.order,
                    document_count=document_count,
                    children_count=children_count,
                    created_at=category.created_at,
                    updated_at=category.updated_at
                ))
            
            return AdminCourseCategoryListResponse(categories=result)
            
        finally:
            db.close()
    
    def create_category(self, request: CreateCourseCategoryRequest) -> AdminCourseCategoryListItem:
        """
        创建目录
        
        Args:
            request: 创建目录请求
            
        Returns:
            新创建的目录信息
            
        Raises:
            ValueError: 父目录不存在
        """
        db = self._get_db()
        try:
            # 如果有父目录，验证父目录是否存在
            if request.parent_id:
                parent = db.query(CourseCategoryModel).filter(
                    CourseCategoryModel.id == request.parent_id
                ).first()
                if not parent:
                    raise ValueError(f"父目录不存在: {request.parent_id}")
            
            # 创建新目录
            new_category = CourseCategoryModel(
                id=str(uuid.uuid4()),
                name=request.name,
                parent_id=request.parent_id,
                order=request.order
            )
            
            db.add(new_category)
            db.commit()
            db.refresh(new_category)
            
            # 获取父目录名称
            parent_name = None
            if new_category.parent_id:
                parent = db.query(CourseCategoryModel).filter(
                    CourseCategoryModel.id == new_category.parent_id
                ).first()
                if parent:
                    parent_name = parent.name
            
            return AdminCourseCategoryListItem(
                id=new_category.id,
                name=new_category.name,
                parent_id=new_category.parent_id,
                parent_name=parent_name,
                order=new_category.order,
                document_count=0,
                children_count=0,
                created_at=new_category.created_at,
                updated_at=new_category.updated_at
            )
            
        finally:
            db.close()
    
    def update_category(self, category_id: str, request: UpdateCourseCategoryRequest) -> Optional[AdminCourseCategoryListItem]:
        """
        更新目录信息
        
        Args:
            category_id: 目录ID
            request: 更新目录请求
            
        Returns:
            更新后的目录信息，如果目录不存在则返回None
            
        Raises:
            ValueError: 父目录不存在或形成循环引用
        """
        db = self._get_db()
        try:
            # 查询目录
            category = db.query(CourseCategoryModel).filter(
                CourseCategoryModel.id == category_id
            ).first()
            
            if not category:
                return None
            
            # 更新字段
            if request.name is not None:
                category.name = request.name
            
            if request.parent_id is not None:
                # 验证父目录存在
                if request.parent_id:
                    parent = db.query(CourseCategoryModel).filter(
                        CourseCategoryModel.id == request.parent_id
                    ).first()
                    if not parent:
                        raise ValueError(f"父目录不存在: {request.parent_id}")
                    
                    # 检查循环引用（简单检查：不能将目录移动到自己或自己的子目录下）
                    if request.parent_id == category_id:
                        raise ValueError("不能将目录移动到自己下面")
                    
                    # TODO: 更严格的循环检查（检查所有子孙节点）
                
                category.parent_id = request.parent_id
            
            if request.order is not None:
                category.order = request.order
            
            category.updated_at = datetime.now()
            
            db.commit()
            db.refresh(category)
            
            # 获取父目录名称
            parent_name = None
            if category.parent_id:
                parent = db.query(CourseCategoryModel).filter(
                    CourseCategoryModel.id == category.parent_id
                ).first()
                if parent:
                    parent_name = parent.name
            
            # 统计数量
            document_count = db.query(CourseDocumentModel).filter(
                CourseDocumentModel.category_id == category.id
            ).count()
            
            children_count = db.query(CourseCategoryModel).filter(
                CourseCategoryModel.parent_id == category.id
            ).count()
            
            return AdminCourseCategoryListItem(
                id=category.id,
                name=category.name,
                parent_id=category.parent_id,
                parent_name=parent_name,
                order=category.order,
                document_count=document_count,
                children_count=children_count,
                created_at=category.created_at,
                updated_at=category.updated_at
            )
            
        finally:
            db.close()
    
    def delete_category(self, category_id: str) -> Tuple[bool, Optional[str]]:
        """
        删除目录
        
        Args:
            category_id: 目录ID
            
        Returns:
            (是否成功, 错误消息)
        """
        db = self._get_db()
        try:
            category = db.query(CourseCategoryModel).filter(
                CourseCategoryModel.id == category_id
            ).first()
            
            if not category:
                return False, "目录不存在"
            
            # 检查是否有子目录
            children_count = db.query(CourseCategoryModel).filter(
                CourseCategoryModel.parent_id == category_id
            ).count()
            
            if children_count > 0:
                return False, "该目录下有子目录，无法删除。请先清空该目录。"
            
            # 检查是否有文档
            document_count = db.query(CourseDocumentModel).filter(
                CourseDocumentModel.category_id == category_id
            ).count()
            
            if document_count > 0:
                return False, "该目录下有文档，无法删除。请先清空该目录。"
            
            # 删除目录
            db.delete(category)
            db.commit()
            
            return True, None
            
        finally:
            db.close()
    
    def move_category_up(self, category_id: str) -> Tuple[bool, Optional[str]]:
        """
        将目录向上移动一位
        
        Args:
            category_id: 目录ID
            
        Returns:
            (是否成功, 错误消息)
        """
        db = self._get_db()
        try:
            # 查询当前目录
            category = db.query(CourseCategoryModel).filter(
                CourseCategoryModel.id == category_id
            ).first()
            
            if not category:
                return False, "目录不存在"
            
            # 查询同一父目录下order值更小的第一个目录（上一个）
            prev_category = db.query(CourseCategoryModel).filter(
                CourseCategoryModel.parent_id == category.parent_id,
                CourseCategoryModel.order < category.order
            ).order_by(desc(CourseCategoryModel.order)).first()
            
            if not prev_category:
                return False, "目录已经是第一个，无法上移"
            
            # 交换 order 值
            category.order, prev_category.order = prev_category.order, category.order
            category.updated_at = datetime.now()
            prev_category.updated_at = datetime.now()
            
            db.commit()
            
            return True, None
            
        finally:
            db.close()
    
    def move_category_down(self, category_id: str) -> Tuple[bool, Optional[str]]:
        """
        将目录向下移动一位
        
        Args:
            category_id: 目录ID
            
        Returns:
            (是否成功, 错误消息)
        """
        db = self._get_db()
        try:
            # 查询当前目录
            category = db.query(CourseCategoryModel).filter(
                CourseCategoryModel.id == category_id
            ).first()
            
            if not category:
                return False, "目录不存在"
            
            # 查询同一父目录下order值更大的第一个目录（下一个）
            next_category = db.query(CourseCategoryModel).filter(
                CourseCategoryModel.parent_id == category.parent_id,
                CourseCategoryModel.order > category.order
            ).order_by(asc(CourseCategoryModel.order)).first()
            
            if not next_category:
                return False, "目录已经是最后一个，无法下移"
            
            # 交换 order 值
            category.order, next_category.order = next_category.order, category.order
            category.updated_at = datetime.now()
            next_category.updated_at = datetime.now()
            
            db.commit()
            
            return True, None
            
        finally:
            db.close()
    
    # ========== 文档管理方法 ==========
    
    def get_documents_by_category(self, category_id: str) -> CourseDocumentListResponse:
        """
        获取指定目录下的文档列表
        
        Args:
            category_id: 目录ID
            
        Returns:
            文档列表响应
        """
        db = self._get_db()
        try:
            # 查询该目录下的所有文档（按order排序）
            documents = db.query(CourseDocumentModel).filter(
                CourseDocumentModel.category_id == category_id
            ).order_by(asc(CourseDocumentModel.order)).all()
            
            document_items = [
                CourseDocumentListItem(
                    id=doc.id,
                    title=doc.title,
                    summary=doc.summary,
                    order=doc.order
                )
                for doc in documents
            ]
            
            return CourseDocumentListResponse(documents=document_items)
            
        finally:
            db.close()
    
    def get_document_detail(self, doc_id: str) -> Optional[CourseDocumentDetail]:
        """
        获取文档详情
        
        Args:
            doc_id: 文档ID
            
        Returns:
            文档详情，如果文档不存在则返回None
        """
        db = self._get_db()
        try:
            document = db.query(CourseDocumentModel).filter(
                CourseDocumentModel.id == doc_id
            ).first()
            
            if not document:
                return None
            
            # 读取文档内容
            file_path = self.storage_root / document.file_path.replace("course_docs/", "")
            
            try:
                content = file_path.read_text(encoding='utf-8')
            except Exception as e:
                print(f"Error reading document file: {e}")
                content = ""
            
            # 计算上一篇和下一篇
            prev_doc = db.query(CourseDocumentModel).filter(
                CourseDocumentModel.category_id == document.category_id,
                CourseDocumentModel.order < document.order
            ).order_by(desc(CourseDocumentModel.order)).first()
            
            next_doc = db.query(CourseDocumentModel).filter(
                CourseDocumentModel.category_id == document.category_id,
                CourseDocumentModel.order > document.order
            ).order_by(asc(CourseDocumentModel.order)).first()
            
            return CourseDocumentDetail(
                id=document.id,
                title=document.title,
                summary=document.summary,
                content=content,
                category_id=document.category_id,
                order=document.order,
                prev_doc_id=prev_doc.id if prev_doc else None,
                next_doc_id=next_doc.id if next_doc else None,
                created_at=document.created_at
            )
            
        finally:
            db.close()
    
    def get_admin_documents(self, page: int = 1, page_size: int = 20, category_id: Optional[str] = None) -> AdminCourseDocumentListResponse:
        """
        获取所有文档列表（管理后台，支持分页和筛选）
        
        Args:
            page: 页码
            page_size: 每页数量
            category_id: 按目录ID筛选
            
        Returns:
            文档列表响应
        """
        db = self._get_db()
        try:
            # 构建查询
            query = db.query(CourseDocumentModel)
            
            # 筛选目录
            if category_id:
                query = query.filter(CourseDocumentModel.category_id == category_id)
            
            # 统计总数
            total = query.count()
            
            # 分页查询
            documents = query.order_by(
                asc(CourseDocumentModel.category_id),
                asc(CourseDocumentModel.order)
            ).offset((page - 1) * page_size).limit(page_size).all()
            
            # 获取目录名称和路径
            result = []
            for doc in documents:
                category = db.query(CourseCategoryModel).filter(
                    CourseCategoryModel.id == doc.category_id
                ).first()
                
                category_name = category.name if category else "未知"
                category_path = self._get_category_path(db, doc.category_id)
                
                result.append(AdminCourseDocumentListItem(
                    id=doc.id,
                    title=doc.title,
                    summary=doc.summary,
                    category_id=doc.category_id,
                    category_name=category_name,
                    category_path=category_path,
                    order=doc.order,
                    created_at=doc.created_at,
                    updated_at=doc.updated_at
                ))
            
            return AdminCourseDocumentListResponse(
                documents=result,
                total=total,
                page=page,
                page_size=page_size
            )
            
        finally:
            db.close()
    
    def create_document(self, title: str, summary: str, category_id: str, 
                       markdown_content: str, order: int = 0) -> AdminCourseDocumentListItem:
        """
        创建文档
        
        Args:
            title: 文档标题
            summary: 文档摘要
            category_id: 所属目录ID
            markdown_content: Markdown内容
            order: 排序顺序
            
        Returns:
            新创建的文档信息
            
        Raises:
            ValueError: 目录不存在
        """
        db = self._get_db()
        try:
            # 验证目录存在
            category = db.query(CourseCategoryModel).filter(
                CourseCategoryModel.id == category_id
            ).first()
            
            if not category:
                raise ValueError(f"目录不存在: {category_id}")
            
            # 生成文档ID
            doc_id = str(uuid.uuid4())
            
            # 构建文件路径
            file_path = f"course_docs/{doc_id}/content.md"
            full_path = self.storage_root / doc_id / "content.md"
            
            # 创建目录并保存文件
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(markdown_content, encoding='utf-8')
            
            # 创建文档记录
            new_document = CourseDocumentModel(
                id=doc_id,
                title=title,
                summary=summary,
                file_path=file_path,
                category_id=category_id,
                order=order
            )
            
            db.add(new_document)
            db.commit()
            db.refresh(new_document)
            
            category_path = self._get_category_path(db, new_document.category_id)
            
            return AdminCourseDocumentListItem(
                id=new_document.id,
                title=new_document.title,
                summary=new_document.summary,
                category_id=new_document.category_id,
                category_name=category.name,
                category_path=category_path,
                order=new_document.order,
                created_at=new_document.created_at,
                updated_at=new_document.updated_at
            )
            
        except Exception as e:
            # 如果出错，清理已创建的文件
            if 'full_path' in locals() and full_path.exists():
                shutil.rmtree(full_path.parent)
            raise e
            
        finally:
            db.close()
    
    def update_document(self, doc_id: str, request: UpdateCourseDocumentRequest) -> Optional[AdminCourseDocumentListItem]:
        """
        更新文档信息（不包括文档内容）
        
        Args:
            doc_id: 文档ID
            request: 更新文档请求
            
        Returns:
            更新后的文档信息，如果文档不存在则返回None
            
        Raises:
            ValueError: 目录不存在
        """
        db = self._get_db()
        try:
            # 查询文档
            document = db.query(CourseDocumentModel).filter(
                CourseDocumentModel.id == doc_id
            ).first()
            
            if not document:
                return None
            
            # 更新字段
            if request.title is not None:
                document.title = request.title
            
            if request.summary is not None:
                document.summary = request.summary
            
            if request.category_id is not None:
                # 验证目录存在
                category = db.query(CourseCategoryModel).filter(
                    CourseCategoryModel.id == request.category_id
                ).first()
                
                if not category:
                    raise ValueError(f"目录不存在: {request.category_id}")
                
                document.category_id = request.category_id
            
            if request.order is not None:
                document.order = request.order
            
            document.updated_at = datetime.now()
            
            db.commit()
            db.refresh(document)
            
            # 获取目录名称和路径
            category = db.query(CourseCategoryModel).filter(
                CourseCategoryModel.id == document.category_id
            ).first()
            
            category_name = category.name if category else "未知"
            category_path = self._get_category_path(db, document.category_id)
            
            return AdminCourseDocumentListItem(
                id=document.id,
                title=document.title,
                summary=document.summary,
                category_id=document.category_id,
                category_name=category_name,
                category_path=category_path,
                order=document.order,
                created_at=document.created_at,
                updated_at=document.updated_at
            )
            
        finally:
            db.close()
    
    def delete_document(self, doc_id: str) -> Tuple[bool, Optional[str]]:
        """
        删除文档（包括文件）
        
        Args:
            doc_id: 文档ID
            
        Returns:
            (是否成功, 错误消息)
        """
        db = self._get_db()
        try:
            document = db.query(CourseDocumentModel).filter(
                CourseDocumentModel.id == doc_id
            ).first()
            
            if not document:
                return False, "文档不存在"
            
            # 删除文件和目录
            file_dir = self.storage_root / doc_id
            if file_dir.exists():
                shutil.rmtree(file_dir)
            
            # 删除数据库记录
            db.delete(document)
            db.commit()
            
            return True, None
            
        except Exception as e:
            return False, f"删除失败: {str(e)}"
            
        finally:
            db.close()
    
    def move_document_up(self, doc_id: str) -> Tuple[bool, Optional[str]]:
        """
        将文档向上移动一位
        
        Args:
            doc_id: 文档ID
            
        Returns:
            (是否成功, 错误消息)
        """
        db = self._get_db()
        try:
            # 查询当前文档
            document = db.query(CourseDocumentModel).filter(
                CourseDocumentModel.id == doc_id
            ).first()
            
            if not document:
                return False, "文档不存在"
            
            # 查询同一目录下order值更小的第一个文档（上一个）
            prev_document = db.query(CourseDocumentModel).filter(
                CourseDocumentModel.category_id == document.category_id,
                CourseDocumentModel.order < document.order
            ).order_by(desc(CourseDocumentModel.order)).first()
            
            if not prev_document:
                return False, "文档已经是第一个，无法上移"
            
            # 交换 order 值
            document.order, prev_document.order = prev_document.order, document.order
            document.updated_at = datetime.now()
            prev_document.updated_at = datetime.now()
            
            db.commit()
            
            return True, None
            
        finally:
            db.close()
    
    def move_document_down(self, doc_id: str) -> Tuple[bool, Optional[str]]:
        """
        将文档向下移动一位
        
        Args:
            doc_id: 文档ID
            
        Returns:
            (是否成功, 错误消息)
        """
        db = self._get_db()
        try:
            # 查询当前文档
            document = db.query(CourseDocumentModel).filter(
                CourseDocumentModel.id == doc_id
            ).first()
            
            if not document:
                return False, "文档不存在"
            
            # 查询同一目录下order值更大的第一个文档（下一个）
            next_document = db.query(CourseDocumentModel).filter(
                CourseDocumentModel.category_id == document.category_id,
                CourseDocumentModel.order > document.order
            ).order_by(asc(CourseDocumentModel.order)).first()
            
            if not next_document:
                return False, "文档已经是最后一个，无法下移"
            
            # 交换 order 值
            document.order, next_document.order = next_document.order, document.order
            document.updated_at = datetime.now()
            next_document.updated_at = datetime.now()
            
            db.commit()
            
            return True, None
            
        finally:
            db.close()

