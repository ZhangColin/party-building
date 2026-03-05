# -*- coding: utf-8 -*-
"""党员管理Service"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import logging

from ..db_models_party import PartyMemberModel
from ..models_party import (
    PartyMemberCreate,
    PartyMemberUpdate,
    PartyMemberDetail,
    PartyMemberListItem,
    PartyMemberListResponse
)

# 配置日志
logger = logging.getLogger(__name__)


class PartyMemberService:
    """党员管理业务逻辑"""

    def __init__(self, db: Session):
        """初始化服务

        Args:
            db: 数据库会话
        """
        self.db = db

    def _orm_to_detail(self, model: PartyMemberModel) -> PartyMemberDetail:
        """将ORM模型转换为详情响应模型

        Args:
            model: ORM模型实例

        Returns:
            PartyMemberDetail: 详情响应模型
        """
        return PartyMemberDetail(
            member_id=model.member_id,
            # 基本信息
            name=model.name,
            gender=model.gender,
            id_card=model.id_card,
            birth_date=model.birth_date,
            education=model.education,
            phone=model.phone,
            email=model.email,
            address=model.address,
            work_unit=model.work_unit,
            job_title=model.job_title,
            # 党务信息
            join_date=model.join_date,
            party_branch=model.party_branch,
            member_type=model.member_type,
            application_date=model.application_date,
            activist_date=model.activist_date,
            candidate_date=model.candidate_date,
            provisional_date=model.provisional_date,
            full_member_date=model.full_member_date,
            party_position=model.party_position,
            introducer_1=model.introducer_1,
            introducer_2=model.introducer_2,
            # 流动党员
            is_mobile=model.is_mobile,
            mobile_type=model.mobile_type,
            mobile_reason=model.mobile_reason,
            # 党费
            monthly_income=float(model.monthly_income) if model.monthly_income else None,
            fee_standard=float(model.fee_standard) if model.fee_standard else None,
            # 状态
            status=model.status,
            # 系统字段
            branch_id=model.branch_id,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _orm_to_list_item(self, model: PartyMemberModel) -> PartyMemberListItem:
        """将ORM模型转换为列表项响应模型

        Args:
            model: ORM模型实例

        Returns:
            PartyMemberListItem: 列表项响应模型
        """
        return PartyMemberListItem(
            member_id=model.member_id,
            name=model.name,
            gender=model.gender,
            birth_date=model.birth_date,
            join_date=model.join_date,
            party_branch=model.party_branch,
            member_type=model.member_type,
            phone=model.phone,
            email=model.email,
            status=model.status,
            created_at=model.created_at
        )

    async def create_member(
        self,
        member_data: PartyMemberCreate
    ) -> PartyMemberDetail:
        """创建党员档案

        Args:
            member_data: 创建党员请求

        Returns:
            PartyMemberDetail: 创建的党员详情

        Raises:
            ValueError: 业务规则错误（身份证号重复等）
        """
        try:
            # 检查身份证号是否已存在
            if member_data.id_card:
                existing = self.db.query(PartyMemberModel).filter(
                    PartyMemberModel.id_card == member_data.id_card
                ).first()
                if existing:
                    raise ValueError(f"身份证号 {member_data.id_card} 已被使用")

            # 创建ORM模型实例
            member_model = PartyMemberModel(
                # 基本信息
                name=member_data.name,
                gender=member_data.gender,
                id_card=member_data.id_card,
                birth_date=member_data.birth_date,
                education=member_data.education,
                phone=member_data.phone,
                email=member_data.email,
                address=member_data.address,
                work_unit=member_data.work_unit,
                job_title=member_data.job_title,
                # 党务信息
                join_date=member_data.join_date,
                party_branch=member_data.party_branch,
                member_type=member_data.member_type or "正式党员",
                application_date=member_data.application_date,
                activist_date=member_data.activist_date,
                candidate_date=member_data.candidate_date,
                provisional_date=member_data.provisional_date,
                full_member_date=member_data.full_member_date,
                party_position=member_data.party_position,
                introducer_1=member_data.introducer_1,
                introducer_2=member_data.introducer_2,
                # 流动党员
                is_mobile=member_data.is_mobile,
                mobile_type=member_data.mobile_type,
                mobile_reason=member_data.mobile_reason,
                # 党费
                monthly_income=member_data.monthly_income,
                fee_standard=member_data.fee_standard,
                # 状态
                status=member_data.status or "正常",
                # 系统字段
                branch_id=member_data.branch_id,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            # 保存到数据库
            self.db.add(member_model)
            self.db.commit()
            self.db.refresh(member_model)

            logger.info(f"成功创建党员档案: {member_model.name} (ID: {member_model.member_id})")

            # 转换为响应模型
            return self._orm_to_detail(member_model)

        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"创建党员档案失败: 数据完整性错误 - {str(e)}")
            raise ValueError("创建党员档案失败：数据冲突")
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建党员档案失败: {str(e)}")
            raise

    async def get_member(
        self,
        member_id: str
    ) -> Optional[PartyMemberDetail]:
        """获取党员详情

        Args:
            member_id: 党员ID

        Returns:
            PartyMemberDetail: 党员详情，如果不存在返回None
        """
        try:
            member_model = self.db.query(PartyMemberModel).filter(
                PartyMemberModel.member_id == member_id,
                PartyMemberModel.status != "停止党籍"  # 过滤软删除的记录
            ).first()

            if member_model is None:
                return None

            return self._orm_to_detail(member_model)

        except Exception as e:
            logger.error(f"获取党员详情失败 (ID: {member_id}): {str(e)}")
            raise

    async def update_member(
        self,
        member_id: str,
        member_data: PartyMemberUpdate
    ) -> Optional[PartyMemberDetail]:
        """更新党员档案

        Args:
            member_id: 党员ID
            member_data: 更新党员请求

        Returns:
            PartyMemberDetail: 更新后的党员详情，如果党员不存在返回None

        Raises:
            ValueError: 业务规则错误（身份证号冲突等）
        """
        try:
            # 查询党员是否存在
            member_model = self.db.query(PartyMemberModel).filter(
                PartyMemberModel.member_id == member_id
            ).first()

            if member_model is None:
                return None

            # 检查身份证号冲突
            if member_data.id_card is not None and member_data.id_card != member_model.id_card:
                existing = self.db.query(PartyMemberModel).filter(
                    and_(
                        PartyMemberModel.id_card == member_data.id_card,
                        PartyMemberModel.member_id != member_id
                    )
                ).first()
                if existing:
                    raise ValueError(f"身份证号 {member_data.id_card} 已被其他党员使用")

            # 更新字段（只更新提供的字段）
            # 基本信息
            if member_data.name is not None:
                member_model.name = member_data.name
            if member_data.gender is not None:
                member_model.gender = member_data.gender
            if member_data.id_card is not None:
                member_model.id_card = member_data.id_card
            if member_data.birth_date is not None:
                member_model.birth_date = member_data.birth_date
            if member_data.education is not None:
                member_model.education = member_data.education
            if member_data.phone is not None:
                member_model.phone = member_data.phone
            if member_data.email is not None:
                member_model.email = member_data.email
            if member_data.address is not None:
                member_model.address = member_data.address
            if member_data.work_unit is not None:
                member_model.work_unit = member_data.work_unit
            if member_data.job_title is not None:
                member_model.job_title = member_data.job_title

            # 党务信息
            if member_data.join_date is not None:
                member_model.join_date = member_data.join_date
            if member_data.party_branch is not None:
                member_model.party_branch = member_data.party_branch
            if member_data.member_type is not None:
                member_model.member_type = member_data.member_type
            if member_data.application_date is not None:
                member_model.application_date = member_data.application_date
            if member_data.activist_date is not None:
                member_model.activist_date = member_data.activist_date
            if member_data.candidate_date is not None:
                member_model.candidate_date = member_data.candidate_date
            if member_data.provisional_date is not None:
                member_model.provisional_date = member_data.provisional_date
            if member_data.full_member_date is not None:
                member_model.full_member_date = member_data.full_member_date
            if member_data.party_position is not None:
                member_model.party_position = member_data.party_position
            if member_data.introducer_1 is not None:
                member_model.introducer_1 = member_data.introducer_1
            if member_data.introducer_2 is not None:
                member_model.introducer_2 = member_data.introducer_2

            # 流动党员
            if member_data.is_mobile is not None:
                member_model.is_mobile = member_data.is_mobile
            if member_data.mobile_type is not None:
                member_model.mobile_type = member_data.mobile_type
            if member_data.mobile_reason is not None:
                member_model.mobile_reason = member_data.mobile_reason

            # 党费
            if member_data.monthly_income is not None:
                member_model.monthly_income = member_data.monthly_income
            if member_data.fee_standard is not None:
                member_model.fee_standard = member_data.fee_standard

            # 状态
            if member_data.status is not None:
                member_model.status = member_data.status

            # 系统字段
            if member_data.branch_id is not None:
                member_model.branch_id = member_data.branch_id

            # 更新时间戳
            member_model.updated_at = datetime.now()

            # 提交更改
            self.db.commit()
            self.db.refresh(member_model)

            logger.info(f"成功更新党员档案: {member_model.name} (ID: {member_model.member_id})")

            # 转换为响应模型
            return self._orm_to_detail(member_model)

        except IntegrityError:
            self.db.rollback()
            logger.error(f"更新党员档案失败 (ID: {member_id}): 数据完整性错误")
            raise ValueError("更新党员档案失败：数据冲突")
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新党员档案失败 (ID: {member_id}): {str(e)}")
            raise

    async def delete_member(
        self,
        member_id: str
    ) -> bool:
        """删除党员档案（软删除，更新状态）

        Args:
            member_id: 党员ID

        Returns:
            bool: 是否删除成功，如果党员不存在返回False
        """
        try:
            # 查询党员是否存在
            member_model = self.db.query(PartyMemberModel).filter(
                PartyMemberModel.member_id == member_id
            ).first()

            if member_model is None:
                return False

            # 软删除：将状态改为"停止党籍"
            member_model.status = "停止党籍"
            member_model.updated_at = datetime.now()

            # 提交更改
            self.db.commit()

            logger.info(f"成功软删除党员档案: {member_model.name} (ID: {member_model.member_id})")

            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"删除党员档案失败 (ID: {member_id}): {str(e)}")
            raise

    async def list_members(
        self,
        page: int = 1,
        page_size: int = 20,
        name: Optional[str] = None,
        party_branch: Optional[str] = None,
        member_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> PartyMemberListResponse:
        """获取党员列表（支持筛选和分页）

        Args:
            page: 页码（从1开始）
            page_size: 每页数量
            name: 姓名筛选（模糊查询）
            party_branch: 党支部筛选（精确匹配）
            member_type: 党员类型筛选（精确匹配）
            status: 状态筛选（精确匹配）

        Returns:
            PartyMemberListResponse: 党员列表响应
        """
        try:
            # 计算偏移量
            offset = (page - 1) * page_size

            # 构建查询条件
            conditions = []

            # 姓名模糊查询
            if name:
                conditions.append(PartyMemberModel.name.like(f"%{name}%"))

            # 党支部精确匹配
            if party_branch:
                conditions.append(PartyMemberModel.party_branch == party_branch)

            # 党员类型精确匹配
            if member_type:
                conditions.append(PartyMemberModel.member_type == member_type)

            # 状态精确匹配
            if status:
                conditions.append(PartyMemberModel.status == status)

            # 自动过滤软删除的记录（状态为"停止党籍"的记录）
            conditions.append(PartyMemberModel.status != "停止党籍")

            # 组合查询条件
            if conditions:
                query = self.db.query(PartyMemberModel).filter(and_(*conditions))
            else:
                query = self.db.query(PartyMemberModel).filter(
                    PartyMemberModel.status != "停止党籍"
                )

            # 获取总数
            total = query.count()

            # 获取分页数据（按创建时间倒序）
            member_models = query.order_by(
                desc(PartyMemberModel.created_at)
            ).offset(offset).limit(page_size).all()

            # 转换为列表项响应模型
            members = [self._orm_to_list_item(model) for model in member_models]

            return PartyMemberListResponse(
                members=members,
                total=total,
                page=page,
                page_size=page_size
            )

        except Exception as e:
            logger.error(f"获取党员列表失败: {str(e)}")
            raise

    async def batch_import_members(
        self,
        members_data: List[PartyMemberCreate]
    ) -> Tuple[int, List[str]]:
        """批量导入党员

        Args:
            members_data: 党员数据列表

        Returns:
            Tuple[int, List[str]]: (成功数量, 失败原因列表)
        """
        success_count = 0
        errors = []

        for idx, member_data in enumerate(members_data, 1):
            try:
                # 检查身份证号是否已存在
                if member_data.id_card:
                    existing = self.db.query(PartyMemberModel).filter(
                        PartyMemberModel.id_card == member_data.id_card
                    ).first()
                    if existing:
                        errors.append(f"第{idx}行: 身份证号 {member_data.id_card} 已被使用")
                        continue

                # 创建ORM模型实例
                member_model = PartyMemberModel(
                    # 基本信息
                    name=member_data.name,
                    gender=member_data.gender,
                    id_card=member_data.id_card,
                    birth_date=member_data.birth_date,
                    education=member_data.education,
                    phone=member_data.phone,
                    email=member_data.email,
                    address=member_data.address,
                    work_unit=member_data.work_unit,
                    job_title=member_data.job_title,
                    # 党务信息
                    join_date=member_data.join_date,
                    party_branch=member_data.party_branch,
                    member_type=member_data.member_type or "正式党员",
                    application_date=member_data.application_date,
                    activist_date=member_data.activist_date,
                    candidate_date=member_data.candidate_date,
                    provisional_date=member_data.provisional_date,
                    full_member_date=member_data.full_member_date,
                    party_position=member_data.party_position,
                    introducer_1=member_data.introducer_1,
                    introducer_2=member_data.introducer_2,
                    # 流动党员
                    is_mobile=member_data.is_mobile,
                    mobile_type=member_data.mobile_type,
                    mobile_reason=member_data.mobile_reason,
                    # 党费
                    monthly_income=member_data.monthly_income,
                    fee_standard=member_data.fee_standard,
                    # 状态
                    status=member_data.status or "正常",
                    # 系统字段
                    branch_id=member_data.branch_id,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )

                # 保存到数据库
                self.db.add(member_model)
                self.db.flush()  # 立即刷新但不提交，以便在循环中捕获错误

                success_count += 1
                logger.info(f"批量导入: 成功导入党员 {member_model.name} (第{idx}行)")

            except IntegrityError as e:
                self.db.rollback()
                error_msg = f"第{idx}行: 数据冲突 - {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
            except Exception as e:
                self.db.rollback()
                error_msg = f"第{idx}行: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)

        # 提交所有成功的记录
        try:
            self.db.commit()
            logger.info(f"批量导入完成: 成功 {success_count} 条, 失败 {len(errors)} 条")
        except Exception as e:
            self.db.rollback()
            logger.error(f"批量导入提交失败: {str(e)}")
            raise

        return success_count, errors
