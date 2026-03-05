# -*- coding: utf-8 -*-
<template>
  <div
    class="file-card"
    :class="{ 'selected': isSelected, 'party-theme': isPartyTheme }"
    @click="handleClick"
    @contextmenu.prevent="handleContextMenu"
  >
    <!-- 复选框 -->
    <div class="file-card-checkbox" @click.stop>
      <el-checkbox :model-value="isSelected" @change="handleToggleSelect" />
    </div>

    <!-- 文件图标 -->
    <div class="file-card-icon">
      <component :is="fileIcon" class="w-12 h-12" />
    </div>

    <!-- 文件信息 -->
    <div class="file-card-info">
      <div class="file-card-name" :title="document.original_filename">
        {{ document.original_filename }}
      </div>
      <div class="file-card-meta">
        <span>{{ fileTypeText }}</span>
        <span v-if="document.file_size">{{ formatFileSize(document.file_size) }}</span>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="file-card-actions">
      <el-dropdown trigger="click" @command="handleAction">
        <button class="action-btn">
          <EllipsisVerticalIcon class="w-5 h-5" />
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="open">
              <EyeIcon class="w-4 h-4" />
              <span>打开</span>
            </el-dropdown-item>
            <el-dropdown-item command="edit">
              <PencilIcon class="w-4 h-4" />
              <span>编辑</span>
            </el-dropdown-item>
            <el-dropdown-item command="download">
              <ArrowDownTrayIcon class="w-4 h-4" />
              <span>下载</span>
            </el-dropdown-item>
            <el-dropdown-item command="rename" divided>
              <PencilSquareIcon class="w-4 h-4" />
              <span>重命名</span>
            </el-dropdown-item>
            <el-dropdown-item command="delete" class="danger-item">
              <TrashIcon class="w-4 h-4" />
              <span>删除</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  DocumentIcon,
  ChartBarIcon,
  ChartPieIcon,
  CodeBracketIcon,
  PhotoIcon,
  EllipsisVerticalIcon,
  EyeIcon,
  PencilIcon,
  ArrowDownTrayIcon,
  PencilSquareIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'
import type { Document, FileType } from '@/types/file-manager'

interface Props {
  document: Document
  isSelected?: boolean
  isPartyTheme?: boolean
}

interface Emits {
  (e: 'click', document: Document): void
  (e: 'toggleSelect', documentId: string): void
  (e: 'open', document: Document): void
  (e: 'edit', document: Document): void
  (e: 'download', document: Document): void
  (e: 'rename', document: Document): void
  (e: 'delete', document: Document): void
}

const props = withDefaults(defineProps<Props>(), {
  isSelected: false,
  isPartyTheme: false
})

const emit = defineEmits<Emits>()

// 文件类型图标映射
const fileIcons: Record<FileType, any> = {
  word: ChartBarIcon,
  pdf: ChartPieIcon,
  excel: ChartBarIcon,
  markdown: CodeBracketIcon,
  text: DocumentIcon,
  image: PhotoIcon
}

const fileIcon = computed(() => fileIcons[props.document.file_type] || DocumentIcon)

const fileTypeTexts: Record<FileType, string> = {
  word: 'Word 文档',
  pdf: 'PDF 文档',
  excel: 'Excel 表格',
  markdown: 'Markdown',
  text: '文本文件',
  image: '图片'
}

const fileTypeText = computed(() => fileTypeTexts[props.document.file_type])

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// 事件处理
const handleClick = () => emit('click', props.document)

const handleToggleSelect = () => emit('toggleSelect', props.document.id)

const handleContextMenu = () => {
  // 可以在这里实现自定义右键菜单
}

const handleAction = (command: string) => {
  switch (command) {
    case 'open':
      emit('open', props.document)
      break
    case 'edit':
      emit('edit', props.document)
      break
    case 'download':
      emit('download', props.document)
      break
    case 'rename':
      emit('rename', props.document)
      break
    case 'delete':
      emit('delete', props.document)
      break
  }
}
</script>

<style scoped>
.file-card {
  @apply relative bg-white rounded-lg border border-gray-200 p-4 cursor-pointer transition-all;
  display: grid;
  grid-template-columns: auto 1fr auto;
  grid-template-rows: auto auto;
  gap: 12px;
}

.file-card:hover {
  @apply shadow-md border-gray-300;
}

.file-card.selected {
  @apply border-red-500 bg-red-50;
}

.file-card.party-theme.selected {
  @apply border-red-600 bg-red-50;
}

/* 复选框 */
.file-card-checkbox {
  grid-row: 1 / -1;
  @apply flex items-center justify-center;
}

/* 图标 */
.file-card-icon {
  grid-column: 2;
  grid-row: 1;
  @apply flex items-center justify-center text-gray-400;
}

.file-card.party-theme .file-card-icon {
  @apply text-red-700;
}

/* 文件信息 */
.file-card-info {
  grid-column: 2;
  grid-row: 2;
  @apply flex flex-col gap-1 min-w-0;
}

.file-card-name {
  @apply font-medium text-gray-900 truncate;
}

.file-card-meta {
  @apply flex items-center gap-2 text-xs text-gray-500;
}

/* 操作按钮 */
.file-card-actions {
  grid-column: 3;
  grid-row: 1 / -1;
  @apply flex items-start;
}

.action-btn {
  @apply p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors;
}

.action-btn:hover {
  @apply text-gray-600;
}

/* 下拉菜单项样式 */
:deep(.el-dropdown-menu__item) {
  @apply flex items-center gap-2;
}

:deep(.danger-item) {
  @apply text-red-600;
}

:deep(.danger-item:hover) {
  @apply bg-red-50;
}
</style>
