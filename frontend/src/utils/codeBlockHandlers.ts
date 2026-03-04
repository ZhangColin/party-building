/**
 * 代码块按钮事件处理器
 * 处理通过 markdownRenderer 生成的代码块复制和预览按钮
 */

/**
 * 初始化代码块按钮的事件监听器
 */
export function initCodeBlockHandlers() {
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
 * 反转义 HTML 实体
 */
function unescapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&amp;': '&',
    '&lt;': '<',
    '&gt;': '>',
    '&quot;': '"',
    '&#039;': "'",
    '&nbsp;': ' ',
  };
  return text.replace(/&(?:amp|lt|gt|quot|#039|nbsp);/g, (m) => map[m] || m);
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

// 添加动画样式
const style = document.createElement('style');
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
