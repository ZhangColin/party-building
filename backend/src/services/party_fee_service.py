# -*- coding: utf-8 -*-
"""党费管理服务"""
from typing import Optional, List, Tuple
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from ..database import SessionLocal
from ..db_models_party import PartyFeeModel


class PartyFeeService:
    """党费管理服务类"""
    
    def __init__(self):
        pass
    
    def _get_db(self):
        """获取数据库会话"""
        return SessionLocal()
    
    def create_fee(
        self,
        member_id: Optional[str],
        member_name: str,
        amount: Decimal,
        payment_date: datetime,
        payment_method: str = "现金",
        fee_month: str = "",
        status: str = "已缴",
        remark: Optional[str] = None
    ) -> dict:
        """创建党费记录"""
        db = self._get_db()
        try:
            fee = PartyFeeModel(
                member_id=member_id,
                member_name=member_name,
                amount=amount,
                payment_date=payment_date,
                payment_method=payment_method,
                fee_month=fee_month,
                status=status,
                remark=remark
            )
            db.add(fee)
            db.commit()
            db.refresh(fee)
            return self._model_to_dict(fee)
        finally:
            db.close()
    
    def get_fee_by_id(self, fee_id: str) -> Optional[dict]:
        """根据ID获取记录"""
        db = self._get_db()
        try:
            fee = db.query(PartyFeeModel).filter(
                PartyFeeModel.fee_id == fee_id
            ).first()
            return self._model_to_dict(fee) if fee else None
        finally:
            db.close()
    
    def get_all_fees(
        self,
        page: int = 1,
        page_size: int = 20,
        member_id: Optional[str] = None,
        fee_month: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Tuple[List[dict], int]:
        """获取党费列表"""
        db = self._get_db()
        try:
            query = db.query(PartyFeeModel)
            
            if member_id:
                query = query.filter(PartyFeeModel.member_id == member_id)
            if fee_month:
                query = query.filter(PartyFeeModel.fee_month == fee_month)
            if status:
                query = query.filter(PartyFeeModel.status == status)
            if keyword:
                query = query.filter(PartyFeeModel.member_name.contains(keyword))
            
            total = query.count()
            offset = (page - 1) * page_size
            fees = query.order_by(desc(PartyFeeModel.payment_date)).offset(offset).limit(page_size).all()
            
            return [self._model_to_dict(f) for f in fees], total
        finally:
            db.close()
    
    def update_fee(self, fee_id: str, **kwargs) -> Optional[dict]:
        """更新记录"""
        db = self._get_db()
        try:
            fee = db.query(PartyFeeModel).filter(
                PartyFeeModel.fee_id == fee_id
            ).first()
            if not fee:
                return None
            
            for key, value in kwargs.items():
                if value is not None and hasattr(fee, key):
                    setattr(fee, key, value)
            
            db.commit()
            db.refresh(fee)
            return self._model_to_dict(fee)
        finally:
            db.close()
    
    def delete_fee(self, fee_id: str) -> bool:
        """删除记录"""
        db = self._get_db()
        try:
            fee = db.query(PartyFeeModel).filter(
                PartyFeeModel.fee_id == fee_id
            ).first()
            if not fee:
                return False
            
            db.delete(fee)
            db.commit()
            return True
        finally:
            db.close()
    
    def _model_to_dict(self, fee: PartyFeeModel) -> dict:
        """将模型转换为字典"""
        return {
            "fee_id": fee.fee_id,
            "member_id": fee.member_id,
            "member_name": fee.member_name,
            "amount": float(fee.amount) if fee.amount else 0,
            "payment_date": fee.payment_date,
            "payment_method": fee.payment_method,
            "fee_month": fee.fee_month,
            "status": fee.status,
            "remark": fee.remark,
            "created_at": fee.created_at,
            "updated_at": fee.updated_at
        }
