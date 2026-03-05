# 党建AI智能平台快速开发计划（基于AI教师平台改造）

## TL;DR

> **核心目标**: 在1天内将现有AI教师平台改造为党建AI智能平台，完成UI党建化、业务模块CRUD、AI功能升级，用于周五演示
>
> **交付物**:
> - 党建风格UI（登录页、主界面、业务模块界面）
> - 党员管理、组织生活管理、党费管理模块（CRUD + 测试）
> - 党建AI问答系统（RAG知识库检索 + 智能回答）
> - 三会一课智能生成工具
> - 演示数据 + 完整测试覆盖
>
> **预计工作量**: 大（30-40小时，1天多）
> **并行执行**: 是 - 4个Wave + 最终验证
> **关键路径**: Wave 1 → Wave 2 → Wave 3 → Wave 4 → Final Verification

---

## Context

### 原始需求

用户需要在1天内完成党建AI智能平台的开发，用于周五向用户演示系统功能完备性和AI能力。项目基于现有AI教师平台改造，保留技术栈和核心框架，添加党建业务模块和专用AI功能。

### 访谈总结

**关键讨论点**:
- **UI策略**: 使用Pencil设计完整原型，党建风格（红色主题），无参考截图，以满足需求为主
- **功能范围**: 批量CRUD开发（党员管理、组织生活管理、党费管理）+ 1-2个AI工具（三会一课生成、党建问答）
- **AI配置**: DeepSeek统一用于文字生成，RAG向量检索（LangChain + FAISS + DeepSeek Embedding），10份核心知识库文档
- **测试策略**: TDD（测试驱动开发），再简单的功能也要有测试
- **演示数据**: 需要准备演示数据，部署由用户自行处理
- **时间策略**: 尽量多做，用户控制节奏

**研究发现**:
- 现有AI教师平台架构完善（Vue 3 + FastAPI + MySQL）
- 已有用户认证、AI工具框架、会话管理等基础设施
- 可以复用现有模板快速开发CRUD功能
- RAG技术可实现语义检索，提升AI问答效果

### Metis审查

**识别的Gap**（已解决）:
- **数据迁移策略**: 明确保留现有数据，新增党建业务数据
- **知识库编码**: UTF-8中文文档，Markdown格式
- **Pencil交付格式**: .pen设计文件 + 导出为代码参考
- **FAISS安装风险**: 已确认可行，如有问题降级为关键词检索

---

## Work Objectives

### 核心目标

在1天内完成AI教师平台向党建AI智能平台的改造，保留核心技术架构，添加党建业务模块，升级AI功能为党建专用，确保系统功能完备性和演示可用性。

### 具体交付物

- **UI设计**: 党建风格完整UI原型（Pencil设计）
- **前端页面**: 登录页、主界面、党员管理、组织生活管理、党费管理、AI工具页面
- **后端API**: 党员管理、组织生活管理、党费管理、党建问答、三会一课生成
- **AI功能**: RAG知识库（10份文档）+ 党建智能问答 + 文稿生成
- **测试覆盖**: 所有CRUD功能单元测试、前端组件测试、API集成测试
- **演示数据**: 党员信息、组织生活记录、党费记录的演示数据

### 完成定义

- [ ] 所有CRUD功能可正常使用（增删改查）
- [ ] 党建AI问答能准确回答10个测试问题
- [ ] 三会一课生成能输出符合规范的文档
- [ ] 所有后端API有单元测试且通过
- [ ] 前端页面渲染正常，无明显UI bug
- [ ] 演示数据完整，能展示系统完备性
- [ ] 系统可成功启动并运行

### 必须有

- 党员管理CRUD（后端 + 前端 + 测试）
- 组织生活管理CRUD（后端 + 前端 + 测试）
- 党费管理CRUD（后端 + 前端 + 测试）
- 党建问答AI功能（RAG检索 + 测试）
- 知识库文档（10份核心文档）
- TDD测试覆盖（所有新增功能）

### 必须没有（Guardrails）

- **不要破坏现有功能**: 保留现有AI教师平台的核心功能（认证、会话管理等）
- **不要过度设计UI**: 简单的红色主题即可，不需要像素级完美
- **不要无限扩展知识库**: 10份文档足够演示，避免时间浪费
- **不要实现复杂流程**: 党员发展流程跟踪、积分系统等复杂功能暂缓
- **不要跳过测试**: 即使是最简单的CRUD也要有测试

---

## Verification Strategy (MANDATORY)

> **零人工干预** — 所有验证由agent执行。无例外。
> 禁止"用户手动测试/确认"作为验收标准。

### 测试决策

- **基础设施存在**: 是（Vitest前端、pytest后端）
- **自动化测试**: 是（TDD模式）
- **框架**: 前端 Vitest + @vue/test-utils，后端 pytest + pytest-asyncio
- **TDD流程**: 每个任务遵循 RED（失败测试）→ GREEN（最小实现）→ REFACTOR

### QA策略

每个任务必须包含agent执行的QA场景（见下方TODO模板）。
证据保存到 `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`。

- **后端API**: 使用Bash (curl) — 发送请求，断言状态码 + 响应字段
- **前端UI**: 使用Playwright (playwright skill) — 导航，交互，断言DOM，截图
- **AI功能**: 使用Bash (curl + DeepSeek API) — 发送问题，验证回答质量
- **知识库**: 使用Bash (Python REPL) — 导入模块，调用检索函数，验证结果

---

## Execution Strategy

### 并行执行Waves

> 通过将独立任务分组到并行waves最大化吞吐量。
> 每个wave完成后进入下一个。
> 目标: 每个wave 3-7个任务。少于3个 = 分拆不足。

```
Wave 1 (立即开始 — 基础搭建，4个任务并行):
├── Task 1: Pencil UI Design (Party Building style) [quick]
├── Task 2: Database Migration (New party module models) [quick]
├── Task 3: Knowledge Base Documents Generation [quick]
└── Task 4: RAG System Setup (LangChain + FAISS) [deep]

Wave 2 (Wave 1完成后 — 后端CRUD APIs，5个任务并行):
├── Task 5: Party Member Management API + Tests [unspecified-high]
├── Task 6: Organization Life Management API + Tests [unspecified-high]
├── Task 7: Party Fee Management API + Tests [unspecified-high]
├── Task 8: Party Building Q&A API + Tests [deep]
└── Task 9: Three Meetings One Lesson Generation API + Tests [deep]

Wave 3 (Wave 2完成后 — 前端实现，5个任务并行):
├── Task 10: Party Member Management UI + Tests [visual-engineering]
├── Task 11: Organization Life Management UI + Tests [visual-engineering]
├── Task 12: Party Fee Management UI + Tests [visual-engineering]
├── Task 13: AI Tools UI (Q&A + Generation) + Tests [visual-engineering]
└── Task 14: Navigation & Layout Update [visual-engineering]

Wave 4 (Wave 3完成后 — 集成与演示准备，4个任务并行):
├── Task 15: Demo Data Generation Script [quick]
├── Task 16: Knowledge Base Initialization Test [unspecified-high]
├── Task 17: End-to-End Integration Test [deep]
└── Task 18: UI Polish & Bug Fixes [unspecified-high]

Wave FINAL (所有任务完成后 — 独立审查，4个并行):
├── Task F1: Plan Compliance Audit (oracle)
├── Task F2: Code Quality Review (unspecified-high)
├── Task F3: Real Manual QA (Party Building scenarios) (unspecified-high)
└── Task F4: Scope Fidelity Check (deep)

关键路径: Task 2 → Task 5 → Task 10 → Task 17 → F1-F4
并行加速: 比顺序执行快约70%
最大并发数: 5 (Waves 2 & 3)
```

### 依赖矩阵（简化版 — 完整计划中包含所有任务）

- **1-4**: 无依赖 — Wave 2-4, 5-9
- **5-9**: 依赖 2, 3, 4 — Wave 3, 10-14
- **10-14**: 依赖 5-9 — Wave 4, 15-18
- **15-18**: 依赖 10-14 — Final Verification
- **F1-F4**: 依赖所有实现任务完成

### Agent分发总结

- **Wave 1**: **4** — T1, T3, T4 → `quick`, T2 → `quick`, T4 → `deep`
- **Wave 2**: **5** — T5-T7 → `unspecified-high`, T8-T9 → `deep`
- **Wave 3**: **5** — T10-T14 → `visual-engineering`
- **Wave 4**: **4** — T15 → `quick`, T16-T18 → `unspecified-high`, T17 → `deep`
- **FINAL**: **4** — F1 → `oracle`, F2-F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

> 实现 + 测试 = 一个任务。永不分离。
> 每个任务必须有: 推荐Agent Profile + 并行化信息 + QA场景。
> **没有QA场景的任务是不完整的。无例外。**

---
### Wave 1: Foundation & Scaffolding

- [ ] 1. Pencil UI Design (Party Building Style)

  **做什么**:
  - 使用Pencil设计党建风格UI完整原型
  - 设计登录页（红色主题、党建元素）
  - 设计主界面（导航栏、侧边栏、主内容区）
  - 设计业务模块页面布局（党员管理、组织生活、党费管理）
  - 导出设计规范（配色方案、字体、间距）

  **不能做**:
  - 不要过度追求像素级完美
  - 不要设计所有细节页面（只设计核心页面）

  **推荐Agent Profile**:
  - **Category**: `visual-engineering`
    - 理由: UI设计任务需要视觉工程能力
  - **Skills**: [`frontend-ui-ux`]
    - `frontend-ui-ux`: 设计师背景，能在没有设计稿的情况下制作出色UI
  - **Skills Evaluated but Omitted**:
    - 无

  **并行化**:
  - **能否并行运行**: 是
  - **并行组**: Wave 1 (with Tasks 2, 3, 4)
  - **阻塞**: Tasks 10-14 (前端实现依赖此设计)
  - **被阻塞**: 无（可立即开始）

  **引用**（关键 - 要详尽）:
  
  **模式引用**（现有代码遵循）:
  - `frontend/src/views/LoginPage.vue` - 现有登录页布局结构
  - `frontend/src/layouts/MainLayout.vue` - 主界面布局参考
  - `frontend/src/components/Header.vue` - 导航栏组件结构
  
  **外部引用**:
  - Pencil官方文档: https://pencil.evolus.vn/ - Pencil使用指南
  - 党建UI风格参考: 红色主题（#D32F2F, #C62828）、金色点缀（#FFD700）
  
  **为什么每个引用重要**:
  - LoginPage.vue: 了解现有登录页结构，避免重新设计
  - MainLayout.vue: 了解主界面布局，确保设计可实现
  - 党建配色: 标准党建红色主题，避免颜色选择纠结

  **验收标准**:
  - [ ] Pencil设计文件已创建: frontend/designs/party-building.pen
  - [ ] 登录页设计完成（包含红色主题、党建Logo位置）
  - [ ] 主界面设计完成（导航栏、侧边栏、内容区布局）
  - [ ] 设计规范文档已导出: frontend/designs/style-guide.md

  **QA场景（强制性）**:

  ```
  Scenario: 设计文件可打开且包含所有必需页面
    Tool: Bash (file check)
    Preconditions: 设计工作已完成
    Steps:
      1. 检查 frontend/designs/party-building.pen 文件存在
      2. 检查文件大小 > 0
      3. 检查 frontend/designs/style-guide.md 文件存在
    Expected Result: 所有文件存在且有效
    Failure Indicators: 文件不存在或大小为0
    Evidence: .sisyphus/evidence/task-01-design-files-check.txt
  ```

  **捕获证据**:
  - [ ] Pencil设计文件截图
  - [ ] 设计规范文档

  **提交**: 是（与Task 2, 3, 4一起）
  - Message: `feat: 党建平台UI设计`
  - Files: frontend/designs/
  - Pre-commit: 无（设计文件无需测试）

---

- [ ] 2. Database Migration (New Party Module Models)

  **做什么**:
  - 创建党建业务模块的数据库模型
  - PartyMemberModel（党员信息表）
  - OrganizationLifeModel（组织生活记录表）
  - PartyFeeModel（党费记录表）
  - PartyKnowledgeModel（党建知识库表，可选）
  - 生成Alembic迁移文件
  - 执行迁移

  **不能做**:
  - 不要修改现有UserModel等核心模型
  - 不要添加复杂的关联关系（保持简单）

  **推荐Agent Profile**:
  - **Category**: `quick`
    - 理由: 数据库模型创建是标准任务，相对简单
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - 无

  **并行化**:
  - **能否并行运行**: 是
  - **并行组**: Wave 1 (with Tasks 1, 3, 4)
  - **阻塞**: Tasks 5-9 (后端API依赖这些模型)
  - **被阻塞**: 无（可立即开始）

  **引用**:
  
  **模式引用**:
  - `backend/src/db_models.py:11-27` - UserModel结构参考（UUID主键、时间戳、关系定义）
  - `backend/src/db_models.py:35-54` - SessionModel外键关系参考
  
  **API/类型引用**:
  - 需求文档: docs/党建AI智能平台功能需求规格说明书.md:406-438 - 党员信息字段定义
  - 需求文档: docs/党建AI智能平台功能需求规格说明书.md:517-541 - 组织生活记录字段定义
  
  **为什么每个引用重要**:
  - db_models.py: 了解现有模型结构，保持一致性
  - 需求文档: 确保字段定义符合业务需求

  **验收标准**:
  - [ ] 模型文件已创建: backend/src/db_models_party.py
  - [ ] PartyMemberModel包含所有必需字段（姓名、性别、出生日期、入党时间等）
  - [ ] OrganizationLifeModel包含所有必需字段（活动类型、主题、时间、参与者等）
  - [ ] PartyFeeModel包含所有必需字段（党员ID、金额、缴纳时间等）
  - [ ] Alembic迁移文件已生成
  - [ ] 迁移已成功执行: `alembic upgrade head`
  - [ ] 后端测试: `pytest backend/tests/unit/test_party_models.py` 通过

  **QA场景**:

  ```
  Scenario: 数据库模型可正常创建和查询
    Tool: Bash (pytest)
    Preconditions: 迁移已执行
    Steps:
      1. 运行 pytest backend/tests/unit/test_party_models.py::test_create_party_member
      2. 运行 pytest backend/tests/unit/test_party_models.py::test_create_organization_life
      3. 运行 pytest backend/tests/unit/test_party_models.py::test_create_party_fee
    Expected Result: 所有测试通过（3 passed）
    Failure Indicators: 任何测试失败
    Evidence: .sisyphus/evidence/task-02-models-test.txt

  Scenario: 数据库表已正确创建
    Tool: Bash (mysql)
    Preconditions: 迁移已执行
    Steps:
      1. 连接到MySQL数据库
      2. 执行 SHOW TABLES LIKE 'party_%';
      3. 验证表存在: party_members, organization_lives, party_fees
    Expected Result: 3个表都存在
    Failure Indicators: 表不存在
    Evidence: .sisyphus/evidence/task-02-tables-check.txt
  ```

  **捕获证据**:
  - [ ] 模型测试输出
  - [ ] 数据库表列表截图

  **提交**: 是（与Task 1, 3, 4一起）

---

- [ ] 3. Knowledge Base Documents Generation

  **做什么**:
  - 生成10份党建核心知识库文档（Markdown格式）
  - 1. 《中国共产党章程》（精简版，约5000字）
  - 2. 《中国共产党纪律处分条例》（摘要，约3000字）
  - 3. 《三会一课操作指南》（约2000字）
  - 4. 《党员发展流程手册》（约2500字）
  - 5. 《二十大报告核心要点》（精简版，约3000字）
  - 6. 《党费收缴标准》（约1000字）
  - 7. 《组织生活会规范》（约1500字）
  - 8. 《民主评议党员办法》（约1200字）
  - 9. 《预备党员转正条件》（约800字）
  - 10. 《党建工作常用术语》（约1000字）
  - 保存到 backend/static/knowledge_base/ 目录

  **不能做**:
  - 不要生成完整版文档（时间不够）
  - 不要添加过多文档（10份足够演示）

  **推荐Agent Profile**:
  - **Category**: `quick`
    - 理由: 文档生成是相对简单的任务
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - 无

  **并行化**:
  - **能否并行运行**: 是
  - **并行组**: Wave 1 (with Tasks 1, 2, 4)
  - **阻塞**: Tasks 4, 8 (知识库初始化和问答功能依赖这些文档)
  - **被阻塞**: 无（可立即开始）

  **引用**:
  
  **外部引用**:
  - 共产党员网: http://www.12371.cn/ - 党章、条例等权威来源
  - 需求文档: docs/党建AI智能平台功能需求规格说明书.md:882-925 - 知识库内容要求
  
  **为什么每个引用重要**:
  - 12371.cn: 确保文档内容权威准确
  - 需求文档: 了解知识库需要覆盖的范围

  **验收标准**:
  - [ ] 10份Markdown文档已创建
  - [ ] 每份文档大小合理（500-5000字）
  - [ ] 文档保存在 backend/static/knowledge_base/ 目录
  - [ ] 文档编码为UTF-8
  - [ ] 文档内容准确（手动抽查2份）

  **QA场景**:

  ```
  Scenario: 所有知识库文档已创建且格式正确
    Tool: Bash (file check)
    Preconditions: 文档生成完成
    Steps:
      1. 检查 backend/static/knowledge_base/ 目录存在
      2. 统计 .md 文件数量
      3. 检查每个文件大小 > 0
      4. 检查文件编码为UTF-8
    Expected Result: 10个Markdown文件，全部UTF-8编码
    Failure Indicators: 文件数量不对或编码错误
    Evidence: .sisyphus/evidence/task-03-knowledge-files-check.txt

  Scenario: 文档内容可正常读取
    Tool: Bash (Python)
    Preconditions: 文档生成完成
    Steps:
      1. 运行Python脚本读取所有文档
      2. 统计总字数
      3. 验证每份文档包含关键词（"党"、"党员"等）
    Expected Result: 总字数约20000字，所有文档包含党建关键词
    Failure Indicators: 文档为空或不包含关键词
    Evidence: .sisyphus/evidence/task-03-content-check.txt
  ```

  **捕获证据**:
  - [ ] 文件列表截图
  - [ ] 文档内容抽查结果

  **提交**: 是（与Task 1, 2, 4一起）

---

- [ ] 4. RAG System Setup (LangChain + FAISS)

  **做什么**:
  - 安装依赖: langchain, faiss-cpu, deepseek-embedding
  - 创建知识库服务: backend/src/services/knowledge_base.py
  - 实现文档加载函数（读取Markdown文件）
  - 实现文档分片函数（RecursiveCharacterTextSplitter, chunk_size=500, overlap=50）
  - 实现向量化函数（DeepSeek Embedding API）
  - 实现向量存储函数（FAISS）
  - 实现检索函数（similarity_search, top_k=3）
  - 创建初始化函数（启动时加载知识库）
  - 编写单元测试

  **不能做**:
  - 不要使用复杂的向量化策略（保持简单）
  - 不要实现持久化（FAISS纯内存即可）

  **推荐Agent Profile**:
  - **Category**: `deep`
    - 理由: RAG系统需要深入理解LangChain和FAISS
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - 无

  **并行化**:
  - **能否并行运行**: 是
  - **并行组**: Wave 1 (with Tasks 1, 2, 3)
  - **阻塞**: Tasks 8 (党建问答功能依赖此系统)
  - **被阻塞**: Task 3 (依赖知识库文档)

  **引用**:
  
  **模式引用**:
  - `backend/src/services/ai_chat_service.py` - 现有AI服务结构参考
  
  **外部引用**:
  - LangChain文档: https://python.langchain.com/docs/modules/data_connection/ - 文档加载和分片
  - FAISS文档: https://faiss.ai/ - 向量存储和检索
  - DeepSeek Embedding: https://platform.deepseek.com/api-docs/ - Embedding API
  
  **为什么每个引用重要**:
  - ai_chat_service.py: 了解现有AI服务结构，保持一致性
  - LangChain/FAISS文档: 确保正确使用API

  **验收标准**:
  - [ ] 依赖已安装: langchain, faiss-cpu, tiktoken
  - [ ] 服务文件已创建: backend/src/services/knowledge_base.py
  - [ ] 文档加载函数可用
  - [ ] 文档分片函数可用（chunk_size=500, overlap=50）
  - [ ] 向量化函数可用（DeepSeek Embedding）
  - [ ] 检索函数可用（返回top_k=3相关文档）
  - [ ] 后端测试: `pytest backend/tests/unit/test_knowledge_base.py` 通过

  **QA场景**:

  ```
  Scenario: 知识库可正常初始化
    Tool: Bash (pytest)
    Preconditions: Task 3的文档已生成
    Steps:
      1. 运行 pytest backend/tests/unit/test_knowledge_base.py::test_initialize_knowledge_base
      2. 验证初始化时间 < 10秒
      3. 验证向量存储包含所有文档片段
    Expected Result: 初始化成功，包含约40个文档片段（20000字 / 500字）
    Failure Indicators: 初始化失败或时间过长
    Evidence: .sisyphus/evidence/task-04-init-test.txt

  Scenario: 知识库检索功能正常
    Tool: Bash (pytest)
    Preconditions: 知识库已初始化
    Steps:
      1. 运行 pytest backend/tests/unit/test_knowledge_base.py::test_search_knowledge
      2. 查询: "预备党员转正条件"
      3. 验证返回3个相关文档片段
      4. 验证结果包含关键词"预备党员"或"转正"
    Expected Result: 返回3个相关片段，至少1个包含关键词
    Failure Indicators: 返回空结果或不相关内容
    Evidence: .sisyphus/evidence/task-04-search-test.txt
  ```

  **捕获证据**:
  - [ ] 初始化测试输出
  - [ ] 检索测试输出
  - [ ] 检索结果示例

  **提交**: 是（与Task 1, 2, 3一起）

### Wave 2: Backend CRUD APIs

- [ ] 5. Party Member Management API + Tests

  **做什么**:
  - 创建后端路由: backend/src/interfaces/routers/party_members.py
  - 实现CRUD端点:
    - GET /api/v1/party-members - 列表查询（支持分页、搜索）
    - POST /api/v1/party-members - 创建党员
    - GET /api/v1/party-members/{id} - 查询详情
    - PATCH /api/v1/party-members/{id} - 更新党员信息
    - DELETE /api/v1/party-members/{id} - 删除党员（软删除）
  - 创建服务层: backend/src/services/party_member_service.py
  - 编写单元测试: backend/tests/unit/test_party_members_api.py
  - 编写集成测试: backend/tests/integration/test_party_members_integration.py

  **不能做**:
  - 不要添加复杂权限控制（先实现基础CRUD）
  - 不要实现批量导入导出（后续优化）

  **推荐Agent Profile**:
  - **Category**: `unspecified-high`
    - 理由: CRUD API开发需要后端工程能力
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - 无

  **并行化**:
  - **能否并行运行**: 是
  - **并行组**: Wave 2 (with Tasks 6, 7, 8, 9)
  - **阻塞**: Tasks 10 (前端党员管理UI依赖此API)
  - **被阻塞**: Task 2 (依赖PartyMemberModel)

  **引用**:
  
  **模式引用**:
  - `backend/src/interfaces/routers/users/users.py` - 现有用户管理API参考
  - `backend/src/services/user_service.py` - 服务层结构参考
  
  **API/类型引用**:
  - 需求文档: docs/党建AI智能平台功能需求规格说明书.md:406-438 - 党员信息字段定义
  - `backend/src/models.py:UserCreate` - Pydantic模型结构参考
  
  **为什么每个引用重要**:
  - users.py: 了解现有API路由结构，保持一致性
  - 需求文档: 确保字段定义符合业务需求

  **验收标准**:
  - [ ] 路由文件已创建
  - [ ] 服务文件已创建
  - [ ] 5个CRUD端点都已实现
  - [ ] 单元测试通过: `pytest backend/tests/unit/test_party_members_api.py`
  - [ ] 集成测试通过: `pytest backend/tests/integration/test_party_members_integration.py`
  - [ ] API文档已生成: FastAPI Swagger UI可访问

  **QA场景**:

  ```
  Scenario: 党员CRUD API可正常使用
    Tool: Bash (curl)
    Preconditions: 后端服务已启动
    Steps:
      1. 创建党员: curl -X POST http://localhost:8000/api/v1/party-members -H "Content-Type: application/json" -d '{"name":"张三","gender":"男","birth_date":"1990-01-01","join_date":"2015-07-01"}'
      2. 查询列表: curl http://localhost:8000/api/v1/party-members
      3. 查询详情: curl http://localhost:8000/api/v1/party-members/{id}
      4. 更新信息: curl -X PATCH http://localhost:8000/api/v1/party-members/{id} -d '{"name":"张三丰"}'
      5. 删除党员: curl -X DELETE http://localhost:8000/api/v1/party-members/{id}
    Expected Result: 所有操作返回200，数据正确创建/更新/删除
    Failure Indicators: 任何操作返回4xx或5xx
    Evidence: .sisyphus/evidence/task-05-member-crud-api.txt
  ```

  **捕获证据**:
  - [ ] API测试输出
  - [ ] Swagger UI截图

  **提交**: 是（与Task 6, 7, 8, 9一起）

---

- [ ] 6. Organization Life Management API + Tests

  **做什么**:
  - 创建后端路由: backend/src/interfaces/routers/organization_lives.py
  - 实现CRUD端点:
    - GET /api/v1/organization-lives - 列表查询
    - POST /api/v1/organization-lives - 创建记录
    - GET /api/v1/organization-lives/{id} - 查询详情
    - PATCH /api/v1/organization-lives/{id} - 更新记录
    - DELETE /api/v1/organization-lives/{id} - 删除记录
  - 创建服务层: backend/src/services/organization_life_service.py
  - 编写单元测试: backend/tests/unit/test_organization_lives_api.py
  - 编写集成测试

  **不能做**:
  - 不要实现AI生成功能（这是Task 9）
  - 不要添加复杂的统计功能

  **推荐Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **并行化**:
  - **能否并行运行**: 是
  - **并行组**: Wave 2 (with Tasks 5, 7, 8, 9)
  - **阻塞**: Tasks 11 (前端组织生活管理UI)
  - **被阻塞**: Task 2 (依赖OrganizationLifeModel)

  **引用**:
  
  **模式引用**:
  - Task 5的路由和服务结构
  
  **API/类型引用**:
  - 需求文档: docs/党建AI智能平台功能需求规格说明书.md:517-541 - 组织生活记录字段

  **验收标准**:
  - [ ] 路由文件已创建
  - [ ] 服务文件已创建
  - [ ] 5个CRUD端点都已实现
  - [ ] 单元测试通过
  - [ ] 集成测试通过

  **QA场景**:

  ```
  Scenario: 组织生活CRUD API可正常使用
    Tool: Bash (curl)
    Preconditions: 后端服务已启动
    Steps:
      1. 创建记录: curl -X POST http://localhost:8000/api/v1/organization-lives -d '{"type":"三会一课","theme":"学习二十大精神","date":"2026-03-05","participants":["张三","李四"]}'
      2. 查询列表: curl http://localhost:8000/api/v1/organization-lives
      3. 更新记录: curl -X PATCH http://localhost:8000/api/v1/organization-lives/{id} -d '{"theme":"学习二十大报告"}'
      4. 删除记录: curl -X DELETE http://localhost:8000/api/v1/organization-lives/{id}
    Expected Result: 所有操作返回200
    Failure Indicators: 任何操作返回4xx或5xx
    Evidence: .sisyphus/evidence/task-06-org-life-crud-api.txt
  ```

  **提交**: 是（与Task 5, 7, 8, 9一起）

---

- [ ] 7. Party Fee Management API + Tests

  **做什么**:
  - 创建后端路由: backend/src/interfaces/routers/party_fees.py
  - 实现CRUD端点:
    - GET /api/v1/party-fees - 列表查询
    - POST /api/v1/party-fees - 创建记录
    - GET /api/v1/party-fees/{id} - 查询详情
    - PATCH /api/v1/party-fees/{id} - 更新记录
    - DELETE /api/v1/party-fees/{id} - 删除记录
  - 创建服务层: backend/src/services/party_fee_service.py
  - 编写单元测试: backend/tests/unit/test_party_fees_api.py
  - 编写集成测试

  **不能做**:
  - 不要实现党费计算器（保持简单）
  - 不要实现在线支付

  **推荐Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: []

  **并行化**:
  - **能否并行运行**: 是
  - **并行组**: Wave 2 (with Tasks 5, 6, 8, 9)
  - **阻塞**: Tasks 12 (前端党费管理UI)
  - **被阻塞**: Task 2 (依赖PartyFeeModel)

  **引用**:
  
  **模式引用**:
  - Task 5的路由和服务结构
  
  **API/类型引用**:
  - 需求文档: docs/党建AI智能平台功能需求规格说明书.md:473-509 - 党费管理字段

  **验收标准**:
  - [ ] 路由文件已创建
  - [ ] 服务文件已创建
  - [ ] 5个CRUD端点都已实现
  - [ ] 单元测试通过
  - [ ] 集成测试通过

  **QA场景**:

  ```
  Scenario: 党费CRUD API可正常使用
    Tool: Bash (curl)
    Preconditions: 后端服务已启动
    Steps:
      1. 创建记录: curl -X POST http://localhost:8000/api/v1/party-fees -d '{"member_id":"xxx","amount":100,"payment_date":"2026-03-05","payment_method":"微信"}'
      2. 查询列表: curl http://localhost:8000/api/v1/party-fees
      3. 更新记录: curl -X PATCH http://localhost:8000/api/v1/party-fees/{id} -d '{"amount":150}'
      4. 删除记录: curl -X DELETE http://localhost:8000/api/v1/party-fees/{id}
    Expected Result: 所有操作返回200
    Failure Indicators: 任何操作返回4xx或5xx
    Evidence: .sisyphus/evidence/task-07-fee-crud-api.txt
  ```

  **提交**: 是（与Task 5, 6, 8, 9一起）

- [ ] 8. Party Building Q&A API + Tests

  **做什么**: 创建党建问答API，集成知识库RAG检索 + DeepSeek AI生成回答
  **不能做**: 不要实现多轮对话、敏感词过滤
  **推荐Agent**: `deep`
  **并行化**: Wave 2 (with Tasks 5, 6, 7, 9)
  **依赖**: Task 4 (RAG系统)
  **验收标准**: API可回答10个测试问题，答案包含相关关键词
  **QA场景**: curl测试问答功能，pytest测试回答质量
  **提交**: 与Task 5-7, 9一起

---

- [ ] 9. Three Meetings One Lesson Generation API + Tests

  **做什么**: 创建三会一课文档生成API，设计Prompt模板，生成书记讲话稿 + 会议记录摘要
  **不能做**: 不要实现模板自定义、历史会议参考
  **推荐Agent**: `deep`
  **并行化**: Wave 2 (with Tasks 5-8)
  **依赖**: DeepSeek API
  **验收标准**: 能生成4种会议类型的标准文档，长度>1000字
  **QA场景**: curl测试生成功能，pytest测试不同类型
  **提交**: 与Task 5-8一起

---

### Wave 3: Frontend Implementation (5 tasks, parallel)

- [ ] 10-14. Frontend UIs for Party Modules (detailed specs in commit message)
  - Task 10: Party Member Management UI (CRUD + Tests)
  - Task 11: Organization Life Management UI (CRUD + Tests)
  - Task 12: Party Fee Management UI (CRUD + Tests)
  - Task 13: AI Tools UI (Q&A + Document Generation)
  - Task 14: Navigation & Layout Update (Party Building Style)
  
  **推荐Agent**: All `visual-engineering`
  **并行化**: All in Wave 3
  **依赖**: Tasks 5-9, Task 1 (UI Design)
  **验收标准**: 所有UI可正常渲染，CRUD操作可用，AI工具可用
  **提交**: 单独commit for frontend

### Wave 4: Integration & Demo Prep (4 tasks, parallel)

- [ ] 15-18. Demo Preparation (detailed specs in commit message)
  - Task 15: Demo Data Generation Script
  - Task 16: Knowledge Base Initialization Test
  - Task 17: End-to-End Integration Test
  - Task 18: UI Polish & Bug Fixes
  
  **推荐Agent**: `quick`, `unspecified-high`, `deep`
  **并行化**: All in Wave 4
  **验收标准**: 演示数据完整，系统可启动，所有功能可用
  **提交**: 单独commit for demo prep






## Final Verification Wave (MANDATORY — 所有实现任务完成后)

> 4个审查agent并行运行。全部必须批准。拒绝 → 修复 → 重新运行。

- [ ] F1. **计划合规审计** — `oracle`
  读取计划全文。对每个"必须有": 验证实现存在（读取文件、curl端点、运行命令）。对每个"必须没有": 搜索代码库中的禁止模式 — 如果发现则拒绝并附上file:line。检查.sisyphus/evidence/中证据文件是否存在。比较交付物与计划。
  输出: `必须有 [N/N] | 必须没有 [N/N] | 任务 [N/N] | 结论: 批准/拒绝`

- [ ] F2. **代码质量审查** — `unspecified-high`
  运行 `tsc --noEmit` + linter + `bun test`。审查所有修改文件: `as any`/`@ts-ignore`、空catch、console.log在prod、注释掉的代码、未使用的导入。检查AI slop: 过度注释、过度抽象、通用名称（data/result/item/temp）。
  输出: `构建 [通过/失败] | Lint [通过/失败] | 测试 [N 通过/N 失败] | 文件 [N clean/N issues] | 结论`

- [ ] F3. **真实手动QA** — `unspecified-high` (+ 如有UI则 `playwright` skill)
  从干净状态开始。执行每个任务的每个QA场景 — 遵循确切步骤、捕获证据。测试跨任务集成（功能协同工作，不是隔离）。测试边缘情况: 空状态、无效输入、快速操作。保存到 `.sisyphus/evidence/final-qa/`。
  输出: `场景 [N/N 通过] | 集成 [N/N] | 边缘情况 [N tested] | 结论`

- [ ] F4. **范围忠实度检查** — `deep`
  对每个任务: 读取"做什么"、读取实际diff（git log/diff）。验证1:1 — 规格中的所有内容都已构建（无缺失）、没有构建规格之外的内容（无范围蔓延）。检查"必须没有"合规性。检测跨任务污染: 任务N触碰任务M的文件。标记未说明的更改。
  输出: `任务 [N/N 合规] | 污染 [CLEAN/N issues] | 未说明 [CLEAN/N files] | 结论`

---

## Commit Strategy

- **Task 1-4**: `feat: 党建平台基础搭建 - UI设计、数据库、知识库、RAG系统` — 前端设计文件、后端migrations、知识库文档、RAG服务
  - Pre-commit: `pytest backend/tests/ -k "knowledge_base or rag"`

- **Task 5-9**: `feat: 党建业务模块后端API - 党员、组织生活、党费、AI问答、文稿生成` — 后端路由、服务、测试
  - Pre-commit: `pytest backend/tests/ -k "party_member or organization_life or party_fee"`

- **Task 10-14**: `feat: 党建业务模块前端UI - 党员、组织生活、党费、AI工具、导航更新` — 前端组件、页面、测试
  - Pre-commit: `npm run test frontend/tests/`

- **Task 15-18**: `feat: 演示准备与集成测试 - 演示数据、知识库初始化、E2E测试、UI优化` — 数据脚本、集成测试、UI修复
  - Pre-commit: `pytest backend/tests/integration/`

---

## Success Criteria

### 验证命令

```bash
# 后端测试
pytest backend/tests/ --cov=src --cov-report=term-missing  # 预期: >80% 覆盖率

# 前端测试
npm run test frontend/tests/  # 预期: 所有测试通过

# 知识库检索测试
curl -X POST http://localhost:8000/api/v1/knowledge/search \
  -H "Content-Type: application/json" \
  -d '{"query": "预备党员转正条件"}'  # 预期: 返回相关文档片段

# 党建问答测试
curl -X POST http://localhost:8000/api/v1/party/qa \
  -H "Content-Type: application/json" \
  -d '{"question": "三会一课的要求是什么？"}'  # 预期: 返回基于知识库的准确回答

# CRUD功能测试
curl http://localhost:8000/api/v1/party-members  # 预期: 返回党员列表（200）
curl http://localhost:8000/api/v1/organization-lives  # 预期: 返回组织生活列表（200）
curl http://localhost:8000/api/v1/party-fees  # 预期: 返回党费列表（200）
```

### 最终检查清单

- [ ] 所有"必须有"功能已实现
- [ ] 所有"必须没有"功能已避免
- [ ] 所有测试通过
- [ ] 知识库检索能回答10个测试问题
- [ ] 党建AI问答演示可用
- [ ] CRUD功能完整可用
- [ ] 演示数据已加载
- [ ] 系统可成功启动
