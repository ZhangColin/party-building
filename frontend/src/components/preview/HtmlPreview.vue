<template>
  <div class="html-preview-wrapper">
    <iframe
      v-if="blobUrl"
      :src="blobUrl"
      class="html-preview-iframe"
      sandbox="allow-scripts allow-same-origin allow-forms allow-modals"
      data-testid="html-preview-iframe"
    />
    <div v-else class="html-preview-empty" data-testid="html-preview-empty">
      No HTML content
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue';

interface Props {
  content: string;
}

const props = defineProps<Props>();

const blobUrl = ref<string | null>(null);

// 清理之前的 Blob URL
const cleanupBlob = () => {
  if (blobUrl.value) {
    URL.revokeObjectURL(blobUrl.value);
    blobUrl.value = null;
  }
};

// 监听内容变化，创建新的 Blob URL
watch(
  () => props.content,
  (newContent) => {
    cleanupBlob();

    if (!newContent) {
      return;
    }

    // 创建 Blob 并生成 URL
    const blob = new Blob([newContent], { type: 'text/html' });
    blobUrl.value = URL.createObjectURL(blob);
  },
  { immediate: true }
);

// 组件卸载时清理
onBeforeUnmount(() => {
  cleanupBlob();
});
</script>

<style scoped>
.html-preview-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.html-preview-iframe {
  width: 100%;
  height: 100%;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background-color: #fff;
}

.html-preview-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  font-style: italic;
}
</style>
