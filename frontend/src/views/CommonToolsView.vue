<template>
  <div class="common-tools-view">
    <!-- 加载中 -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p class="loading-text">加载中...</p>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">
        <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <h2 class="error-title">加载失败</h2>
      <p class="error-message">{{ error }}</p>
      <button class="retry-button" @click="loadCategories">重试</button>
    </div>

    <!-- 工具卡片 -->
    <div v-else class="tools-container">
      <!-- 按分类显示工具 -->
      <div v-for="category in categories" :key="category.id" class="category-section">
        <!-- 分类标题 - 美化设计 -->
        <div class="category-header">
          <div class="category-icon-bg">
            <component :is="getIconComponent(category.icon)" class="w-4 h-4" />
          </div>
          <h2 class="category-name">{{ category.name }}</h2>
          <span class="category-count">{{ category.tools.length }}</span>
        </div>

        <!-- 工具卡片列表 - 网格布局 -->
        <div class="tools-grid">
          <div
            v-for="tool in category.tools"
            :key="tool.id"
            class="tool-card"
            @click="navigateToTool(tool)"
          >
            <!-- 左侧：图标+标题 -->
            <div class="tool-header">
              <div class="tool-icon-wrapper">
                <component :is="getIconComponent(tool.icon)" class="w-6 h-6" />
              </div>
              <h3 class="tool-name">{{ tool.name }}</h3>
            </div>

            <!-- 下方：描述 -->
            <p class="tool-description">{{ tool.description }}</p>
          </div>

          <!-- 添加工具卡片 -->
          <div
            class="tool-card add-card"
            @click="handleAddTool(category.id)"
          >
            <div class="tool-header">
              <div class="tool-icon-wrapper add-icon">
                <PlusIcon class="w-6 h-6" />
              </div>
              <h3 class="tool-name">添加工具</h3>
            </div>
            <p class="tool-description">上传 HTML 工具到此分类</p>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="categories.length === 0" class="empty-state">
        <WrenchIcon class="w-16 h-16 text-gray-300" />
        <h3 class="empty-title">暂无工具</h3>
        <p class="empty-description">目前还没有可用的工具</p>
      </div>
    </div>

    <!-- 添加工具对话框 -->
    <AddHtmlContentDialog
      v-model="showAddDialog"
      title="添加工具"
      submit-text="添加"
      :max-file-size-m-b="5"
      @submit="handleSubmitAdd"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  WrenchIcon,
  DocumentTextIcon,
  ChartBarIcon,
  CodeBracketIcon,
  TableCellsIcon,
  PlusIcon,
} from '@heroicons/vue/24/outline'
import { ElMessage } from 'element-plus'
import { ApiService } from '../services/apiClient'
import type { ToolCategoryGroup, CommonToolListItem } from '../types'
import AddHtmlContentDialog from '../components/AddHtmlContentDialog.vue'
import { recommendToolIcon } from '../utils/iconRecommendation'

const router = useRouter()

// 图标映射
const iconComponents: Record<string, any> = {
  'document-text': DocumentTextIcon,
  'chart-bar': ChartBarIcon,
  'code-bracket': CodeBracketIcon,
  'table-cells': TableCellsIcon,
  'wrench': WrenchIcon,
}

/**
 * 获取图标组件
 */
function getIconComponent(iconName?: string) {
  if (!iconName) return WrenchIcon
  return iconComponents[iconName] || WrenchIcon
}

// 状态
const loading = ref(true)
const error = ref<string | null>(null)
const categories = ref<ToolCategoryGroup[]>([])

/**
 * 加载工具分类列表
 */
const loadCategories = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await ApiService.getCommonToolCategories()
    categories.value = response.categories
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载失败，请稍后重试'
    console.error('加载工具分类失败:', err)
  } finally {
    loading.value = false
  }
}

/**
 * 导航到工具页面
 */
const navigateToTool = (tool: CommonToolListItem) => {
  if (tool.type === 'built_in') {
    // 内置工具：导航到对应的路由
    router.push(`/common-tools/${tool.id}`)
  } else if (tool.type === 'html') {
    // HTML工具：导航到HTML工具运行器
    router.push(`/common-tools/html/${tool.id}`)
  }
}

// 添加工具对话框
const showAddDialog = ref(false)
const currentCategoryId = ref<string>('')

/**
 * 处理添加工具
 */
const handleAddTool = (categoryId: string) => {
  currentCategoryId.value = categoryId
  showAddDialog.value = true
}

/**
 * 计算当前分类的最大 order
 */
const getMaxOrderInCategory = (categoryId: string): number => {
  const category = categories.value.find(cat => cat.id === categoryId)
  if (!category || category.tools.length === 0) {
    return 0
  }
  return Math.max(...category.tools.map(tool => tool.order || 0))
}

/**
 * 处理提交添加工具
 */
const handleSubmitAdd = async (data: { name: string; description: string; htmlFile: File }) => {
  try {
    // 自动推荐图标
    const icon = recommendToolIcon(data.name, data.description)
    
    // 计算排序值（当前分类最大 order + 1）
    const order = getMaxOrderInCategory(currentCategoryId.value) + 1
    
    // 调用 API 创建工具
    await ApiService.createHtmlTool(
      data.name,
      data.description,
      currentCategoryId.value,
      data.htmlFile,
      icon,
      order,
      true // 默认可见
    )
    
    ElMessage.success('添加成功')
    
    // 关闭对话框
    showAddDialog.value = false
    
    // 重新加载数据
    await loadCategories()
  } catch (error) {
    console.error('添加工具失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '添加失败，请稍后重试')
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.common-tools-view {
  @apply h-full w-full overflow-y-auto;
  background-color: theme('colors.gray.50');
}

/* 加载中 */
.loading-container {
  @apply flex flex-col items-center justify-center h-full gap-4;
}

.spinner {
  @apply w-12 h-12 border-4 border-gray-200 border-t-blue-500 rounded-full;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  @apply text-gray-600 text-base;
}

/* 错误提示 */
.error-container {
  @apply flex flex-col items-center justify-center h-full gap-4 px-6;
}

.error-icon {
  @apply text-red-500;
}

.error-title {
  @apply text-xl font-semibold text-gray-900;
}

.error-message {
  @apply text-gray-600 text-center;
}

.retry-button {
  @apply px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors;
}

/* 工具容器 */
.tools-container {
  @apply p-6 md:p-8 max-w-7xl mx-auto;
}

/* 分类区域 */
.category-section {
  @apply mb-12;
}

.category-section:last-child {
  @apply mb-0;
}

/* 分类标题 */
.category-header {
  @apply flex items-center gap-3 mb-6;
}

.category-icon-bg {
  @apply w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white shadow-sm;
}

.category-name {
  @apply text-xl font-semibold text-gray-900;
  letter-spacing: -0.5px;
}

.category-count {
  @apply text-sm text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full;
}

/* 工具网格 */
.tools-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4;
}

/* 工具卡片 */
.tool-card {
  @apply bg-white rounded-xl p-5 cursor-pointer transition-all duration-200 border border-gray-100;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
}

.tool-card:hover {
  @apply border-blue-200 shadow-md;
  transform: translateY(-2px);
}

/* 卡片头部：图标+标题横向排列 */
.tool-header {
  @apply flex items-center gap-3 mb-3;
}

.tool-icon-wrapper {
  @apply w-10 h-10 rounded-lg bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center text-gray-600 flex-shrink-0;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.tool-name {
  @apply text-base font-semibold text-gray-900 leading-tight;
  letter-spacing: -0.3px;
}

.tool-description {
  @apply text-sm text-gray-600 leading-relaxed line-clamp-2;
}

/* 添加卡片样式 */
.add-card {
  @apply border-2 border-dashed border-gray-300;
  background-color: rgba(249, 250, 251, 0.5);
}

.add-card:hover {
  @apply border-blue-400 bg-blue-50;
}

.add-card .tool-icon-wrapper.add-icon {
  @apply bg-gradient-to-br from-blue-50 to-blue-100 text-blue-600;
}

.add-card .tool-name {
  @apply text-blue-600;
}

.add-card .tool-description {
  @apply text-gray-500;
}

/* 空状态 */
.empty-state {
  @apply flex flex-col items-center justify-center py-16 gap-4;
}

.empty-title {
  @apply text-xl font-semibold text-gray-900;
}

.empty-description {
  @apply text-gray-600 text-center;
}

/* 响应式 - 平板 */
@media (min-width: 768px) and (max-width: 1023px) {
  .tools-container {
    @apply p-6;
  }

  .tools-grid {
    @apply grid-cols-2;
  }
}

/* 响应式 - 移动端 */
@media (max-width: 767px) {
  .tools-container {
    @apply p-4;
  }

  .category-section {
    @apply mb-8;
  }

  .category-header {
    @apply mb-4;
  }

  .category-name {
    @apply text-lg;
  }

  .tools-grid {
    @apply grid-cols-1 gap-3;
  }

  .tool-card {
    @apply p-4;
  }
}
</style>
