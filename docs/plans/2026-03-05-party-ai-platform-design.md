# 党建AI智能平台设计方案

> 设计日期：2026年3月5日
> 设计师：Claude (Sonnet 4.6)
> 状态：已批准

---

## 一、项目概述

### 1.1 项目定位
将现有AI教师平台转型为**党建AI智能平台**，复用底层技术架构，专注于党建领域AI应用。

### 1.2 核心目标
- 为党务工作者提供AI驱动的智能工具
- 提高党建工作效率和质量
- 确保政治合规性和内容准确性

### 1.3 技术基础
- **前端**：Vue 3 + Element Plus + Tailwind CSS + Pinia
- **后端**：FastAPI + SQLAlchemy + PyMySQL
- **数据库**：MySQL + Alembic
- **AI服务**：DeepSeek/Kimi + 向量RAG
- **测试**：Vitest + Playwright + pytest

---

## 二、功能架构

### 2.1 MVP功能范围

#### AI工具模块
1. **三会一课一键生成** - 生成支部党员大会、支委会、党小组会、党课相关文稿
2. **党员教育学习材料生成** - 生成学习心得、宣讲提纲、学习笔记等
3. **工作总结与汇报材料生成** - 季度/年度总结、专项汇报、述职报告
4. **党日活动策划方案生成** - 完整活动方案、主持词、宣传文案
5. **党规党纪智能问答** - 基于知识库的智能问答系统

#### 管理系统模块
1. **党员档案管理** - 信息录入、编辑、查询、导入导出、流动党员管理
2. **组织生活管理** - 三会一课记录、主题党日、组织生活会、民主评议
3. **党费管理** - 党费计算、缴纳记录、台账统计、欠缴提醒

#### 知识库系统
- **核心党内法规库**（50-100份）- 党章、准则、条例等
- **重要文件精神库**（200-300份）- 党代会报告、重要讲话等
- **党务工作指南库**（50-100份）- 流程指引、操作手册等
- **学习材料库**（100-200份）- 理论文章、典型案例等

### 2.2 导航结构

```yaml
modules:
  - name: "AI党建助手"
    type: "toolset"
    config_source: "tools/party_ai"
    icon: "sparkles"
    order: 1

  - name: "党员管理"
    type: "page"
    page_path: "/admin/party-members"
    icon: "user-group"
    order: 2

  - name: "组织生活"
    type: "page"
    page_path: "/admin/organization-life"
    icon: "calendar"
    order: 3

  - name: "党费管理"
    type: "page"
    page_path: "/admin/party-fees"
    icon: "currency-yen"
    order: 4

  - name: "知识库"
    type: "page"
    page_path: "/knowledge-base"
    icon: "book-open"
    order: 5
```

---

## 三、UI设计

### 3.1 设计风格
**现代党建风（红色+简约）**
- 主色调：红色系，体现党建特色
- 设计风格：现代简约，清爽专业
- 避免过多传统装饰元素

### 3.2 主题色系

```css
主色调：#C8102E（中国红）
辅助色：#FFD700（金色）、#8B0000（深红）
背景色：#FAFAFA（浅灰白）
文字色：#1A1A1A（深灰）
边框色：#E5E5E5
成功色：#22C55E（绿色）
警告色：#F59E0B（橙色）
错误色：#EF4444（红色）
```

### 3.3 改造范围
1. **全局样式变量** - `frontend/src/styles/variables.css`
2. **顶部导航栏** - 红色渐变背景，金色党徽元素
3. **按钮样式** - 主按钮红色、次要按钮白色红边
4. **表格/表单** - 红色主题色
5. **AI对话界面** - 保持现有布局，调整配色
6. **图标** - 党建相关图标（党徽、红旗等）

### 3.4 党徽/元素使用
- 顶部Logo：党徽图标 + "党建AI智能平台"
- 首页Banner：红色渐变 + 标语
- 404/错误页：党建风格插画

---

## 四、数据库设计

### 4.1 党员档案管理

**party_members 表**
```sql
- id: 主键
- name: 姓名
- gender: 性别
- id_card: 身份证号
- birth_date: 出生日期
- education: 学历
- phone: 手机号
- email: 邮箱
- address: 现居住地址
- work_unit: 工作单位
- job_title: 职务/职称

# 党务信息
- member_type: 党员类型（正式/预备）
- application_date: 入党申请书提交时间
- activist_date: 确定为积极分子时间
- candidate_date: 确定为发展对象时间
- provisional_date: 接收为预备党员时间
- full_member_date: 转正时间
- party_position: 党内职务
- introducer_1: 介绍人1
- introducer_2: 介绍人2

# 流动党员
- is_mobile: 是否流动党员
- mobile_type: 流动类型（流出/流入）
- mobile_reason: 流动原因

# 党费
- monthly_income: 月收入
- fee_standard: 党费标准（月缴金额）

# 系统字段
- branch_id: 所属支部ID
- created_at: 创建时间
- updated_at: 更新时间
```

### 4.2 组织生活管理

**organization_activities 表**
```sql
- id: 主键
- activity_type: 活动类型（三会一课/主题党日/组织生活会/民主评议）
- meeting_type: 会议类型（支部党员大会/支委会/党小组会/党课）
- theme: 活动主题
- activity_date: 活动时间
- location: 活动地点
- host: 主持人
- recorder: 记录人
- expected_count: 应到人数
- actual_count: 实到人数
- absent_members: 缺席人员（JSON）
- agenda: 会议议程（JSON）
- content: 活动内容（详细记录）
- resolutions: 决议事项
- photos: 活动照片（JSON数组）
- attachments: 附件材料（JSON数组）

# 系统字段
- branch_id: 所属支部ID
- created_by: 创建人ID
- created_at: 创建时间
- updated_at: 更新时间
```

### 4.3 党费管理

**party_fee_records 表**
```sql
- id: 主键
- member_id: 党员ID
- amount: 缴纳金额
- payment_date: 缴纳时间
- payment_method: 缴纳方式（现金/转账/微信/支付宝）
- collector: 收款人
- notes: 备注
- branch_id: 所属支部ID
- created_at: 创建时间
```

**party_fee_standards 表**
```sql
- id: 主键
- member_id: 党员ID
- monthly_income: 月收入
- fee_amount: 应缴金额
- effective_date: 生效日期
- branch_id: 所属支部ID
- created_at: 创建时间
```

### 4.4 知识库系统

**knowledge_documents 表**
```sql
- id: 主键
- title: 文档标题
- category: 分类（core_regulations/important_documents/work_guides/study_materials）
- file_path: 文件路径
- file_type: 文件类型（PDF/Word/TXT）
- chunk_count: 分块数量
- vector_collection: 向量集合名称
- metadata: 元数据（JSON）- 发布时间、文号、关键词等
- uploaded_by: 上传者ID
- created_at: 创建时间
- updated_at: 更新时间
```

**knowledge_categories 表**
```sql
- id: 主键
- name: 分类名称
- code: 分类代码
- description: 描述
- order: 排序
```

---

## 五、权限控制

### 5.1 角色定义

1. **系统管理员**
   - 权限：全部权限
   - 职责：系统配置、用户管理、数据维护

2. **上级组织管理员**
   - 权限：查看多个支部数据、生成汇总报表
   - 职责：监督指导、数据分析

3. **支部书记/党务干事**
   - 权限：管理本支部数据、审核上报材料
   - 职责：日常工作管理、材料上报

4. **普通党员**
   - 权限：查看个人信息、参与组织生活、使用AI工具
   - 职责：参加学习、提交思想汇报

### 5.2 权限矩阵

| 功能模块 | 系统管理员 | 上级组织管理员 | 支部书记/干事 | 普通党员 |
|---------|:----------:|:-------------:|:-------------:|:--------:|
| AI工具使用 | ✅ | ✅ | ✅ | ✅ |
| 党员档案（全部） | ✅ | ✅（查看） | ✅（本支部） | ❌ |
| 党员档案（本人） | ✅ | ❌ | ❌ | ✅（查看） |
| 组织生活管理 | ✅ | ✅（查看统计） | ✅（本支部） | ✅（查看） |
| 党费管理 | ✅ | ✅（查看统计） | ✅（本支部） | ❌ |
| 党费（本人） | ✅ | ❌ | ❌ | ✅（查看） |
| 知识库管理 | ✅ | ✅（查看） | ❌ | ❌ |
| 用户管理 | ✅ | ✅（查看） | ❌ | ❌ |
| 系统配置 | ✅ | ❌ | ❌ | ❌ |

### 5.3 数据隔离
- **支部级隔离**：每个支部只能管理自己的数据
- **上级组织跨支部查看**：上级组织管理员可查看所有下级支部数据
- **个人数据保护**：普通党员仅可查看自己的个人信息

---

## 六、知识库RAG系统

### 6.1 技术选型

- **向量数据库**：Chroma（轻量级，适合MVP）
- **Embedding模型**：通义千问Embedding（国产合规）
- **文档处理**：PyPDF2 + python-docx
- **RAG框架**：LangChain

### 6.2 知识库内容分类

```
knowledge_base/
├── core_regulations/      # 核心党内法规（50-100份）
│   ├── 党章.pdf
│   ├── 纪律处分条例.pdf
│   ├── 廉洁自律准则.pdf
│   └── ...
├── important_documents/   # 重要文件精神（200-300份）
│   ├── 二十大报告.pdf
│   ├── 中央全会文件.pdf
│   └── ...
├── work_guides/          # 党务工作指南（50-100份）
│   ├── 入党流程指引.pdf
│   ├── 党费收缴标准.pdf
│   └── ...
└── study_materials/      # 学习材料（100-200份）
    ├── 理论文章.pdf
    ├── 典型案例.pdf
    └── ...
```

### 6.3 RAG工作流程

1. **文档上传**
   - 管理员通过知识库管理页面上传PDF/Word文档
   - 选择分类、填写元数据（标题、发布时间、文号等）

2. **文档处理**
   - 系统自动解析文档内容
   - 按段落/章节分块（chunk_size=500, overlap=50）
   - 使用Embedding模型向量化每个chunk

3. **向量存储**
   - 将向量存储到Chroma数据库
   - 建立元数据索引（分类、时间、关键词）

4. **智能检索**
   - AI问答时，将用户问题向量化
   - 在Chroma中检索最相关的top-k个chunk
   - 将检索结果作为上下文传给大模型

5. **答案生成**
   - 大模型基于检索到的上下文生成答案
   - 标注引用来源
   - 输出合规性过滤

### 6.4 合规保障

- **敏感词过滤**：输出内容过政治敏感词库
- **来源标注**：所有回答必须标注引用来源
- **免责声明**：AI生成内容仅供参考
- **人工审核**：高风险内容可设置人工审核

---

## 七、AI工具配置

### 7.1 配置目录结构

```
configs/tools/party_ai/
├── categories.yaml          # 工具分类
├── three_meetings.yaml      # 三会一课一键生成
├── party_education.yaml     # 党员教育学习材料生成
├── work_summary.yaml        # 工作总结与汇报材料生成
├── activity_plan.yaml       # 党日活动策划方案生成
├── smart_qa.yaml            # 党规党纪智能问答
└── prompts/
    ├── three_meetings.md
    ├── party_education.md
    ├── work_summary.md
    ├── activity_plan.md
    └── smart_qa.md
```

### 7.2 工具分类（categories.yaml）

```yaml
categories:
  - name: "智能文稿生成"
    order: 1
    tools:
      - three_meetings
      - party_education
      - work_summary
      - activity_plan

  - name: "智能问答"
    order: 2
    tools:
      - smart_qa
```

### 7.3 工具配置示例（three_meetings.yaml）

```yaml
tool_id: "three_meetings"
name: "三会一课一键生成"
description: "输入会议基本信息，AI自动生成符合规范的党务会议文档"
category: "智能文稿生成"
system_prompt_file: "prompts/three_meetings.md"
welcome_message: "欢迎使用三会一课一键生成工具！请输入会议类型和主题，我将为您生成会议讲话稿、会议记录等材料。"
icon: "calendar"
order: 1
visible: true
type: "normal"
toolset_id: "party_ai"
content_type: "text"
```

### 7.4 提示词设计要点

每个AI工具的提示词包含：
- **角色定位**：明确AI的专业身份（如"资深的党务工作助手"）
- **任务描述**：清晰说明需要完成什么任务
- **输入格式**：定义用户需要提供哪些信息
- **输出格式**：定义生成内容的结构和格式
- **质量要求**：政治正确、表述规范、内容准确
- **示例参考**：提供1-2个优质示例（可选）

---

## 八、实施任务清单

### 阶段一：基础设施改造

1. ✅ UI主题改造
   - 创建党建主题样式变量
   - 修改导航栏、按钮、表格样式
   - 添加党徽等党建元素

2. ✅ AI工具配置
   - 创建party_ai工具集目录
   - 配置5个AI工具（YAML + 提示词）
   - 更新导航配置

3. ✅ 数据库迁移
   - 设计并创建party_members表
   - 设计并创建organization_activities表
   - 设计并创建party_fee_records表
   - 设计并创建party_fee_standards表
   - 设计并创建knowledge_documents表
   - 设计并创建knowledge_categories表
   - 编写Alembic迁移脚本

### 阶段二：后端API开发

4. ✅ 党员管理API
   - CRUD接口（增删改查）
   - 批量导入导出
   - 流动党员管理
   - 党费标准计算

5. ✅ 组织生活API
   - 活动记录CRUD
   - 照片上传
   - 统计报表接口

6. ✅ 党费管理API
   - 缴费记录CRUD
   - 党费计算器
   - 欠缴统计
   - 缴费提醒

7. ✅ 知识库RAG
   - 文档上传接口
   - 文档解析与分块
   - 向量化处理
   - RAG检索接口
   - 智能问答接口

### 阶段三：前端页面开发

8. ✅ 党员管理页面（/admin/party-members）
   - 党员列表（表格）
   - 新增/编辑表单
   - 批量导入导出
   - 详情查看

9. ✅ 组织生活管理页面（/admin/organization-life）
   - 活动列表
   - 新增/编辑表单
   - 照片上传
   - 统计图表

10. ✅ 党费管理页面（/admin/party-fees）
    - 缴费记录列表
    - 党费标准设置
    - 统计报表
    - 欠缴名单

11. ✅ 知识库管理页面（/knowledge-base）
    - 文档列表
    - 上传界面
    - 分类管理
    - 预览功能

### 阶段四：权限与优化

12. ✅ 权限控制实现
    - 4级角色定义
    - 权限中间件
    - 数据隔离
    - 前端路由守卫

13. ✅ 测试与优化
    - 单元测试（后端）
    - 组件测试（前端）
    - E2E测试
    - 性能优化
    - 安全加固

---

## 九、技术依赖

### 后端新增依赖

```txt
# requirements.txt 新增
chromadb>=0.4.0          # 向量数据库
langchain>=0.1.0         # RAG框架
dashscope>=1.0.0         # 通义千问SDK
pypdf2>=3.0.0           # PDF解析
python-docx>=1.0.0      # Word解析
```

### 前端依赖
无需新增，复用现有库

---

## 十、风险与应对

### 10.1 政治合规风险
**风险**：AI生成内容政治不正确、出现错误表述
**应对**：
- 使用国家备案的国产大模型
- 建立敏感词过滤机制
- 人工审核关键内容
- 建立快速响应机制

### 10.2 知识库质量风险
**风险**：知识库内容不准确、更新不及时
**应对**：
- 权威来源优先（共产党员网）
- 定期更新机制
- 内容审核流程
- 用户反馈机制

### 10.3 用户接受度风险
**风险**：用户对AI工具不信任、不愿使用
**应对**：
- 充分测试，确保质量
- 提供详细的使用指引
- 收集反馈，快速迭代
- 培训和支持

---

## 十一、后续迭代方向

### V1.5（3-6个月后）
- 党员发展流程跟踪
- 积分制考核系统
- 数据分析大屏
- 移动端优化

### V2.0（6-12个月后）
- 宣传内容生成
- AI语音客服
- 对接官方党建系统
- 对接企业微信/钉钉

---

## 附录

### A. 参考文档
- 党建AI智能平台功能需求规格说明书.md
- 中国共产党章程
- 中国共产党基层组织工作条例
- 关于中国共产党党费收缴、使用和管理的规定

### B. 设计决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| UI风格 | 现代党建风（红色+简约） | 既体现党建特色又保持现代化 |
| AI工具配置 | YAML配置文件 | 复用现有架构，开发效率高 |
| 知识库实现 | 向量RAG系统 | AI回答质量高，可扩展 |
| 后台管理 | 扩展现有Admin | 系统统一，维护方便 |
| 向量数据库 | Chroma | 轻量级，适合MVP快速迭代 |
| Embedding模型 | 通义千问 | 国产合规，性能优秀 |
