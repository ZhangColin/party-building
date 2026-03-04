<template>
  <div class="works-display-page">
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

    <!-- 作品卡片 -->
    <div v-else class="works-container">
      <!-- 按分类显示作品 -->
      <div v-for="category in categories" :key="category.id" class="category-section">
        <!-- 分类标题 -->
        <div class="category-header">
          <div class="category-icon-bg">
            <component :is="getIconComponent(category.icon)" class="w-4 h-4" />
          </div>
          <h2 class="category-name">{{ category.name }}</h2>
          <span class="category-count">{{ category.works.length }}</span>
        </div>

        <!-- 作品卡片列表 - 网格布局 -->
        <div class="works-grid">
          <div
            v-for="work in category.works"
            :key="work.id"
            class="work-card"
            @click="navigateToWork(work.id)"
          >
            <!-- 左侧：图标+标题 -->
            <div class="work-header">
              <div class="work-icon-wrapper">
                <component :is="getIconComponent(work.icon)" class="w-6 h-6" />
              </div>
              <h3 class="work-name">{{ work.name }}</h3>
            </div>

            <!-- 下方：描述 -->
            <p class="work-description">{{ work.description }}</p>
          </div>

          <!-- 添加作品卡片 -->
          <div
            class="work-card add-card"
            @click="handleAddWork(category.id)"
          >
            <div class="work-header">
              <div class="work-icon-wrapper add-icon">
                <PlusIcon class="w-6 h-6" />
              </div>
              <h3 class="work-name">添加教案学案</h3>
            </div>
            <p class="work-description">上传教案学案到此分类</p>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="categories.length === 0" class="empty-state">
        <PhotoIcon class="w-16 h-16 text-gray-300" />
        <h3 class="empty-title">暂无作品</h3>
        <p class="empty-description">目前还没有可展示的作品</p>
      </div>
    </div>

    <!-- 添加作品对话框 -->
    <AddHtmlContentDialog
      v-model="showAddDialog"
      title="添加教案学案"
      submit-text="添加"
      :max-file-size-m-b="10"
      @submit="handleSubmitAdd"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import {
  PhotoIcon,
  SparklesIcon,
  ChartBarIcon,
  StarIcon,
  CursorArrowRaysIcon,
  PresentationChartLineIcon,
  PlusIcon,
} from '@heroicons/vue/24/outline'
import { ElMessage } from 'element-plus'
import { useWorksStore } from '../stores/worksStore'
import { ApiService } from '../services/apiClient'
import AddHtmlContentDialog from '../components/AddHtmlContentDialog.vue'
import { recommendWorkIcon } from '../utils/iconRecommendation'

const router = useRouter()
const worksStore = useWorksStore()
const { categories, loading, error } = storeToRefs(worksStore)

// 图标映射
const iconComponents: Record<string, any> = {
  'photo': PhotoIcon,
  'sparkles': SparklesIcon,
  'chart-bar': ChartBarIcon,
  'star': StarIcon,
  'cursor-arrow-rays': CursorArrowRaysIcon,
  'presentation-chart-line': PresentationChartLineIcon,
}

/**
 * 获取图标组件
 */
function getIconComponent(iconName?: string) {
  if (!iconName) return PhotoIcon
  return iconComponents[iconName] || PhotoIcon
}

/**
 * 加载作品分类列表
 */
const loadCategories = async () => {
  await worksStore.fetchCategories()
}

/**
 * 导航到作品详情页
 */
const navigateToWork = (workId: string) => {
  router.push(`/works/${workId}`)
}

// 添加作品对话框
const showAddDialog = ref(false)
const currentCategoryId = ref<string>('')

/**
 * 处理添加作品
 */
const handleAddWork = (categoryId: string) => {
  currentCategoryId.value = categoryId
  showAddDialog.value = true
}

/**
 * 计算当前分类的最大 order
 */
const getMaxOrderInCategory = (categoryId: string): number => {
  const category = categories.value.find(cat => cat.id === categoryId)
  if (!category || category.works.length === 0) {
    return 0
  }
  return Math.max(...category.works.map(work => work.order || 0))
}

/**
 * 处理提交添加作品
 */
const handleSubmitAdd = async (data: { name: string; description: string; htmlFile: File }) => {
  try {
    // 自动推荐图标
    const icon = recommendWorkIcon(data.name, data.description)
    
    // 计算排序值（当前分类最大 order + 1）
    const order = getMaxOrderInCategory(currentCategoryId.value) + 1
    
    // 调用 API 创建作品
    await ApiService.createWork(
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
    console.error('添加作品失败:', error)
    ElMessage.error(error instanceof Error ? error.message : '添加失败，请稍后重试')
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.works-display-page {
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
  @apply flex flex-col items-center justify-center h-full gap-4 px-4;
}

.error-icon {
  @apply text-red-500;
}

.error-title {
  @apply text-xl font-semibold text-gray-900;
}

.error-message {
  @apply text-gray-600 text-center max-w-md;
}

.retry-button {
  @apply px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors;
}

/* 作品容器 */
.works-container {
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

/* 作品网格 */
.works-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4;
}

/* 作品卡片 */
.work-card {
  @apply bg-white rounded-xl p-5 cursor-pointer transition-all duration-200 border border-gray-100;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
}

.work-card:hover {
  @apply border-blue-200 shadow-md;
  transform: translateY(-2px);
}

.work-header {
  @apply flex items-center gap-3 mb-3;
}

.work-icon-wrapper {
  @apply w-10 h-10 rounded-lg bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center text-gray-600 flex-shrink-0;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.work-name {
  @apply text-base font-semibold text-gray-900 leading-tight;
  letter-spacing: -0.3px;
}

.work-description {
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

.add-card .work-icon-wrapper.add-icon {
  @apply bg-gradient-to-br from-blue-50 to-blue-100 text-blue-600;
}

.add-card .work-name {
  @apply text-blue-600;
}

.add-card .work-description {
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
  .works-container {
    @apply p-6;
  }

  .works-grid {
    @apply grid-cols-2;
  }
}

/* 响应式 - 移动端 */
@media (max-width: 767px) {
  .works-container {
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

  .works-grid {
    @apply grid-cols-1 gap-3;
  }

  .work-card {
    @apply p-4;
  }
}
</style>
