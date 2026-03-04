# AI 教师平台 - 编码指南

> 本文档为 AI 编码代理提供项目构建、测试和代码风格指南。

## 项目概览

这是一个全栈 AI 教师平台项目，包含：
- **前端**：Vue 3 + TypeScript + Vite + Element Plus + Tailwind CSS
- **后端**：FastAPI + SQLAlchemy + PyMySQL（Python）
- **数据库**：MySQL（通过 Alembic 进行迁移管理）
- **测试**：Vitest（前端单元测试）、Playwright（前端 E2E）、pytest（后端）

---

## 构建命令

### 前端命令（在 `frontend/` 目录下执行）

```bash
# 开发服务器
npm run dev              # 启动 Vite 开发服务器（默认 http://localhost:5173）

# 构建
npm run build            # 类型检查 + 生产构建

# 单元测试（Vitest）
npm run test                        # 运行所有单元测试
npm run test -- path/to/test.spec.ts  # 运行单个测试文件
npm run test:ui                     # 启动 Vitest UI 界面
npm run test:coverage               # 运行测试并生成覆盖率报告

# E2E 测试（Playwright）
npm run test:e2e          # 运行所有 E2E 测试
npm run test:e2e:ui       # 启动 Playwright UI 界面
npm run test:e2e:debug    # 调试模式运行 E2E 测试
```

### 后端命令（在 `backend/` 目录下执行）

```bash
# 开发服务器（需要先激活虚拟环境）
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 测试（pytest）
pytest                              # 运行所有测试
pytest tests/unit/test_file.py      # 运行单个测试文件
pytest tests/unit/test_file.py::test_function_name  # 运行单个测试函数
pytest -m unit                      # 只运行单元测试
pytest -m integration               # 只运行集成测试
pytest --cov=src --cov-report=html  # 生成覆盖率报告

# 数据库迁移（Alembic）
alembic revision --autogenerate -m "描述信息"  # 生成迁移文件
alembic upgrade head                          # 应用迁移
alembic downgrade -1                          # 回滚一个版本
alembic current                               # 查看当前版本
```

---

## 代码风格指南

### 通用规范

- **语言**：所有代码注释、文档字符串、变量名必须使用**中文**
- **编码**：Python 文件开头添加 `# -*- coding: utf-8 -*-`
- **编辑器**：统一使用 UTF-8 编码，使用 LF 换行符

---

### 前端代码风格（Vue 3 + TypeScript）

#### 文件组织

```
frontend/
├── src/
│   ├── components/      # 可复用组件
│   ├── views/           # 页面视图
│   ├── layouts/         # 布局组件
│   ├── stores/          # Pinia 状态管理
│   ├── services/        # API 服务
│   ├── composables/     # Vue 组合式函数
│   ├── utils/           # 工具函数
│   ├── types/           # TypeScript 类型定义
│   └── router/          # Vue Router 配置
└── tests/
    ├── unit/            # 单元测试
    └── e2e/             # E2E 测试
```

#### 导入顺序

```typescript
// 1. Vue 核心库
import { ref, computed, onMounted } from 'vue'

// 2. 第三方库
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

// 3. 项目内部模块（使用 @ 别名）
import { useAuthStore } from '@/stores/authStore'
import { ApiService } from '@/services/apiClient'
import type { UserInfo } from '@/types'
```

#### 组件命名

- **组件文件**：PascalCase（如 `UserProfile.vue`）
- **组件注册**：PascalCase
- **Props**：camelCase
- **事件**：kebab-case（如 `@update-user`）

```vue
<script setup lang="ts">
import { ref } from 'vue'

// Props 定义（使用 TypeScript）
interface Props {
  userId: string
  userName?: string
}
const props = defineProps<Props>()

// 事件定义
const emit = defineEmits<{
  updateUser: [user: UserInfo]
}>()

// 响应式状态
const loading = ref(false)
</script>
```

#### TypeScript 规范

- **严格模式**：已启用 `strict: true`，禁止使用 `any` 类型
- **类型导入**：使用 `import type` 导入纯类型
- **路径别名**：使用 `@/` 代替相对路径
- **未使用变量**：已启用 `noUnusedLocals` 和 `noUnusedParameters`

```typescript
// ✅ 正确
import type { UserInfo } from '@/types'
const user = ref<UserInfo | null>(null)

// ❌ 错误
const user: any = {}  // 禁止使用 any
```

#### 样式规范（Tailwind CSS）

- 使用 Tailwind 实用类优先
- 自定义颜色系统（见 `tailwind.config.js`）：
  - `primary-*`：主色（蓝色系）
  - `success-*`、`warning-*`、`error-*`、`info-*`：语义色
- 复杂样式使用 scoped CSS

```vue
<template>
  <button class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600">
    提交
  </button>
</template>
```

#### 测试规范

- **文件命名**：`*.spec.ts` 或 `*.test.ts`
- **测试位置**：`tests/unit/` 或 `tests/views/`
- **测试框架**：Vitest + @vue/test-utils

```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import UserProfile from '@/components/UserProfile.vue'

describe('UserProfile', () => {
  it('应该正确渲染用户名', () => {
    const wrapper = mount(UserProfile, {
      props: { userName: '张三' }
    })
    expect(wrapper.text()).toContain('张三')
  })
})
```

---

### 后端代码风格（FastAPI + Python）

#### 文件组织

```
backend/
├── src/
│   ├── interfaces/      # 接口层（路由、中间件）
│   ├── application/     # 应用层（服务、DTO）
│   ├── domain/          # 领域层（实体、仓库接口）
│   ├── infrastructure/  # 基础设施层（数据库、外部服务）
│   ├── models.py        # Pydantic 模型
│   └── main.py          # 应用入口
├── tests/
│   ├── unit/            # 单元测试
│   └── integration/     # 集成测试
└── alembic/             # 数据库迁移
```

#### 导入顺序

```python
# -*- coding: utf-8 -*-
"""模块文档字符串"""

# 1. 标准库
import logging
from typing import Annotated

# 2. 第三方库
from fastapi import APIRouter, Depends, HTTPException

# 3. 项目内部模块
from src.models import UserInfo
from src.interfaces.auth import get_current_user
```

#### 命名规范

- **文件名**：snake_case（如 `user_service.py`）
- **类名**：PascalCase（如 `UserService`）
- **函数/方法**：snake_case（如 `get_user_by_id`）
- **常量**：UPPER_SNAKE_CASE（如 `MAX_RETRY_COUNT`）
- **变量**：snake_case（如 `user_name`）

#### 函数和类定义

```python
from typing import Annotated
from fastapi import Depends

# 依赖注入使用 Annotated
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> UserInfo:
    """
    获取当前认证用户
    
    Args:
        token: JWT 认证令牌
    
    Returns:
        用户信息对象
    
    Raises:
        HTTPException: 令牌无效或过期时抛出 401 错误
    """
    # 实现代码
    pass
```

#### 错误处理

```python
from fastapi import HTTPException

# ✅ 正确：使用 HTTPException
if not user:
    raise HTTPException(
        status_code=404,
        detail=f"用户 '{user_id}' 不存在"
    )

# ✅ 正确：使用统一的错误处理中间件
# 所有异常会被 src/interfaces/middleware/error_handler.py 捕获
```

#### 异步规范

- **异步函数**：所有 I/O 操作（数据库、API 调用）必须使用 `async/await`
- **测试**：使用 `pytest-asyncio`，已在 `pytest.ini` 中配置

```python
# ✅ 正确
async def get_users():
    users = await db.execute(select(User))
    return users

# 测试
@pytest.mark.asyncio
async def test_get_users():
    users = await get_users()
    assert len(users) > 0
```

#### 测试规范

- **文件命名**：`test_*.py`
- **测试类**：`Test*`（可选）
- **测试函数**：`test_*`
- **标记**：使用 `@pytest.mark.unit` 或 `@pytest.mark.integration`

```python
import pytest
from src.services.user_service import UserService

@pytest.mark.unit
class TestUserService:
    """用户服务测试"""
    
    def test_create_user(self):
        """测试创建用户"""
        service = UserService()
        user = service.create_user(
            username="张三",
            email="zhangsan@example.com"
        )
        assert user.username == "张三"
```

---

## 数据库迁移

### 创建迁移

```bash
cd backend

# 1. 修改 SQLAlchemy 模型（src/db_models.py）

# 2. 生成迁移文件
alembic revision --autogenerate -m "添加用户头像字段"

# 3. 检查生成的迁移文件（alembic/versions/）

# 4. 应用迁移
alembic upgrade head
```

---

## 环境配置

### 前端环境变量

前端无需 `.env` 文件，配置在 `vite.config.ts` 中完成。

### 后端环境变量

```bash
# 复制示例配置
cd backend
cp .env.example .env

# 关键配置项
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/ai_teacher_platform
JWT_SECRET_KEY=your-secret-key-min-32-chars
CURRENT_PROVIDER=deepseek  # 或 openai / kimi
```

---

## Git 提交规范

使用约定式提交：

```
feat: 添加用户头像上传功能
fix: 修复登录页面样式问题
docs: 更新 API 文档
refactor: 重构用户服务代码
test: 添加用户服务单元测试
chore: 更新依赖版本
```

---

## 常见陷阱

### 前端

- ❌ 不要在 Vue 组件中使用 `any` 类型
- ❌ 不要直接修改 props，使用 emit 事件
- ❌ 不要在模板中使用复杂表达式，提取到 computed

### 后端

- ❌ 不要在路由中直接写业务逻辑，应该在 service 层
- ❌ 不要使用同步数据库操作，必须使用 `async/await`
- ❌ 不要硬编码配置，使用环境变量

---

## 相关文档

- [Vue 3 文档](https://cn.vuejs.org/)
- [FastAPI 文档](https://fastapi.tiangolo.com/zh/)
- [Tailwind CSS 文档](https://tailwindcss.com/)
- [Element Plus 文档](https://element-plus.org/zh-CN/)
- [Alembic 文档](https://alembic.sqlalchemy.org/)
