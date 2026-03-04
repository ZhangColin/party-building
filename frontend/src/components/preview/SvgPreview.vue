<template>
  <div class="svg-preview-wrapper">
    <div
      v-if="sanitizedSvg"
      class="svg-preview-content"
      v-html="sanitizedSvg"
      data-testid="svg-preview-content"
      @click="handleDownload"
    />
    <div v-else class="svg-preview-empty" data-testid="svg-preview-empty">
      No SVG content
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import DOMPurify from 'dompurify';

interface Props {
  content: string;
  filename?: string;
}

const props = withDefaults(defineProps<Props>(), {
  filename: 'artifact.svg',
});

const emit = defineEmits<{
  download: [blob: Blob];
}>();

const sanitizedSvg = computed(() => {
  if (!props.content) return '';

  // 验证是否为有效的SVG
  if (!props.content.includes('<svg') && !props.content.includes('<?xml')) {
    return '';
  }

  // 使用DOMPurify清理SVG，仅允许SVG相关标签
  return DOMPurify.sanitize(props.content, {
    USE_PROFILES: { svg: true, svgFilters: true },
    ALLOWED_TAGS: [
      'svg', 'path', 'circle', 'rect', 'line', 'polygon', 'polyline',
      'ellipse', 'text', 'g', 'defs', 'linearGradient', 'radialGradient',
      'stop', 'use', 'foreignObject', 'image', 'pattern', 'mask',
    ],
  });
});

const handleDownload = () => {
  // 创建Blob对象
  const blob = new Blob([props.content], { type: 'image/svg+xml' });

  // 创建下载链接
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = props.filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);

  emit('download', blob);
};
</script>

<style scoped>
.svg-preview-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.svg-preview-content {
  max-width: 100%;
  max-height: 100%;
  cursor: pointer;
  transition: transform 0.2s;
}

.svg-preview-content:hover {
  transform: scale(1.02);
}

.svg-preview-content :deep(svg) {
  display: block;
  max-width: 100%;
  max-height: 100%;
}

.svg-preview-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  font-style: italic;
}
</style>
