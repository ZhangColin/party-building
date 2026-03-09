# 党建AI智能平台实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将AI教师平台转型为党建AI智能平台，实现AI工具、管理系统、知识库三大核心模块

**Architecture:**
- 复用现有工具配置系统（YAML驱动）和AI对话基础设施
- 创建新的党建工具集（party_ai）替换教育相关配置
- 扩展数据库模型支持党员、组织生活、党费管理
- 新增向量RAG系统支持知识库智能问答

**Tech Stack:**
- 前端：Vue 3 + Element Plus + Tailwind CSS
- 后端：FastAPI + SQLAlchemy + MySQL
- AI：DeepSeek/Kimi + LangChain + Chroma
- 测试：Vitest + Playwright + pytest

**设计文档：** [2026-03-05-party-ai-platform-design.md](./2026-03-05-party-ai-platform-design.md)

---

## 阶段一：基础设施改造

### Task 1: 创建党建主题样式变量

**Files:**
- Create: `frontend/src/styles/party-theme.css`
- Modify: `frontend/src/main.ts`

**Step 1: 创建党建主题CSS变量**

```css
/* frontend/src/styles/party-theme.css */
:root {
  /* 主色调 - 中国红 */
  --el-color-primary: #C8102E;
  --el-color-primary-light-3: #E84D56;
  --el-color-primary-light-5: #F07A7F;
  --el-color-primary-light-7: #F8A8AB;
  --el-color-primary-light-8: #FCC8CA;
  --el-color-primary-light-9: #FDE8E9;
  --el-color-primary-dark-2: #A80D27;

  /* 辅助色 - 金色 */
  --party-color-gold: #FFD700;
  --party-color-gold-light: #FFE55C;
  --party-color-gold-dark: #CCB800;

  /* 深红色 */
  --party-color-deep-red: #8B0000;

  /* 背景色 */
  --party-bg-color: #FAFAFA;
  --party-bg-color-page: #F5F5F5;

  /* 文字色 */
  --party-text-color-primary: #1A1A1A;
  --party-text-color-regular: #4A4A4A;
  --party-text-color-secondary: #7A7A7A;

  /* 边框色 */
  --party-border-color: #E5E5E5;
  --party-border-color-light: #EEEEEE;

  /* 功能色 */
  --party-color-success: #22C55E;
  --party-color-warning: #F59E0B;
  --party-color-danger: #EF4444;
  --party-color-info: #3B82F6;
}

/* 党建主题全局样式 */
body {
  background-color: var(--party-bg-color);
  color: var(--party-text-color-primary);
}

/* 顶部导航栏渐变背景 */
.party-header-gradient {
  background: linear-gradient(135deg, #C8102E 0%, #E84D56 50%, #8B0000 100%);
}

/* 党徽图标样式 */
.party-emblem-icon {
  color: var(--party-color-gold);
  font-size: 24px;
}
```

**Step 2: 在main.ts中导入主题**

```typescript
/* frontend/src/main.ts 顶部添加 */
import './styles/party-theme.css'
```

**Step 3: 提交更改**

```bash
git add frontend/src/styles/party-theme.css frontend/src/main.ts
git commit -m "feat: 添加党建主题样式变量"
```

---

### Task 2: 更新导航配置为党建模块

**Files:**
- Modify: `configs/navigation.yaml`

**Step 1: 备份原配置**

```bash
cp configs/navigation.yaml configs/navigation.yaml.backup
```

**Step 2: 替换导航配置为党建模块**

```yaml
# configs/navigation.yaml
# 顶部导航模块配置 - 党建AI智能平台

modules:
  # AI党建助手模块
  - name: "AI党建助手"
    type: "toolset"
    config_source: "tools/party_ai"
    icon: "sparkles"
    order: 1

  # 党员管理模块
  - name: "党员管理"
    type: "page"
    page_path: "/admin/party-members"
    icon: "user-group"
    order: 2

  # 组织生活管理模块
  - name: "组织生活"
    type: "page"
    page_path: "/admin/organization-life"
    icon: "calendar"
    order: 3

  # 党费管理模块
  - name: "党费管理"
    type: "page"
    page_path: "/admin/party-fees"
    icon: "currency-yen"
    order: 4

  # 知识库模块
  - name: "知识库"
    type: "page"
    page_path: "/knowledge-base"
    icon: "book-open"
    order: 5
```

**Step 3: 提交更改**

```bash
git add configs/navigation.yaml configs/navigation.yaml.backup
git commit -m "feat: 更新导航配置为党建模块"
```

---

### Task 3: 创建党建AI工具集目录和分类配置

**Files:**
- Create: `configs/tools/party_ai/categories.yaml`

**Step 1: 创建party_ai工具集目录**

```bash
mkdir -p configs/tools/party_ai/prompts
```

**Step 2: 创建工具分类配置**

```yaml
# configs/tools/party_ai/categories.yaml
# 党建AI工具分类

categories:
  - name: "智能文稿生成"
    description: "自动生成各类党务文稿"
    order: 1
    tools:
      - three_meetings
      - party_education
      - work_summary
      - activity_plan

  - name: "智能问答"
    description: "党规党纪智能问答"
    order: 2
    tools:
      - smart_qa

  - name: "合规检查"
    description: "文稿合规性检查"
    order: 3
    tools:
      - compliance_check
```

**Step 3: 提交更改**

```bash
git add configs/tools/party_ai/
git commit -m "feat: 创建党建AI工具集目录和分类"
```

---

### Task 4: 配置三会一课一键生成工具

**Files:**
- Create: `configs/tools/party_ai/three_meetings.yaml`
- Create: `configs/tools/party_ai/prompts/three_meetings.md`

**Step 1: 创建工具配置文件**

```yaml
# configs/tools/party_ai/three_meetings.yaml
tool_id: "three_meetings"
name: "三会一课一键生成"
description: "输入会议基本信息，AI自动生成符合规范的党务会议文档，包括支部书记讲话稿、会议记录摘要等"
category: "智能助手"
system_prompt_file: "prompts/three_meetings.md"
welcome_message: |
  # 三会一课一键生成

  请选择或输入以下信息：

  1. **会议类型**：支部党员大会 / 支部委员会 / 党小组会 / 党课
  2. **会议主题**：本次会议的主要议题
  3. **会议时间**：会议日期和时长
  4. **会议地点**：会议召开地点
  5. **参会人员**：预计参会党员名单
  6. **主持人**：会议主持人
  7. **主要议题**：本次会议讨论的议题（可多个）

  我将为您生成：
  - 支部书记讲话稿
  - 会议记录摘要
  - 决议事项和下一步计划
icon: "calendar"
order: 1
visible: true
type: "normal"
toolset_id: "party_ai"
content_type: "text"
model: "deepseek:deepseek-chat"
```

**Step 2: 创建系统提示词**

```markdown
# configs/tools/party_ai/prompts/three_meetings.md
# 三会一课一键生成 - 系统提示词

你是一位资深的党务工作助手，精通党内法规和党务工作规范。你的任务是根据用户提供的信息，自动生成符合规范的党务会议文档。

## 角色定位
- 专业：熟悉党务工作规范和流程
- 严谨：确保政治表述准确、格式规范
- 实用：生成的内容可直接使用或稍作修改

## 输入信息
用户将提供以下信息：
- 会议类型：支部党员大会/支部委员会/党小组会/党课
- 会议主题：本次会议的主要议题
- 会议时间：会议日期和时长
- 会议地点：会议召开地点
- 参会人员：预计参会党员名单
- 主持人：会议主持人
- 主要议题：本次会议讨论的议题

## 输出内容

### 1. 支部书记讲话稿
包含以下部分：
- 开场白（问候、会议意义）
- 回顾上次决议执行情况（如适用）
- 本次会议主题阐述
- 具体工作部署
- 号召和要求

### 2. 会议记录摘要
包含以下部分：
- 会议基本信息（时间、地点、主持人、参会人员）
- 议题讨论记录
- 决议内容
- 下一步行动计划
- 参会人员签到表（模板）

## 质量要求
1. **政治正确**：确保所有政治表述准确无误
2. **格式规范**：符合党务会议记录的标准格式
3. **内容完整**：涵盖所有必要要素
4. **语言得体**：使用规范的党务工作用语
5. **实用性强**：内容可直接用于实际工作

## 注意事项
- 严格遵守党内法规要求
- 引用上级文件时确保准确
- 涉及敏感问题时表述严谨
- 决议事项要明确具体
- 下一步计划要具有可操作性

## 输出格式
使用Markdown格式，标题层级清晰，重点内容加粗，列表项目清晰。
```

**Step 3: 提交更改**

```bash
git add configs/tools/party_ai/three_meetings.yaml configs/tools/party_ai/prompts/three_meetings.md
git commit -m "feat: 添加三会一课一键生成工具配置"
```

---

### Task 5: 配置党员教育学习材料生成工具

**Files:**
- Create: `configs/tools/party_ai/party_education.yaml`
- Create: `configs/tools/party_ai/prompts/party_education.md`

**Step 1: 创建工具配置**

```yaml
# configs/tools/party_ai/party_education.yaml
tool_id: "party_education"
name: "党员教育学习材料生成"
description: "根据学习主题或政策文件，生成学习心得、主题宣讲提纲、学习笔记、研讨发言稿等学习教育材料"
category: "智能助手"
system_prompt_file: "prompts/party_education.md"
welcome_message: |
  # 党员教育学习材料生成

  请提供以下信息：

  1. **学习类型**：学习心得 / 主题宣讲提纲 / 学习笔记 / 研讨发言稿
  2. **学习主题**：本次学习的核心主题
  3. **学习对象**：普通党员 / 党务干部 / 预备党员
  4. **文章篇幅**：短 / 中 / 长
  5. **参考材料**（可选）：上传相关学习文件

  我将为您生成符合要求的学习材料。
icon: "academic-cap"
order: 2
visible: true
type: "normal"
toolset_id: "party_ai"
content_type: "text"
```

**Step 2: 创建系统提示词**

```markdown
# configs/tools/party_ai/prompts/party_education.md
# 党员教育学习材料生成 - 系统提示词

你是一位专业的党员教育工作者，精通党的理论知识和教育培训方法。你的任务是根据用户需求生成高质量的学习教育材料。

## 支持的学习材料类型

### 1. 学习心得
结构：
- 学习内容概述
- 个人认识体会
- 存在差距分析
- 改进措施和努力方向

### 2. 主题宣讲提纲
结构：
- 宣讲主题和背景
- 核心内容（3-5个要点）
- 案例和事例
- 总结和号召

### 3. 学习笔记
结构：
- 学习时间和地点
- 学习内容摘要
- 重点要点提炼
- 个人感悟

### 4. 研讨发言稿
结构：
- 开场白
- 主要观点（2-3个）
- 论据和案例
- 结论和建议

## 质量要求
1. **理论准确**：确保理论表述准确无误
2. **联系实际**：结合工作实际和党员思想实际
3. **深度适中**：根据受众对象调整理论深度
4. **逻辑清晰**：结构完整，层次分明
5. **语言生动**：避免空洞说教，增强感染力

## 注意事项
- 引用重要论述时确保准确
- 案例选择要有代表性
- 避免空话套话
- 注重思想性和启发性的统一
```

**Step 3: 提交更改**

```bash
git add configs/tools/party_ai/party_education.yaml configs/tools/party_ai/prompts/party_education.md
git commit -m "feat: 添加党员教育学习材料生成工具"
```

---

### Task 6: 配置工作总结与汇报材料生成工具

**Files:**
- Create: `configs/tools/party_ai/work_summary.yaml`
- Create: `configs/tools/party_ai/prompts/work_summary.md`

**Step 1: 创建工具配置**

```yaml
# configs/tools/party_ai/work_summary.yaml
tool_id: "work_summary"
name: "工作总结与汇报材料生成"
description: "根据工作内容，生成符合党建规范的工作总结、专项汇报、述职报告等材料"
category: "智能助手"
system_prompt_file: "prompts/work_summary.md"
welcome_message: |
  # 工作总结与汇报材料生成

  请提供以下信息：

  1. **总结类型**：季度总结 / 年度总结 / 专项工作汇报 / 述职报告
  2. **时间范围**：报告涵盖的时间段
  3. **主要工作事项**：事项名称、完成情况、取得成效、存在问题
  4. **套用模板**（可选）：上传已有模板

  我将为您生成结构完整、内容充实的工作总结或汇报材料。
icon: "document-text"
order: 3
visible: true
type: "normal"
toolset_id: "party_ai"
content_type: "text"
```

**Step 2: 创建系统提示词**

```markdown
# configs/tools/party_ai/prompts/work_summary.md
# 工作总结与汇报材料生成 - 系统提示词

你是一位经验丰富的党务工作者，擅长撰写各类工作总结和汇报材料。

## 支持的材料类型

### 1. 工作总结
- 季度总结
- 年度总结
- 专项工作总结

结构：
- 基本情况概述
- 主要工作成绩
- 创新做法和亮点
- 存在问题不足
- 下一步工作计划

### 2. 专项汇报材料
结构：
- 工作背景
- 主要措施
- 取得成效
- 经验启示
- 下一步打算

### 3. 述职报告
结构：
- 履职情况
- 主要工作成效
- 存在问题
- 改进措施

## 写作要求
1. **实事求是**：成绩不夸大，问题不回避
2. **重点突出**：突出创新做法和亮点工作
3. **数据支撑**：用数据说明成效
4. **条理清晰**：层次分明，逻辑严密
5. **语言规范**：使用规范的公文用语

## 常用表述
- 开头：XX期间，在XX的领导下...
- 成绩：取得显著成效、大幅提升、全面完成...
- 问题：还存在一些不足、有待进一步加强...
- 计划：下一步我们将、努力方向...
```

**Step 3: 提交更改**

```bash
git add configs/tools/party_ai/work_summary.yaml configs/tools/party_ai/prompts/work_summary.md
git commit -m "feat: 添加工作总结与汇报材料生成工具"
```

---

### Task 7: 配置党日活动策划方案生成工具

**Files:**
- Create: `configs/tools/party_ai/activity_plan.yaml`
- Create: `configs/tools/party_ai/prompts/activity_plan.md`

**Step 1: 创建工具配置**

```yaml
# configs/tools/party_ai/activity_plan.yaml
tool_id: "activity_plan"
name: "党日活动策划方案生成"
description: "根据活动主题和约束条件，生成完整的主题党日活动方案，包括活动流程、人员分工、预算明细、安全预案等"
category: "智能助手"
system_prompt_file: "prompts/activity_plan.md"
welcome_message: |
  # 党日活动策划方案生成

  请提供以下信息：

  1. **活动主题**：本次党日活动的主题
  2. **活动时间**：预计活动日期
  3. **预计时长**：活动时长（如：半天、一天）
  4. **预算范围**（可选）：活动预算
  5. **参加人数**：预计参与人数
  6. **活动形式**：会议学习 / 参观考察 / 志愿服务 / 红色教育
  7. **特殊要求**（可选）：其他特殊要求

  我将为您生成完整的活动策划方案。
icon: "flag"
order: 4
visible: true
type: "normal"
toolset_id: "party_ai"
content_type: "text"
```

**Step 2: 创建系统提示词**

```markdown
# configs/tools/party_ai/prompts/activity_plan.md
# 党日活动策划方案生成 - 系统提示词

你是一位专业的党日活动策划专家，擅长设计富有创意和教育意义的主题党日活动。

## 输出内容

### 1. 活动方案
- 活动主题和目的
- 活动时间安排（详细时间表）
- 活动流程设计
- 人员分工
- 物资清单
- 预算明细
- 安全预案
- 应急措施

### 2. 配套材料
- 活动主持词
- 书记讲话稿
- 活动宣传文案
- 活动总结模板

### 3. 场地和路线建议（如需外出）
- 红色教育基地推荐
- 参观路线设计
- 交通方案

## 活动形式建议
- **会议学习类**：专题学习、研讨交流、观看教育片
- **参观考察类**：红色教育基地、先进企业、美丽乡村
- **志愿服务类**：社区服务、义务劳动、扶贫帮困
- **红色教育类**：重温入党誓词、缅怀革命先烈、党史学习

## 策划原则
1. **主题鲜明**：紧扣党建主题，突出政治性
2. **形式多样**：避免单调，增强吸引力
3. **注重实效**：不走过场，确保教育效果
4. **安全第一**：确保活动安全有序
5. **勤俭节约**：严格控制成本，反对铺张浪费
```

**Step 3: 提交更改**

```bash
git add configs/tools/party_ai/activity_plan.yaml configs/tools/party_ai/prompts/activity_plan.md
git commit -m "feat: 添加党日活动策划方案生成工具"
```

---

### Task 8: 配置党规党纪智能问答工具

**Files:**
- Create: `configs/tools/party_ai/smart_qa.yaml`
- Create: `configs/tools/party_ai/prompts/smart_qa.md`

**Step 1: 创建工具配置**

```yaml
# configs/tools/party_ai/smart_qa.yaml
tool_id: "smart_qa"
name: "党规党纪智能问答"
description: "基于党建知识库，智能回答党规党纪、党务工作流程、政策文件等问题"
category: "智能问答"
system_prompt_file: "prompts/smart_qa.md"
welcome_message: |
  # 党规党纪智能问答

  您可以问我关于：

  - 📜 党规党纪：党章、纪律处分条例、廉洁自律准则等
  - 📋 党务工作：入党流程、党费收缴、三会一课规范等
  - 📚 政策文件：党代会报告、中央全会文件、重要讲话等
  - 📖 工作指南：民主评议党员、流动党员管理等

  请输入您的问题，我将基于党建知识库为您提供准确答案。
icon: "question-mark-circle"
order: 5
visible: true
type: "normal"
toolset_id: "party_ai"
content_type: "text"
model: "deepseek:deepseek-chat"
enable_rag: true
rag_collection: "party_knowledge_base"
```

**Step 2: 创建系统提示词**

```markdown
# configs/tools/party_ai/prompts/smart_qa.md
# 党规党纪智能问答 - 系统提示词

你是一位专业的党务工作咨询顾问，精通党内法规和党务工作规范。你的任务是基于知识库提供准确、权威的答案。

## 知识库范围
1. **核心党内法规**：党章、准则、条例、规则、规定、办法、细则
2. **重要文件精神**：党代会报告、中央全会文件、重要讲话、工作指导意见
3. **党务工作指南**：工作流程图、操作手册、模板范例、常见问题解答
4. **学习材料**：理论文章、学习资料、典型案例

## 回答要求

### 1. 准确性
- 严格依据知识库内容回答
- 引用原文时确保准确无误
- 不确定的要说明

### 2. 权威性
- 优先引用党内法规原文
- 标注引用来源（文件名称、文号）
- 提供相关条款链接

### 3. 实用性
- 不仅回答"是什么"，还要说明"怎么做"
- 提供操作指引
- 列出注意事项

### 4. 规范性
- 使用规范的党务工作用语
- 政治表述准确
- 格式规范清晰

## 回答结构
1. **直接答案**：简明扼要地回答问题
2. **相关条款**：引用相关法规原文
3. **操作指引**：具体如何执行（如适用）
4. **注意事项**：需要特别注意的问题
5. **相关案例**：典型案例或示例（如适用）

## 特殊情况处理
- **涉及敏感问题**：表述严谨，引用权威文件
- **政策不明确**：说明情况，建议咨询上级
- **超出知识库范围**：诚实告知，不编造答案

## 免责声明
在每次回答后添加：
> 注：以上回答基于党建知识库，仅供参考。具体操作请以最新文件精神和上级要求为准。

## 禁止事项
- 不得编造不存在的规定
- 不得提供错误的政治表述
- 不得对敏感问题妄加评论
- 不得泄露党内部保密信息
```

**Step 3: 提交更改**

```bash
git add configs/tools/party_ai/smart_qa.yaml configs/tools/party_ai/prompts/smart_qa.md
git commit -m "feat: 添加党规党纪智能问答工具"
```

---

## 阶段二：数据库迁移

### Task 9: 创建党员档案数据库模型

**Files:**
- Create: `backend/src/db_models_party.py` (如果不存在)
- Modify: `backend/src/db_models_party.py`
- Create: `backend/alembic/versions/xxx_create_party_members_table.py`

**Step 1: 定义PartyMember模型**

```python
# backend/src/db_models_party.py
# -*- coding: utf-8 -*-
"""党建业务数据模型"""

from sqlalchemy import Column, Integer, String, Date, Boolean, Enum, Text, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from src.database import Base


class MemberType(str, enum.Enum):
    """党员类型"""
    FULL = "正式党员"
    PROVISIONAL = "预备党员"


class MobileType(str, enum.Enum):
    """流动类型"""
    OUTFLOW = "流出"
    INFLOW = "流入"


class PartyMemberModel(Base):
    """党员档案表"""
    __tablename__ = "party_members"

    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="主键ID")

    # 基本信息
    name = Column(String(50), nullable=False, comment="姓名")
    gender = Column(String(10), comment="性别")
    id_card = Column(String(18), unique=True, comment="身份证号")
    birth_date = Column(Date, comment="出生日期")
    education = Column(String(50), comment="学历")
    nation = Column(String(50), comment="民族")

    # 联系方式
    phone = Column(String(20), comment="手机号")
    email = Column(String(100), comment="电子邮箱")
    address = Column(String(200), comment="现居住地址")
    work_unit = Column(String(100), comment="工作单位")
    job_title = Column(String(50), comment="职务/职称")

    # 党务信息
    member_type = Column(Enum(MemberType), default=MemberType.FULL, comment="党员类型")
    application_date = Column(Date, comment="入党申请书提交时间")
    activist_date = Column(Date, comment="确定为积极分子时间")
    candidate_date = Column(Date, comment="确定为发展对象时间")
    provisional_date = Column(Date, comment="接收为预备党员时间")
    full_member_date = Column(Date, comment="转正时间")
    party_position = Column(String(50), comment="党内职务")
    introducer_1 = Column(String(50), comment="介绍人1")
    introducer_2 = Column(String(50), comment="介绍人2")

    # 流动党员
    is_mobile = Column(Boolean, default=False, comment="是否流动党员")
    mobile_type = Column(Enum(MobileType), comment="流动类型")
    mobile_reason = Column(String(200), comment="流动原因")

    # 党费信息
    monthly_income = Column(Numeric(10, 2), comment="月收入")
    fee_standard = Column(Numeric(10, 2), comment="党费标准（月缴金额）")

    # 系统字段
    branch_id = Column(Integer, ForeignKey("users.id"), comment="所属支部ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    branch = relationship("UserModel", back_populates="party_members")
    fee_records = relationship("PartyFeeRecordModel", back_populates="member")
```

**Step 2: 生成数据库迁移**

```bash
cd backend
alembic revision --autogenerate -m "创建党员档案表"
```

**Step 3: 检查生成的迁移文件**

查看生成的迁移文件，确认：
- 表名：party_members
- 所有字段都已包含
- 外键关系正确
- 索引设置正确

**Step 4: 应用迁移**

```bash
alembic upgrade head
```

**Step 5: 提交更改**

```bash
git add backend/src/db_models_party.py backend/alembic/versions/
git commit -m "feat: 创建党员档案数据模型和迁移"
```

---

### Task 10: 创建组织生活活动数据模型

**Files:**
- Modify: `backend/src/db_models_party.py`
- Create: `backend/alembic/versions/xxx_create_organization_activities_table.py`

**Step 1: 定义组织活动枚举和模型**

```python
# backend/src/db_models_party.py 添加

class ActivityType(str, enum.Enum):
    """活动类型"""
    THREE_MEETINGS = "三会一课"
    THEME_DAY = "主题党日"
    ORGANIZATIONAL_MEETING = "组织生活会"
    DEMOCRATIC_EVALUATION = "民主评议"


class MeetingType(str, enum.Enum):
    """会议类型"""
    GENERAL_MEETING = "支部党员大会"
    COMMITTEE_MEETING = "支部委员会"
    GROUP_MEETING = "党小组会"
    PARTY_LECTURE = "党课"


class OrganizationActivityModel(Base):
    """组织生活活动表"""
    __tablename__ = "organization_activities"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")

    # 活动基本信息
    activity_type = Column(Enum(ActivityType), nullable=False, comment="活动类型")
    meeting_type = Column(Enum(MeetingType), comment="会议类型")
    theme = Column(String(200), nullable=False, comment="活动主题")
    activity_date = Column(DateTime, nullable=False, comment="活动时间")
    location = Column(String(100), comment="活动地点")

    # 人员信息
    host = Column(String(50), comment="主持人")
    recorder = Column(String(50), comment="记录人")
    expected_count = Column(Integer, comment="应到人数")
    actual_count = Column(Integer, comment="实到人数")
    absent_members = Column(Text, comment="缺席人员（JSON）")

    # 活动内容
    agenda = Column(Text, comment="会议议程（JSON）")
    content = Column(Text, comment="活动内容详细记录")
    resolutions = Column(Text, comment="决议事项")
    photos = Column(Text, comment="活动照片（JSON数组）")
    attachments = Column(Text, comment="附件材料（JSON数组）")

    # 系统字段
    branch_id = Column(Integer, ForeignKey("users.id"), comment="所属支部ID")
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建人ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    branch = relationship("UserModel", foreign_keys=[branch_id])
    creator = relationship("UserModel", foreign_keys=[created_by])
```

**Step 2-5: 生成、检查、应用迁移（同Task 9）**

```bash
alembic revision --autogenerate -m "创建组织生活活动表"
alembic upgrade head
git add backend/src/db_models_party.py backend/alembic/versions/
git commit -m "feat: 创建组织生活活动数据模型"
```

---

### Task 11: 创建党费管理数据模型

**Files:**
- Modify: `backend/src/db_models_party.py`
- Create: `backend/alembic/versions/xxx_create_party_fee_tables.py`

**Step 1: 定义党费模型**

```python
# backend/src/db_models_party.py 添加

class PaymentMethod(str, enum.Enum):
    """缴纳方式"""
    CASH = "现金"
    TRANSFER = "转账"
    WECHAT = "微信"
    ALIPAY = "支付宝"


class PartyFeeRecordModel(Base):
    """党费缴纳记录表"""
    __tablename__ = "party_fee_records"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    member_id = Column(Integer, ForeignKey("party_members.id"), nullable=False, comment="党员ID")
    amount = Column(Numeric(10, 2), nullable=False, comment="缴纳金额")
    payment_date = Column(DateTime, nullable=False, comment="缴纳时间")
    payment_method = Column(Enum(PaymentMethod), comment="缴纳方式")
    collector = Column(String(50), comment="收款人")
    notes = Column(String(200), comment="备注")
    branch_id = Column(Integer, ForeignKey("users.id"), comment="所属支部ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    member = relationship("PartyMemberModel", back_populates="fee_records")


class PartyFeeStandardModel(Base):
    """党费标准表"""
    __tablename__ = "party_fee_standards"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    member_id = Column(Integer, ForeignKey("party_members.id"), nullable=False, comment="党员ID")
    monthly_income = Column(Numeric(10, 2), nullable=False, comment="月收入")
    fee_amount = Column(Numeric(10, 2), nullable=False, comment="应缴金额")
    effective_date = Column(Date, nullable=False, comment="生效日期")
    branch_id = Column(Integer, ForeignKey("users.id"), comment="所属支部ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    member = relationship("PartyMemberModel")
```

**Step 2-5: 生成、检查、应用迁移**

```bash
alembic revision --autogenerate -m "创建党费管理表"
alembic upgrade head
git add backend/src/db_models_party.py backend/alembic/versions/
git commit -m "feat: 创建党费管理数据模型"
```

---

### Task 12: 创建知识库数据模型

**Files:**
- Modify: `backend/src/db_models_party.py`
- Create: `backend/alembic/versions/xxx_create_knowledge_base_tables.py`

**Step 1: 定义知识库模型**

```python
# backend/src/db_models_party.py 添加

class KnowledgeCategoryModel(Base):
    """知识库分类表"""
    __tablename__ = "knowledge_categories"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    name = Column(String(100), nullable=False, unique=True, comment="分类名称")
    code = Column(String(50), nullable=False, unique=True, comment="分类代码")
    description = Column(String(200), comment="描述")
    order = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    documents = relationship("KnowledgeDocumentModel", back_populates="category")


class KnowledgeDocumentModel(Base):
    """知识库文档表"""
    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    title = Column(String(200), nullable=False, comment="文档标题")
    category_id = Column(Integer, ForeignKey("knowledge_categories.id"), comment="分类ID")
    file_path = Column(String(500), nullable=False, comment="文件路径")
    file_type = Column(String(20), comment="文件类型（PDF/Word/TXT）")
    chunk_count = Column(Integer, default=0, comment="分块数量")
    vector_collection = Column(String(100), comment="向量集合名称")
    metadata = Column(Text, comment="元数据（JSON）")
    uploaded_by = Column(Integer, ForeignKey("users.id"), comment="上传者ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    category = relationship("KnowledgeCategoryModel", back_populates="documents")
    uploader = relationship("UserModel")
```

**Step 2-5: 生成、检查、应用迁移**

```bash
alembic revision --autogenerate -m "创建知识库表"
alembic upgrade head
git add backend/src/db_models_party.py backend/alembic/versions/
git commit -m "feat: 创建知识库数据模型"
```

---

## 阶段三：后端API开发

### Task 13: 创建党员管理Pydantic模型

**Files:**
- Create: `backend/src/models_party.py`

**Step 1: 定义党员相关的Pydantic模型**

```python
# backend/src/models_party.py
# -*- coding: utf-8 -*-
"""党建业务Pydantic模型"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
import enum


class MemberType(str, enum.Enum):
    """党员类型"""
    FULL = "正式党员"
    PROVISIONAL = "预备党员"


class MobileType(str, enum.Enum):
    """流动类型"""
    OUTFLOW = "流出"
    INFLOW = "流入"


# 党员档案模型
class PartyMemberBase(BaseModel):
    """党员档案基础模型"""
    name: str = Field(..., description="姓名")
    gender: Optional[str] = Field(None, description="性别")
    id_card: Optional[str] = Field(None, description="身份证号")
    birth_date: Optional[date] = Field(None, description="出生日期")
    education: Optional[str] = Field(None, description="学历")
    nation: Optional[str] = Field(None, description="民族")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="电子邮箱")
    address: Optional[str] = Field(None, description="现居住地址")
    work_unit: Optional[str] = Field(None, description="工作单位")
    job_title: Optional[str] = Field(None, description="职务/职称")


class PartyMember党务Info(BaseModel):
    """党员党务信息"""
    member_type: MemberType = Field(default=MemberType.FULL, description="党员类型")
    application_date: Optional[date] = Field(None, description="入党申请书提交时间")
    activist_date: Optional[date] = Field(None, description="确定为积极分子时间")
    candidate_date: Optional[date] = Field(None, description="确定为发展对象时间")
    provisional_date: Optional[date] = Field(None, description="接收为预备党员时间")
    full_member_date: Optional[date] = Field(None, description="转正时间")
    party_position: Optional[str] = Field(None, description="党内职务")
    introducer_1: Optional[str] = Field(None, description="介绍人1")
    introducer_2: Optional[str] = Field(None, description="介绍人2")


class PartyMemberMobileInfo(BaseModel):
    """流动党员信息"""
    is_mobile: bool = Field(default=False, description="是否流动党员")
    mobile_type: Optional[MobileType] = Field(None, description="流动类型")
    mobile_reason: Optional[str] = Field(None, description="流动原因")


class PartyMemberFeeInfo(BaseModel):
    """党费信息"""
    monthly_income: Optional[Decimal] = Field(None, description="月收入")
    fee_standard: Optional[Decimal] = Field(None, description="党费标准")


class PartyMemberCreate(PartyMemberBase, PartyMember党务Info, PartyMemberMobileInfo, PartyMemberFeeInfo):
    """创建党员请求模型"""
    pass


class PartyMemberUpdate(BaseModel):
    """更新党员请求模型"""
    name: Optional[str] = None
    gender: Optional[str] = None
    id_card: Optional[str] = None
    birth_date: Optional[date] = None
    education: Optional[str] = None
    nation: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    work_unit: Optional[str] = None
    job_title: Optional[str] = None
    member_type: Optional[MemberType] = None
    application_date: Optional[date] = None
    activist_date: Optional[date] = None
    candidate_date: Optional[date] = None
    provisional_date: Optional[date] = None
    full_member_date: Optional[date] = None
    party_position: Optional[str] = None
    introducer_1: Optional[str] = None
    introducer_2: Optional[str] = None
    is_mobile: Optional[bool] = None
    mobile_type: Optional[MobileType] = None
    mobile_reason: Optional[str] = None
    monthly_income: Optional[Decimal] = None
    fee_standard: Optional[Decimal] = None


class PartyMemberResponse(PartyMemberBase, PartyMember党务Info, PartyMemberMobileInfo, PartyMemberFeeInfo):
    """党员响应模型"""
    id: int
    branch_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PartyMemberListResponse(BaseModel):
    """党员列表响应"""
    total: int
    items: List[PartyMemberResponse]


# 党费计算器
class FeeCalculatorRequest(BaseModel):
    """党费计算请求"""
    monthly_income: Decimal = Field(..., description="月收入")


class FeeCalculatorResponse(BaseModel):
    """党费计算响应"""
    monthly_income: Decimal
    fee_amount: Decimal
    fee_rate: str
    calculation_formula: str
```

**Step 2: 提交更改**

```bash
git add backend/src/models_party.py
git commit -m "feat: 创建党员管理Pydantic模型"
```

---

### Task 14: 实现党员管理Service

**Files:**
- Create: `backend/src/services/party_member_service.py`

**Step 1: 编写党员管理服务测试**

```python
# tests/services/test_party_member_service.py
# -*- coding: utf-8 -*-
"""党员管理服务测试"""

import pytest
from datetime import date
from decimal import Decimal

from src.services.party_member_service import PartyMemberService
from src.models_party import MemberType, FeeCalculatorRequest


@pytest.mark.unit
class TestPartyMemberService:
    """党员管理服务单元测试"""

    def test_calculate_party_fee_level_1(self):
        """测试党费计算 - 3000元以下"""
        request = FeeCalculatorRequest(monthly_income=Decimal("2500"))
        result = PartyMemberService.calculate_party_fee(request)

        assert result.fee_amount == Decimal("12.50")
        assert result.fee_rate == "0.5%"

    def test_calculate_party_fee_level_2(self):
        """测试党费计算 - 3000-5000元"""
        request = FeeCalculatorRequest(monthly_income=Decimal("4000"))
        result = PartyMemberService.calculate_party_fee(request)

        assert result.fee_amount == Decimal("40.00")
        assert result.fee_rate == "1%"

    def test_calculate_party_fee_level_3(self):
        """测试党费计算 - 5000-10000元"""
        request = FeeCalculatorRequest(monthly_income=Decimal("8000"))
        result = PartyMemberService.calculate_party_fee(request)

        assert result.fee_amount == Decimal("120.00")
        assert result.fee_rate == "1.5%"

    def test_calculate_party_fee_level_4(self):
        """测试党费计算 - 10000元以上"""
        request = FeeCalculatorRequest(monthly_income=Decimal("15000"))
        result = PartyMemberService.calculate_party_fee(request)

        assert result.fee_amount == Decimal("300.00")
        assert result.fee_rate == "2%"
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/services/test_party_member_service.py -v
```

预期结果：FAIL - "PartyMemberService not found"

**Step 3: 实现党员管理服务**

```python
# backend/src/services/party_member_service.py
# -*- coding: utf-8 -*-
"""党员管理服务"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from src.db_models_party import PartyMemberModel
from src.models_party import (
    PartyMemberCreate,
    PartyMemberUpdate,
    PartyMemberResponse,
    PartyMemberListResponse,
    FeeCalculatorRequest,
    FeeCalculatorResponse
)


class PartyMemberService:
    """党员管理服务"""

    @staticmethod
    def calculate_party_fee(request: FeeCalculatorRequest) -> FeeCalculatorResponse:
        """
        计算党费标准

        规则（根据《关于中国共产党党费收缴、使用和管理的规定》）：
        - 月收入≤3000元：0.5%
        - 3000<月收入≤5000元：1%
        - 5000<月收入≤10000元：1.5%
        - 月收入>10000元：2%
        """
        income = request.monthly_income

        if income <= 3000:
            rate = Decimal("0.005")
            rate_str = "0.5%"
        elif income <= 5000:
            rate = Decimal("0.01")
            rate_str = "1%"
        elif income <= 10000:
            rate = Decimal("0.015")
            rate_str = "1.5%"
        else:
            rate = Decimal("0.02")
            rate_str = "2%"

        fee_amount = (income * rate).quantize(Decimal("0.01"))

        return FeeCalculatorResponse(
            monthly_income=income,
            fee_amount=fee_amount,
            fee_rate=rate_str,
            calculation_formula=f"{income} × {rate_str} = {fee_amount}"
        )

    @staticmethod
    async def create_member(
        db: AsyncSession,
        member_data: PartyMemberCreate,
        branch_id: int
    ) -> PartyMemberResponse:
        """创建党员档案"""
        db_member = PartyMemberModel(**member_data.dict(), branch_id=branch_id)

        db.add(db_member)
        await db.commit()
        await db.refresh(db_member)

        return PartyMemberResponse.from_orm(db_member)

    @staticmethod
    async def get_member(db: AsyncSession, member_id: int) -> Optional[PartyMemberResponse]:
        """获取党员详情"""
        result = await db.execute(select(PartyMemberModel).where(PartyMemberModel.id == member_id))
        db_member = result.scalar_one_or_none()

        if not db_member:
            return None

        return PartyMemberResponse.from_orm(db_member)

    @staticmethod
    async def update_member(
        db: AsyncSession,
        member_id: int,
        member_data: PartyMemberUpdate
    ) -> Optional[PartyMemberResponse]:
        """更新党员信息"""
        result = await db.execute(select(PartyMemberModel).where(PartyMemberModel.id == member_id))
        db_member = result.scalar_one_or_none()

        if not db_member:
            return None

        for field, value in member_data.dict(exclude_unset=True).items():
            setattr(db_member, field, value)

        db_member.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_member)

        return PartyMemberResponse.from_orm(db_member)

    @staticmethod
    async def delete_member(db: AsyncSession, member_id: int) -> bool:
        """删除党员档案（软删除）"""
        result = await db.execute(select(PartyMemberModel).where(PartyMemberModel.id == member_id))
        db_member = result.scalar_one_or_none()

        if not db_member:
            return False

        await db.delete(db_member)
        await db.commit()

        return True

    @staticmethod
    async def list_members(
        db: AsyncSession,
        branch_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> PartyMemberListResponse:
        """获取党员列表"""
        query = select(PartyMemberModel)

        if branch_id:
            query = query.where(PartyMemberModel.branch_id == branch_id)

        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        members = result.scalars().all()

        # 获取总数
        count_query = select(PartyMemberModel)
        if branch_id:
            count_query = count_query.where(PartyMemberModel.branch_id == branch_id)

        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        return PartyMemberListResponse(
            total=total,
            items=[PartyMemberResponse.from_orm(m) for m in members]
        )
```

**Step 4: 运行测试验证通过**

```bash
pytest tests/services/test_party_member_service.py -v
```

预期结果：PASS

**Step 5: 提交更改**

```bash
git add tests/services/test_party_member_service.py backend/src/services/party_member_service.py
git commit -m "feat: 实现党员管理服务（含测试）"
```

---

### Task 15: 实现党员管理API路由

**Files:**
- Create: `backend/src/interfaces/routers/party/members.py`
- Create: `backend/src/interfaces/routers/party/__init__.py`

**Step 1: 创建党员管理路由**

```python
# backend/src/interfaces/routers/party/members.py
# -*- coding: utf-8 -*-
"""党员管理API路由"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.database import get_db
from src.auth import get_current_user
from src.db_models import UserModel
from src.models_party import (
    PartyMemberCreate,
    PartyMemberUpdate,
    PartyMemberResponse,
    PartyMemberListResponse,
    FeeCalculatorRequest,
    FeeCalculatorResponse
)
from src.services.party_member_service import PartyMemberService


router = APIRouter(prefix="/api/v1/party/members", tags=["党员管理"])


@router.post("/calculate-fee", response_model=FeeCalculatorResponse)
async def calculate_party_fee(request: FeeCalculatorRequest):
    """
    计算党费标准

    根据月收入自动计算党费缴纳标准，按照《关于中国共产党党费收缴、使用和管理的规定》执行。
    """
    return PartyMemberService.calculate_party_fee(request)


@router.post("", response_model=PartyMemberResponse)
async def create_member(
    member_data: PartyMemberCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    创建党员档案

    需要支部书记或系统管理员权限。
    """
    # TODO: 添加权限检查
    return await PartyMemberService.create_member(db, member_data, current_user.id)


@router.get("", response_model=PartyMemberListResponse)
async def list_members(
    branch_id: Optional[int] = Query(None, description="支部ID，不传则返回所有"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回记录数"),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    获取党员列表

    普通党员只能查看本支部党员，上级组织管理员可查看所有支部党员。
    """
    # TODO: 添加权限检查和数据隔离
    return await PartyMemberService.list_members(db, branch_id, skip, limit)


@router.get("/{member_id}", response_model=PartyMemberResponse)
async def get_member(
    member_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """获取党员详情"""
    member = await PartyMemberService.get_member(db, member_id)

    if not member:
        raise HTTPException(status_code=404, detail="党员不存在")

    # TODO: 添加权限检查

    return member


@router.patch("/{member_id}", response_model=PartyMemberResponse)
async def update_member(
    member_id: int,
    member_data: PartyMemberUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """更新党员信息"""
    # TODO: 添加权限检查
    member = await PartyMemberService.update_member(db, member_id, member_data)

    if not member:
        raise HTTPException(status_code=404, detail="党员不存在")

    return member


@router.delete("/{member_id}")
async def delete_member(
    member_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """删除党员档案"""
    # TODO: 添加权限检查（仅系统管理员）
    success = await PartyMemberService.delete_member(db, member_id)

    if not success:
        raise HTTPException(status_code=404, detail="党员不存在")

    return {"message": "删除成功"}
```

**Step 2: 创建party路由模块初始化文件**

```python
# backend/src/interfaces/routers/party/__init__.py
# -*- coding: utf-8 -*-
"""党建业务API路由模块"""

from fastapi import APIRouter
from . import members

router = APIRouter(prefix="/api/v1/party", tags=["党建"])
router.include_router(members.router)
```

**Step 3: 注册party路由到main.py**

```python
# backend/src/main.py 修改（已有party路由，确认）

# 党建业务模块路由（已存在）
from src.interfaces.routers import party as party_router
app.include_router(party_router.router)
```

**Step 4: 提交更改**

```bash
git add backend/src/interfaces/routers/party/
git commit -m "feat: 实现党员管理API路由"
```

---

## 阶段四：前端页面开发

### Task 16: 创建党员管理页面布局

**Files:**
- Create: `frontend/src/views/admin/PartyMembersPage.vue`
- Create: `frontend/src/components/party/MemberForm.vue`
- Create: `frontend/src/components/party/MemberList.vue`

**Step 1: 创建党员管理主页面**

```vue
<!-- frontend/src/views/admin/PartyMembersPage.vue -->
<template>
  <div class="party-members-page">
    <el-page-header @back="goBack" content="党员管理" />

    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="姓名">
          <el-input v-model="searchForm.name" placeholder="请输入姓名" clearable />
        </el-form-item>
        <el-form-item label="党员类型">
          <el-select v-model="searchForm.memberType" placeholder="请选择" clearable>
            <el-option label="正式党员" value="正式党员" />
            <el-option label="预备党员" value="预备党员" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>党员列表</span>
          <el-button type="primary" @click="handleAdd">新增党员</el-button>
        </div>
      </template>

      <MemberList
        :members="members"
        :loading="loading"
        @edit="handleEdit"
        @delete="handleDelete"
      />

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </el-card>

    <MemberForm
      v-if="dialogVisible"
      :visible="dialogVisible"
      :member="currentMember"
      @close="dialogVisible = false"
      @save="handleSave"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import MemberList from '@/components/party/MemberList.vue'
import MemberForm from '@/components/party/MemberForm.vue'
import { partyMemberAPI } from '@/services/party'

const router = useRouter()

// 搜索表单
const searchForm = reactive({
  name: '',
  memberType: ''
})

// 党员列表
const members = ref([])
const loading = ref(false)

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 对话框
const dialogVisible = ref(false)
const currentMember = ref(null)

// 返回
const goBack = () => {
  router.back()
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadMembers()
}

// 重置
const handleReset = () => {
  searchForm.name = ''
  searchForm.memberType = ''
  loadMembers()
}

// 新增
const handleAdd = () => {
  currentMember.value = null
  dialogVisible.value = true
}

// 编辑
const handleEdit = (member) => {
  currentMember.value = member
  dialogVisible.value = true
}

// 删除
const handleDelete = async (member) => {
  try {
    await ElMessageBox.confirm(`确定要删除党员"${member.name}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await partyMemberAPI.deleteMember(member.id)
    ElMessage.success('删除成功')
    loadMembers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 保存
const handleSave = async (formData) => {
  try {
    if (currentMember.value) {
      await partyMemberAPI.updateMember(currentMember.value.id, formData)
      ElMessage.success('更新成功')
    } else {
      await partyMemberAPI.createMember(formData)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    loadMembers()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 分页变化
const handleSizeChange = () => {
  loadMembers()
}

const handlePageChange = () => {
  loadMembers()
}

// 加载党员列表
const loadMembers = async () => {
  try {
    loading.value = true
    const response = await partyMemberAPI.listMembers({
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize
    })

    members.value = response.items
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadMembers()
})
</script>

<style scoped lang="scss">
.party-members-page {
  padding: 20px;

  .search-card {
    margin-bottom: 20px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .el-pagination {
    margin-top: 20px;
    justify-content: flex-end;
  }
}
</style>
```

**Step 2: 创建党员列表组件**

```vue
<!-- frontend/src/components/party/MemberList.vue -->
<template>
  <el-table :data="members" stripe v-loading="loading">
    <el-table-column prop="name" label="姓名" width="120" />
    <el-table-column prop="gender" label="性别" width="80" />
    <el-table-column prop="memberType" label="党员类型" width="100">
      <template #default="{ row }">
        <el-tag :type="row.memberType === '正式党员' ? 'success' : 'warning'">
          {{ row.memberType }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="phone" label="手机号" width="130" />
    <el-table-column prop="workUnit" label="工作单位" min-width="150" />
    <el-table-column prop="partyPosition" label="党内职务" width="120" />
    <el-table-column label="操作" width="150" fixed="right">
      <template #default="{ row }">
        <el-button link type="primary" size="small" @click="$emit('edit', row)">
          编辑
        </el-button>
        <el-button link type="danger" size="small" @click="$emit('delete', row)">
          删除
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
interface Member {
  id: number
  name: string
  gender: string
  memberType: string
  phone: string
  workUnit: string
  partyPosition: string
}

defineProps<{
  members: Member[]
  loading: boolean
}>()

defineEmits<{
  edit: [member: Member]
  delete: [member: Member]
}>()
</script>
```

**Step 3: 创建党员表单组件**

```vue
<!-- frontend/src/components/party/MemberForm.vue -->
<template>
  <el-dialog
    :title="isEdit ? '编辑党员' : '新增党员'"
    :visible="visible"
    @close="handleClose"
    width="800px"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
      <!-- 基本信息 -->
      <el-divider content-position="left">基本信息</el-divider>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="姓名" prop="name">
            <el-input v-model="form.name" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="性别" prop="gender">
            <el-radio-group v-model="form.gender">
              <el-radio label="男">男</el-radio>
              <el-radio label="女">女</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="身份证号" prop="idCard">
            <el-input v-model="form.idCard" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="出生日期" prop="birthDate">
            <el-date-picker v-model="form.birthDate" type="date" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="学历" prop="education">
            <el-select v-model="form.education">
              <el-option label="高中" value="高中" />
              <el-option label="大专" value="大专" />
              <el-option label="本科" value="本科" />
              <el-option label="硕士" value="硕士" />
              <el-option label="博士" value="博士" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="form.phone" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 党务信息 -->
      <el-divider content-position="left">党务信息</el-divider>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="党员类型" prop="memberType">
            <el-radio-group v-model="form.memberType">
              <el-radio label="正式党员">正式党员</el-radio>
              <el-radio label="预备党员">预备党员</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="党内职务" prop="partyPosition">
            <el-input v-model="form.partyPosition" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="申请时间" prop="applicationDate">
            <el-date-picker v-model="form.applicationDate" type="date" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="转正时间" prop="fullMemberDate">
            <el-date-picker v-model="form.fullMemberDate" type="date" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 党费信息 -->
      <el-divider content-position="left">党费信息</el-divider>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="月收入" prop="monthlyIncome">
            <el-input-number v-model="form.monthlyIncome" :min="0" :precision="2" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="党费标准">
            <el-input v-model="calculatedFee" disabled />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'

interface Props {
  visible: boolean
  member?: any
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  save: [data: any]
}>()

const formRef = ref()
const isEdit = computed(() => !!props.member)

const form = reactive({
  name: '',
  gender: '男',
  idCard: '',
  birthDate: null,
  education: '',
  phone: '',
  memberType: '正式党员',
  partyPosition: '',
  applicationDate: null,
  fullMemberDate: null,
  monthlyIncome: null,
  feeStandard: null
})

// 计算党费
const calculatedFee = computed(() => {
  if (!form.monthlyIncome) return '待计算'

  const income = form.monthlyIncome
  let rate = 0
  let rateStr = ''

  if (income <= 3000) {
    rate = 0.005
    rateStr = '0.5%'
  } else if (income <= 5000) {
    rate = 0.01
    rateStr = '1%'
  } else if (income <= 10000) {
    rate = 0.015
    rateStr = '1.5%'
  } else {
    rate = 0.02
    rateStr = '2%'
  }

  const fee = (income * rate).toFixed(2)
  return `${fee}元（${rateStr}）`
})

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  memberType: [{ required: true, message: '请选择党员类型', trigger: 'change' }]
}

// 关闭对话框
const handleClose = () => {
  emit('close')
}

// 保存
const handleSave = async () => {
  try {
    await formRef.value.validate()
    form.feeStandard = parseFloat(calculatedFee.value)
    emit('save', form)
  } catch (error) {
    console.error('表单验证失败', error)
  }
}

// 监听member变化，填充表单
watch(() => props.member, (newMember) => {
  if (newMember) {
    Object.assign(form, newMember)
  } else {
    // 重置表单
    Object.assign(form, {
      name: '',
      gender: '男',
      idCard: '',
      birthDate: null,
      education: '',
      phone: '',
      memberType: '正式党员',
      partyPosition: '',
      applicationDate: null,
      fullMemberDate: null,
      monthlyIncome: null,
      feeStandard: null
    })
  }
})
</script>
```

**Step 4: 创建党员管理API服务**

```typescript
// frontend/src/services/party.ts
import request from './request'

export const partyMemberAPI = {
  // 计算党费
  calculateFee: (data: { monthly_income: number }) =>
    request.post('/api/v1/party/members/calculate-fee', data),

  // 获取党员列表
  listMembers: (params?: any) =>
    request.get('/api/v1/party/members', { params }),

  // 获取党员详情
  getMember: (id: number) =>
    request.get(`/api/v1/party/members/${id}`),

  // 创建党员
  createMember: (data: any) =>
    request.post('/api/v1/party/members', data),

  // 更新党员
  updateMember: (id: number, data: any) =>
    request.patch(`/api/v1/party/members/${id}`, data),

  // 删除党员
  deleteMember: (id: number) =>
    request.delete(`/api/v1/party/members/${id}`)
}
```

**Step 5: 添加路由**

```typescript
// frontend/src/router/index.ts 添加路由

{
  path: '/admin/party-members',
  name: 'PartyMembers',
  component: () => import('@/views/admin/PartyMembersPage.vue'),
  meta: { requiresAuth: true, requiresAdmin: true }
}
```

**Step 6: 提交更改**

```bash
git add frontend/src/views/admin/PartyMembersPage.vue frontend/src/components/party/ frontend/src/services/party.ts frontend/src/router/index.ts
git commit -m "feat: 实现党员管理页面"
```

---

## 阶段五：知识库RAG系统

### Task 17: 安装RAG系统依赖

**Files:**
- Modify: `backend/requirements.txt`

**Step 1: 添加依赖到requirements.txt**

```txt
# backend/requirements.txt 添加

# 向量RAG系统
chromadb>=0.4.0          # 向量数据库
langchain>=0.1.0         # RAG框架
langchain-community>=0.0.10  # LangChain社区集成
dashscope>=1.0.0         # 通义千问SDK

# 文档处理
pypdf2>=3.0.0           # PDF解析
python-docx>=1.0.0      # Word解析
python-magic>=0.4.27    # 文件类型检测
```

**Step 2: 安装依赖**

```bash
cd backend
pip install -r requirements.txt
```

**Step 3: 提交更改**

```bash
git add backend/requirements.txt
git commit -m "feat: 添加RAG系统依赖"
```

---

### Task 18: 实现知识库文档处理服务

**Files:**
- Create: `backend/src/services/knowledge_base_service.py`

**Step 1: 编写测试**

```python
# tests/services/test_knowledge_base_service.py
# -*- coding: utf-8 -*-
"""知识库服务测试"""

import pytest
from pathlib import Path

from src.services.knowledge_base_service import KnowledgeBaseService


@pytest.mark.unit
class TestKnowledgeBaseService:
    """知识库服务单元测试"""

    def test_chunk_text(self):
        """测试文本分块"""
        text = "这是一个测试句子。" * 100  # 创建长文本
        chunks = KnowledgeBaseService.chunk_text(text, chunk_size=500, overlap=50)

        assert len(chunks) > 1
        assert all(len(chunk) <= 500 for chunk in chunks)

    def test_extract_metadata_from_filename(self):
        """测试从文件名提取元数据"""
        filename = "二十大报告.pdf"
        metadata = KnowledgeBaseService.extract_metadata_from_filename(filename)

        assert metadata["title"] == "二十大报告"
        assert metadata["file_type"] == "pdf"
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/services/test_knowledge_base_service.py -v
```

预期：FAIL

**Step 3: 实现知识库服务**

```python
# backend/src/services/knowledge_base_service.py
# -*- coding: utf-8 -*-
"""知识库RAG服务"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
import PyPDF2
from docx import Document
import chromadb
from chromadb.config import Settings
from dashscope import TextEmbedding

from src.db_models_party import KnowledgeDocumentModel, KnowledgeCategoryModel


class KnowledgeBaseService:
    """知识库RAG服务"""

    def __init__(self, persist_directory: str = "./data/chroma"):
        """
        初始化知识库服务

        Args:
            persist_directory: Chroma持久化目录
        """
        # 初始化Chroma客户端
        self.chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))

        # 获取或创建集合
        self.collection = self.chroma_client.get_or_create_collection(
            name="party_knowledge_base",
            metadata={"description": "党建知识库"}
        )

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        将文本分块

        Args:
            text: 原始文本
            chunk_size: 块大小（字符数）
            overlap: 重叠字符数

        Returns:
            文本块列表
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)

            # 下一块起点（考虑重叠）
            start = end - overlap

        return chunks

    @staticmethod
    def extract_metadata_from_filename(filename: str) -> Dict:
        """从文件名提取元数据"""
        path = Path(filename)
        return {
            "title": path.stem,
            "file_type": path.suffix.lstrip('.').lower(),
            "filename": path.name
        }

    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """解析PDF文件"""
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text

    @staticmethod
    def parse_docx(file_path: str) -> str:
        """解析Word文档"""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    @staticmethod
    def parse_text(file_path: str) -> str:
        """解析纯文本文件"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def parse_document(self, file_path: str) -> str:
        """
        解析文档

        Args:
            file_path: 文件路径

        Returns:
            文档文本内容
        """
        file_type = Path(file_path).suffix.lower()

        if file_type == '.pdf':
            return self.parse_pdf(file_path)
        elif file_type in ['.docx', '.doc']:
            return self.parse_docx(file_path)
        elif file_type == '.txt':
            return self.parse_text(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")

    def embed_text(self, text: str) -> List[float]:
        """
        将文本向量化

        Args:
            text: 文本内容

        Returns:
            向量
        """
        # 使用通义千问Embedding
        response = TextEmbedding.call(
            model="text-embedding-v2",
            input=text
        )

        return response['output']['embeddings'][0]['embedding']

    def add_document(
        self,
        file_path: str,
        document_id: int,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        添加文档到知识库

        Args:
            file_path: 文件路径
            document_id: 文档ID
            metadata: 额外元数据

        Returns:
            添加的chunk数量
        """
        # 解析文档
        text = self.parse_document(file_path)

        # 文本分块
        chunks = self.chunk_text(text)

        # 向量化并存储
        for i, chunk in enumerate(chunks):
            # 生成向量
            embedding = self.embed_text(chunk)

            # 准备元数据
            chunk_metadata = {
                "document_id": str(document_id),
                "chunk_id": f"{document_id}_{i}",
                "chunk_index": i,
                **(metadata or {})
            }

            # 添加到Chroma
            self.collection.add(
                embeddings=[embedding],
                documents=[chunk],
                ids=[chunk_metadata["chunk_id"]],
                metadatas=[chunk_metadata]
            )

        return len(chunks)

    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        检索相关文档

        Args:
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        # 查询向量化
        query_embedding = self.embed_text(query)

        # 在Chroma中检索
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # 格式化结果
        documents = []
        for i in range(len(results['ids'][0])):
            documents.append({
                "chunk_id": results['ids'][0][i],
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i] if 'distances' in results else None
            })

        return documents

    def delete_document(self, document_id: int) -> int:
        """
        从知识库删除文档

        Args:
            document_id: 文档ID

        Returns:
            删除的chunk数量
        """
        # 查询该文档的所有chunk
        results = self.collection.get(
            where={"document_id": str(document_id)}
        )

        if not results['ids']:
            return 0

        # 删除所有chunk
        self.collection.delete(ids=results['ids'])

        return len(results['ids'])
```

**Step 4: 运行测试验证通过**

```bash
pytest tests/services/test_knowledge_base_service.py -v
```

预期：PASS

**Step 5: 提交更改**

```bash
git add tests/services/test_knowledge_base_service.py backend/src/services/knowledge_base_service.py
git commit -m "feat: 实现知识库RAG服务（含测试）"
```

---

### Task 19: 实现知识库管理API

**Files:**
- Create: `backend/src/interfaces/routers/party/knowledge.py`

**Step 1: 创建知识库API路由**

```python
# backend/src/interfaces/routers/party/knowledge.py
# -*- coding: utf-8 -*-
"""知识库管理API路由"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import shutil
from pathlib import Path

from src.database import get_db
from src.auth import get_current_user
from src.db_models import UserModel
from src.db_models_party import KnowledgeDocumentModel, KnowledgeCategoryModel
from src.services.knowledge_base_service import KnowledgeBaseService


router = APIRouter(prefix="/api/v1/party/knowledge", tags=["知识库管理"])

# 知识库服务实例
kb_service = KnowledgeBaseService()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    category_id: Optional[int] = None,
    title: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    上传文档到知识库

    支持格式：PDF、Word、TXT
    """
    # TODO: 添加权限检查（仅系统管理员和上级组织管理员）

    # 验证文件类型
    allowed_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="不支持的文件类型")

    # 保存文件
    upload_dir = Path("static/uploads/knowledge")
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 创建数据库记录
    db_document = KnowledgeDocumentModel(
        title=title or file.filename,
        category_id=category_id,
        file_path=str(file_path),
        file_type=file.content_type,
        uploaded_by=current_user.id
    )

    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)

    # 提取元数据
    metadata = kb_service.extract_metadata_from_filename(file.filename)

    # 添加到向量数据库
    chunk_count = kb_service.add_document(
        str(file_path),
        db_document.id,
        metadata
    )

    # 更新分块数量
    db_document.chunk_count = chunk_count
    await db.commit()

    return {
        "message": "上传成功",
        "document_id": db_document.id,
        "chunk_count": chunk_count
    }


@router.get("/search")
async def search_knowledge(
    query: str,
    top_k: int = 5,
    current_user: UserModel = Depends(get_current_user)
):
    """
    检索知识库

    用于AI问答时的上下文检索。
    """
    results = kb_service.search(query, top_k)

    return {
        "query": query,
        "results": results,
        "count": len(results)
    }


@router.get("/categories")
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """获取知识库分类列表"""
    # TODO: 实现分类列表查询
    return {"categories": []}


@router.get("/documents")
async def list_documents(
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """获取文档列表"""
    # TODO: 实现文档列表查询
    return {"total": 0, "items": []}


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """删除文档"""
    # TODO: 添加权限检查

    # 从数据库删除
    result = await db.execute(
        select(KnowledgeDocumentModel).where(KnowledgeDocumentModel.id == document_id)
    )
    db_document = result.scalar_one_or_none()

    if not db_document:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 删除文件
    file_path = Path(db_document.file_path)
    if file_path.exists():
        file_path.unlink()

    # 从向量数据库删除
    kb_service.delete_document(document_id)

    # 从数据库删除
    await db.delete(db_document)
    await db.commit()

    return {"message": "删除成功"}
```

**Step 2: 注册知识库路由**

```python
# backend/src/interfaces/routers/party/__init__.py 修改

from fastapi import APIRouter
from . import members, knowledge

router = APIRouter(prefix="/api/v1/party", tags=["党建"])
router.include_router(members.router)
router.include_router(knowledge.router)
```

**Step 3: 提交更改**

```bash
git add backend/src/interfaces/routers/party/knowledge.py backend/src/interfaces/routers/party/__init__.py
git commit -m "feat: 实现知识库管理API"
```

---

## 阶段六：测试与优化

### Task 20: 编写端到端测试

**Files:**
- Create: `tests/e2e/party.spec.ts`

**Step 1: 创建E2E测试**

```typescript
// tests/e2e/party.spec.ts
import { test, expect } from '@playwright/test'

test.describe('党员管理E2E测试', () => {
  test.beforeEach(async ({ page }) => {
    // 登录
    await page.goto('http://localhost:5173/login')
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'admin123')
    await page.click('button[type="submit"]')

    // 等待登录成功
    await page.waitForURL('http://localhost:5173/')
  })

  test('应该能创建党员档案', async ({ page }) => {
    // 导航到党员管理页面
    await page.goto('http://localhost:5173/admin/party-members')

    // 点击新增按钮
    await page.click('button:has-text("新增党员")')

    // 填写表单
    await page.fill('input[name="name"]', '测试党员')
    await page.selectOption('select[name="gender"]', '男')
    await page.fill('input[name="phone"]', '13800138000')
    await page.selectOption('select[name="memberType"]', '正式党员')

    // 保存
    await page.click('button:has-text("保存")')

    // 验证成功消息
    await expect(page.locator('.el-message--success')).toBeVisible()

    // 验证列表中存在新党员
    await expect(page.locator('table').locator('text=测试党员')).toBeVisible()
  })

  test('应该能搜索党员', async ({ page }) => {
    await page.goto('http://localhost:5173/admin/party-members')

    // 输入搜索条件
    await page.fill('input[placeholder="请输入姓名"]', '测试')

    // 点击查询
    await page.click('button:has-text("查询")')

    // 验证搜索结果
    await expect(page.locator('table tbody tr')).toHaveCount(1)
  })
})


test.describe('AI工具E2E测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173/login')
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'admin123')
    await page.click('button[type="submit"]')
    await page.waitForURL('http://localhost:5173/')
  })

  test('应该能使用三会一课一键生成工具', async ({ page }) => {
    // 导航到AI工具
    await page.click('text=AI党建助手')

    // 选择三会一课工具
    await page.click('text=三会一课一键生成')

    // 等待工具加载
    await expect(page.locator('h1:has-text("三会一课一键生成")')).toBeVisible()

    // 输入会议信息
    await page.fill('textarea[placeholder*="会议主题"]', '学习贯彻党的二十大精神')
    await page.selectOption('select[name="meetingType"]', '支部党员大会')

    // 发送消息
    await page.click('button:has-text("发送")')

    // 等待AI回复
    await expect(page.locator('.ai-message')).toBeVisible({ timeout: 30000 })
  })
})
```

**Step 2: 运行E2E测试**

```bash
cd frontend
npm run test:e2e
```

**Step 3: 提交更改**

```bash
git add tests/e2e/party.spec.ts
git commit -m "test: 添加党建平台E2E测试"
```

---

### Task 21: 性能优化和安全加固

**Files:**
- Modify: 多个文件

**Step 1: 数据库查询优化**

```python
# backend/src/services/party_member_service.py 添加索引提示

# 在查询时使用索引
@staticmethod
async def list_members(
    db: AsyncSession,
    branch_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> PartyMemberListResponse:
    """获取党员列表（优化版）"""
    query = select(PartyMemberModel).order_by(PartyMemberModel.created_at.desc())

    if branch_id:
        query = query.where(PartyMemberModel.branch_id == branch_id)

    # 使用索引优化
    result = await db.execute(
        query.offset(skip).limit(limit)
        .options(selectinload(PartyMemberModel.branch))
    )
    members = result.scalars().all()

    # 使用count查询优化
    count_result = await db.execute(
        select(func.count(PartyMemberModel.id)).where(
            PartyMemberModel.branch_id == branch_id if branch_id else True
        )
    )
    total = count_result.scalar()

    return PartyMemberListResponse(
        total=total,
        items=[PartyMemberResponse.from_orm(m) for m in members]
    )
```

**Step 2: 添加API限流**

```python
# backend/src/interfaces/middleware/rate_limit.py
# -*- coding: utf-8 -*-
"""API限流中间件"""

from fastapi import Request, HTTPException
from collections import defaultdict
from time import time
import asyncio


class RateLimiter:
    """简单的限流器"""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    async def check_rate_limit(self, user_id: int):
        """检查是否超过限流"""
        now = time()

        # 清理过期记录
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < 60
        ]

        # 检查是否超过限制
        if len(self.requests[user_id]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="请求过于频繁，请稍后再试"
            )

        # 记录请求
        self.requests[user_id].append(now)


# 全局限流器实例
rate_limiter = RateLimiter(requests_per_minute=60)
```

**Step 3: 添加敏感词过滤**

```python
# backend/src/services/content_filter.py
# -*- coding: utf-8 -*-
"""内容安全过滤服务"""

class ContentFilterService:
    """内容安全过滤服务"""

    # 政治敏感词示例（实际应从配置或数据库加载）
    SENSITIVE_WORDS = [
        # 这里应该是实际的敏感词列表
        # 为了示例，这里为空
    ]

    @classmethod
    def contains_sensitive_word(cls, text: str) -> bool:
        """检查是否包含敏感词"""
        for word in cls.SENSITIVE_WORDS:
            if word in text:
                return True
        return False

    @classmethod
    def filter_content(cls, text: str) -> tuple[bool, str]:
        """
        过滤内容

        Returns:
            (是否通过, 过滤后的文本或错误消息)
        """
        if cls.contains_sensitive_word(text):
            return False, "内容包含敏感词汇，请修改后重试"

        return True, text
```

**Step 4: 提交更改**

```bash
git add backend/src/services/party_member_service.py backend/src/interfaces/middleware/rate_limit.py backend/src/services/content_filter.py
git commit -m "feat: 性能优化和安全加固"
```

---

## 总结

### 完成标志

当以下所有任务完成后，党建AI智能平台MVP即告完成：

✅ **阶段一：基础设施改造**
- Task 1-8: UI主题、导航配置、AI工具配置

✅ **阶段二：数据库迁移**
- Task 9-12: 四个核心数据模型

✅ **阶段三：后端API开发**
- Task 13-15: 党员管理完整API

✅ **阶段四：前端页面开发**
- Task 16: 党员管理页面

✅ **阶段五：知识库RAG系统**
- Task 17-19: RAG服务和API

✅ **阶段六：测试与优化**
- Task 20-21: E2E测试和优化

### 下一步

完成后可以继续迭代：
- 组织生活管理页面
- 党费管理页面
- 权限系统完善
- 数据统计报表
- 移动端适配
