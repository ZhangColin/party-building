# AI 内容保存功能设计文档

**日期**: 2026-03-05
**状态**: 设计已批准

---

## 一、功能概述

将 AI 生成的内容（代码块或整条回复）保存到知识库或党建活动，形成内容沉淀闭环。

---

## 二、保存入口

### 2.1 代码块保存按钮

| 项目 | 说明 |
|------|------|
| **位置** | 在代码块预览按钮旁边 |
| **实现文件** | `frontend/src/utils/markdownRenderer.ts` |
| **保存内容** | 只保存代码块内容（纯代码） |
| **图标** | FolderIcon 或保存图标 |

### 2.2 整条回复保存按钮

| 项目 | 说明 |
|------|------|
| **位置** | 在 AI 回复的复制按钮旁边（`MessageItem.vue` 的工具栏） |
| **实现文件** | `frontend/src/components/chat/MessageItem.vue` |
| **保存内容** | 保存整条 AI 回复的 Markdown 格式 |
| **图标** | FolderIcon + "知识库"/FlagIcon + "党建活动" |

---

## 三、保存对话框

### 3.1 扩展 CreateFileDialog.vue

```typescript
interface Props {
  modelValue: boolean
  mode: 'create' | 'save'     // 新建模式 vs 保存模式
  categories: Category[]
  defaultCategoryId?: string | null
  isPartyTheme?: boolean
  content?: string            // 保存模式下传入内容
  target: 'knowledge' | 'party'  // 目标类型
  defaultFilename?: string    // 默认文件名
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm', data: { categoryId: string; filename: string; content?: string }): void
}
```

### 3.2 对话框内容

| 字段 | 说明 |
|------|------|
| **目标目录** | 级联选择器（el-cascader），复用现有逻辑 |
| **文件名** | 输入框，带 `.md` 后缀显示 |
| **默认值** | 从内容提取标题（第一行 `# 标题`）或会话标题 |

### 3.3 保存按钮设计

在 `MessageItem.vue` 工具栏添加两个保存按钮：

```vue
<div class="message-toolbar">
  <!-- 复制按钮（现有） -->
  <button class="copy-button" @click="handleCopy">
    <DocumentDuplicateIcon />
  </button>

  <!-- 保存到知识库按钮（新增） -->
  <button class="save-button" @click="handleSaveToKnowledge" title="保存到知识库">
    <FolderIcon />
  </button>

  <!-- 保存到党建活动按钮（新增） -->
  <button class="save-button" @click="handleSaveToParty" title="保存到党建活动">
    <FlagIcon />
  </button>
</div>
```

---

## 四、文件名冲突处理

### 4.1 保存前检查流程

```
用户点击保存 → 检查同名文件 → 存在？
  ├─ 是 → 弹出确认对话框（覆盖/重命名/取消）
  │   ├─ 覆盖 → 直接保存（删除原文件，创建新文件）
  │   ├─ 重命名 → 生成新文件名（如 标题(1).md）→ 保存
  │   └─ 取消 → 返回对话框
  └─ 否 → 直接保存
```

### 4.2 冲突确认对话框

使用 `ElMessageBox.confirm`，提供三个按钮：

```typescript
ElMessageBox.confirm(
  '文件 "xxx.md" 已存在，是否覆盖？',
  '文件名冲突',
  {
    confirmButtonText: '覆盖',
    cancelButtonText: '取消',
    distinguishCancelAndClose: true,
    type: 'warning',
  }
).then(() => {
  // 覆盖：先删除原文件，再保存
}).catch((action) => {
  if (action === 'cancel') {
    // 取消，返回对话框
  }
})
```

或提供"重命名"选项：

```typescript
ElMessageBox({
  title: '文件名冲突',
  message: h('div', null, [
    h('p', null, '文件 "xxx.md" 已存在'),
    h('p', { class: 'text-sm text-gray-500' }, '请选择操作：')
  ]),
  showCancelButton: true,
  confirmButtonText: '覆盖',
  cancelButtonText: '重命名',
  distinguishCancelAndClose: true,
})
```

---

## 五、保存成功反馈

| 项目 | 说明 |
|------|------|
| **Toast 提示** | `"已保存到 知识库/某目录/文件名.md"` |
| **跳转行为** | 不跳转，保持当前聊天状态 |
| **UI 实现** | 使用 `ElMessage.success()` |

---

## 六、技术实现要点

### 6.1 前端组件修改清单

| 文件 | 修改内容 |
|------|---------|
| `CreateFileDialog.vue` | 添加 `mode`、`content`、`target`、`defaultFilename` 属性 |
| `MessageItem.vue` | 添加两个保存按钮，实现保存逻辑 |
| `markdownRenderer.ts` | 代码块 header 添加保存按钮 |
| `codeBlockHandlers.ts` | 添加保存按钮的事件处理 |

### 6.2 API 调用

**知识库**：`POST /api/v1/knowledge/documents`
**党建活动**：`POST /api/v1/party-activities/documents`

请求体：
```typescript
{
  category_id: string
  filename: string
  content: string
}
```

响应体：
```typescript
{
  id: string
  category_id: string
  filename: string
  original_filename: string
  markdown_path: string
  created_at: string
}
```

### 6.3 文件名提取逻辑

```typescript
function extractDefaultFilename(content: string, sessionTitle: string): string {
  // 1. 尝试提取第一行 # 标题
  const titleMatch = content.match(/^#\s+(.+)$/m)
  if (titleMatch) return sanitizeFilename(titleMatch[1].trim())

  // 2. 使用会话标题
  if (sessionTitle) return sanitizeFilename(sessionTitle)

  // 3. 默认标题
  return 'AI回复-' + new Date().toLocaleDateString('zh-CN')
}

// 清理文件名中的非法字符
function sanitizeFilename(name: string): string {
  return name.replace(/[<>:"/\\|?*]/g, '').trim()
}
```

### 6.4 代码块保存按钮实现

修改 `markdownRenderer.ts` 中的代码块渲染：

```typescript
// 在现有按钮旁边添加保存按钮
<button
  class="save-button"
  data-code-type="${artifactType}"
  data-code-content="${codeContentForCopy}"
  title="保存到知识库"
>
  <svg viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
    <!-- FolderIcon path -->
  </svg>
</button>
```

---

## 七、样式规范

### 7.1 保存按钮样式

```css
.save-button {
  @apply p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors;
}

.save-button:hover {
  @apply text-red-600;
}
```

### 7.2 工具栏样式调整

```css
.message-toolbar {
  @apply flex gap-1;
}
```

---

## 八、验收标准

1. ✅ 点击代码块保存按钮，弹出保存对话框
2. ✅ 点击 AI 回复的保存按钮，弹出保存对话框
3. ✅ 文件名默认值正确提取（标题或会话名）
4. ✅ 选择目录后可以保存
5. ✅ 文件名冲突时弹出确认对话框
6. ✅ 保存成功后显示 Toast 提示
7. ✅ 保存的文件可以在知识库/党建活动中查看和编辑
8. ✅ 无控制台报错

---

## 九、后续扩展

- [ ] 保存后询问是否跳转到目标目录
- [ ] 记住上次保存位置
- [ ] 支持保存到最近使用的目录
- [ ] 批量保存多条 AI 回复
