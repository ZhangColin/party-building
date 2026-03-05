/**
 * 代码块按钮事件处理器
 * 处理通过 markdownRenderer 生成的代码块复制、预览和保存按钮
 */

import type { Category } from '@/types/file-manager'
import { unescapeHtml } from './htmlUtils'

/** 目录数据缓存 */
let knowledgeCategoriesCache: Category[] = []
let partyCategoriesCache: Category[] = []

/** 标记事件监听器是否已注册 */
let isHandlerRegistered = false

/**
 * 初始化代码块按钮的事件监听器
 * 防止重复注册
 */
export function initCodeBlockHandlers() {
  // 防止重复注册事件监听器
  if (isHandlerRegistered) {
    return;
  }
  isHandlerRegistered = true;

  // 使用事件委托处理动态生成的按钮
  document.addEventListener('click', handleCodeBlockClick);
}

/**
 * 处理代码块按钮点击事件
 */
function handleCodeBlockClick(event: Event) {
  const target = event.target as HTMLElement;

  // 查找最近的按钮元素（处理点击图标的情况）
  const button = target.closest('button') as HTMLButtonElement;
  if (!button) return;

  // 处理复制代码按钮
  if (button.classList.contains('copy-code-button')) {
    handleCopyCode(button);
    return;
  }

  // 处理预览按钮
  if (button.classList.contains('preview-button')) {
    handlePreview(button);
    return;
  }

  // 保存到知识库按钮
  if (button.classList.contains('save-to-knowledge-button')) {
    handleSaveToKnowledge(button);
    return;
  }

  // 保存到党建活动按钮
  if (button.classList.contains('save-to-party-button')) {
    handleSaveToParty(button);
    return;
  }
}

/**
 * 处理复制代码
 */
function handleCopyCode(button: HTMLButtonElement) {
  const codeContent = button.getAttribute('data-code-content');
  if (!codeContent) {
    console.warn('[CodeBlock] 未找到代码内容');
    return;
  }

  // 反转义 HTML 实体
  const decodedContent = unescapeHtml(codeContent);

  // 复制到剪贴板
  navigator.clipboard.writeText(decodedContent)
    .then(() => {
      // 显示成功提示
      showToast('代码已复制到剪贴板');

      // 更新按钮状态
      const originalContent = button.innerHTML;
      button.innerHTML = `
        <svg viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
        </svg>
      `;
      button.classList.add('copied');

      // 2秒后恢复原始状态
      setTimeout(() => {
        button.innerHTML = originalContent;
        button.classList.remove('copied');
      }, 2000);
    })
    .catch((err) => {
      console.error('[CodeBlock] 复制失败:', err);
      showToast('复制失败，请重试', 'error');
    });
}

/**
 * 处理预览按钮
 */
function handlePreview(button: HTMLButtonElement) {
  const artifactData = button.getAttribute('data-artifact-content');
  if (!artifactData) {
    console.warn('[CodeBlock] 未找到 artifact 数据');
    return;
  }

  try {
    const artifact = JSON.parse(unescapeHtml(artifactData));

    // 触发全局预览事件，使用 window 对象传递
    const previewEvent = new CustomEvent('codeblock-preview', {
      detail: { artifact },
      bubbles: true,
    });

    // 从按钮向上冒泡到文档
    button.dispatchEvent(previewEvent);

    // 也向 window 派发，确保 ChatArea 能监听到
    window.dispatchEvent(previewEvent);

    console.log('[CodeBlock] 触发预览事件:', artifact);
  } catch (err) {
    console.error('[CodeBlock] 解析 artifact 数据失败:', err);
    showToast('预览失败', 'error');
  }
}

/**
 * 显示 Toast 提示
 */
function showToast(message: string, type: 'success' | 'error' = 'success') {
  // 检查是否有全局 Toast
  const globalToast = (window as any).__showToast;
  if (globalToast) {
    globalToast(message);
    return;
  }

  // 创建简单的提示元素
  const toast = document.createElement('div');
  toast.className = `code-block-toast code-block-toast-${type}`;
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: ${type === 'success' ? '#10b981' : '#ef4444'};
    color: white;
    padding: 10px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 10000;
    animation: slideUp 0.3s ease-out;
  `;

  document.body.appendChild(toast);

  // 3秒后移除
  setTimeout(() => {
    toast.style.animation = 'slideDown 0.3s ease-out';
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 300);
  }, 3000);
}

/**
 * 处理保存到知识库
 */
async function handleSaveToKnowledge(button: HTMLButtonElement) {
  const codeContent = button.getAttribute('data-code-content');
  if (!codeContent) {
    console.warn('[CodeBlock] 未找到代码内容');
    return;
  }

  const decodedContent = unescapeHtml(codeContent);

  try {
    // 动态导入依赖
    const { ElMessage } = await import('element-plus');
    const { getCategoryTree, getDocuments, createDocument } = await import('@/services/knowledgeApi');
    const { extractDefaultFilename } = await import('@/utils/filenameExtractor');

    // 加载目录树
    if (knowledgeCategoriesCache.length === 0) {
      knowledgeCategoriesCache = await getCategoryTree();
    }

    // 构造 API 服务对象
    const apiService = { getDocuments, createDocument };

    // 显示保存对话框
    showSaveDialog('knowledge', decodedContent, knowledgeCategoriesCache, ElMessage, apiService, extractDefaultFilename);
  } catch (error) {
    console.error('[CodeBlock] 保存到知识库失败:', error);
    showToast('保存失败，请重试', 'error');
  }
}

/**
 * 处理保存到党建活动
 */
async function handleSaveToParty(button: HTMLButtonElement) {
  const codeContent = button.getAttribute('data-code-content');
  if (!codeContent) {
    console.warn('[CodeBlock] 未找到代码内容');
    return;
  }

  const decodedContent = unescapeHtml(codeContent);

  try {
    const { ElMessage } = await import('element-plus');
    const { getCategoryTree, getDocuments, createDocument } = await import('@/services/partyActivityApi');
    const { extractDefaultFilename } = await import('@/utils/filenameExtractor');

    if (partyCategoriesCache.length === 0) {
      partyCategoriesCache = await getCategoryTree();
    }

    // 构造 API 服务对象
    const apiService = { getDocuments, createDocument };

    showSaveDialog('party', decodedContent, partyCategoriesCache, ElMessage, apiService, extractDefaultFilename);
  } catch (error) {
    console.error('[CodeBlock] 保存到党建活动失败:', error);
    showToast('保存失败，请重试', 'error');
  }
}

/**
 * 显示保存对话框
 */
async function showSaveDialog(
  target: 'knowledge' | 'party',
  content: string,
  categories: Category[],
  ElMessage: any,
  apiService: any,
  extractDefaultFilename: (content: string, title?: string) => string
) {
  // 动态导入 Vue 和 Element Plus 组件
  const { createApp, ref, h } = await import('vue');
  const { ElDialog, ElCascader, ElInput, ElButton, ElMessageBox } = await import('element-plus');

  // 创建对话框容器
  const container = document.createElement('div');
  document.body.appendChild(container);

  // 提取默认文件名
  const defaultFilename = extractDefaultFilename(content);

  // 创建 Vue 应用
  const app = createApp({
    setup() {
      const visible = ref(true);
      const categoryId = ref<string | null>(null);
      const filename = ref(defaultFilename);
      const loading = ref(false);

      const categoryOptions = buildCascaderOptions(categories);

      const handleSave = async () => {
        if (!categoryId.value) {
          ElMessage.warning('请选择目标目录');
          return;
        }
        if (!filename.value.trim()) {
          ElMessage.warning('请输入文件名');
          return;
        }

        loading.value = true;
        try {
          const fullFilename = filename.value.trim() + '.md';

          // 获取现有文件列表检查冲突
          const existingFiles = await apiService.getDocuments(categoryId.value);
          const existingNames = existingFiles.map((f: any) => f.original_filename);

          // 检查冲突
          if (existingNames.includes(fullFilename)) {
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
              );
            } catch (action: any) {
              loading.value = false;
              if (action === 'cancel') {
                // 重命名
                const { generateUniqueFilename } = await import('@/utils/filenameExtractor');
                const uniqueName = generateUniqueFilename(filename.value.trim(), existingNames);
                filename.value = uniqueName;
                await handleSave();
              }
              return;
            }
          }

          // 保存（代码块内容用 markdown 代码块包裹）
          const wrappedContent = wrapCodeBlock(content);
          await apiService.createDocument({
            category_id: categoryId.value,
            filename: fullFilename,
            content: wrappedContent
          });

          const categoryName = findCategoryName(categories, categoryId.value);
          const targetName = target === 'knowledge' ? '知识库' : '党建活动';

          ElMessage.success(`已保存到 ${targetName}/${categoryName}/${fullFilename}`);
          visible.value = false;
        } catch (error) {
          console.error('[CodeBlock] 保存失败:', error);
          ElMessage.error('保存失败，请重试');
        } finally {
          loading.value = false;
        }
      };

      return () => h(
        ElDialog,
        {
          modelValue: visible.value,
          'onUpdate:modelValue': (v: boolean) => visible.value = v,
          title: target === 'knowledge' ? '保存到知识库' : '保存到党建活动',
          width: '500px',
          onClose: () => {
            app.unmount();
            container.remove();
          }
        },
        {
          default: () => h('div', { class: 'p-4' }, [
            h('div', { class: 'mb-4' }, [
              h('label', { class: 'block text-sm font-medium mb-2' }, '目标目录'),
              h(ElCascader, {
                modelValue: categoryId.value,
                'onUpdate:modelValue': (v: any) => categoryId.value = v as string | null,
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
            h(ElButton, { onClick: () => visible.value = false }, () => '取消'),
            h(ElButton, {
              type: 'primary',
              loading: loading.value,
              onClick: handleSave
            }, () => '保存')
          ])
        }
      );
    }
  });

  app.mount(container);
}

/**
 * 构建级联选择器选项
 */
function buildCascaderOptions(categories: Category[]): any[] {
  return categories.map(cat => ({
    value: cat.id,
    label: cat.name,
    children: cat.children?.length ? buildCascaderOptions(cat.children) : undefined
  }));
}

/**
 * 查找目录名称
 */
function findCategoryName(categories: Category[], id: string): string {
  for (const cat of categories) {
    if (cat.id === id) return cat.name;
    if (cat.children) {
      const found = findCategoryName(cat.children, id);
      if (found) return found;
    }
  }
  return '未知目录';
}

/**
 * 包裹代码块为 markdown 格式
 */
function wrapCodeBlock(content: string): string {
  // 简单推断语言
  let lang = 'text';
  if (content.includes('<html') || content.includes('<div')) lang = 'html';
  else if (content.includes('import ') || content.includes('export ')) lang = 'javascript';
  else if (content.includes('def ') || content.includes('class ')) lang = 'python';

  return `\`\`\`${lang}\n${content}\n\`\`\``;
}

// 添加动画样式（幂等性：检查是否已存在）
const styleId = 'code-block-handlers-styles';
let existingStyle = document.getElementById(styleId);
if (!existingStyle) {
  const style = document.createElement('style');
  style.id = styleId;
  style.textContent = `
    @keyframes slideUp {
      from {
        opacity: 0;
        transform: translateX(-50%) translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateX(-50%) translateY(0);
      }
    }

    @keyframes slideDown {
      from {
        opacity: 1;
        transform: translateX(-50%) translateY(0);
      }
      to {
        opacity: 0;
        transform: translateX(-50%) translateY(20px);
      }
    }

    .copy-code-button.copied {
      color: #10b981 !important;
    }
  `;
  document.head.appendChild(style);
}
