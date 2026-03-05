<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <!-- 搜索框 -->
    <div class="search-area">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索文件名..."
        clearable
      >
        <template #prefix>
          <MagnifyingGlassIcon class="w-4 h-4" />
        </template>
      </el-input>
    </div>

    <!-- 文件列表 -->
    <div class="file-list" v-loading="loading">
      <div
        v-for="file in filteredFiles"
        :key="file.id"
        class="file-item"
        :class="{ selected: isFileSelected(file.id) }"
        @click="toggleFile(file)"
      >
        <el-checkbox
          :model-value="isFileSelected(file.id)"
          @change="toggleFile(file)"
        />
        <DocumentIcon class="file-icon" />
        <div class="file-info">
          <div class="file-name">{{ file.title || file.name }}</div>
          <div class="file-meta">
            <span class="file-category">{{ getCategoryName(file.category_id) }}</span>
            <span v-if="file.size" class="file-size">{{ formatSize(file.size) }}</span>
          </div>
        </div>
      </div>

      <el-empty
        v-if="!loading && filteredFiles.length === 0"
        description="暂无文件"
      />
    </div>

    <!-- 底部操作栏 -->
    <template #footer>
      <div class="dialog-footer">
        <span class="selection-info">已选择 {{ selectedCount }} 个文件</span>
        <div class="footer-buttons">
          <el-button @click="handleClose">取消</el-button>
          <el-button
            type="primary"
            :disabled="selectedCount === 0"
            @click="handleConfirm"
          >
            确定
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { DocumentIcon, MagnifyingGlassIcon } from '@heroicons/vue/24/outline'
import { ElMessage } from 'element-plus'
import type { ChatAttachment } from '@/types'

/**
 * 文件选择对话框支持的源类型
 */
export type FileSource = 'knowledge' | 'party'

/**
 * 文件项接口（知识库和党建活动文件的通用接口）
 */
export interface FileItem {
  id: string
  title?: string
  name?: string
  category_id?: string
  size?: number
  content?: string
}

interface Props {
  modelValue: boolean
  source: FileSource
  files: FileItem[]
  categories?: Array<{ id: string; name: string }>
  loading?: boolean
  maxFiles?: number
}

const props = withDefaults(defineProps<Props>(), {
  files: () => [],
  categories: () => [],
  loading: false,
  maxFiles: 5
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'confirm': [files: ChatAttachment[]]
  'search': [keyword: string]
}>()

// 状态
const searchKeyword = ref('')
const selectedFiles = ref<Set<string>>(new Set())

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const title = computed(() => {
  return props.source === 'knowledge' ? '从知识库选择文件' : '从党建活动选择文件'
})

const selectedCount = computed(() => selectedFiles.value.size)

const filteredFiles = computed(() => {
  if (!searchKeyword.value) {
    return props.files
  }
  const keyword = searchKeyword.value.toLowerCase()
  return props.files.filter(file => {
    const name = (file.title || file.name || '').toLowerCase()
    return name.includes(keyword)
  })
})

// 方法
function isFileSelected(id: string): boolean {
  return selectedFiles.value.has(id)
}

function toggleFile(file: FileItem) {
  if (selectedFiles.value.has(file.id)) {
    selectedFiles.value.delete(file.id)
  } else {
    if (selectedFiles.value.size >= props.maxFiles) {
      ElMessage.warning(`最多只能选择 ${props.maxFiles} 个文件`)
      return
    }
    selectedFiles.value.add(file.id)
  }
}

function getCategoryName(categoryId?: string): string {
  if (!categoryId) return '未分类'
  const category = props.categories.find(c => c.id === categoryId)
  return category?.name || categoryId
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function handleClose() {
  visible.value = false
}

function handleConfirm() {
  const attachments: ChatAttachment[] = []
  selectedFiles.value.forEach(id => {
    const file = props.files.find(f => f.id === id)
    if (file) {
      attachments.push({
        id: file.id,
        name: file.title || file.name || '未命名',
        type: props.source,
        size: file.size || 0,
        status: 'ready'
      })
    }
  })
  emit('confirm', attachments)
  // 清空选择
  selectedFiles.value.clear()
  searchKeyword.value = ''
  visible.value = false
}

// 监听搜索关键词变化
watch(searchKeyword, (newKeyword) => {
  emit('search', newKeyword)
})

// 监听对话框打开，清空状态
watch(visible, (isOpen) => {
  if (!isOpen) {
    selectedFiles.value.clear()
    searchKeyword.value = ''
  }
})
</script>

<style scoped>
.search-area {
  margin-bottom: 16px;
}

.file-list {
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.file-item:hover {
  background-color: #f5f5f5;
}

.file-item.selected {
  background-color: #e8f4fd;
  border: 1px solid #409eff;
}

.file-icon {
  width: 20px;
  height: 20px;
  color: #666;
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta {
  display: flex;
  gap: 8px;
  margin-top: 4px;
  font-size: 12px;
  color: #999;
}

.file-category {
  padding: 2px 6px;
  background-color: #f0f0f0;
  border-radius: 4px;
}

.file-size {
  color: #999;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.selection-info {
  font-size: 14px;
  color: #666;
}

.footer-buttons {
  display: flex;
  gap: 8px;
}

/* 滚动条样式 */
.file-list::-webkit-scrollbar {
  width: 6px;
}

.file-list::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.file-list::-webkit-scrollbar-thumb {
  background: #d1d1d1;
  border-radius: 3px;
}

.file-list::-webkit-scrollbar-thumb:hover {
  background: #b1b1b1;
}
</style>
