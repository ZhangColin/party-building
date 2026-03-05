<template>
  <div class="tool-selector" :class="{ collapsed: isCollapsed }">
    <div v-if="!isCollapsed" class="tool-selector-content">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <span class="loading-text">加载工具列表...</span>
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="error-state">
        <span class="error-text">{{ error }}</span>
      </div>
      
      <!-- 工具列表 -->
      <div v-else class="tool-list">
        <!-- 所有工具都按分类组织 -->
        <div
          v-for="category in categories"
          :key="category.name"
          class="tool-category"
        >
          <div class="category-header">
            <div v-if="category.icon" class="category-icon">
              <component :is="getIconComponent(category.icon)" class="w-5 h-5" />
            </div>
            <span class="category-name">{{ category.name }}</span>
          </div>
          <div class="category-tools">
            <div
              v-for="tool in category.tools"
              :key="tool.tool_id"
              :class="['tool-card', { active: activeToolId === tool.tool_id }]"
              @click="handleToolClick(tool)"
            >
              <div class="tool-icon">
                <component 
                  v-if="tool.icon" 
                  :is="getIconComponent(tool.icon)" 
                  class="w-5 h-5" 
                />
                <CommandLineIcon v-else class="w-5 h-5" />
              </div>
              <div class="tool-info">
                <div class="tool-name">{{ tool.name }}</div>
                <div v-if="tool.description" class="tool-description">
                  {{ tool.description }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ApiService } from '../services/apiClient'
import type { CategoryGroup, ToolListItem } from '../types'
import {
  DocumentTextIcon,
  PhotoIcon,
  VideoCameraIcon,
  SparklesIcon,
  CommandLineIcon,
  BeakerIcon,
  CubeIcon,
  CodeBracketIcon,
  PaintBrushIcon,
  AcademicCapIcon,
  BriefcaseIcon,
  UserGroupIcon,
  ChartBarIcon,
  Cog6ToothIcon,
} from '@heroicons/vue/24/outline'

const props = defineProps<{
  collapsed?: boolean
  toolsetId?: string  // 工具集ID（可选），如果指定则只加载该工具集的工具
}>()

const emit = defineEmits<{
  'tool-change': [tool: ToolListItem]
  'collapse-change': [collapsed: boolean]
}>()

const categories = ref<CategoryGroup[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const activeToolId = ref<string | null>(null)
const isCollapsed = ref(props.collapsed ?? false)

// 图标名称到组件的映射
const iconMap: Record<string, any> = {
  'document-text': DocumentTextIcon,
  'photo': PhotoIcon,
  'video-camera': VideoCameraIcon,
  'sparkles': SparklesIcon,
  'command-line': CommandLineIcon,
  'beaker': BeakerIcon,
  'cube': CubeIcon,
  'code-bracket': CodeBracketIcon,
  'paint-brush': PaintBrushIcon,
  'academic-cap': AcademicCapIcon,
  'briefcase': BriefcaseIcon,
  'user-group': UserGroupIcon,
  'chart-bar': ChartBarIcon,
  'cog-6-tooth': Cog6ToothIcon,
}

function getIconComponent(iconName: string) {
  return iconMap[iconName] || CommandLineIcon
}

// 从 API 加载工具列表
async function loadTools() {
  loading.value = true
  error.value = null
  
  try {
    // 根据是否有 toolsetId 决定调用哪个 API
    const response = props.toolsetId
      ? await ApiService.getToolsetTools(props.toolsetId)
      : await ApiService.getTools()

    if (!response) {
      throw new Error('API returned undefined response')
    }

    if (!response.categories) {
      console.error('[AIToolSelector] Response missing categories:', response)
      throw new Error('API response missing categories field')
    }

    categories.value = response.categories
    
    // 如果有工具，默认选中第一个（包括占位工具）
    if (categories.value.length > 0 && categories.value[0]?.tools && categories.value[0].tools.length > 0) {
      const firstTool = categories.value[0].tools[0]
      if (firstTool) {
        activeToolId.value = firstTool.tool_id
        emit('tool-change', firstTool)
      }
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载工具列表失败'
    console.error('加载工具列表失败:', err)
  } finally {
    loading.value = false
  }
}

// 监听 toolsetId 变化，重新加载工具
watch(() => props.toolsetId, () => {
  loadTools()
})

function handleToolClick(tool: ToolListItem) {
  // 占位工具也触发 tool-change 事件，让父组件处理显示敬请期待页面
  activeToolId.value = tool.tool_id
  emit('tool-change', tool)
}

// 同步外部传入的 collapsed 状态
watch(() => props.collapsed, (newVal) => {
  if (newVal !== undefined) {
    isCollapsed.value = newVal
  }
})

onMounted(() => {
  loadTools()
})
</script>

<style scoped>
.tool-selector {
  height: 100%;
  position: relative;
  transition: width 0.3s;
}

.tool-selector.collapsed {
  width: 0;
  overflow: visible; /* 允许按钮显示在容器外 */
}

.tool-selector-content {
  padding: 20px 16px;
  height: 100%;
  overflow-y: auto;
}

.loading-state,
.error-state {
  @apply flex flex-col items-center justify-center py-8;
}

.loading-spinner {
  @apply w-8 h-8 border-4 border-gray-200 border-t-primary-500 rounded-full animate-spin mb-2;
}

.loading-text {
  @apply text-sm text-gray-500;
}

.error-text {
  @apply text-sm text-red-500;
}

.tool-list {
  @apply flex flex-col gap-4;
}

/* 工具分类 */
.tool-category {
  @apply mb-1;
}

.category-header {
  @apply flex items-center gap-2 px-2 py-2 mb-2;
}

.category-icon {
  @apply w-5 h-5 text-gray-500;
}

.category-name {
  @apply text-sm font-semibold;
  color: #C8102E; /* 党建主题红色 */
}

.category-tools {
  @apply flex flex-col gap-2 pl-7;
}

/* 工具卡片（缩小版） */
.tool-card {
  @apply flex items-center gap-2.5 px-3 py-2.5 rounded-lg cursor-pointer transition-all duration-200;
  background-color: theme('colors.white');
  border: 1px solid theme('colors.gray.200');
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.tool-card:hover {
  border-color: rgba(200, 16, 46, 0.3); /* 测红色边框 */
  background-color: rgba(200, 16, 46, 0.05); /* 浅红色背景 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.tool-card.active {
  border-color: #C8102E; /* 党建主题红色 */
  background-color: rgba(200, 16, 46, 0.1); /* 浅红色背景 */
  box-shadow: 0 2px 4px rgba(200, 16, 46, 0.15);
}

.tool-icon {
  @apply flex-shrink-0 w-8 h-8 rounded-md flex items-center justify-center;
  background-color: theme('colors.gray.100');
  color: theme('colors.gray.600');
  transition: all 0.2s;
}

.tool-card:hover .tool-icon {
  background-color: rgba(200, 16, 46, 0.1); /* 测红色背景 */
  color: #C8102E; /* 党建主题红色 */
}

.tool-card.active .tool-icon {
  background-color: #C8102E; /* 党建主题红色 */
  color: white;
}

.tool-info {
  @apply flex-1 min-w-0;
}

.tool-name {
  @apply text-sm font-medium text-gray-900;
}

.tool-description {
  @apply text-xs text-gray-500 mt-0.5 line-clamp-1;
}

.tool-card.active .tool-name {
  color: #C8102E; /* 党建主题红色 */
  font-weight: 600;
}

/* 平板端响应式（768px - 1023px） */
@media (min-width: 768px) and (max-width: 1023px) {
  .tool-selector-content {
    padding: 16px 12px;
  }
  
  .category-name {
    font-size: 13px;
  }
  
  .tool-card {
    padding: 10px 12px;
  }
  
  .tool-icon {
    width: 32px;
    height: 32px;
  }
  
  .tool-name {
    font-size: 13px;
  }
}

/* 移动端响应式 */
@media (max-width: 767px) {
  .tool-selector-content {
    padding: 16px 12px;
  }
}
</style>
