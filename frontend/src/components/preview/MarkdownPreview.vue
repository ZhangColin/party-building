<template>
  <div
    id="markdown-preview-content"
    class="markdown-preview markdown-content"
    v-html="renderedHtml"
    data-testid="markdown-preview"
  />
  <div v-if="hasError" class="markdown-error" data-testid="markdown-error">
    Markdown 渲染失败，请检查内容格式
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { renderMarkdown } from '@/utils/markdownRenderer';

interface Props {
  content: string;
}

const props = defineProps<Props>();
const hasError = ref(false);

const renderedHtml = computed(() => {
  if (!props.content) return '';

  try {
    const result = renderMarkdown(props.content);
    hasError.value = false;
    return result;
  } catch (error) {
    console.error('Markdown rendering failed:', error);
    hasError.value = true;
    return '';
  }
});
</script>

<style scoped>
@import '@/styles/markdown.css';

.markdown-preview {
  line-height: 1.6;
  color: #333;
}

.markdown-error {
  padding: 12px;
  background-color: #fee2e2;
  border: 1px solid #ef4444;
  border-radius: 4px;
  color: #991b1b;
  margin-top: 8px;
}
</style>
