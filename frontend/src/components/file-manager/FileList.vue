# -*- coding: utf-8 -*-
<template>
  <div class="file-list" :class="{ 'party-theme': isPartyTheme }">
    <!-- 表头 -->
    <div class="file-list-header">
      <div class="file-list-checkbox">
        <el-checkbox
          :model-value="allSelected"
          :indeterminate="someSelected"
          @change="handleSelectAll"
        />
      </div>
      <div class="file-list-name">文件名</div>
      <div class="file-list-type">类型</div>
      <div class="file-list-size">大小</div>
      <div class="file-list-date">修改时间</div>
      <div class="file-list-actions">操作</div>
    </div>

    <!-- 文件列表 -->
    <div class="file-list-body">
      <div
        v-for="document in documents"
        :key="document.id"
        class="file-list-item"
        :class="{ 'selected': selectedIds.has(document.id) }"
        @click="handleClick(document)"
      >
        <div class="file-list-checkbox" @click.stop>
          <el-checkbox
            :model-value="selectedIds.has(document.id)"
            @change="handleToggleSelect(document.id)"
          />
        </div>
        <div class="file-list-name">
          <component :is="getFileIcon(document.file_type)" class="file-icon" />
          <span class="file-name-text" :title="document.original_filename">
            {{ document.original_filename }}
          </span>
        </div>
        <div class="file-list-type">{{ getFileTypeText(document.file_type) }}</div>
        <div class="file-list-size">
          {{ document.file_size ? formatFileSize(document.file_size) : '-' }}
        </div>
        <div class="file-list-date">{{ formatDate(document.updated_at) }}</div>
        <div class="file-list-actions" @click.stop>
          <el-dropdown trigger="click" @command="(cmd: string) => handleAction(cmd, document)">
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

      <!-- 空状态 -->
      <div v-if="documents.length === 0" class="file-list-empty">
        <DocumentIcon class="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <p class="text-gray-500">暂无文件</p>
      </div>
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
  documents: Document[]
  selectedIds: Set<string>
  isPartyTheme?: boolean
}

interface Emits {
  (e: 'click', document: Document): void
  (e: 'toggleSelect', documentId: string): void
  (e: 'selectAll'): void
  (e: 'clearSelection'): void
  (e: 'open', document: Document): void
  (e: 'edit', document: Document): void
  (e: 'download', document: Document): void
  (e: 'rename', document: Document): void
  (e: 'delete', document: Document): void
}

const props = withDefaults(defineProps<Props>(), {
  isPartyTheme: false
})

const emit = defineEmits<Emits>()

// 选择状态
const allSelected = computed(() => props.documents.length > 0 && props.selectedIds.size === props.documents.length)
const someSelected = computed(() => props.selectedIds.size > 0 && !allSelected.value)

// 文件类型图标映射
const fileIcons: Record<FileType, any> = {
  word: ChartBarIcon,
  pdf: ChartPieIcon,
  excel: ChartBarIcon,
  markdown: CodeBracketIcon,
  text: DocumentIcon,
  image: PhotoIcon
}

const getFileIcon = (fileType: FileType) => fileIcons[fileType] || DocumentIcon

const fileTypeTexts: Record<FileType, string> = {
  word: 'Word',
  pdf: 'PDF',
  excel: 'Excel',
  markdown: 'Markdown',
  text: '文本',
  image: '图片'
}

const getFileTypeText = (fileType: FileType) => fileTypeTexts[fileType]

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// 格式化日期
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days} 天前`

  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

// 事件处理
const handleClick = (document: Document) => emit('click', document)

const handleToggleSelect = (documentId: string) => emit('toggleSelect', documentId)

const handleSelectAll = () => {
  if (allSelected.value) {
    emit('clearSelection')
  } else {
    emit('selectAll')
  }
}

const handleAction = (command: string, document: Document) => {
  switch (command) {
    case 'open':
      emit('open', document)
      break
    case 'edit':
      emit('edit', document)
      break
    case 'download':
      emit('download', document)
      break
    case 'rename':
      emit('rename', document)
      break
    case 'delete':
      emit('delete', document)
      break
  }
}
</script>

<style scoped>
.file-list {
  @apply bg-white rounded-lg border border-gray-200 overflow-hidden;
}

/* 表头 */
.file-list-header {
  @apply flex items-center bg-gray-50 border-b border-gray-200 px-4 py-3 text-sm font-medium text-gray-700;
}

.file-list-checkbox {
  @apply w-10 flex-shrink-0;
}

.file-list-name {
  @apply flex-1 flex items-center gap-2 min-w-0;
}

.file-list-type {
  @apply w-20 flex-shrink-0;
}

.file-list-size {
  @apply w-24 flex-shrink-0;
}

.file-list-date {
  @apply w-24 flex-shrink-0;
}

.file-list-actions {
  @apply w-16 flex-shrink-0 text-right;
}

/* 文件项 */
.file-list-body {
  @apply divide-y divide-gray-100;
}

.file-list-item {
  @apply flex items-center px-4 py-3 cursor-pointer transition-colors hover:bg-gray-50;
}

.file-list-item.selected {
  @apply bg-red-50;
}

.file-list-item.party-theme.selected {
  @apply bg-red-50;
}

.file-icon {
  @apply w-5 h-5 text-gray-400 flex-shrink-0;
}

.file-name-text {
  @apply truncate;
}

.action-btn {
  @apply p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors;
}

/* 空状态 */
.file-list-empty {
  @apply flex flex-col items-center justify-center py-16 text-gray-400;
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
