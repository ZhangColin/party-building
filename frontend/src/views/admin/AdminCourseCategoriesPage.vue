<template>
  <div class="admin-course-categories-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>课程目录管理</h3>
          <el-button type="primary" @click="handleCreate">创建目录</el-button>
        </div>
      </template>

      <el-table 
        :data="categoryTreeTableData" 
        v-loading="loading" 
        style="width: 100%"
        row-key="id"
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        default-expand-all
      >
        <el-table-column prop="name" label="目录名称" width="300" />
        <el-table-column prop="order" label="排序" width="100" />
        <el-table-column prop="document_count" label="文档数" width="100" />
        <el-table-column prop="children_count" label="子目录数" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" @click="handleMoveUp(row)">上移</el-button>
            <el-button size="small" @click="handleMoveDown(row)">下移</el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row)"
              :disabled="row.document_count > 0 || row.children_count > 0"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑目录对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑目录' : '创建目录'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="目录名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入目录名称" />
        </el-form-item>
        <el-form-item label="父目录" prop="parent_id">
          <el-tree-select
            v-model="form.parent_id"
            :data="categoryTreeData"
            placeholder="请选择父目录（可选，留空则为根目录）"
            clearable
            check-strictly
            :render-after-expand="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="排序" prop="order">
          <el-input-number v-model="form.order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { ApiService } from '../../services/apiClient'
import type {
  AdminCourseCategoryListItem,
  CreateCourseCategoryRequest,
  UpdateCourseCategoryRequest,
} from '../../types'

// 目录列表
const categories = ref<AdminCourseCategoryListItem[]>([])
const loading = ref(false)

// 对话框
const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const isEdit = ref(false)
const submitting = ref(false)
const form = reactive<(CreateCourseCategoryRequest | UpdateCourseCategoryRequest) & { id?: string }>({
  name: '',
  parent_id: null,
  order: 0,
})

// 可选的父目录列表（编辑时排除自己）
const availableParentCategories = computed(() => {
  if (isEdit.value && form.id) {
    return categories.value.filter(cat => cat.id !== form.id)
  }
  return categories.value
})

// 构建树形数据（用于树形选择器）
const categoryTreeData = computed(() => {
  const availableCategories = availableParentCategories.value
  
  // 构建树形结构的递归函数
  const buildTree = (parentId: string | null): any[] => {
    return availableCategories
      .filter(cat => cat.parent_id === parentId)
      .map(cat => ({
        value: cat.id,
        label: cat.name,
        children: buildTree(cat.id),
      }))
  }
  
  return buildTree(null)
})

// 构建树形表格数据
const categoryTreeTableData = computed(() => {
  // 递归构建树形结构
  const buildTree = (parentId: string | null): AdminCourseCategoryListItem[] => {
    return categories.value
      .filter(cat => cat.parent_id === parentId)
      .sort((a, b) => a.order - b.order)
      .map(cat => ({
        ...cat,
        children: buildTree(cat.id),
      }))
  }
  
  return buildTree(null)
})

// 表单验证规则
const rules: FormRules = {
  name: [
    { required: true, message: '请输入目录名称', trigger: 'blur' },
    { min: 1, max: 100, message: '目录名称长度为1-100个字符', trigger: 'blur' },
  ],
  order: [{ required: true, message: '请输入排序', trigger: 'blur' }],
}

/**
 * 加载目录列表
 */
async function loadCategories() {
  loading.value = true
  try {
    const response = await ApiService.getAdminCourseCategories()
    categories.value = response.categories
  } catch (error: any) {
    ElMessage.error(error.message || '加载目录列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 创建目录
 */
function handleCreate() {
  Object.assign(form, {
    name: '',
    parent_id: null,
    order: 0,
  })
  isEdit.value = false
  formRef.value?.clearValidate()
  dialogVisible.value = true
}

/**
 * 编辑目录
 */
function handleEdit(category: AdminCourseCategoryListItem) {
  Object.assign(form, {
    id: category.id,
    name: category.name,
    parent_id: category.parent_id || null,
    order: category.order,
  })
  isEdit.value = true
  formRef.value?.clearValidate()
  dialogVisible.value = true
}

/**
 * 提交表单
 */
async function handleSubmit() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    if (isEdit.value && form.id) {
      // 更新目录
      const request: UpdateCourseCategoryRequest = {
        name: form.name,
        parent_id: form.parent_id,
        order: form.order,
      }
      await ApiService.updateCourseCategory(form.id, request)
      ElMessage.success('目录更新成功')
    } else {
      // 创建目录
      const request: CreateCourseCategoryRequest = {
        name: form.name!,
        parent_id: form.parent_id,
        order: form.order,
      }
      await ApiService.createCourseCategory(request)
      ElMessage.success('目录创建成功')
    }

    dialogVisible.value = false
    await loadCategories()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

/**
 * 删除目录
 */
async function handleDelete(category: AdminCourseCategoryListItem) {
  try {
    await ElMessageBox.confirm(
      `确定要删除目录"${category.name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
  } catch {
    return
  }

  try {
    await ApiService.deleteCourseCategory(category.id)
    ElMessage.success('目录删除成功')
    await loadCategories()
  } catch (error: any) {
    ElMessage.error(error.message || '删除失败')
  }
}

/**
 * 上移目录
 */
async function handleMoveUp(category: AdminCourseCategoryListItem) {
  try {
    await ApiService.moveCourseCategoryUp(category.id)
    ElMessage.success('目录已上移')
    await loadCategories()
  } catch (error: any) {
    ElMessage.error(error.message || '上移失败')
  }
}

/**
 * 下移目录
 */
async function handleMoveDown(category: AdminCourseCategoryListItem) {
  try {
    await ApiService.moveCourseCategoryDown(category.id)
    ElMessage.success('目录已下移')
    await loadCategories()
  } catch (error: any) {
    ElMessage.error(error.message || '下移失败')
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.admin-course-categories-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}
</style>

