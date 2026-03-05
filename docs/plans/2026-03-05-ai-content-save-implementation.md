# AI 内容保存功能实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 AI 生成的内容（代码块或整条回复）保存到知识库或党建活动

**Architecture:** 扩展现有的 CreateFileDialog 组件支持保存模式，在 MessageItem 工具栏和代码块中添加保存按钮，调用现有的知识库/党建活动创建文档 API

**Tech Stack:** Vue 3 + TypeScript + Element Plus（前端），FastAPI + SQLAlchemy（后端已有 API）

---

## 任务概览

1. 扩展 CreateFileDialog.vue 支持保存模式
2. 创建文件名提取工具函数
3. 在 MessageItem.vue 中添加保存按钮
4. 在 markdownRenderer.ts 中添加代码块保存按钮
5. 实现文件名冲突检测和处理
6. 连接后端 API 并处理响应

---

## Task 1: 扩展 CreateFileDialog.vue 支持保存模式

**Files:**
- Modify: `frontend/src/components/file-manager/CreateFileDialog.vue`

**Step 1: 添加新的 Props 定义**

在 `<script setup lang="ts">` 中更新 Props 接口：

```typescript
interface Props {
  modelValue: boolean
  mode?: 'create' | 'save'     // 新建模式 vs 保存模式
  categories: Category[]
  defaultCategoryId?: string | null
  isPartyTheme?: boolean
  content?: string              // 保存模式下传入内容
  target?: 'knowledge' | 'party'  // 目标类型（用于标题）
  defaultFilename?: string      // 默认文件名
}

const props = withDefaults(defineProps<Props>(), {
  defaultCategoryId: null,
  isPartyTheme: false,
  mode: 'create',
  content: '',
  target: 'knowledge',
  defaultFilename: ''
})
```

**Step 2: 更新 Emits 接口**

```typescript
interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm', data: { categoryId: string; filename: string; content?: string }): void
}

const emit = defineEmits<Emits>()
```

**Step 3: 更新标题显示**

在 `<template>` 中更新对话框标题：

```vue
<el-dialog
  v-model="visible"
  :title="mode === 'save' ? (target === 'knowledge' ? '保存到知识库' : '保存到党建活动') : '新建 Markdown 文件'"
  :width="500"
  :close-on-click-modal="false"
  @closed="handleClosed"
>
```

**Step 4: 添加文件名默认值逻辑**

在 form 初始化中更新：

```typescript
const form = reactive<{
  categoryId: string | null
  filename: string
  content: string
}>({
  categoryId: props.defaultCategoryId,
  filename: props.defaultFilename || '',
  content: props.content || ''
})
```

**Step 5: 监听 props 变化更新 form**

```typescript
watch(() => props.defaultFilename, (newVal) => {
  if (newVal && props.mode === 'save') {
    form.filename = newVal
  }
})

watch(() => props.content, (newVal) => {
  if (newVal !== undefined) {
    form.content = newVal
  }
})
```

**Step 6: 条件隐藏内容输入框（仅新建模式显示）**

```vue
<el-form-item v-if="mode === 'create'" label="初始内容">
  <el-input
    v-model="form.content"
    type="textarea"
    :rows="6"
    placeholder="可选：输入初始内容（支持 Markdown 语法）"
  />
</el-form-item>
```

**Step 7: 更新确认处理**

```typescript
const handleConfirm = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    emit('confirm', {
      categoryId: form.categoryId!,
      filename: form.filename + '.md',
      content: props.mode === 'save' ? form.content : undefined
    })
    visible.value = false
  } catch {
    // 验证失败
  }
}
```

**Step 8: 在保存模式下重置时不重置文件名**

```typescript
const handleClosed = () => {
  formRef.value?.resetFields()
  if (props.mode === 'save') {
    // 保存模式不清空文件名，下次打开可能还是同一内容
    form.content = props.content || ''
  } else {
    form.content = ''
  }
}
```

**Step 9: 添加 mode 的 computed**

```typescript
const mode = computed(() => props.mode)
const target = computed(() => props.target)
```

**Step 10: 测试组件**

创建测试文件或手动测试：打开对话框，验证标题和表单行为正确

**Step 11: 提交**

```bash
git add frontend/src/components/file-manager/CreateFileDialog.vue
git commit -m "feat: 扩展 CreateFileDialog 支持保存模式"
```

---

## Task 2: 创建文件名提取工具函数

**Files:**
- Create: `frontend/src/utils/filenameExtractor.ts`

**Step 1: 创建工具函数文件**

```typescript
# -*- coding: utf-8 -*-
/**
 * 文件名提取工具
 */

/**
 * 从内容或会话标题中提取默认文件名
 * @param content - Markdown 内容
 * @param sessionTitle - 会话标题
 * @returns 提取的文件名（不含扩展名）
 */
export function extractDefaultFilename(content: string, sessionTitle?: string): string {
  // 1. 尝试提取第一行 # 标题
  const titleMatch = content.match(/^#\s+(.+)$/m)
  if (titleMatch) {
    return sanitizeFilename(titleMatch[1].trim())
  }

  // 2. 使用会话标题
  if (sessionTitle) {
    return sanitizeFilename(sessionTitle)
  }

  // 3. 默认标题
  const date = new Date()
  const dateStr = date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).replace(/\//g, '-')
  return `AI回复-${dateStr}`
}

/**
 * 清理文件名中的非法字符
 * @param name - 原始文件名
 * @returns 清理后的文件名
 */
export function sanitizeFilename(name: string): string {
  // 移除 Windows/Linux 文件名非法字符
  let cleaned = name.replace(/[<>:"/\\|?*]/g, '').trim()

  // 限制长度（50个字符以内）
  if (cleaned.length > 50) {
    cleaned = cleaned.substring(0, 50)
  }

  // 避免空文件名
  if (!cleaned) {
    return '未命名文件'
  }

  return cleaned
}

/**
 * 生成带数字后缀的文件名
 * @param baseFilename - 基础文件名
 * @param existingNames - 已存在的文件名列表
 * @returns 不冲突的文件名
 */
export function generateUniqueFilename(baseFilename: string, existingNames: string[]): string {
  const cleanBase = sanitizeFilename(baseFilename)

  // 如果基础名称不冲突，直接返回
  if (!existingNames.includes(cleanBase + '.md')) {
    return cleanBase
  }

  // 尝试添加数字后缀
  let counter = 1
  let newName
  do {
    newName = `${cleanBase}(${counter})`
    counter++
  } while (existingNames.includes(newName + '.md'))

  return newName
}
```

**Step 2: 编写单元测试**

创建 `frontend/src/utils/__tests__/filenameExtractor.spec.ts`：

```typescript
# -*- coding: utf-8 -*-
import { describe, it, expect } from 'vitest'
import { extractDefaultFilename, sanitizeFilename, generateUniqueFilename } from '../filenameExtractor'

describe('filenameExtractor', () => {
  describe('extractDefaultFilename', () => {
    it('应该提取第一行 # 标题', () => {
      const content = '# 这是标题\n\n内容'
      expect(extractDefaultFilename(content)).toBe('这是标题')
    })

    it('应该使用会话标题作为备选', () => {
      const content = '没有标题的内容'
      expect(extractDefaultFilename(content, '会话名称')).toBe('会话名称')
    })

    it('应该使用默认日期格式', () => {
      const content = '没有标题的内容'
      const result = extractDefaultFilename(content)
      expect(result).toMatch(/^AI回复-\d{2}-\d{2}-\d{2}$/)
    })
  })

  describe('sanitizeFilename', () => {
    it('应该移除非法字符', () => {
      expect(sanitizeFilename('file<>name')).toBe('filename')
    })

    it('应该限制长度为50字符', () => {
      const longName = 'a'.repeat(100)
      expect(sanitizeFilename(longName)).toHaveLength(50)
    })

    it('应该返回未命名文件当输入为空', () => {
      expect(sanitizeFilename('   ')).toBe('未命名文件')
    })
  })

  describe('generateUniqueFilename', () => {
    it('应该返回基础名称当不冲突时', () => {
      expect(generateUniqueFilename('test', [])).toBe('test')
    })

    it('应该添加数字后缀当冲突时', () => {
      expect(generateUniqueFilename('test', ['test.md'])).toBe('test(1)')
    })

    it('应该递增数字直到找到可用名称', () => {
      expect(generateUniqueFilename('test', ['test.md', 'test(1).md'])).toBe('test(2)')
    })
  })
})
```

**Step 3: 运行测试**

```bash
cd frontend
npm run test -- src/utils/__tests__/filenameExtractor.spec.ts
```

Expected: 所有测试通过

**Step 4: 提交**

```bash
git add frontend/src/utils/filenameExtractor.ts frontend/src/utils/__tests__/filenameExtractor.spec.ts
git commit -m "feat: 添加文件名提取工具函数和测试"
```

---

## Task 3: 在 MessageItem.vue 中添加保存按钮

**Files:**
- Modify: `frontend/src/components/chat/MessageItem.vue`
- Create: `frontend/src/components/chat/SaveToDialog.vue`

**Step 1: 创建 SaveToDialog 组件**

创建 `frontend/src/components/chat/SaveToDialog.vue`：

```vue
# -*- coding: utf-8 -*-
<template>
  <CreateFileDialog
    v-model="visible"
    mode="save"
    :target="target"
    :categories="categories"
    :default-filename="defaultFilename"
    :content="content"
    :is-party-theme="true"
    @confirm="handleConfirm"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import CreateFileDialog from '../file-manager/CreateFileDialog.vue'
import * as knowledgeApi from '@/services/knowledgeApi'
import * as partyActivityApi from '@/services/partyActivityApi'
import type { Category } from '@/types/file-manager'
import { generateUniqueFilename } from '@/utils/filenameExtractor'

interface Props {
  modelValue: boolean
  target: 'knowledge' | 'party'
  content: string
  categories: Category[]
  sessionTitle?: string
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'saved', path: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 从内容中提取默认文件名
const defaultFilename = computed(() => {
  // 提取第一行标题作为默认文件名
  const titleMatch = props.content.match(/^#\s+(.+)$/m)
  if (titleMatch) {
    return titleMatch[1].trim()
  }
  return props.sessionTitle || 'AI回复'
})

const handleConfirm = async (data: { categoryId: string; filename: string; content?: string }) => {
  try {
    const { categoryId, filename, content } = data

    // 获取目录下现有文件列表，检查冲突
    const existingFiles = props.target === 'knowledge'
      ? await knowledgeApi.getDocuments(categoryId)
      : await partyActivityApi.getDocuments(categoryId)

    const existingNames = existingFiles.map(f => f.original_filename)

    // 检查文件名是否已存在
    if (existingNames.includes(filename)) {
      // 使用 ElMessageBox 询问用户
      const { ElMessageBox } = await import('element-plus')
      try {
        await ElMessageBox.confirm(
          `文件 "${filename}" 已存在，是否覆盖？`,
          '文件名冲突',
          {
            confirmButtonText: '覆盖',
            cancelButtonText: '重命名',
            distinguishCancelAndClose: true,
            type: 'warning',
          }
        )
        // 用户选择覆盖，继续保存
      } catch (action) => {
        if (action === 'cancel') {
          // 用户选择重命名，生成新文件名
          const uniqueName = generateUniqueFilename(
            filename.replace('.md', ''),
            existingNames
          )
          // 递归调用，使用新文件名
          await handleConfirm({ categoryId, filename: uniqueName + '.md', content })
          return
        } else {
          // 用户取消，关闭对话框
          return
        }
      }
    }

    // 调用 API 保存
    if (props.target === 'knowledge') {
      await knowledgeApi.createDocument({
        category_id: categoryId,
        filename: filename,
        content: content || ''
      })
    } else {
      await partyActivityApi.createDocument({
        category_id: categoryId,
        filename: filename,
        content: content || ''
      })
    }

    // 获取目录名称用于提示
    const findCategoryName = (cats: Category[], id: string): string => {
      for (const cat of cats) {
        if (cat.id === id) return cat.name
        if (cat.children) {
          const found = findCategoryName(cat.children, id)
          if (found) return found
        }
      }
      return '未知目录'
    }

    const categoryName = findCategoryName(props.categories, categoryId)
    const targetName = props.target === 'knowledge' ? '知识库' : '党建活动'

    ElMessage.success(`已保存到 ${targetName}/${categoryName}/${filename}`)
    emit('saved', `${targetName}/${categoryName}/${filename}`)
    visible.value = false
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败，请重试')
  }
}
</script>
```

**Step 2: 修改 MessageItem.vue 添加保存按钮**

在 `<script setup lang="ts">` 中添加导入：

```typescript
import {
  DocumentDuplicateIcon,
  DocumentIcon,
  FolderIcon,
  FlagIcon
} from '@heroicons/vue/24/outline'
import { ref, computed } from 'vue'
import { renderMarkdown } from '@/utils/markdownRenderer'
import { useClipboard } from '@/composables/useClipboard'
import type { Message, MessageAttachment } from '@/types'
import SaveToDialog from './SaveToDialog.vue'
import * as knowledgeApi from '@/services/knowledgeApi'
import * as partyActivityApi from '@/services/partyActivityApi'
```

添加状态变量：

```typescript
// 保存对话框状态
const showSaveToKnowledge = ref(false)
const showSaveToParty = ref(false)
const knowledgeCategories = ref<Category[]>([])
const partyCategories = ref<Category[]>([])
```

添加加载目录函数：

```typescript
// 加载知识库目录树
async function loadKnowledgeCategories() {
  if (knowledgeCategories.value.length > 0) return
  try {
    knowledgeCategories.value = await knowledgeApi.getCategoryTree()
  } catch (error) {
    console.error('加载知识库目录失败:', error)
  }
}

// 加载党建活动目录树
async function loadPartyCategories() {
  if (partyCategories.value.length > 0) return
  try {
    partyCategories.value = await partyActivityApi.getCategoryTree()
  } catch (error) {
    console.error('加载党建活动目录失败:', error)
  }
}
```

添加保存处理函数：

```typescript
// 保存到知识库
async function handleSaveToKnowledge() {
  await loadKnowledgeCategories()
  showSaveToKnowledge.value = true
}

// 保存到党建活动
async function handleSaveToParty() {
  await loadPartyCategories()
  showSaveToParty.value = true
}

// 保存成功回调
function handleSaved(path: string) {
  console.log('已保存到:', path)
}
```

**Step 3: 在模板中添加保存按钮**

找到 message-toolbar 部分，添加保存按钮：

```vue
<div
  class="message-toolbar"
  :class="{ 'toolbar-visible': showToolbar }"
>
  <!-- 复制按钮（现有） -->
  <button
    class="copy-button"
    @click="handleCopy"
    title="复制"
    data-testid="copy-button"
  >
    <DocumentDuplicateIcon />
  </button>

  <!-- 只在 AI 消息时显示保存按钮 -->
  <template v-if="message.role === 'assistant'">
    <button
      class="save-button"
      @click="handleSaveToKnowledge"
      title="保存到知识库"
    >
      <FolderIcon />
    </button>
    <button
      class="save-button"
      @click="handleSaveToParty"
      title="保存到党建活动"
    >
      <FlagIcon />
    </button>
  </template>
</div>
```

**Step 4: 在模板末尾添加保存对话框组件**

```vue
<!-- 保存对话框 -->
<SaveToDialog
  v-model="showSaveToKnowledge"
  target="knowledge"
  :content="message.content"
  :categories="knowledgeCategories"
  :session-title="sessionTitle"
  @saved="handleSaved"
/>
<SaveToDialog
  v-model="showSaveToParty"
  target="party"
  :content="message.content"
  :categories="partyCategories"
  :session-title="sessionTitle"
  @saved="handleSaved"
/>
```

**Step 5: 添加 sessionTitle prop**

```typescript
interface Props {
  message: Message
  sessionTitle?: string  // 新增
}
```

**Step 6: 添加保存按钮样式**

在 `<style scoped>` 中添加：

```css
.save-button {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: #999;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  padding: 0;
}

.save-button:hover {
  background: rgba(200, 16, 46, 0.1);
  color: #C8102E;
}

.save-button svg {
  width: 16px;
  height: 16px;
}
```

**Step 7: 测试保存功能**

1. 启动前端：`cd frontend && npm run dev`
2. 打开浏览器，进入 AI 聊天页面
3. 等待 AI 回复后，将鼠标悬停在回复上
4. 点击保存到知识库/党建活动按钮
5. 验证对话框弹出，可以选择目录和修改文件名
6. 验证保存成功后显示 Toast 提示

**Step 8: 提交**

```bash
git add frontend/src/components/chat/MessageItem.vue frontend/src/components/chat/SaveToDialog.vue
git commit -m "feat: 在 AI 回复中添加保存到知识库/党建活动按钮"
```

---

## Task 4: 在 markdownRenderer.ts 中添加代码块保存按钮

**Files:**
- Modify: `frontend/src/utils/markdownRenderer.ts`
- Modify: `frontend/src/utils/codeBlockHandlers.ts`

**Step 1: 在 markdownRenderer.ts 中添加保存按钮**

找到代码块渲染部分（在 `return`<div class="code-block-wrapper">` 之前），修改按钮组：

```typescript
// 返回带预览、复制和保存按钮的代码块
return `<div class="code-block-wrapper">
  <div class="code-block-header">
    <span class="code-language">${escapeHtml(lang)}</span>
    <div class="code-block-actions">
      <button
        class="preview-button"
        data-artifact-type="${artifactType}"
        data-artifact-content="${artifactJson}"
        title="预览 ${artifactType.toUpperCase()} 内容"
      >
        <svg viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
          <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
          <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/>
        </svg>
      </button>
      <button
        class="save-to-knowledge-button"
        data-code-type="${artifactType}"
        data-code-content="${codeContentForCopy}"
        title="保存到知识库"
      >
        <svg viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
          <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"/>
        </svg>
      </button>
      <button
        class="save-to-party-button"
        data-code-type="${artifactType}"
        data-code-content="${codeContentForCopy}"
        title="保存到党建活动"
      >
        <svg viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
          <path fill-rule="evenodd" d="M3 6a3 3 0 013-3h10a1 1 0 01.8 1.6L14.25 8l2.55 3.4A1 1 0 0116 13H6a1 1 0 00-1 1v3a1 1 0 11-2 0V6z" clip-rule="evenodd"/>
        </svg>
      </button>
      <button
        class="copy-code-button"
        data-code-content="${codeContentForCopy}"
        title="复制代码"
      >
        <svg viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
          <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z"/>
          <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z"/>
        </svg>
      </button>
    </div>
  </div>
  <pre><code class="language-${lang}">${codeContent}</code></pre>
</div>`
```

**Step 2: 更新 codeBlockHandlers.ts 添加保存按钮事件处理**

在 `frontend/src/utils/codeBlockHandlers.ts` 中添加保存按钮处理：

```typescript
# -*- coding: utf-8 -*-
/**
 * 代码块按钮事件处理
 */

import { ElMessage } from 'element-plus'
import * as knowledgeApi from '@/services/knowledgeApi'
import * as partyActivityApi from '@/services/partyActivityApi'
import { extractDefaultFilename, generateUniqueFilename } from './filenameExtractor'
import type { Category } from '@/types/file-manager'

// 缓存的目录数据
let knowledgeCategoriesCache: Category[] = []
let partyCategoriesCache: Category[] = []

/**
 * 初始化代码块按钮事件监听
 */
export function initCodeBlockHandlers() {
  // 使用事件委托处理所有代码块按钮点击
  document.addEventListener('click', handleCodeBlockClick)
}

/**
 * 处理代码块按钮点击
 */
async function handleCodeBlockClick(event: Event) {
  const target = event.target as HTMLElement
  const button = target.closest('button') as HTMLButtonElement

  if (!button) return

  // 预览按钮（现有逻辑，保持不变）
  if (button.classList.contains('preview-button')) {
    handlePreviewButton(button)
    return
  }

  // 复制按钮（现有逻辑，保持不变）
  if (button.classList.contains('copy-code-button')) {
    handleCopyButton(button)
    return
  }

  // 保存到知识库按钮
  if (button.classList.contains('save-to-knowledge-button')) {
    await handleSaveToKnowledge(button)
    return
  }

  // 保存到党建活动按钮
  if (button.classList.contains('save-to-party-button')) {
    await handleSaveToParty(button)
    return
  }
}

/**
 * 处理预览按钮点击（现有逻辑）
 */
function handlePreviewButton(button: HTMLButtonElement) {
  const artifactJson = button.dataset.artifactContent
  if (!artifactJson) return

  try {
    const artifact = JSON.parse(artifactJson)
    window.dispatchEvent(new CustomEvent('codeblock-preview', {
      detail: { artifact }
    }))
  } catch (error) {
    console.error('解析 artifact 数据失败:', error)
  }
}

/**
 * 处理复制按钮点击（现有逻辑）
 */
function handleCopyButton(button: HTMLButtonElement) {
  const codeContent = button.dataset.codeContent
  if (!codeContent) return

  // 解码 HTML 实体
  const decodedContent = decodeHtmlEntities(codeContent)

  navigator.clipboard.writeText(decodedContent).then(() => {
    const originalHTML = button.innerHTML
    button.innerHTML = '<svg viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>'
    setTimeout(() => {
      button.innerHTML = originalHTML
    }, 2000)
  })
}

/**
 * 处理保存到知识库
 */
async function handleSaveToKnowledge(button: HTMLButtonElement) {
  const codeContent = button.dataset.codeContent
  if (!codeContent) return

  const decodedContent = decodeHtmlEntities(codeContent)

  try {
    // 加载目录树
    if (knowledgeCategoriesCache.length === 0) {
      knowledgeCategoriesCache = await knowledgeApi.getCategoryTree()
    }

    // 显示保存对话框
    showSaveDialog('knowledge', decodedContent, knowledgeCategoriesCache)
  } catch (error) {
    console.error('加载知识库目录失败:', error)
    ElMessage.error('加载知识库目录失败')
  }
}

/**
 * 处理保存到党建活动
 */
async function handleSaveToParty(button: HTMLButtonElement) {
  const codeContent = button.dataset.codeContent
  if (!codeContent) return

  const decodedContent = decodeHtmlEntities(codeContent)

  try {
    // 加载目录树
    if (partyCategoriesCache.length === 0) {
      partyCategoriesCache = await partyActivityApi.getCategoryTree()
    }

    // 显示保存对话框
    showSaveDialog('party', decodedContent, partyCategoriesCache)
  } catch (error) {
    console.error('加载党建活动目录失败:', error)
    ElMessage.error('加载党建活动目录失败')
  }
}

/**
 * 显示保存对话框
 */
async function showSaveDialog(
  target: 'knowledge' | 'party',
  content: string,
  categories: Category[]
) {
  const { ElDialog, ElCascader, ElInput, ElButton } = await import('element-plus')

  // 创建对话框容器
  const container = document.createElement('div')
  document.body.appendChild(container)

  // 提取默认文件名
  const defaultFilename = extractDefaultFilename(content)

  // 创建 Vue 应用
  const { createApp, ref, h } = await import('vue')

  const app = createApp({
    setup() {
      const visible = ref(true)
      const categoryId = ref<string | null>(null)
      const filename = ref(defaultFilename)
      const loading = ref(false)

      const categoryOptions = buildCascaderOptions(categories)

      const handleSave = async () => {
        if (!categoryId.value) {
          ElMessage.warning('请选择目标目录')
          return
        }
        if (!filename.value.trim()) {
          ElMessage.warning('请输入文件名')
          return
        }

        loading.value = true
        try {
          const fullFilename = filename.value.trim() + '.md'

          // 获取现有文件列表
          const existingFiles = target === 'knowledge'
            ? await knowledgeApi.getDocuments(categoryId.value)
            : await partyActivityApi.getDocuments(categoryId.value)

          const existingNames = existingFiles.map(f => f.original_filename)

          // 检查冲突
          if (existingNames.includes(fullFilename)) {
            const { ElMessageBox } = await import('element-plus')
            try {
              await ElMessageBox.confirm(
                `文件 "${fullFilename}" 已存在，是否覆盖？`,
                '文件名冲突',
                {
                  confirmButtonText: '覆盖',
                  cancelButtonText: '重命名',
                  distinguishCancelAndClose: true,
                  type: 'warning',
                }
              )
            } catch (action: any) {
              loading.value = false
              if (action === 'cancel') {
                // 重命名
                const uniqueName = generateUniqueFilename(filename.value.trim(), existingNames)
                filename.value = uniqueName
                // 递归调用保存
                await handleSave()
              }
              return
            }
          }

          // 调用 API 保存
          if (target === 'knowledge') {
            await knowledgeApi.createDocument({
              category_id: categoryId.value,
              filename: fullFilename,
              content: `\`\`\`${getCodeLanguage(content)}\n${content}\n\`\`\``
            })
          } else {
            await partyActivityApi.createDocument({
              category_id: categoryId.value,
              filename: fullFilename,
              content: `\`\`\`${getCodeLanguage(content)}\n${content}\n\`\`\``
            })
          }

          // 查找目录名称
          const categoryName = findCategoryName(categories, categoryId.value)
          const targetName = target === 'knowledge' ? '知识库' : '党建活动'

          ElMessage.success(`已保存到 ${targetName}/${categoryName}/${fullFilename}`)
          visible.value = false
        } catch (error) {
          console.error('保存失败:', error)
          ElMessage.error('保存失败，请重试')
        } finally {
          loading.value = false
        }
      }

      const handleClose = () => {
        visible.value = false
      }

      return () => h(
        ElDialog,
        {
          modelValue: visible.value,
          'onUpdate:modelValue': (v: boolean) => visible.value = v,
          title: target === 'knowledge' ? '保存到知识库' : '保存到党建活动',
          width: '500px',
          onClose: () => {
            app.unmount()
            container.remove()
          }
        },
        {
          default: () => h('div', { class: 'p-4' }, [
            h('div', { class: 'mb-4' }, [
              h('label', { class: 'block text-sm font-medium mb-2' }, '目标目录'),
              h(ElCascader, {
                modelValue: categoryId.value,
                'onUpdate:modelValue': (v: string) => categoryId.value = v,
                options: categoryOptions,
                    props: {
                      checkStrictly: true,
                      emitPath: false
                    },
                    class: 'w-full',
                    placeholder: '选择目录'
                  })
            ]),
            h('div', { class: 'mb-4' }, [
              h('label', { class: 'block text-sm font-medium mb-2' }, '文件名'),
              h('div', { class: 'relative' }, [
                h(ElInput, {
                  modelValue: filename.value,
                  'onUpdate:modelValue': (v: string) => filename.value = v,
                  placeholder: '输入文件名（不含扩展名）'
                }),
                h('span', { class: 'absolute right-3 top-1/2 -translate-y-1/2 text-gray-400' }, '.md')
              ])
            ])
          ]),
          footer: () => h('div', { class: 'flex justify-end gap-2' }, [
            h(ElButton, { onClick: handleClose }, () => '取消'),
            h(ElButton, {
              type: 'primary',
              loading: loading.value,
              onClick: handleSave
            }, () => '保存')
          ])
        }
      )
    }
  })

  app.mount(container)
}

/**
 * 构建级联选择器选项
 */
function buildCascaderOptions(categories: Category[]): any[] {
  return categories.map(cat => ({
    value: cat.id,
    label: cat.name,
    children: cat.children?.length ? buildCascaderOptions(cat.children) : undefined
  }))
}

/**
 * 查找目录名称
 */
function findCategoryName(categories: Category[], id: string): string {
  for (const cat of categories) {
    if (cat.id === id) return cat.name
    if (cat.children) {
      const found = findCategoryName(cat.children, id)
      if (found) return found
    }
  }
  return '未知目录'
}

/**
 * 推断代码语言（用于保存时包装代码块）
 */
function getCodeLanguage(content: string): string {
  // 简单推断，可以根据内容特征
  if (content.includes('<html') || content.includes('<div')) return 'html'
  if (content.includes('import ') || content.includes('export ')) return 'javascript'
  if (content.includes('def ') || content.includes('class ')) return 'python'
  return 'text'
}

/**
 * 解码 HTML 实体
 */
function decodeHtmlEntities(text: string): string {
  const textarea = document.createElement('textarea')
  textarea.innerHTML = text
  return textarea.value
}

// 导出初始化函数
export { initCodeBlockHandlers }
```

**Step 3: 在 ChatArea.vue 中初始化代码块处理器**

在 `onMounted` 中添加初始化：

```typescript
import { initCodeBlockHandlers } from '@/utils/codeBlockHandlers'

onMounted(() => {
  // ... 现有代码
  initCodeBlockHandlers()
})
```

**Step 4: 添加保存按钮样式**

在 `frontend/src/styles/markdown.css` 中添加：

```css
/* 代码块保存按钮样式 */
.save-to-knowledge-button,
.save-to-party-button {
  @apply p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors;
}

.save-to-knowledge-button svg,
.save-to-party-button svg {
  @apply w-4 h-4;
}
```

**Step 5: 测试代码块保存功能**

1. 启动前端
2. 发送消息让 AI 生成带代码块的回复
3. 点击代码块保存按钮（文件夹图标或旗帜图标）
4. 验证保存对话框弹出
5. 选择目录并保存
6. 验证保存成功提示

**Step 6: 提交**

```bash
git add frontend/src/utils/markdownRenderer.ts frontend/src/utils/codeBlockHandlers.ts frontend/src/styles/markdown.css
git commit -m "feat: 在代码块中添加保存到知识库/党建活动按钮"
```

---

## Task 5: 传递 sessionTitle 到 MessageItem

**Files:**
- Modify: `frontend/src/components/chat/MessageList.vue`
- Modify: `frontend/src/components/ChatPanel.vue`

**Step 1: 在 MessageList.vue 中传递 sessionTitle**

找到 MessageItem 的使用位置，添加 prop：

```vue
<MessageItem
  :message="message"
  :session-title="sessionTitle"
  @mouseenter="handleMouseEnter"
  @mouseleave="handleMouseLeave"
/>
```

确保 MessageList 组件接收 sessionTitle 作为 prop：

```typescript
interface Props {
  messages: Message[]
  streamingContent?: string
  autoScroll?: boolean
  sessionTitle?: string  // 新增
}
```

**Step 2: 在 ChatPanel.vue 中传递 sessionTitle**

```vue
<MessageList
  ref="messageListRef"
  :messages="messages"
  :streaming-content="streamingContent"
  :auto-scroll="autoScroll"
  :session-title="sessionTitle"
/>
```

添加 prop 到 ChatPanel：

```typescript
interface Props {
  // ... 现有 props
  sessionTitle?: string  // 新增
}
```

**Step 3: 在 ChatArea.vue 中传递会话标题**

从 sessionStore 获取当前会话标题并传递：

```typescript
// 获取当前会话标题
const currentSessionTitle = computed(() => {
  return sessionStore.currentSession?.title || ''
})
```

```vue
<ChatPanel
  ref="chatPanelRef"
  :tool-id="toolId"
  :messages="sessionStore.messages"
  :welcome-message="welcomeMessage"
  :session-id="currentSessionId ?? undefined"
  :conversation-collapsed="conversationListCollapsed"
  :error="sessionStore.error ?? undefined"
  :is-loading="sessionStore.loading"
  :session-title="currentSessionTitle"
  class="chat-panel"
  :style="showPreview ? { width: chatPanelWidth + 'px' } : {}"
  @send="handleSendMessage"
  @retry="handleRetry"
  @preview="openPreview"
  @open-knowledge="handleOpenKnowledge"
  @open-party-activity="handleOpenPartyActivity"
/>
```

**Step 4: 提交**

```bash
git add frontend/src/components/chat/MessageList.vue frontend/src/components/ChatPanel.vue frontend/src/components/ChatArea.vue
git commit -m "feat: 传递会话标题到 MessageItem 用于文件名提取"
```

---

## Task 6: 添加 E2E 测试

**Files:**
- Create: `frontend/tests/e2e/save-content.spec.ts`

**Step 1: 创建 E2E 测试文件**

```typescript
# -*- coding: utf-8 -*-
import { test, expect } from '@playwright/test'

test.describe('AI 内容保存功能', () => {
  test.beforeEach(async ({ page }) => {
    // 登录
    await page.goto('http://localhost:5173')
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'admin123')
    await page.click('button[type="submit"]')
    await page.waitForURL('**/tools')
  })

  test('应该显示 AI 回复的保存按钮', async ({ page }) => {
    // 进入 AI 聊天页面
    await page.click('text=AI 教研员')
    await page.waitForSelector('.chat-panel')

    // 发送消息
    await page.fill('textarea[placeholder*="输入"]', '写一个 Vue 组件')
    await page.click('button:has-text("发送")')

    // 等待 AI 回复
    await page.waitForSelector('.message-assistant')

    // 将鼠标悬停在 AI 回复上
    const assistantMessage = page.locator('.message-assistant').last()
    await assistantMessage.hover()

    // 验证保存按钮存在
    await expect(assistantMessage.locator('.save-button')).toHaveCount(2)
  })

  test('应该能够保存 AI 回复到知识库', async ({ page }) => {
    // 进入 AI 聊天页面
    await page.click('text=AI 教研员')
    await page.waitForSelector('.chat-panel')

    // 发送消息
    await page.fill('textarea[placeholder*="输入"]', '写一段测试文本')
    await page.click('button:has-text("发送")')

    // 等待 AI 回复
    await page.waitForSelector('.message-assistant')
    const assistantMessage = page.locator('.message-assistant').last()
    await assistantMessage.hover()

    // 点击保存到知识库按钮
    await assistantMessage.locator('.save-button').first().click()

    // 验证保存对话框打开
    await expect(page.locator('.el-dialog__title')).toContainText('保存到知识库')

    // 选择目录（假设有根目录）
    await page.click('.el-cascader')

    // 输入文件名
    const filenameInput = page.locator('input[placeholder*="文件名"]')
    await filenameInput.fill('测试文件')

    // 点击保存
    await page.click('button:has-text("保存")')

    // 验证成功提示
    await expect(page.locator('.el-message--success')).toBeVisible()
  })

  test('应该在文件名冲突时显示确认对话框', async ({ page }) => {
    // 这个测试需要预先存在同名文件，或者使用 mock API
    test.skip('需要 mock API 或预先创建文件')
  })
})
```

**Step 2: 运行 E2E 测试**

```bash
cd frontend
npm run test:e2e
```

**Step 3: 提交**

```bash
git add frontend/tests/e2e/save-content.spec.ts
git commit -m "test: 添加保存功能 E2E 测试"
```

---

## Task 7: 清理和优化

**Files:**
- Modify: 多个文件

**Step 1: 检查控制台无报错**

运行开发服务器，检查浏览器控制台无错误

**Step 2: 检查样式一致性**

确保保存按钮样式与党建主题一致

**Step 3: 代码格式化**

```bash
cd frontend
npm run format
```

**Step 4: 类型检查**

```bash
cd frontend
npm run build
```

**Step 5: 最终提交**

```bash
git add -A
git commit -m "chore: 清理和优化保存功能代码"
```

---

## 验收清单

完成所有任务后，验证以下功能：

- [ ] AI 回复工具栏显示两个保存按钮
- [ ] 代码块显示两个保存按钮
- [ ] 点击保存按钮弹出对话框
- [ ] 文件名默认值正确提取
- [ ] 可以选择目录和修改文件名
- [ ] 文件名冲突时显示确认对话框
- [ ] 保存成功后显示 Toast 提示
- [ ] 保存的文件可以在知识库/党建活动中查看
- [ ] 无控制台报错
- [ ] E2E 测试通过

---

## 相关文件清单

| 文件 | 操作 |
|------|------|
| `frontend/src/components/file-manager/CreateFileDialog.vue` | 修改 |
| `frontend/src/utils/filenameExtractor.ts` | 新建 |
| `frontend/src/utils/__tests__/filenameExtractor.spec.ts` | 新建 |
| `frontend/src/components/chat/MessageItem.vue` | 修改 |
| `frontend/src/components/chat/SaveToDialog.vue` | 新建 |
| `frontend/src/components/chat/MessageList.vue` | 修改 |
| `frontend/src/components/ChatPanel.vue` | 修改 |
| `frontend/src/components/ChatArea.vue` | 修改 |
| `frontend/src/utils/markdownRenderer.ts` | 修改 |
| `frontend/src/utils/codeBlockHandlers.ts` | 修改 |
| `frontend/src/styles/markdown.css` | 修改 |
| `frontend/tests/e2e/save-content.spec.ts` | 新建 |
