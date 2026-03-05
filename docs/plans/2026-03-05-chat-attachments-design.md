# AI聊天附件功能设计文档

**日期**: 2026-03-05
**状态**: 设计已批准
**相关文档**: [/Users/zhangcolin/.claude/plans/eager-prancing-noodle.md](../../../.claude/plans/eager-prancing-noodle.md)

---

## 一、需求概述

在现有AI聊天功能基础上，支持文件附件，使用户能够：
1. 从本地电脑上传文件
2. 从知识库选择已存储的文件
3. 从党建活动选择已存储的文件

附件内容会被注入到 AI 的上下文中，使 AI 能够基于用户提供的内容生成回复。

---

## 二、需求确认

| 项目 | 确认方案 |
|------|----------|
| 文件来源 | 本地上传 + 知识库选择 + 党建活动选择 |
| 文件数量 | 最多 5 个 |
| 单文件大小 | 最大 10MB |
| 内容注入 | system_prompt 中注入 |
| 发送后行为 | 自动清空文件列表 |
| 临时存储 | 后端临时目录，需清理机制 |

---

## 三、整体架构

### 前端组件结构

```
ChatArea.vue (容器)
 └── ChatPanel.vue (消息展示区)
 └── ChatInput.vue (扩展，新增附件功能)
      ├── 文件操作按钮区 (3个按钮)
      ├── 附件标签展示区 (已选文件)
      └── 原有输入框 + 发送按钮
```

### 后端 API 结构

```
POST   /api/v1/temp-files/upload                  # 上传临时文件
POST   /api/v1/tools/{tool_id}/chat/stream        # 扩展：支持 attached_files
POST   /api/v1/knowledge/documents/batch          # 批量获取知识库文件内容
POST   /api/v1/party-activities/documents/batch   # 批量获取党建活动文件内容
```

### 数据流

```
用户选择文件 → 上传到临时目录 → 存储 temp_file_id
用户发送消息 → 携带 temp_file_id 列表
后端读取文件内容 → 注入 system_prompt → 调用 AI
发送完成 → 清空前端附件列表 → 标记临时文件可清理
```

---

## 四、前端设计

### ChatInput.vue 扩展

**新增类型**：
```typescript
interface AttachedFile {
  id: string           // 临时文件ID或知识库文件ID
  name: string         // 文件名
  type: 'temp' | 'knowledge' | 'party'
  size: number         // 文件大小（字节）
  status: 'uploading' | 'ready' | 'error'
}
```

**新增 Props**：
```typescript
interface Props {
  // ... 现有 props
  maxFiles?: number        // 最大文件数，默认 5
  maxFileSize?: number     // 最大文件大小（字节），默认 10MB
}
```

**新增 Emits**：
```typescript
interface Emits {
  // ... 现有 emits
  send: [content: string, attachedFiles: AttachedFile[]]
}
```

**新增 UI 元素**：

1. **文件操作按钮区**（输入框上方）
   - 上传本地文件按钮
   - 从知识库选择按钮
   - 从党建活动选择按钮

2. **附件标签展示区**（按钮区上方）
   - 文件名 + 大小
   - 删除按钮（每个附件）
   - 上传进度条（上传中时）

3. **消息中的附件展示**
   - 用户消息下方显示已发送的文件列表
   - 文件名 + 类型图标

### 新建 FileSelectorDialog.vue

复用现有的文件选择逻辑，提供一个简洁的对话框：
- 左侧：目录树
- 右侧：文件列表（支持多选）
- 底部：确定/取消按钮

### 前端类型扩展

**扩展 Message 接口**（`frontend/src/types/index.ts`）：
```typescript
export interface Message {
  // ... 现有字段
  attachments?: MessageAttachment[]
}

export interface MessageAttachment {
  id: string
  name: string
  type: 'temp' | 'knowledge' | 'party'
  size: number
}
```

---

## 五、后端设计

### 临时文件上传接口

**端点**：`POST /api/v1/temp-files/upload`

**请求**：`multipart/form-data`
- `file`: 文件内容

**响应**：
```json
{
  "temp_id": "uuid",
  "filename": "原文件名.docx",
  "size": 12345,
  "content_preview": "文件内容的前1000字符（用于AI预览）"
}
```

**存储**：`backend/uploads/temp/{temp_id}.tmp`

### 批量获取知识库文件内容

**端点**：`POST /api/v1/knowledge/documents/batch`

**请求**：
```json
{
  "document_ids": ["id1", "id2", ...]
}
```

**响应**：
```json
{
  "documents": [
    {
      "id": "id1",
      "filename": "文件名.md",
      "content": "文件完整内容"
    }
  ]
}
```

### 聊天接口扩展

**端点**：`POST /api/v1/tools/{tool_id}/chat/stream`

**请求扩展**（ChatRequest）：
```json
{
  "message": "用户问题",
  "session_id": "...",
  "attached_files": [
    {
      "id": "temp_id或document_id",
      "type": "temp|knowledge|party",
      "name": "文件名"
    }
  ]
}
```

### 临时文件清理机制

- **用后即删**：消息发送成功后立即删除临时文件
- **定时清理**：每小时清理超过 1 小时的残留临时文件

### 配置变更

**backend/.env.example** 新增：
```bash
# 临时文件配置
TEMP_FILE_MAX_SIZE_MB=10
TEMP_FILE_CLEANUP_INTERVAL_HOURS=1
TEMP_FILE_MAX_AGE_HOURS=1
```

---

## 六、AI 内容注入设计

### System Prompt 构造

**注入格式**：
```
[原始 system_prompt]

---
用户附件内容：
【文件1：文件名.docx】
[文件内容]

【文件2：文件名.pdf】
[文件内容]

---
```

### 内容处理策略

| 文件类型 | 处理方式 |
|----------|----------|
| Markdown/文本 | 直接注入完整内容 |
| Word/PDF/Excel | 使用已转换的 Markdown 内容 |
| 图片 | 暂不支持 |
| 超大文件 | 截取前 5000 字符 + 提示"内容已截断" |

### Token 控制

- 单文件内容超过 10000 字符时截断
- 所有附件总内容超过 30000 字符时，按文件顺序截断
- 在截断处添加提示：`（因内容过长，后续内容已省略）`

---

## 七、错误处理和用户体验

### 前端错误处理

| 场景 | 处理方式 |
|------|----------|
| 文件超限（数量/大小） | 验证时拦截，Toast 提示具体限制 |
| 上传失败 | 显示错误状态，允许重试或删除 |
| 读取知识库文件失败 | Toast 提示，从列表中移除 |
| 发送时部分文件失败 | 提示哪些文件失败，继续发送成功部分 |

### 后端错误处理

| 场景 | 处理方式 |
|------|----------|
| 临时文件不存在 | 跳过该文件，记录日志 |
| 文件内容为空 | 跳过该文件 |
| 文件格式不支持 | 返回 400 错误 |
| 清理临时文件失败 | 记录日志，不影响主流程 |

### 用户体验细节

1. **上传进度**：显示进度条，上传中禁用发送按钮
2. **文件预览**：hover 显示文件大小和类型
3. **快捷键**：文件选中状态按 Delete 删除
4. **拖拽上传**：支持拖拽文件到输入区域
5. **Toast 提示**：
   - 上传成功：`"文件上传成功"`
   - 发送成功：`"已发送 3 个附件"`
   - 发送失败：`"部分附件发送失败，请重试"`

---

## 八、测试策略

### 测试环境

**使用独立测试数据库**：
- 配置：`backend/.env.test` 或测试专用数据库
- 测试前创建临时数据库，测试后清理
- 不使用开发库的数据

### 单元测试

**前端**：
- `ChatInput.spec.ts` - 文件上传、验证、删除逻辑
- `FileSelectorDialog.spec.ts` - 文件选择交互

**后端**：
- `test_temp_files.py` - 上传、清理、验证
- `test_chat_with_attachments.py` - 带附件的对话逻辑

### 集成测试（E2E）

1. 上传本地文件 → 发送消息 → 验证 AI 理解内容
2. 选择知识库文件 → 发送消息 → 验证 AI 引用文件
3. 混合上传 → 发送消息 → 验证处理多种来源
4. 超限文件 → 验证错误提示
5. 发送后验证文件列表清空

### 手动验收标准

每个功能单元完成后：
1. ✅ 功能正常运行
2. ✅ 无控制台报错
3. ✅ 基本错误处理（网络失败、文件不存在等）
4. ✅ 测试数据库独立运行

---

## 九、实现优先级

### 第一阶段：后端基础
1. 临时文件上传接口
2. 批量获取文件内容接口
3. 聊天接口扩展

### 第二阶段：前端基础
1. ChatInput 组件扩展
2. 文件上传和验证
3. 附件展示和删除

### 第三阶段：文件选择
1. FileSelectorDialog 组件
2. 知识库文件选择
3. 党建活动文件选择

### 第四阶段：集成和测试
1. AI 内容注入
2. 错误处理完善
3. 单元测试和 E2E 测试

---

## 十、相关文件

**前端组件**：
- [ChatInput.vue](frontend/src/components/ChatInput.vue) - 需扩展
- [ChatPanel.vue](frontend/src/components/ChatPanel.vue) - 需添加附件展示
- [FileManagementLayout.vue](frontend/src/layouts/FileManagementLayout.vue) - 复用参考
- [KnowledgeView.vue](frontend/src/views/KnowledgeView.vue) - 复用参考

**前端类型**：
- [types/index.ts](frontend/src/types/index.ts) - 扩展 Message 接口

**后端接口**：
- [chat.py](backend/src/interfaces/routers/tools/chat.py) - 扩展聊天接口
- [knowledge_service.py](backend/src/services/knowledge_service.py) - 批量获取

**后端服务**：
- [ai_service.py](backend/src/services/ai_service.py) - 内容注入逻辑
