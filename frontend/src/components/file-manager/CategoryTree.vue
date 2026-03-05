# -*- coding: utf-8 -*-
<template>
  <div class="category-tree" :class="{ 'party-theme': isPartyTheme }">
    <!-- 树形头部 -->
    <div class="tree-header">
      <h3 class="tree-title">{{ title }}</h3>
      <div class="tree-actions">
        <button class="action-btn" @click="handleExpandAll" title="展开所有">
          <ChevronDownIcon class="w-4 h-4" />
        </button>
        <button class="action-btn" @click="handleCollapseAll" title="折叠所有">
          <ChevronRightIcon class="w-4 h-4" />
        </button>
        <button class="action-btn" @click="handleAddRoot" title="添加根目录">
          <PlusIcon class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- 搜索框 -->
    <div v-if="searchable" class="tree-search">
      <el-input
        v-model="searchQuery"
        placeholder="搜索目录..."
        :prefix-icon="Search"
        clearable
        size="small"
      />
    </div>

    <!-- 树形结构 -->
    <el-tree-v2
      ref="treeRef"
      :data="filteredCategories"
      :props="treeProps"
      :item-size="32"
      :height="treeHeight"
      :expand-on-click-node="false"
      :highlight-current="true"
      :current-node-key="currentCategoryId"
      :default-expanded-keys="expandedKeys"
      :filter-method="filterMethod"
      @node-click="handleNodeClick"
      @node-contextmenu="handleContextMenu"
    >
      <template #default="{ node, data }">
        <div class="tree-node group" :class="{ 'is-current': data.id === currentCategoryId }">
          <!-- 目录图标 -->
          <component
            :is="getNodeIcon(node, data)"
            class="node-icon"
          />

          <!-- 目录名称 -->
          <span class="node-label">{{ node.label }}</span>

          <!-- 操作按钮 -->
          <div class="node-actions" @click.stop>
            <el-dropdown trigger="click" @command="(cmd: string) => handleAction(cmd, data)">
              <button class="node-action-btn">
                <EllipsisVerticalIcon class="w-4 h-4" />
              </button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="add">
                    <PlusIcon class="w-4 h-4" />
                    <span>添加子目录</span>
                  </el-dropdown-item>
                  <el-dropdown-item command="rename">
                    <PencilIcon class="w-4 h-4" />
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
    </el-tree-v2>

    <!-- 空状态 -->
    <div v-if="categories.length === 0" class="tree-empty">
      <FolderIcon class="w-12 h-12 text-gray-300 mx-auto mb-2" />
      <p class="text-gray-500 text-sm">暂无目录</p>
      <button class="add-first-btn" @click="handleAddRoot">
        <PlusIcon class="w-4 h-4" />
        <span>创建第一个目录</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import {
  ChevronDownIcon,
  ChevronRightIcon,
  PlusIcon,
  FolderIcon,
  FolderOpenIcon,
  EllipsisVerticalIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'
import type { Category } from '@/types/file-manager'

interface Props {
  categories: Category[]
  currentCategoryId?: string | null
  title?: string
  searchable?: boolean
  isPartyTheme?: boolean
  height?: number
}

interface Emits {
  (e: 'select', category: Category): void
  (e: 'add', parentId: string | null): void
  (e: 'rename', category: Category): void
  (e: 'delete', category: Category): void
}

const props = withDefaults(defineProps<Props>(), {
  currentCategoryId: null,
  title: '目录',
  searchable: true,
  isPartyTheme: false,
  height: 400
})

const emit = defineEmits<Emits>()

const searchQuery = ref('')
const expandedKeys = ref<string[]>([])

// 树形组件配置
const treeProps = {
  value: 'id',
  label: 'name',
  children: 'children'
}

// 树高度
const treeHeight = computed(() => {
  const headerHeight = 50
  const searchHeight = props.searchable ? 40 : 0
  return props.height - headerHeight - searchHeight
})

// 过滤后的目录
const filteredCategories = computed(() => {
  if (!searchQuery.value.trim()) {
    return props.categories
  }
  return filterCategories(props.categories, searchQuery.value.toLowerCase())
})

// 过滤目录（递归）
const filterCategories = (categories: Category[], query: string): Category[] => {
  const result: Category[] = []
  for (const category of categories) {
    const matchesName = category.name.toLowerCase().includes(query)
    const filteredChildren = category.children?.length
      ? filterCategories(category.children, query)
      : []

    if (matchesName || filteredChildren.length > 0) {
      result.push({
        ...category,
        children: filteredChildren.length > 0 ? filteredChildren : category.children
      })
    }
  }
  return result
}

// 树节点过滤方法
const filterMethod = (query: string, node: any) => {
  const category = node.data as Category
  return category.name.toLowerCase().includes(query.toLowerCase())
}

// 获取节点图标
const getNodeIcon = (node: any, _data: Category) => {
  return node.expanded ? FolderOpenIcon : FolderIcon
}

// 事件处理
const handleNodeClick = (data: Category) => {
  emit('select', data)
}

const handleAction = (command: string, data: Category) => {
  switch (command) {
    case 'add':
      emit('add', data.id)
      break
    case 'rename':
      emit('rename', data)
      break
    case 'delete':
      emit('delete', data)
      break
  }
}

const handleContextMenu = (event: MouseEvent, _data: any) => {
  event.preventDefault()
  // 可以在这里实现自定义右键菜单
}

const handleExpandAll = () => {
  const allKeys = getAllCategoryKeys(props.categories)
  expandedKeys.value = allKeys
}

const handleCollapseAll = () => {
  expandedKeys.value = []
}

const handleAddRoot = () => {
  emit('add', null)
}

// 获取所有目录的 ID
const getAllCategoryKeys = (categories: Category[]): string[] => {
  const keys: string[] = []
  const traverse = (cats: Category[]) => {
    for (const cat of cats) {
      keys.push(cat.id)
      if (cat.children?.length) {
        traverse(cat.children)
      }
    }
  }
  traverse(categories)
  return keys
}

// 监听当前目录变化，自动展开
watch(() => props.currentCategoryId, (newId) => {
  if (newId && !expandedKeys.value.includes(newId)) {
    // 获取路径并展开
    const path = getCategoryPath(props.categories, newId)
    expandedKeys.value = [...new Set([...expandedKeys.value, ...path])]
  }
})

// 获取目录路径（用于展开）
const getCategoryPath = (categories: Category[], targetId: string, path: string[] = []): string[] => {
  for (const category of categories) {
    const currentPath = [...path, category.id]
    if (category.id === targetId) {
      return currentPath.slice(0, -1) // 不包含目标节点本身
    }
    if (category.children?.length) {
      const result = getCategoryPath(category.children, targetId, currentPath)
      if (result.length > 0 || category.children.some(c => c.id === targetId)) {
        return result
      }
    }
  }
  return []
}

// 暴露方法
defineExpose({
  expandAll: handleExpandAll,
  collapseAll: handleCollapseAll,
  expandNode: (nodeId: string) => {
    if (!expandedKeys.value.includes(nodeId)) {
      expandedKeys.value = [...expandedKeys.value, nodeId]
    }
  }
})
</script>

<style scoped>
.category-tree {
  @apply flex flex-col bg-white rounded-lg border border-gray-200 overflow-hidden;
}

/* 树头部 */
.tree-header {
  @apply flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gray-50;
}

.tree-title {
  @apply text-sm font-semibold text-gray-700;
}

.tree-actions {
  @apply flex items-center gap-1;
}

.action-btn {
  @apply p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-200 rounded transition-colors;
}

/* 搜索框 */
.tree-search {
  @apply px-3 py-2 border-b border-gray-100;
}

/* 树节点 */
.tree-node {
  @apply flex items-center gap-2 w-full h-full;
}

.tree-node.is-current {
  @apply bg-red-50;
}

.tree-node.party-theme.is-current {
  @apply bg-red-50;
}

.node-icon {
  @apply w-4 h-4 text-gray-400 flex-shrink-0;
}

.tree-node.is-current .node-icon {
  @apply text-red-600;
}

.node-label {
  @apply flex-1 text-sm text-gray-700 truncate;
}

.node-actions {
  @apply opacity-100 transition-opacity;
}

.node-action-btn {
  @apply p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded;
}

/* 空状态 */
.tree-empty {
  @apply flex flex-col items-center justify-center py-12 text-gray-400;
}

.add-first-btn {
  @apply flex items-center gap-1 mt-4 px-4 py-2 text-sm font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors;
}

/* 下拉菜单样式 */
:deep(.el-dropdown-menu__item) {
  @apply flex items-center gap-2;
}

:deep(.danger-item) {
  @apply text-red-600;
}

:deep(.danger-item:hover) {
  @apply bg-red-50;
}

/* Element Plus Tree V2 样式覆盖 */
:deep(.el-tree-v2__wrapper) {
  @apply bg-transparent;
}

:deep(.el-tree-v2__item) {
  @apply hover:bg-gray-50;
}

:deep(.el-tree-v2__item.is-current) {
  @apply bg-red-50;
}
</style>
