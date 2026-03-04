# -*- coding: utf-8 -*-
"""AI 教师平台后端主应用"""
import sys
import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

# 添加项目根目录到路径，以便访问配置目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入新的模块化路由（interfaces层）
from src.interfaces.routers.tools import list as tools_list_router
from src.interfaces.routers.tools import chat as tools_chat_router
from src.interfaces.routers.tools import conversations as tools_conversations_router
from src.interfaces.routers.tools import media as tools_media_router
from src.interfaces.routers.auth import auth as new_auth_router
from src.interfaces.routers import sessions as new_sessions_router
from src.interfaces.routers import users as new_users_router
from src.interfaces.routers.admin import tools as new_admin_tools_router
from src.interfaces.routers import works as new_works_router
from src.interfaces.routers import courses as new_courses_router
from src.interfaces.routers import common as new_common_router

# 导入错误处理中间件
from src.interfaces.middleware.error_handler import error_handler

# 创建 FastAPI 应用
app = FastAPI(title="AI Teacher Platform Backend")

# ==================== 静态文件服务 ====================

# 挂载静态文件目录
# 优先使用环境变量指定的目录，否则使用默认目录
static_dir = Path(os.getenv("STATIC_DIR", str(project_root / "backend" / "static")))
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
else:
    logger.warning(f"静态文件目录不存在: {static_dir}")

# 确保static下的media目录存在（用于存储生成的音频、视频等）
media_dir = static_dir / "media"
media_dir.mkdir(parents=True, exist_ok=True)


# ==================== 中间件注册 ====================

# 注册统一错误处理中间件
app.middleware("http")(error_handler)


# ==================== 路由注册 ====================

# 新的工具路由（interfaces层）- 使用前缀
app.include_router(tools_list_router.router, prefix="/api/v1")
app.include_router(tools_chat_router.router, prefix="/api/v1")
app.include_router(tools_conversations_router.router, prefix="/api/v1")
app.include_router(tools_media_router.router, prefix="/api/v1")

# 认证相关路由（新架构 - interfaces层）
app.include_router(new_auth_router.router)

# 会话管理路由（新架构 - interfaces层）
app.include_router(new_sessions_router.router)

# 用户管理路由（新架构 - interfaces层）
app.include_router(new_users_router.router)

# 管理员工具路由（新架构 - interfaces层）
app.include_router(new_admin_tools_router.router)

# 用户管理路由（旧路由 - 已迁移到 interfaces 层）
# 已迁移到 interfaces 层的端点：
#   - GET /admin/users -> interfaces/routers/users/users.py
#   - POST /admin/users -> interfaces/routers/users/users.py
#   - GET /admin/users/{user_id} -> interfaces/routers/users/users.py
#   - PATCH /admin/users/{user_id} -> interfaces/routers/users/users.py
#   - DELETE /admin/users/{user_id} -> interfaces/routers/users/users.py
#   - POST /admin/users/{user_id}/reset-password -> interfaces/routers/users/users.py
# TODO: 完全删除旧 users_router

# 会话管理路由（旧路由 - 已迁移到 interfaces 层）
# 已迁移到 interfaces 层的端点：
#   - GET /sessions/{session_id} -> interfaces/routers/sessions/sessions.py
#   - PATCH /sessions/{session_id} -> interfaces/routers/sessions/sessions.py
#   - DELETE /sessions/{session_id} -> interfaces/routers/sessions/sessions.py
#   - GET /agents/{agent_id}/sessions -> 已废弃，返回空列表
# TODO: 完全删除旧 sessions_router
# app.include_router(sessions_router)

# AI 工具路由（旧路由）
# ✅ 所有端点已迁移到 interfaces 层（2026-03-01）
# 已删除的文件：backend/src/routers/tools.py
# 迁移位置：
#   - GET /tools -> interfaces/routers/tools/list.py
#   - GET /toolsets/{toolset_id}/tools -> interfaces/routers/tools/list.py
#   - POST /tools/{tool_id}/chat -> interfaces/routers/tools/chat.py
#   - POST /tools/{tool_id}/chat/stream -> interfaces/routers/tools/chat.py
#   - GET /tools/{tool_id}/conversations -> interfaces/routers/tools/conversations.py
#   - DELETE /tools/{tool_id}/conversations/{conv_id} -> interfaces/routers/tools/conversations.py
#   - GET /tools/{tool_id}/conversations/{conv_id} -> interfaces/routers/tools/conversations.py
#   - POST /tools/{tool_id}/generate-media -> interfaces/routers/tools/media.py
# 未迁移的辅助端点（已删除，前端未使用）：
#   - GET /tools/{tool_id}/chat - OPTIONS请求等辅助端点
# task_storage 已迁移到 common.py

# 管理员工具路由（旧路由 - 已迁移到 interfaces 层）
# ✅ 所有端点已迁移到 interfaces 层（2026-03-02）
# 已删除的文件：backend/src/routers/admin_tools.py
# 迁移位置：interfaces/routers/admin/tools.py
# app.include_router(admin_tools_router)

# 教案学案路由（新架构 - interfaces层）
# ✅ 所有端点已迁移到 interfaces 层（2026-03-02）
# 迁移位置：interfaces/routers/works/works.py
# TODO: 完全删除旧 works_router
app.include_router(new_works_router.works.router)

# 课程文档路由（新架构 - interfaces层）
# ✅ 所有端点已迁移到 interfaces 层（2026-03-02）
# ✅ 旧路由已删除
# 迁移位置：interfaces/routers/courses/courses.py
app.include_router(new_courses_router.router)

# 通用功能路由（新架构 - interfaces层）
# ✅ 已迁移到 interfaces 层（2026-03-02）
# 迁移位置：interfaces/routers/common/common.py
# 保留端点：
#   - GET /navigation -> 导航配置
#   - GET /tasks/{task_id} -> 查询任务状态
#   - POST /convert/markdown-to-word -> Markdown转Word
#   - GET /common-tools/categories -> 工具分类（✅ 已恢复 2026-03-03）
# 删除端点（未使用）：
#   - GET /common-tools/tools/{tool_id} -> 工具详情
app.include_router(new_common_router.router)
# app.include_router(common_router)  # 旧路由已迁移


# ==================== 已废弃的 Agent API ====================
# 保留这些接口是为了向后兼容，实际功能已迁移到 Tool API

@app.get("/api/v1/agents")
async def get_agents():
    """获取所有已配置的 Agent 列表（已废弃，请使用 GET /api/v1/tools）"""
    from src.services.agent_service import AgentService
    from src.models import AgentListResponse, AgentListItem

    agent_service = AgentService(config_dir=str(project_root / "configs" / "agents"))
    agents = agent_service.load_all_agents()

    # 转换为 API 响应格式
    agent_items = [
        AgentListItem(
            agent_id=agent.agent_id,
            name=agent.name,
            description=agent.description,
            icon=None  # MVP阶段暂不支持icon
        )
        for agent in agents
    ]

    return AgentListResponse(agents=agent_items)


@app.post("/api/v1/agents/{agent_id}/sessions")
async def create_agent_session(agent_id: str):
    """为指定的 Agent 创建新会话（已废弃，请使用 POST /api/v1/tools/{tool_id}/chat）"""
    from src.services.agent_service import AgentService
    from src.services.ai_service import AIService
    from src.services.artifact_parser import ArtifactParser
    from src.models import SessionInitResponse
    import uuid

    agent_service = AgentService(config_dir=str(project_root / "configs" / "agents"))
    ai_service = AIService()
    artifact_parser = ArtifactParser()

    # 获取 Agent
    agent = agent_service.get_agent_by_id(agent_id)

    if not agent:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    # 生成欢迎消息
    welcome_message = await ai_service.generate_welcome_message(agent.system_prompt)

    # 解析欢迎消息中的成果物
    artifacts = artifact_parser.parse_from_markdown(welcome_message)

    # 注意：此 API 已废弃，不再创建真实会话
    # 返回一个临时 session_id（仅用于兼容旧代码）
    temp_session_id = str(uuid.uuid4())

    return SessionInitResponse(
        session_id=temp_session_id,
        welcome_message=welcome_message,
        ui_config=agent.ui_config,
        artifacts=artifacts
    )


# ==================== 健康检查 ====================

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": "ai-teacher-platform"}


# ==================== 启动事件 ====================

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化操作"""
    logger.info("AI Teacher Platform Backend 启动中...")
    logger.info(f"项目根目录: {project_root}")
    logger.info(f"静态文件目录: {static_dir}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理操作"""
    logger.info("AI Teacher Platform Backend 关闭中...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
