# -*- coding: utf-8 -*-
"""组织生活管理服务"""
from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from ..database import SessionLocal
from ..db_models_party import OrganizationLifeModel


class OrganizationLifeService:
    """组织生活管理服务类"""
    
    def __init__(self):
        pass
    
    def _get_db(self):
        """获取数据库会话"""
        return SessionLocal()
    
    def create_record(
        self,
        activity_type: str,
        title: str,
        activity_date: datetime,
        location: Optional[str] = None,
        participants_count: int = 0,
        content: Optional[str] = None,
        organizer: Optional[str] = None
    ) -> dict:
        """创建组织生活记录"""
        db = self._get_db()
        try:
            record = OrganizationLifeModel(
                activity_type=activity_type,
                title=title,
                activity_date=activity_date,
                location=location,
                participants_count=participants_count,
                content=content,
                organizer=organizer
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return self._model_to_dict(record)
        finally:
            db.close()
    
    def get_record_by_id(self, life_id: str) -> Optional[dict]:
        """根据ID获取记录"""
        db = self._get_db()
        try:
            record = db.query(OrganizationLifeModel).filter(
                OrganizationLifeModel.life_id == life_id
            ).first()
            return self._model_to_dict(record) if record else None
        finally:
            db.close()
    
    def get_all_records(
        self,
        page: int = 1,
        page_size: int = 20,
        activity_type: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Tuple[List[dict], int]:
        """获取记录列表"""
        db = self._get_db()
        try:
            query = db.query(OrganizationLifeModel)
            
            if activity_type:
                query = query.filter(OrganizationLifeModel.activity_type == activity_type)
            if keyword:
                query = query.filter(
                    or_(
                        OrganizationLifeModel.title.contains(keyword),
                        OrganizationLifeModel.content.contains(keyword)
                    )
                )
            
            total = query.count()
            offset = (page - 1) * page_size
            records = query.order_by(desc(OrganizationLifeModel.activity_date)).offset(offset).limit(page_size).all()
            
            return [self._model_to_dict(r) for r in records], total
        finally:
            db.close()
    
    def update_record(self, life_id: str, **kwargs) -> Optional[dict]:
        """更新记录"""
        db = self._get_db()
        try:
            record = db.query(OrganizationLifeModel).filter(
                OrganizationLifeModel.life_id == life_id
            ).first()
            if not record:
                return None
            
            for key, value in kwargs.items():
                if value is not None and hasattr(record, key):
                    setattr(record, key, value)
            
            db.commit()
            db.refresh(record)
            return self._model_to_dict(record)
        finally:
            db.close()
    
    def delete_record(self, life_id: str) -> bool:
        """删除记录"""
        db = self._get_db()
        try:
            record = db.query(OrganizationLifeModel).filter(
                OrganizationLifeModel.life_id == life_id
            ).first()
            if not record:
                return False
            
            db.delete(record)
            db.commit()
            return True
        finally:
            db.close()
    
    def _model_to_dict(self, record: OrganizationLifeModel) -> dict:
        """将模型转换为字典"""
        return {
            "life_id": record.life_id,
            "activity_type": record.activity_type,
            "title": record.title,
            "activity_date": record.activity_date,
            "location": record.location,
            "participants_count": record.participants_count,
            "content": record.content,
            "organizer": record.organizer,
            "created_at": record.created_at,
            "updated_at": record.updated_at
        }
