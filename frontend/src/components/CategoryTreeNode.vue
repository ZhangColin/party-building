<template>
  <div class="category-tree-node">
    <!-- 当前节点 -->
    <div
      class="node-content"
      :class="{ active: isSelected, 'has-children': hasChildren }"
      @click="handleClick"
    >
      <!-- 展开/收起图标 -->
      <button
        v-if="hasChildren"
        class="expand-button"
        @click.stop="toggleExpand"
      >
        <ChevronRightIcon
          class="w-4 h-4 transition-transform"
          :class="{ 'rotate-90': isExpanded }"
        />
      </button>
      <span v-else class="expand-placeholder"></span>

      <!-- 文件夹图标 -->
      <FolderIcon v-if="!isExpanded" class="node-icon" />
      <FolderOpenIcon v-else class="node-icon" />

      <!-- 节点名称 -->
      <span class="node-name">{{ node.name }}</span>
    </div>

    <!-- 子节点 -->
    <div v-if="hasChildren && isExpanded" class="children-container">
      <CategoryTreeNode
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :selectedId="selectedId"
        @select="$emit('select', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  ChevronRightIcon,
  FolderIcon,
  FolderOpenIcon,
} from '@heroicons/vue/24/outline'
import type { CourseCategoryNode } from '../types'

interface Props {
  node: CourseCategoryNode
  selectedId: string | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  select: [categoryId: string]
}>()

const isExpanded = ref(false)

const hasChildren = computed(() => {
  return props.node.children && props.node.children.length > 0
})

const isSelected = computed(() => {
  return props.selectedId === props.node.id
})

/**
 * 切换展开/收起
 */
const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}

/**
 * 处理节点点击
 */
const handleClick = () => {
  emit('select', props.node.id)
  // 自动展开有子节点的目录
  if (hasChildren.value && !isExpanded.value) {
    isExpanded.value = true
  }
}
</script>

<style scoped>
.category-tree-node {
  @apply select-none;
}

.node-content {
  @apply flex items-center gap-1.5 px-2 py-1.5 rounded cursor-pointer hover:bg-gray-100 transition-colors;
}

.node-content.active {
  @apply bg-blue-50 text-blue-700 hover:bg-blue-100;
}

.expand-button {
  @apply flex-shrink-0 p-0.5 hover:bg-gray-200 rounded transition-colors;
}

.node-content.active .expand-button:hover {
  @apply bg-blue-200;
}

.expand-placeholder {
  @apply flex-shrink-0 w-5;
}

.node-icon {
  @apply w-4 h-4 flex-shrink-0 text-gray-500;
}

.node-content.active .node-icon {
  @apply text-blue-600;
}

.node-name {
  @apply flex-1 text-sm text-gray-700 truncate;
}

.node-content.active .node-name {
  @apply text-blue-700 font-medium;
}

.children-container {
  @apply ml-4 mt-0.5 space-y-0.5;
}
</style>

