<template>
  <div class="admin-tools-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>常用工具管理</h3>
          <div class="header-buttons">
            <el-button type="primary" @click="handleCreateBuiltInTool">创建内置工具</el-button>
            <el-button type="primary" @click="handleUploadHtmlTool">上传HTML工具</el-button>
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
          v-model="filterType"
          placeholder="筛选类型"
          clearable
          @change="handleFilterChange"
          style="width: 150px"
        >
          <el-option label="全部类型" :value="undefined" />
          <el-option label="内置工具" value="built_in" />
          <el-option label="HTML工具" value="html" />
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

      <!-- 工具列表表格 -->
      <el-table
        :data="tools"
        v-loading="loading"
        style="width: 100%; margin-top: 16px"
      >
        <el-table-column prop="name" label="工具名称" width="200" />
        <el-table-column prop="description" label="描述" width="250" show-overflow-tooltip />
        <el-table-column prop="category_name" label="分类" width="120" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.type === 'built_in'" type="success">内置</el-tag>
            <el-tag v-else>HTML</el-tag>
          </template>
        </el-table-column>
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
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
        style="margin-top: 16px; justify-content: flex-end"
      />
    </el-card>

    <!-- 创建内置工具对话框 -->
    <el-dialog
      v-model="createBuiltInDialogVisible"
      title="创建内置工具"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="createBuiltInFormRef"
        :model="createBuiltInForm"
        :rules="createBuiltInRules"
        label-width="100px"
      >
        <el-form-item label="工具名称" prop="name">
          <el-input v-model="createBuiltInForm.name" placeholder="请输入工具名称" />
        </el-form-item>
        <el-form-item label="工具描述" prop="description">
          <el-input
            v-model="createBuiltInForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入工具描述"
          />
        </el-form-item>
        <el-form-item label="所属分类" prop="category_id">
          <el-select v-model="createBuiltInForm.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="图标" prop="icon">
          <IconSelector v-model="createBuiltInForm.icon" />
        </el-form-item>
        <el-form-item label="排序" prop="order">
          <el-input-number v-model="createBuiltInForm.order" :min="0" />
        </el-form-item>
        <el-form-item label="可见">
          <el-checkbox v-model="createBuiltInForm.visible">设置为可见</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createBuiltInDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateBuiltInSubmit" :loading="submitting">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 上传HTML工具对话框 -->
    <el-dialog
      v-model="uploadHtmlDialogVisible"
      title="上传HTML工具"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="uploadHtmlFormRef"
        :model="uploadHtmlForm"
        :rules="uploadHtmlRules"
        label-width="100px"
      >
        <el-form-item label="工具名称" prop="name">
          <el-input v-model="uploadHtmlForm.name" placeholder="请输入工具名称" />
        </el-form-item>
        <el-form-item label="工具描述" prop="description">
          <el-input
            v-model="uploadHtmlForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入工具描述"
          />
        </el-form-item>
        <el-form-item label="所属分类" prop="category_id">
          <el-select v-model="uploadHtmlForm.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="HTML文件" prop="html_file">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept=".html"
          >
            <el-button>选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">只能上传.html文件，且不超过5MB</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="图标" prop="icon">
          <IconSelector v-model="uploadHtmlForm.icon" />
        </el-form-item>
        <el-form-item label="排序" prop="order">
          <el-input-number v-model="uploadHtmlForm.order" :min="0" />
        </el-form-item>
        <el-form-item label="可见">
          <el-checkbox v-model="uploadHtmlForm.visible">设置为可见</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadHtmlDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUploadHtmlSubmit" :loading="submitting">
          上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑工具对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑工具"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="100px"
      >
        <el-form-item label="工具名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入工具名称" />
        </el-form-item>
        <el-form-item label="工具描述" prop="description">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入工具描述"
          />
        </el-form-item>
        <el-form-item label="所属分类" prop="category_id">
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
        <el-form-item label="可见">
          <el-checkbox v-model="editForm.visible">设置为可见</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEditSubmit" :loading="submitting">
          保存
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
  AdminCommonToolListItem,
  CreateBuiltInToolRequest,
  UpdateToolRequest,
  AdminToolCategoryListItem,
} from '../../types'
import HeroIcon from '../../components/HeroIcon.vue'
import IconSelector from '../../components/admin/IconSelector.vue'
import { recommendIcon } from '../../utils/iconRecommendation'

// 工具列表数据
const tools = ref<AdminCommonToolListItem[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

// 筛选器
const filterCategoryId = ref<string | undefined>(undefined)
const filterType = ref<string | undefined>(undefined)
const filterVisible = ref<boolean | undefined>(undefined)

// 分类列表
const categories = ref<AdminToolCategoryListItem[]>([])
const categoryLoading = ref(false)

// 创建内置工具对话框
const createBuiltInDialogVisible = ref(false)
const createBuiltInFormRef = ref<FormInstance>()
const createBuiltInForm = reactive<CreateBuiltInToolRequest>({
  name: '',
  description: '',
  category_id: '',
  icon: '',
  order: 0,
  visible: true,
})

// 上传HTML工具对话框
const uploadHtmlDialogVisible = ref(false)
const uploadHtmlFormRef = ref<FormInstance>()
const uploadHtmlForm = reactive({
  name: '',
  description: '',
  category_id: '',
  icon: '',
  order: 0,
  visible: true,
  html_file: null as File | null,
})

// 编辑工具对话框
const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editForm = reactive<UpdateToolRequest & { id?: string }>({
  name: '',
  description: '',
  category_id: '',
  icon: '',
  order: 0,
  visible: true,
})


// 提交状态
const submitting = ref(false)

// 表单验证规则
const createBuiltInRules: FormRules = {
  name: [
    { required: true, message: '请输入工具名称', trigger: 'blur' },
    { min: 1, max: 100, message: '工具名称长度为1-100个字符', trigger: 'blur' },
  ],
  description: [
    { required: true, message: '请输入工具描述', trigger: 'blur' },
    { min: 1, max: 200, message: '工具描述长度为1-200个字符', trigger: 'blur' },
  ],
  category_id: [
    { required: true, message: '请选择分类', trigger: 'change' },
  ],
}

const uploadHtmlRules: FormRules = {
  name: [
    { required: true, message: '请输入工具名称', trigger: 'blur' },
    { min: 1, max: 100, message: '工具名称长度为1-100个字符', trigger: 'blur' },
  ],
  description: [
    { required: true, message: '请输入工具描述', trigger: 'blur' },
    { min: 1, max: 200, message: '工具描述长度为1-200个字符', trigger: 'blur' },
  ],
  category_id: [
    { required: true, message: '请选择分类', trigger: 'change' },
  ],
  html_file: [
    { required: true, message: '请选择HTML文件', trigger: 'change' },
  ],
}

const editRules: FormRules = {
  name: [
    { min: 1, max: 100, message: '工具名称长度为1-100个字符', trigger: 'blur' },
  ],
  description: [
    { min: 1, max: 200, message: '工具描述长度为1-200个字符', trigger: 'blur' },
  ],
}

/**
 * 加载工具列表
 */
async function loadTools() {
  loading.value = true
  try {
    const response = await ApiService.getAdminTools(
      currentPage.value,
      pageSize.value,
      filterCategoryId.value,
      filterType.value,
      filterVisible.value
    )
    tools.value = response.tools
    total.value = response.total
  } catch (error: any) {
    ElMessage.error(error.message || '加载工具列表失败')
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
    const response = await ApiService.getAdminToolCategories()
    categories.value = response.categories
  } catch (error: any) {
    ElMessage.error(error.message || '加载分类列表失败')
  } finally {
    categoryLoading.value = false
  }
}

/**
 * 筛选变化
 */
function handleFilterChange() {
  currentPage.value = 1
  loadTools()
}

/**
 * 页码变化
 */
function handlePageChange() {
  loadTools()
}

/**
 * 每页数量变化
 */
function handleSizeChange() {
  currentPage.value = 1
  loadTools()
}

/**
 * 创建内置工具
 */
function handleCreateBuiltInTool() {
  Object.assign(createBuiltInForm, {
    name: '',
    description: '',
    category_id: '',
    icon: '',
    order: 0,
    visible: true,
  })
  createBuiltInFormRef.value?.clearValidate()
  createBuiltInDialogVisible.value = true
}

/**
 * 提交创建内置工具
 */
async function handleCreateBuiltInSubmit() {
  if (!createBuiltInFormRef.value) return

  await createBuiltInFormRef.value.validate(async (valid) => {
    if (!valid) return

    // 如果没有选择图标，自动推荐一个
    if (!createBuiltInForm.icon || createBuiltInForm.icon.trim() === '') {
      createBuiltInForm.icon = recommendIcon(createBuiltInForm.name, createBuiltInForm.description, 'wrench')
    }

    submitting.value = true
    try {
      await ApiService.createBuiltInTool(createBuiltInForm)
      ElMessage.success('创建工具成功')
      createBuiltInDialogVisible.value = false
      loadTools()
    } catch (error: any) {
      ElMessage.error(error.message || '创建工具失败')
    } finally {
      submitting.value = false
    }
  })
}

/**
 * 上传HTML工具
 */
function handleUploadHtmlTool() {
  Object.assign(uploadHtmlForm, {
    name: '',
    description: '',
    category_id: '',
    icon: '',
    order: 0,
    visible: true,
    html_file: null,
  })
  uploadHtmlFormRef.value?.clearValidate()
  uploadHtmlDialogVisible.value = true
}

/**
 * 文件变化
 */
function handleFileChange(file: any) {
  uploadHtmlForm.html_file = file.raw
}

/**
 * 文件移除
 */
function handleFileRemove() {
  uploadHtmlForm.html_file = null
}

/**
 * 提交上传HTML工具
 */
async function handleUploadHtmlSubmit() {
  if (!uploadHtmlFormRef.value) return
  if (!uploadHtmlForm.html_file) {
    ElMessage.error('请选择HTML文件')
    return
  }

  await uploadHtmlFormRef.value.validate(async (valid) => {
    if (!valid) return

    // 如果没有选择图标，自动推荐一个
    if (!uploadHtmlForm.icon || uploadHtmlForm.icon.trim() === '') {
      uploadHtmlForm.icon = recommendIcon(uploadHtmlForm.name, uploadHtmlForm.description, 'wrench')
    }

    submitting.value = true
    try {
      await ApiService.createHtmlTool(
        uploadHtmlForm.name,
        uploadHtmlForm.description,
        uploadHtmlForm.category_id,
        uploadHtmlForm.html_file!,
        uploadHtmlForm.icon,
        uploadHtmlForm.order,
        uploadHtmlForm.visible
      )
      ElMessage.success('上传工具成功')
      uploadHtmlDialogVisible.value = false
      loadTools()
    } catch (error: any) {
      ElMessage.error(error.message || '上传工具失败')
    } finally {
      submitting.value = false
    }
  })
}

/**
 * 编辑工具
 */
function handleEdit(tool: AdminCommonToolListItem) {
  Object.assign(editForm, {
    id: tool.id,
    name: tool.name,
    description: tool.description,
    category_id: tool.category_id,
    icon: tool.icon || '',
    order: tool.order,
    visible: tool.visible,
  })
  editFormRef.value?.clearValidate()
  editDialogVisible.value = true
}

/**
 * 提交编辑工具
 */
async function handleEditSubmit() {
  if (!editFormRef.value || !editForm.id) return

  await editFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const { id, ...requestData } = editForm
      await ApiService.updateTool(id!, requestData)
      ElMessage.success('更新工具成功')
      editDialogVisible.value = false
      loadTools()
    } catch (error: any) {
      ElMessage.error(error.message || '更新工具失败')
    } finally {
      submitting.value = false
    }
  })
}

/**
 * 删除工具
 */
async function handleDelete(tool: AdminCommonToolListItem) {
  try {
    await ElMessageBox.confirm(
      `确定要删除工具 ${tool.name} 吗？删除后无法恢复。`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value = true
    try {
      await ApiService.deleteTool(tool.id)
      ElMessage.success('删除工具成功')
      loadTools()
    } catch (error: any) {
      ElMessage.error(error.message || '删除工具失败')
    } finally {
      loading.value = false
    }
  } catch {
    // 用户取消
  }
}

/**
 * 上移工具
 */
async function handleMoveUp(tool: AdminCommonToolListItem) {
  try {
    await ApiService.moveToolUp(tool.id)
    ElMessage.success('工具已上移')
    loadTools()
  } catch (error: any) {
    ElMessage.error(error.message || '上移失败')
  }
}

/**
 * 下移工具
 */
async function handleMoveDown(tool: AdminCommonToolListItem) {
  try {
    await ApiService.moveToolDown(tool.id)
    ElMessage.success('工具已下移')
    loadTools()
  } catch (error: any) {
    ElMessage.error(error.message || '下移失败')
  }
}

/**
 * 切换可见性
 */
async function handleToggleVisibility(tool: AdminCommonToolListItem) {
  try {
    const response = await ApiService.toggleToolVisibility(tool.id)
    ElMessage.success(response.message)
    loadTools()
  } catch (error: any) {
    ElMessage.error(error.message || '切换可见性失败')
  }
}


// 组件挂载时加载数据
onMounted(() => {
  loadCategories()
  loadTools()
})
</script>

<style scoped>
.admin-tools-page {
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
