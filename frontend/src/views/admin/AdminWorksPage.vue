<template>
  <div class="admin-works-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>作品展示管理</h3>
          <div class="header-buttons">
            <el-button type="primary" @click="handleUploadWork">上传作品</el-button>
          </div>
        </div>
      </template>

      <!-- 筛选器 -->
      <div class="filter-bar">
        <el-select
          v-model="filterCategoryId"
          placeholder="筛选分类"
          clearable
          @change="handleFilterChange"
          style="width: 150px"
        >
          <el-option label="全部分类" :value="undefined" />
          <el-option
            v-for="category in categories"
            :key="category.id"
            :label="category.name"
            :value="category.id"
          />
        </el-select>

        <el-select
          v-model="filterVisible"
          placeholder="筛选可见性"
          clearable
          @change="handleFilterChange"
          style="width: 150px"
        >
          <el-option label="全部" :value="undefined" />
          <el-option label="可见" :value="true" />
          <el-option label="隐藏" :value="false" />
        </el-select>
      </div>

      <!-- 作品列表表格 -->
      <el-table
        :data="works"
        v-loading="loading"
        style="width: 100%; margin-top: 16px"
      >
        <el-table-column prop="name" label="作品名称" width="200" />
        <el-table-column prop="description" label="描述" width="250" show-overflow-tooltip />
        <el-table-column prop="category_name" label="分类" width="120" />
        <el-table-column prop="icon" label="图标" width="80">
          <template #default="{ row }">
            <HeroIcon v-if="row.icon" :name="row.icon" class="icon-preview" />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="order" label="排序" width="80" />
        <el-table-column prop="visible" label="可见" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.visible" type="success">是</el-tag>
            <el-tag v-else type="info">否</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="400" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" @click="handleMoveUp(row)">上移</el-button>
            <el-button size="small" @click="handleMoveDown(row)">下移</el-button>
            <el-button size="small" @click="handleToggleVisibility(row)">
              {{ row.visible ? '隐藏' : '显示' }}
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadWorks"
        @current-change="loadWorks"
        style="margin-top: 16px; justify-content: flex-end"
      />
    </el-card>

    <!-- 上传作品对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传作品"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="uploadFormRef"
        :model="uploadForm"
        :rules="uploadRules"
        label-width="100px"
      >
        <el-form-item label="作品名称" prop="name">
          <el-input v-model="uploadForm.name" placeholder="请输入作品名称" />
        </el-form-item>
        <el-form-item label="作品描述" prop="description">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入作品描述"
          />
        </el-form-item>
        <el-form-item label="分类" prop="category_id">
          <el-select v-model="uploadForm.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="图标" prop="icon">
          <IconSelector v-model="uploadForm.icon" />
        </el-form-item>
        <el-form-item label="HTML文件" prop="html_file">
          <el-upload
            :auto-upload="false"
            :limit="1"
            accept=".html"
            :on-change="handleFileChange"
            :file-list="fileList"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">只支持.html文件，大小不超过10MB</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="排序" prop="order">
          <el-input-number v-model="uploadForm.order" :min="0" />
        </el-form-item>
        <el-form-item label="是否可见" prop="visible">
          <el-switch v-model="uploadForm.visible" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUploadSubmit" :loading="submitting">上传</el-button>
      </template>
    </el-dialog>

    <!-- 编辑作品对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑作品"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="100px"
      >
        <el-form-item label="作品名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入作品名称" />
        </el-form-item>
        <el-form-item label="作品描述" prop="description">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入作品描述"
          />
        </el-form-item>
        <el-form-item label="分类" prop="category_id">
          <el-select v-model="editForm.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="图标" prop="icon">
          <IconSelector v-model="editForm.icon" />
        </el-form-item>
        <el-form-item label="排序" prop="order">
          <el-input-number v-model="editForm.order" :min="0" />
        </el-form-item>
        <el-form-item label="是否可见" prop="visible">
          <el-switch v-model="editForm.visible" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEditSubmit" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules, type UploadFile } from 'element-plus'
import { ApiService } from '../../services/apiClient'
import type {
  AdminWorkListItem,
  UpdateWorkRequest,
  AdminWorkCategoryListItem,
} from '../../types'
import HeroIcon from '../../components/HeroIcon.vue'
import IconSelector from '../../components/admin/IconSelector.vue'
import { recommendIcon } from '../../utils/iconRecommendation'

// 作品列表数据
const works = ref<AdminWorkListItem[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

// 筛选器
const filterCategoryId = ref<string | undefined>(undefined)
const filterVisible = ref<boolean | undefined>(undefined)

// 分类列表
const categories = ref<AdminWorkCategoryListItem[]>([])
const categoryLoading = ref(false)

// 上传作品对话框
const uploadDialogVisible = ref(false)
const uploadFormRef = ref<FormInstance>()
const uploadForm = reactive({
  name: '',
  description: '',
  category_id: '',
  icon: '',
  order: 0,
  visible: true,
  html_file: null as File | null,
})
const fileList = ref<UploadFile[]>([])

// 编辑作品对话框
const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editForm = reactive<UpdateWorkRequest & { id?: string }>({
  name: '',
  description: '',
  category_id: '',
  icon: '',
  order: 0,
  visible: true,
})

const submitting = ref(false)

// 表单验证规则
const uploadRules: FormRules = {
  name: [
    { required: true, message: '请输入作品名称', trigger: 'blur' },
    { min: 1, max: 100, message: '作品名称长度为1-100个字符', trigger: 'blur' },
  ],
  description: [
    { required: true, message: '请输入作品描述', trigger: 'blur' },
    { min: 1, max: 200, message: '作品描述长度为1-200个字符', trigger: 'blur' },
  ],
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
  html_file: [
    {
      required: true,
      validator: (_rule, _value, callback) => {
        if (!uploadForm.html_file) {
          callback(new Error('请选择HTML文件'))
        } else {
          callback()
        }
      },
      trigger: 'change',
    },
  ],
}

const editRules: FormRules = {
  name: [
    { min: 1, max: 100, message: '作品名称长度为1-100个字符', trigger: 'blur' },
  ],
  description: [
    { min: 1, max: 200, message: '作品描述长度为1-200个字符', trigger: 'blur' },
  ],
}

/**
 * 加载作品列表
 */
async function loadWorks() {
  loading.value = true
  try {
    const response = await ApiService.getAdminWorks(
      currentPage.value,
      pageSize.value,
      filterCategoryId.value,
      filterVisible.value
    )
    works.value = response.works
    total.value = response.total
  } catch (error: any) {
    ElMessage.error(error.message || '加载作品列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 加载分类列表
 */
async function loadCategories() {
  categoryLoading.value = true
  try {
    const response = await ApiService.getAdminWorkCategories()
    categories.value = response.categories
  } catch (error: any) {
    ElMessage.error(error.message || '加载分类列表失败')
  } finally {
    categoryLoading.value = false
  }
}

/**
 * 筛选改变
 */
function handleFilterChange() {
  currentPage.value = 1
  loadWorks()
}

/**
 * 上传作品
 */
function handleUploadWork() {
  Object.assign(uploadForm, {
    name: '',
    description: '',
    category_id: '',
    icon: '',
    order: 0,
    visible: true,
    html_file: null,
  })
  fileList.value = []
  uploadFormRef.value?.clearValidate()
  uploadDialogVisible.value = true
}

/**
 * 文件选择变化
 */
function handleFileChange(file: UploadFile) {
  if (!file.raw) return

  // 文件大小验证（10MB）
  if (file.raw.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过10MB')
    fileList.value = []
    uploadForm.html_file = null
    return
  }

  // 文件类型验证
  if (!file.name.endsWith('.html')) {
    ElMessage.error('只支持.html文件')
    fileList.value = []
    uploadForm.html_file = null
    return
  }

  uploadForm.html_file = file.raw
  fileList.value = [file]
}

/**
 * 提交上传表单
 */
async function handleUploadSubmit() {
  if (!uploadFormRef.value) return

  await uploadFormRef.value.validate(async (valid) => {
    if (!valid) return

    // 如果没有选择图标，自动推荐一个
    if (!uploadForm.icon || uploadForm.icon.trim() === '') {
      uploadForm.icon = recommendIcon(uploadForm.name, uploadForm.description, 'photo')
    }

    submitting.value = true
    try {
      await ApiService.createWork(
        uploadForm.name,
        uploadForm.description,
        uploadForm.category_id,
        uploadForm.html_file!,
        uploadForm.icon,
        uploadForm.order,
        uploadForm.visible
      )
      ElMessage.success('上传作品成功')
      uploadDialogVisible.value = false
      loadWorks()
    } catch (error: any) {
      ElMessage.error(error.message || '上传作品失败')
    } finally {
      submitting.value = false
    }
  })
}

/**
 * 编辑作品
 */
function handleEdit(work: AdminWorkListItem) {
  Object.assign(editForm, {
    id: work.id,
    name: work.name,
    description: work.description || '',
    category_id: work.category_id,
    icon: work.icon || '',
    order: work.order,
    visible: work.visible,
  })
  editFormRef.value?.clearValidate()
  editDialogVisible.value = true
}

/**
 * 提交编辑表单
 */
async function handleEditSubmit() {
  if (!editFormRef.value) return

  await editFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const { id, ...requestData } = editForm
      await ApiService.updateWork(id!, requestData)
      ElMessage.success('更新作品成功')
      editDialogVisible.value = false
      loadWorks()
    } catch (error: any) {
      ElMessage.error(error.message || '更新作品失败')
    } finally {
      submitting.value = false
    }
  })
}

/**
 * 删除作品
 */
async function handleDelete(work: AdminWorkListItem) {
  try {
    await ElMessageBox.confirm(
      `确定要删除作品 ${work.name} 吗？删除后无法恢复。`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value = true
    try {
      await ApiService.deleteWork(work.id)
      ElMessage.success('删除作品成功')
      loadWorks()
    } catch (error: any) {
      ElMessage.error(error.message || '删除作品失败')
    } finally {
      loading.value = false
    }
  } catch {
    // 用户取消
  }
}

/**
 * 上移作品
 */
async function handleMoveUp(work: AdminWorkListItem) {
  try {
    await ApiService.moveWorkUp(work.id)
    ElMessage.success('作品已上移')
    loadWorks()
  } catch (error: any) {
    ElMessage.error(error.message || '上移失败')
  }
}

/**
 * 下移作品
 */
async function handleMoveDown(work: AdminWorkListItem) {
  try {
    await ApiService.moveWorkDown(work.id)
    ElMessage.success('作品已下移')
    loadWorks()
  } catch (error: any) {
    ElMessage.error(error.message || '下移失败')
  }
}

/**
 * 切换可见性
 */
async function handleToggleVisibility(work: AdminWorkListItem) {
  try {
    const response = await ApiService.toggleWorkVisibility(work.id)
    ElMessage.success(response.message)
    loadWorks()
  } catch (error: any) {
    ElMessage.error(error.message || '切换可见性失败')
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadCategories()
  loadWorks()
})
</script>

<style scoped>
.admin-works-page {
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

.header-buttons {
  display: flex;
  gap: 12px;
}

.filter-bar {
  display: flex;
  gap: 12px;
}

.icon-preview {
  width: 24px;
  height: 24px;
}
</style>
