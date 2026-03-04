<template>
  <div class="admin-work-categories-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>作品分类管理</h3>
          <el-button type="primary" @click="handleCreate">创建分类</el-button>
        </div>
      </template>

      <el-table :data="categories" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="分类名称" width="200" />
        <el-table-column prop="icon" label="图标" width="100">
          <template #default="{ row }">
            <HeroIcon v-if="row.icon" :name="row.icon" class="icon-preview" />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="order" label="排序" width="100" />
        <el-table-column prop="work_count" label="作品数" width="100" />
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
              :disabled="row.work_count > 0"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑分类对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑分类' : '创建分类'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="图标" prop="icon">
          <IconSelector v-model="form.icon" />
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { ApiService } from '../../services/apiClient'
import type {
  AdminWorkCategoryListItem,
  CreateWorkCategoryRequest,
  UpdateWorkCategoryRequest,
} from '../../types'
import HeroIcon from '../../components/HeroIcon.vue'
import IconSelector from '../../components/admin/IconSelector.vue'
import { recommendIcon } from '../../utils/iconRecommendation'

// 分类列表
const categories = ref<AdminWorkCategoryListItem[]>([])
const loading = ref(false)

// 对话框
const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const isEdit = ref(false)
const submitting = ref(false)
const form = reactive<(CreateWorkCategoryRequest | UpdateWorkCategoryRequest) & { id?: string }>({
  name: '',
  icon: '',
  order: 0,
})

// 表单验证规则
const rules: FormRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 50, message: '分类名称长度为1-50个字符', trigger: 'blur' },
  ],
  order: [{ required: true, message: '请输入排序', trigger: 'blur' }],
}

/**
 * 加载分类列表
 */
async function loadCategories() {
  loading.value = true
  try {
    const response = await ApiService.getAdminWorkCategories()
    categories.value = response.categories
  } catch (error: any) {
    ElMessage.error(error.message || '加载分类列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 创建分类
 */
function handleCreate() {
  Object.assign(form, {
    name: '',
    icon: '',
    order: 0,
  })
  isEdit.value = false
  formRef.value?.clearValidate()
  dialogVisible.value = true
}

/**
 * 编辑分类
 */
function handleEdit(category: AdminWorkCategoryListItem) {
  Object.assign(form, {
    id: category.id,
    name: category.name,
    icon: category.icon || '',
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
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    // 如果没有选择图标，自动推荐一个
    if (!form.icon || form.icon.trim() === '') {
      form.icon = recommendIcon(form.name || '', '', 'photo')
    }

    submitting.value = true
    try {
      if (isEdit.value && form.id) {
        const { id, ...requestData } = form
        await ApiService.updateWorkCategory(id!, requestData)
        ElMessage.success('更新分类成功')
      } else {
        await ApiService.createWorkCategory(form as CreateWorkCategoryRequest)
        ElMessage.success('创建分类成功')
      }
      dialogVisible.value = false
      loadCategories()
    } catch (error: any) {
      ElMessage.error(error.message || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

/**
 * 删除分类
 */
async function handleDelete(category: AdminWorkCategoryListItem) {
  if (category.work_count > 0) {
    ElMessage.warning('该分类下还有作品，无法删除')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除分类 ${category.name} 吗？删除后无法恢复。`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value = true
    try {
      await ApiService.deleteWorkCategory(category.id)
      ElMessage.success('删除分类成功')
      loadCategories()
    } catch (error: any) {
      ElMessage.error(error.message || '删除分类失败')
    } finally {
      loading.value = false
    }
  } catch {
    // 用户取消
  }
}

/**
 * 上移分类
 */
async function handleMoveUp(category: AdminWorkCategoryListItem) {
  try {
    await ApiService.moveWorkCategoryUp(category.id)
    ElMessage.success('分类已上移')
    loadCategories()
  } catch (error: any) {
    ElMessage.error(error.message || '上移失败')
  }
}

/**
 * 下移分类
 */
async function handleMoveDown(category: AdminWorkCategoryListItem) {
  try {
    await ApiService.moveWorkCategoryDown(category.id)
    ElMessage.success('分类已下移')
    loadCategories()
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
.admin-work-categories-page {
  width: 100%;
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

.icon-preview {
  width: 24px;
  height: 24px;
}
</style>
