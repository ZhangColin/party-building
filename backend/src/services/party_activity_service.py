# -*- coding: utf-8 -*-
"""党建活动文件管理服务"""
import logging
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.db_models_party import PartyActivityCategoryModel, PartyActivityDocumentModel
from src.services.file_conversion_service import FileConversionService

logger = logging.getLogger(__name__)


class PartyActivityService:
    """党建活动文件管理服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.conversion_service = FileConversionService()
        self.upload_dir = Path("uploads/party-activity")
        self.original_dir = self.upload_dir / "original"
        self.markdown_dir = self.upload_dir / "markdown"

    # ==================== 目录管理 ====================

    async def create_category(self, name: str, parent_id: str = None) -> dict:
        """创建目录"""
        await self._check_category_name_unique(name, parent_id)

        category = PartyActivityCategoryModel(
            id=str(uuid.uuid4()),
            name=name,
            parent_id=parent_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)

        return self._category_to_dict(category)

    async def _check_category_name_unique(self, name: str, parent_id: str = None) -> None:
        """检查目录名称唯一"""
        stmt = select(PartyActivityCategoryModel).where(
            and_(
                PartyActivityCategoryModel.name == name,
                PartyActivityCategoryModel.parent_id == parent_id
            )
        )
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise ValueError(f"同级目录中已存在名为 '{name}' 的目录")

    async def update_category(self, category_id: str, name: str = None, parent_id: str = None) -> dict:
        """更新目录"""
        stmt = select(PartyActivityCategoryModel).where(PartyActivityCategoryModel.id == category_id)
        result = await self.db.execute(stmt)
        category = result.scalar_one_or_none()

        if not category:
            raise ValueError(f"目录不存在: {category_id}")

        if name and name != category.name:
            await self._check_category_name_unique(name, parent_id or category.parent_id)
            category.name = name

        if parent_id is not None:
            if parent_id == category_id:
                raise ValueError("不能将目录移动到自己下面")
            category.parent_id = parent_id

        category.updated_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(category)

        return self._category_to_dict(category)

    async def delete_category(self, category_id: str) -> bool:
        """删除目录"""
        # 检查子目录
        stmt = select(PartyActivityCategoryModel).where(PartyActivityCategoryModel.parent_id == category_id)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise ValueError("请先删除子目录")

        # 检查文件
        stmt = select(PartyActivityDocumentModel).where(PartyActivityDocumentModel.category_id == category_id)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise ValueError("请先删除目录下的文件")

        stmt = select(PartyActivityCategoryModel).where(PartyActivityCategoryModel.id == category_id)
        result = await self.db.execute(stmt)
        category = result.scalar_one_or_none()

        if not category:
            raise ValueError(f"目录不存在: {category_id}")

        await self.db.delete(category)
        await self.db.commit()
        return True

    async def get_category_tree(self) -> list:
        """获取目录树"""
        stmt = select(PartyActivityCategoryModel).order_by(
            PartyActivityCategoryModel.order,
            PartyActivityCategoryModel.created_at
        )
        result = await self.db.execute(stmt)
        all_categories = result.scalars().all()

        category_map = {c.id: self._category_to_dict(c) for c in all_categories}
        tree = []

        for category_dict in category_map.values():
            if category_dict["parent_id"]:
                parent = category_map.get(category_dict["parent_id"])
                if parent:
                    parent.setdefault("children", []).append(category_dict)
            else:
                tree.append(category_dict)

        return tree

    def _category_to_dict(self, category: PartyActivityCategoryModel) -> dict:
        """模型转字典"""
        return {
            "id": category.id,
            "name": category.name,
            "parent_id": category.parent_id,
            "order": category.order,
            "created_at": category.created_at.isoformat(),
            "updated_at": category.updated_at.isoformat(),
            "children": []
        }

    # ==================== 文件管理 ====================

    async def create_document(
        self,
        category_id: str,
        filename: str,
        content: str,
        uploaded_by: str = None
    ) -> dict:
        """新建 Markdown 文件"""
        # 确保目录存在
        self.markdown_dir.mkdir(parents=True, exist_ok=True)

        # 保存 Markdown 文件
        markdown_filename = f"{uuid.uuid4()}.md"
        markdown_path = self.markdown_dir / markdown_filename
        markdown_path.write_text(content, encoding="utf-8")

        # 创建数据库记录
        document = PartyActivityDocumentModel(
            id=str(uuid.uuid4()),
            category_id=category_id,
            filename=markdown_filename,
            original_filename=filename,
            markdown_path=str(markdown_path),
            file_type="markdown",
            file_size=len(content.encode("utf-8")),
            uploaded_by=uploaded_by,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)

        return self._document_to_dict(document)

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        category_id: str,
        uploaded_by: str = None
    ) -> dict:
        """上传文件"""
        file_type = self.conversion_service._get_file_type(filename)
        if not file_type:
            raise ValueError(f"不支持的文件类型: {filename}")

        # 确保目录存在
        self.original_dir.mkdir(parents=True, exist_ok=True)
        self.markdown_dir.mkdir(parents=True, exist_ok=True)

        # 保存原文件
        original_filename = f"{uuid.uuid4()}{Path(filename).suffix}"
        original_path = self.original_dir / original_filename
        original_path.write_bytes(file_content)

        # 转换
        try:
            markdown_content = await self.conversion_service.convert_to_markdown(
                str(original_path), file_type
            )
        except Exception as e:
            original_path.unlink(missing_ok=True)
            raise ValueError(f"文件转换失败: {str(e)}")

        # 保存 Markdown
        markdown_filename = f"{uuid.uuid4()}.md"
        markdown_path = self.markdown_dir / markdown_filename
        markdown_path.write_text(markdown_content, encoding="utf-8")

        document = PartyActivityDocumentModel(
            id=str(uuid.uuid4()),
            category_id=category_id,
            filename=markdown_filename,
            original_filename=filename,
            original_path=str(original_path),
            markdown_path=str(markdown_path),
            file_type=file_type,
            file_size=len(file_content),
            uploaded_by=uploaded_by,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)

        return self._document_to_dict(document)

    async def get_documents(self, category_id: str = None) -> list:
        """获取文件列表"""
        stmt = select(PartyActivityDocumentModel)

        if category_id:
            stmt = stmt.where(PartyActivityDocumentModel.category_id == category_id)

        stmt = stmt.order_by(PartyActivityDocumentModel.created_at.desc())
        result = await self.db.execute(stmt)
        return [self._document_to_dict(d) for d in result.scalars().all()]

    async def get_document(self, document_id: str) -> dict:
        """获取文件详情"""
        stmt = select(PartyActivityDocumentModel).where(PartyActivityDocumentModel.id == document_id)
        result = await self.db.execute(stmt)
        document = result.scalar_one_or_none()

        if not document:
            raise ValueError(f"文件不存在: {document_id}")

        doc_dict = self._document_to_dict(document)
        if document.markdown_path:
            doc_dict["content"] = Path(document.markdown_path).read_text(encoding="utf-8")

        return doc_dict

    async def update_document(self, document_id: str, content: str) -> dict:
        """更新文件内容"""
        stmt = select(PartyActivityDocumentModel).where(PartyActivityDocumentModel.id == document_id)
        result = await self.db.execute(stmt)
        document = result.scalar_one_or_none()

        if not document:
            raise ValueError(f"文件不存在: {document_id}")

        if document.markdown_path:
            Path(document.markdown_path).write_text(content, encoding="utf-8")

        document.updated_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(document)

        return self._document_to_dict(document)

    async def delete_document(self, document_id: str) -> bool:
        """删除文件"""
        stmt = select(PartyActivityDocumentModel).where(PartyActivityDocumentModel.id == document_id)
        result = await self.db.execute(stmt)
        document = result.scalar_one_or_none()

        if not document:
            raise ValueError(f"文件不存在: {document_id}")

        # 删除物理文件
        if document.original_path:
            Path(document.original_path).unlink(missing_ok=True)
        if document.markdown_path:
            Path(document.markdown_path).unlink(missing_ok=True)

        await self.db.delete(document)
        await self.db.commit()

        return True

    async def batch_get_documents(self, document_ids: list[str]) -> list[dict]:
        """批量获取文档内容"""
        documents = []

        for doc_id in document_ids:
            stmt = select(PartyActivityDocumentModel).where(PartyActivityDocumentModel.id == doc_id)
            result = await self.db.execute(stmt)
            doc = result.scalar_one_or_none()

            if doc and doc.markdown_path:
                try:
                    markdown_path = Path(doc.markdown_path)
                    if markdown_path.exists():
                        content = markdown_path.read_text(encoding="utf-8")
                        documents.append({
                            "id": doc.id,
                            "filename": doc.original_filename,
                            "content": content
                        })
                except Exception as e:
                    logger.warning(f"读取文档 {doc_id} 内容失败: {e}")

        return documents

    def _document_to_dict(self, document: PartyActivityDocumentModel) -> dict:
        """模型转字典"""
        return {
            "id": document.id,
            "category_id": document.category_id,
            "filename": document.filename,
            "original_filename": document.original_filename,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "uploaded_by": document.uploaded_by,
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat()
        }
