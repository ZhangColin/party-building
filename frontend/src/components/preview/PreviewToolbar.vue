<template>
  <div class="preview-toolbar" data-testid="preview-toolbar">
    <button
      v-if="showMarkdownDownload"
      class="toolbar-btn"
      @click="handleDownloadMarkdown"
      data-testid="btn-download-markdown"
      title="下载 Markdown"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
        <polyline points="7 10 12 15 17 10"></polyline>
        <line x1="12" y1="15" x2="12" y2="3"></line>
      </svg>
      <span class="btn-text">Markdown</span>
    </button>

    <button
      v-if="showMarkdownDownload"
      class="toolbar-btn"
      @click="handleDownloadWord"
      :disabled="props.isDownloadingWord"
      data-testid="btn-download-word"
      :title="props.isDownloadingWord ? '正在转换...' : '下载 Word 文档'"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
        <polyline points="7 10 12 15 17 10"></polyline>
        <line x1="12" y1="15" x2="12" y2="3"></line>
      </svg>
      <span class="btn-text">{{ props.isDownloadingWord ? '转换中...' : 'Word' }}</span>
    </button>

    <button
      v-if="showMarkdownDownload"
      class="toolbar-btn"
      @click="handleDownloadPDF"
      :disabled="props.isDownloadingPDF"
      data-testid="btn-download-pdf"
      :title="props.isDownloadingPDF ? '正在生成 PDF...' : '下载 PDF 文档'"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
        <polyline points="7 10 12 15 17 10"></polyline>
        <line x1="12" y1="15" x2="12" y2="3"></line>
      </svg>
      <span class="btn-text">{{ props.isDownloadingPDF ? '生成中...' : 'PDF' }}</span>
    </button>

    <button
      v-if="showSvgDownload"
      class="toolbar-btn"
      @click="handleDownloadSvg"
      data-testid="btn-download-svg"
      title="下载 SVG"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
        <polyline points="7 10 12 15 17 10"></polyline>
        <line x1="12" y1="15" x2="12" y2="3"></line>
      </svg>
      <span class="btn-text">SVG</span>
    </button>

    <button
      class="toolbar-btn"
      @click="handleToggleFullscreen"
      data-testid="btn-toggle-fullscreen"
      :title="isFullscreen ? '退出全屏' : '全屏'"
    >
      <svg v-if="!isFullscreen" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
      </svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3"></path>
      </svg>
    </button>

    <button
      class="toolbar-btn"
      @click="handleClosePreview"
      data-testid="btn-close-preview"
      title="关闭预览"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  artifactType: string;
  isFullscreen?: boolean;
  isDownloadingWord?: boolean;
  isDownloadingPDF?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  isFullscreen: false,
  isDownloadingWord: false,
  isDownloadingPDF: false,
});

const emit = defineEmits<{
  downloadMarkdown: [];
  downloadWord: [];
  downloadPDF: [];
  downloadSvg: [];
  toggleFullscreen: [];
  closePreview: [];
}>();

const showMarkdownDownload = computed(() => {
  return props.artifactType === 'markdown';
});

const showSvgDownload = computed(() => {
  return props.artifactType === 'svg';
});

const handleDownloadMarkdown = () => {
  emit('downloadMarkdown');
};

const handleDownloadWord = () => {
  emit('downloadWord');
};

const handleDownloadPDF = () => {
  console.log('[PreviewToolbar] handleDownloadPDF 被调用')
  console.log('[PreviewToolbar] 当前 isDownloadingPDF 状态:', props.isDownloadingPDF)
  console.log('[PreviewToolbar] 按钮是否被禁用:', props.isDownloadingPDF === true)
  console.log('[PreviewToolbar] 准备 emit downloadPDF 事件')
  emit('downloadPDF');
  console.log('[PreviewToolbar] 已 emit downloadPDF 事件')
};

const handleDownloadSvg = () => {
  emit('downloadSvg');
};

const handleToggleFullscreen = () => {
  emit('toggleFullscreen');
};

const handleClosePreview = () => {
  emit('closePreview');
};
</script>

<style scoped>
.preview-toolbar {
  display: flex;
  gap: 8px;
  padding: 8px;
  background-color: #f5f5f5;
  align-items: center;
  justify-content: flex-end;
  /* 党建主题：分隔线样式 */
  border-bottom: 2px solid #FFD700;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background-color: white;
  border: 1px solid #d0d0d0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: all 0.2s;
}

.toolbar-btn:hover:not(:disabled) {
  background-color: #f0f0f0;
  border-color: #C8102E; /* 党建主题红色 */
  color: #C8102E;
}

.toolbar-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-text {
  font-size: 13px;
}
</style>
