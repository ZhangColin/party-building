# -*- coding: utf-8 -*-
"""党建模块 API 路由"""
import logging
from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query

from src.models_party import (
    # 党员管理模型（已迁移到 members.py）
    # PartyMemberCreate,
    # PartyMemberUpdate,
    # PartyMemberListItem,
    # PartyMemberListResponse,
    # PartyMemberDetail,
    OrganizationLifeCreate,
    OrganizationLifeUpdate,
    OrganizationLifeListItem,
    OrganizationLifeListResponse,
    OrganizationLifeDetail,
    PartyFeeCreate,
    PartyFeeUpdate,
    PartyFeeListItem,
    PartyFeeListResponse,
    PartyFeeDetail,
    PartyQARequest,
    PartyQAResponse,
    MeetingGenerateRequest,
    MeetingGenerateResponse,
)
# 党员服务已迁移到 members.py
# from src.services.party_member_service import PartyMemberService
from src.services.organization_life_service import OrganizationLifeService
from src.services.party_fee_service import PartyFeeService
from src.models import UserInfo
from src.interfaces.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/party", tags=["党建管理"])


# ==================== 依赖注入 ====================

# 党员服务已迁移到 members.py
# def get_party_member_service() -> PartyMemberService:
#     """获取党员服务"""
#     return PartyMemberService()

def get_organization_life_service() -> OrganizationLifeService:
    """获取组织生活服务"""
    return OrganizationLifeService()

def get_party_fee_service() -> PartyFeeService:
    """获取党费服务"""
    return PartyFeeService()


# ==================== 党员管理 API ====================
# ✅ 已迁移到 interfaces/routers/party/members.py（2026-03-05）
# 新端点：
#   - POST   /api/v1/party/members - 创建党员档案
#   - GET    /api/v1/party/members - 党员列表（支持筛选分页）
#   - GET    /api/v1/party/members/{id} - 获取党员详情
#   - PATCH  /api/v1/party/members/{id} - 更新党员档案
#   - DELETE /api/v1/party/members/{id} - 删除党员档案（软删除）
#   - POST   /api/v1/party/members/batch-import - 批量导入党员
# 以下旧端点已删除，避免路由冲突


# ==================== 组织生活管理 API ====================

@router.get("/organization-lives", response_model=OrganizationLifeListResponse)
async def list_organization_lives(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    activity_type: Optional[str] = Query(None, description="活动类型筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    service: OrganizationLifeService = Depends(get_organization_life_service)
):
    """获取组织生活列表"""
    records, total = service.get_all_records(
        page=page,
        page_size=page_size,
        activity_type=activity_type,
        keyword=keyword
    )
    return OrganizationLifeListResponse(
        records=[OrganizationLifeListItem(**r) for r in records],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/organization-lives", response_model=OrganizationLifeDetail, status_code=status.HTTP_201_CREATED)
async def create_organization_life(
    request: OrganizationLifeCreate,
    service: OrganizationLifeService = Depends(get_organization_life_service)
):
    """创建组织生活记录"""
    record = service.create_record(
        activity_type=request.activity_type,
        title=request.title,
        activity_date=request.activity_date,
        location=request.location,
        participants_count=request.participants_count,
        content=request.content,
        organizer=request.organizer
    )
    return OrganizationLifeDetail(**record)


@router.get("/organization-lives/{life_id}", response_model=OrganizationLifeDetail)
async def get_organization_life(
    life_id: str,
    service: OrganizationLifeService = Depends(get_organization_life_service)
):
    """获取组织生活详情"""
    record = service.get_record_by_id(life_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return OrganizationLifeDetail(**record)


@router.patch("/organization-lives/{life_id}", response_model=OrganizationLifeDetail)
async def update_organization_life(
    life_id: str,
    request: OrganizationLifeUpdate,
    service: OrganizationLifeService = Depends(get_organization_life_service)
):
    """更新组织生活记录"""
    record = service.update_record(life_id, **request.model_dump(exclude_unset=True))
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return OrganizationLifeDetail(**record)


@router.delete("/organization-lives/{life_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization_life(
    life_id: str,
    service: OrganizationLifeService = Depends(get_organization_life_service)
):
    """删除组织生活记录"""
    success = service.delete_record(life_id)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    return None


# ==================== 党费管理 API ====================

@router.get("/fees", response_model=PartyFeeListResponse)
async def list_party_fees(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    member_id: Optional[str] = Query(None, description="党员ID筛选"),
    fee_month: Optional[str] = Query(None, description="缴费月份筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    service: PartyFeeService = Depends(get_party_fee_service)
):
    """获取党费列表"""
    fees, total = service.get_all_fees(
        page=page,
        page_size=page_size,
        member_id=member_id,
        fee_month=fee_month,
        status=status,
        keyword=keyword
    )
    return PartyFeeListResponse(
        fees=[PartyFeeListItem(**f) for f in fees],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/fees", response_model=PartyFeeDetail, status_code=status.HTTP_201_CREATED)
async def create_party_fee(
    request: PartyFeeCreate,
    service: PartyFeeService = Depends(get_party_fee_service)
):
    """创建党费记录"""
    fee = service.create_fee(
        member_id=request.member_id,
        member_name=request.member_name,
        amount=request.amount,
        payment_date=request.payment_date,
        payment_method=request.payment_method,
        fee_month=request.fee_month,
        status=request.status,
        remark=request.remark
    )
    return PartyFeeDetail(**fee)


@router.get("/fees/{fee_id}", response_model=PartyFeeDetail)
async def get_party_fee(
    fee_id: str,
    service: PartyFeeService = Depends(get_party_fee_service)
):
    """获取党费详情"""
    fee = service.get_fee_by_id(fee_id)
    if not fee:
        raise HTTPException(status_code=404, detail="记录不存在")
    return PartyFeeDetail(**fee)


@router.patch("/fees/{fee_id}", response_model=PartyFeeDetail)
async def update_party_fee(
    fee_id: str,
    request: PartyFeeUpdate,
    service: PartyFeeService = Depends(get_party_fee_service)
):
    """更新党费记录"""
    fee = service.update_fee(fee_id, **request.model_dump(exclude_unset=True))
    if not fee:
        raise HTTPException(status_code=404, detail="记录不存在")
    return PartyFeeDetail(**fee)


@router.delete("/fees/{fee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_party_fee(
    fee_id: str,
    service: PartyFeeService = Depends(get_party_fee_service)
):
    """删除党费记录"""
    success = service.delete_fee(fee_id)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    return None


# ==================== 党建问答 API ====================

@router.post("/qa", response_model=PartyQAResponse)
async def party_qa(
    request: PartyQARequest,
    current_user: Annotated[UserInfo, Depends(get_current_user)] = None
):
    """
    党建AI问答
    
    基于知识库的智能问答功能
    """
    try:
        # 导入知识库服务
        from src.services.knowledge_base_service import KnowledgeBaseService
        from src.services.ai_service import AIService
        import uuid
        
        kb_service = KnowledgeBaseService()
        ai_service = AIService()
        
        # 初始化知识库（如果尚未初始化）
        if not kb_service.is_initialized():
            await kb_service.initialize()
        
        # 检索相关文档
        relevant_docs = kb_service.search(request.question, top_k=3)
        
        # 构建上下文
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        sources = [doc.metadata.get("source", "未知来源") for doc in relevant_docs]
        
        # 构建Prompt
        system_prompt = f"""你是一个专业的党建知识助手。请根据以下知识库内容回答用户的问题。
如果知识库中没有相关内容，请根据你的理解回答，但要说明这不是来自官方知识库。

知识库内容：
{context}

请用专业、准确、简洁的语言回答用户的问题。"""

        # 调用AI生成回答
        answer = await ai_service.chat(
            messages=[{"role": "user", "content": request.question}],
            system_prompt=system_prompt
        )
        
        return PartyQAResponse(
            answer=answer,
            sources=sources,
            session_id=request.session_id or str(uuid.uuid4())
        )
    except Exception as e:
        logger.error(f"党建问答失败: {e}")
        raise HTTPException(status_code=500, detail=f"问答服务暂时不可用: {str(e)}")


# ==================== 三会一课生成 API ====================

@router.post("/meetings/generate", response_model=MeetingGenerateResponse)
async def generate_meeting_document(
    request: MeetingGenerateRequest,
    current_user: Annotated[UserInfo, Depends(get_current_user)] = None
):
    """
    三会一课文档生成
    
    自动生成会议记录、党课讲稿等文档
    """
    try:
        from src.services.ai_service import AIService
        
        ai_service = AIService()
        
        # 根据会议类型选择模板
        templates = {
            "支部党员大会": "支部党员大会是党支部的最高领导机关。会议由党支部书记主持，全体党员参加。",
            "支部委员会": "支部委员会是党支部的领导班子，负责党支部的日常工作。",
            "党小组会": "党小组会是党小组活动的主要形式，由党小组长主持。",
            "党课": "党课是党组织对党员进行教育的重要形式，通常由支部书记或优秀党员主讲。"
        }
        
        meeting_desc = templates.get(request.meeting_type, "党建会议")
        
        # 构建生成Prompt
        system_prompt = f"""你是一个专业的党建工作助手，擅长撰写党建文档。
请根据以下要求生成一份规范的{request.meeting_type}文档。

会议类型说明：{meeting_desc}

要求：
1. 格式规范，符合党建文档标准
2. 内容充实，有实际意义
3. 语言正式，表述准确
4. 输出Markdown格式"""

        user_message = f"""请生成一份{request.meeting_type}文档：
- 会议主题：{request.theme}
- 会议日期：{request.date}
- 参会人员：{', '.join(request.participants) if request.participants else '全体党员'}
- 额外要求：{request.additional_requirements or '无'}

请生成完整的会议文档，包括：
1. 会议基本信息
2. 会议议程
3. 会议内容
4. 会议决议（如有）
5. 下一步工作安排"""

        content = await ai_service.chat(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt
        )
        
        return MeetingGenerateResponse(
            content=content,
            meeting_type=request.meeting_type,
            theme=request.theme
        )
    except Exception as e:
        logger.error(f"会议文档生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"文档生成服务暂时不可用: {str(e)}")
