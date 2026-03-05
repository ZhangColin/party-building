# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 提供在此代码库中工作的指导。

## 项目概览

这是一个全栈**党建AI智能平台**项目（前身为 AI 教师平台）：
- **前端**：Vue 3 + TypeScript + Vite + Element Plus + Tailwind CSS + Pinia
- **后端**：FastAPI + SQLAlchemy + PyMySQL (Python)
- **数据库**：MySQL + Alembic 迁移管理
- **测试**：Vitest（前端单元测试）、Playwright（E2E 测试）、pytest（后端测试）

平台为教育工作者提供 AI 驱动的工具，包括 AI 教研员、常用工具、教案学案和课程文档。

## 开发命令

### 前端（在 `frontend/` 目录下执行）

```bash
npm run dev              # 启动 Vite 开发服务器（http://localhost:5173）
npm run build            # 类型检查 + 生产构建
npm run test             # 运行所有单元测试
npm run test -- path/to/test.spec.ts  # 运行单个测试文件
npm run test:ui          # 启动 Vitest UI 界面
npm run test:coverage    # 生成覆盖率报告
npm run test:e2e         # 运行 Playwright E2E 测试
```

### 后端（在 `backend/` 目录下执行）

```bash
# 开发服务器（需先激活虚拟环境）
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 测试
pytest                              # 运行所有测试
pytest tests/unit/test_file.py      # 运行单个测试文件
pytest tests/unit/test_file.py::test_function  # 运行单个测试函数
pytest -m unit                      # 只运行单元测试
pytest -m integration               # 只运行集成测试
pytest --cov=src --cov-report=html  # 生成覆盖率报告

# 数据库迁移
alembic revision --autogenerate -m "描述信息"  # 生成迁移文件
alembic upgrade head                          # 应用迁移
alembic downgrade -1                          # 回滚一个版本
```

## 架构设计

### 后端分层架构

后端采用**分层架构**，使用 `interfaces` 层作为 API 接口层：

```
backend/src/
├── interfaces/          # API 接口层（路由、中间件、依赖注入）
│   ├── routers/         # 按业务领域分组的路由模块
│   │   ├── auth/        # 认证相关端点
│   │   ├── sessions/    # 会话/聊天管理
│   │   ├── tools/       # AI 工具（列表、聊天、会话、媒体）
│   │   ├── users/       # 用户管理
│   │   ├── admin/       # 管理员端点
│   │   ├── works/       # 教案学案
│   │   ├── courses/     # 课程文档
│   │   ├── common/      # 通用端点
│   │   └── party/       # 党建业务模块
│   ├── middleware/      # HTTP 中间件（错误处理）
│   ├── dependencies.py  # 依赖注入
│   └── auth.py          # 认证工具
├── services/            # 业务逻辑层
├── models.py            # Pydantic 模型（DTO、实体）
├── db_models.py         # SQLAlchemy ORM 模型
├── database.py          # 数据库连接管理
├── config_loader.py     # YAML 配置加载器
└── main.py              # FastAPI 应用入口
```

**核心架构模式：**
- **路由模块化**：每个业务域在 `interfaces/routers/{domain}/` 下有独立路由
- **服务层**：业务逻辑位于 `services/{domain}_service.py`
- **依赖注入**：使用 `Annotated` 配合 `Depends`
- **异步优先**：所有 I/O 操作（数据库、API）必须使用 `async/await`
- **统一错误处理**：在 `interfaces/middleware/error_handler.py` 中集中处理

**Agent API → Tool API 迁移说明：**
项目已从 "Agent" 术语迁移到 "Tool" 术语。保留的 Agent 端点仅为向后兼容，新功能应使用 Tool 端点。

### 前端架构

```
frontend/src/
├── views/               # 页面组件
├── components/          # 可复用组件
├── layouts/             # 布局组件（MainLayout、AdminLayout 等）
├── stores/              # Pinia 状态管理
├── router/              # Vue Router 配置
├── services/            # API 客户端服务
├── utils/               # 工具函数
├── types/               # TypeScript 类型定义
└── assets/              # 静态资源
```

**核心模式：**
- **路由守卫**：认证和管理员权限检查在 `router/index.ts`
- **路径别名**：使用 `@/` 从 src 导入
- **Pinia 状态管理**：`authStore`、`navigationStore`、`agentStore`、`coursesStore`、`worksStore`

## 配置系统

### 导航和工具配置

平台使用 **YAML 配置系统**管理导航和 AI 工具：

- `configs/navigation.yaml`：顶部导航模块配置
- `configs/tools/{toolset_id}/categories.yaml`：工具分类
- `configs/tools/{toolset_id}/{tool_id}.yaml`：单个工具配置
- `configs/tools/{toolset_id}/prompts/{prompt}.md`：系统提示词

**工具配置结构示例：**
```yaml
tool_id: "unique_tool_id"
name: "工具显示名称"
description: "工具描述"
category: "分类名称"
system_prompt_file: "prompts/tool_prompt.md"  # 相对于工具集目录
welcome_message: "向用户显示的欢迎消息"
icon: "hero-icon-name"
order: 1
visible: true
type: "normal"  # 或 "placeholder"
toolset_id: "ai_tools"  # 工具集 ID
model: "deepseek:deepseek-chat"  # 可选：覆盖默认模型
content_type: "text"  # 或 "multimodal"
media_type: "image"  # 多模态类型：image/audio/video
```

**添加新工具步骤：**
1. 在 `configs/tools/{toolset_id}/{tool_id}.yaml` 创建配置
2. 如使用 `system_prompt_file`，添加提示词文件
3. 前端通过 `GET /api/v1/tools` 自动发现工具

### 环境变量

后端使用 `.env` 文件（参考 `backend/.env.example`）：
- `DATABASE_URL`：MySQL 连接字符串
- `JWT_SECRET_KEY`：JWT 签名密钥（至少 32 字符）
- `CURRENT_PROVIDER`：默认 AI 提供商（deepseek/openai/kimi）
- 各提供商密钥：`DEEPSEEK_API_KEY`、`OPENAI_API_KEY` 等

## 数据库

### ORM 模型

SQLAlchemy 模型位于 [backend/src/db_models.py](backend/src/db_models.py)：
- `UserModel`：用户认证信息
- `SessionModel`：聊天会话（关联用户和工具）
- `MessageModel`：聊天消息及成果物
- `ArtifactModel`：AI 生成内容（markdown、HTML、SVG）
- `CommonToolModel`：常用工具数据库
- `WorkModel`：教案学案
- `CourseCategoryModel` / `CourseDocumentModel`：课程文档层级结构

### 迁移管理

**创建迁移步骤：**
1. 修改 `src/db_models.py` 中的模型
2. 运行 `alembic revision --autogenerate -m "描述"`
3. 检查 `backend/alembic/versions/` 中生成的文件
4. 执行 `alembic upgrade head` 应用迁移

**重要提示：** 应用自动生成的迁移前务必检查。

## 代码规范

### 语言规范
- **所有代码注释、文档字符串和变量名必须使用中文**
- Python 文件头部添加 `# -*- coding: utf-8 -*-`

### Python（后端）
- **异步函数**：所有 I/O 操作必须使用 `async/await`
- **依赖注入**：使用 `Annotated` 配合 `Depends`
- **错误处理**：使用 `HTTPException`，中间件统一处理
- **命名规范**：文件名/函数用 snake_case，类名用 PascalCase
- **导入顺序**：标准库 → 第三方库 → 项目内部

### TypeScript（前端）
- **严格模式**：禁止使用 `any` 类型
- **类型导入**：纯类型导入使用 `import type`
- **组件命名**：文件名使用 PascalCase（如 `UserProfile.vue`）
- **导入顺序**：Vue → 第三方库 → 项目内部（使用 `@/` 别名）
- **测试文件**：命名为 `*.spec.ts`，位于 `tests/unit/` 或 `tests/views/`

## 关键文件说明

- [backend/src/main.py](backend/src/main.py) - FastAPI 应用、路由注册、中间件
- [backend/src/models.py](backend/src/models.py) - Pydantic 模型（Tool、Navigation 等）
- [backend/src/db_models.py](backend/src/db_models.py) - SQLAlchemy ORM 模型
- [backend/src/interfaces/routers/tools/chat.py](backend/src/interfaces/routers/tools/chat.py) - 工具聊天流式端点
- [backend/src/services/tool_service.py](backend/src/services/tool_service.py) - 工具业务逻辑
- [backend/src/services/ai_service.py](backend/src/services/ai_service.py) - AI 提供商抽象
- [frontend/src/router/index.ts](frontend/src/router/index.ts) - Vue Router 路由守卫
- [configs/navigation.yaml](configs/navigation.yaml) - 导航结构配置

## 党建业务模块

项目包含党建业务模块，具有独立的模型和服务：
- `backend/src/db_models_party.py`：党建专用 ORM 模型
- `backend/src/services/party_member_service.py`：党员管理
- `backend/src/services/organization_life_service.py`：组织生活活动
- `backend/src/services/party_fee_service.py`：党费管理
- `backend/src/services/knowledge_base_service.py`：知识库服务
- `backend/src/interfaces/routers/party/`：党建模块 API 路由

## 样式规范

### 党建主题色彩

项目使用党建主题色彩系统，定义在 `frontend/src/styles/party-theme.css`：

- **主红色:** `#C8102E`（中国红）
- **金色:** `#FFD700`（五星金）
- **深红色:** `#8B0000`

### 使用全局 CSS 类

优先使用预定义的全局类：
- `.party-card`: 卡片容器（金色左边框）
- `.party-btn-primary`: 主按钮（红色渐变）
- `.party-menu-item-active`: 菜单激活态（金色左边框）
- `.party-title-underline`: 标题装饰（金色底线）

详细类列表参见 `party-theme.css`。

