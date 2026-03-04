<template>
  <div class="admin-course-documents-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>课程文档管理</h3>
          <div class="header-controls">
            <el-select
              v-model="filterCategoryId"
              placeholder="按目录筛选"
              clearable
              style="width: 200px; margin-right: 10px"
              @change="loadDocuments"
            >
              <el-option
                v-for="cat in allCategories"
                :key="cat.id"
                :label="cat.name"
                :value="cat.id"
              />
            </el-select>
            <el-button type="primary" @click="handleCreate">创建文档</el-button>
          </div>
        </div>
      </template>

      <el-table :data="documents" v-loading="loading" style="width: 100%">
        <el-table-column prop="title" label="文档标题" width="250" />
        <el-table-column prop="category_path" label="所属目录" width="300" show-overflow-tooltip />
        <el-table-column prop="summary" label="摘要" min-width="300" show-overflow-tooltip />
        <el-table-column prop="order" label="排序" width="80" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" @click="handleMoveUp(row)">上移</el-button>
            <el-button size="small" @click="handleMoveDown(row)">下移</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">
              删除
            </el-button>
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
        @size-change="loadDocuments"
        @current-change="loadDocuments"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 创建文档对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="创建文档"
      width="600px"
      :close-on-click-modal="false"
      v-if="!isEdit"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="文档标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入文档标题" />
        </el-form-item>
        <el-form-item label="文档摘要" prop="summary">
          <el-input
            v-model="form.summary"
            type="textarea"
            :rows="3"
            placeholder="请输入文档摘要"
          />
        </el-form-item>
        <el-form-item label="所属目录" prop="category_id">
          <el-tree-select
            v-model="form.category_id"
            :data="categoryTreeData"
            placeholder="请选择目录"
            check-strictly
            :render-after-expand="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="排序" prop="order">
          <el-input-number v-model="form.order" :min="0" />
        </el-form-item>
        <el-form-item label="Markdown文件" prop="markdown_file">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
            accept=".md,.markdown"
          >
            <el-button>选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">只支持.md或.markdown文件，大小不超过5MB</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑文档对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑文档"
      width="600px"
      :close-on-click-modal="false"
      v-if="isEdit"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="editRules"
        label-width="100px"
      >
        <el-form-item label="文档标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入文档标题" />
        </el-form-item>
        <el-form-item label="文档摘要" prop="summary">
          <el-input
            v-model="form.summary"
            type="textarea"
            :rows="3"
            placeholder="请输入文档摘要"
          />
        </el-form-item>
        <el-form-item label="所属目录" prop="category_id">
          <el-tree-select
            v-model="form.category_id"
            :data="categoryTreeData"
            placeholder="请选择目录"
            check-strictly
            :render-after-expand="false"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import {
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type FormRules,
  type UploadFile,
  type UploadInstance,
} from 'element-plus'
import { ApiService } from '../../services/apiClient'
import type {
  AdminCourseDocumentListItem,
  AdminCourseCategoryListItem,
  UpdateCourseDocumentRequest,
} from '../../types'

// 文档列表
const documents = ref<AdminCourseDocumentListItem[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

// 筛选
const filterCategoryId = ref<string>('')
const allCategories = ref<AdminCourseCategoryListItem[]>([])

// 对话框
const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const uploadRef = ref<UploadInstance>()
const isEdit = ref(false)
const submitting = ref(false)
const selectedFile = ref<File | null>(null)
const fileList = ref<UploadFile[]>([])

const form = reactive<{
  id?: string
  title?: string
  summary?: string
  category_id?: string
  order?: number
  markdown_file?: File
}>({
  title: '',
  summary: '',
  category_id: '',
  order: 0,
})

// 构建树形数据（用于树形选择器）
const categoryTreeData = computed(() => {
  // 构建树形结构的递归函数
  const buildTree = (parentId: string | null): any[] => {
    return allCategories.value
      .filter(cat => cat.parent_id === parentId)
      .map(cat => ({
        value: cat.id,
        label: cat.name,
        children: buildTree(cat.id),
      }))
  }
  
  return buildTree(null)
})

// 创建表单验证规则
const rules: FormRules = {
  title: [
    { required: true, message: '请输入文档标题', trigger: 'blur' },
    { min: 1, max: 200, message: '文档标题长度为1-200个字符', trigger: 'blur' },
  ],
  summary: [
    { required: true, message: '请输入文档摘要', trigger: 'blur' },
    { min: 1, max: 500, message: '文档摘要长度为1-500个字符', trigger: 'blur' },
  ],
  category_id: [{ required: true, message: '请选择目录', trigger: 'change' }],
  order: [{ required: true, message: '请输入排序', trigger: 'blur' }],
  markdown_file: [
    {
      validator: (_rule, _value, callback) => {
        if (!selectedFile.value) {
          callback(new Error('请选择Markdown文件'))
        } else {
          callback()
        }
      },
      trigger: 'change',
    },
  ],
}

// 编辑表单验证规则
const editRules: FormRules = {
  title: [
    { min: 1, max: 200, message: '文档标题长度为1-200个字符', trigger: 'blur' },
  ],
  summary: [
    { min: 1, max: 500, message: '文档摘要长度为1-500个字符', trigger: 'blur' },
  ],
}

/**
 * 加载目录列表
 */
async function loadCategories() {
  try {
    const response = await ApiService.getAdminCourseCategories()
    allCategories.value = response.categories
  } catch (error: any) {
    ElMessage.error(error.message || '加载目录列表失败')
  }
}

/**
 * 加载文档列表
 */
async function loadDocuments() {
  loading.value = true
  try {
    const response = await ApiService.getAdminCourseDocuments(
      currentPage.value,
      pageSize.value,
      filterCategoryId.value || undefined
    )
    documents.value = response.documents
    total.value = response.total
  } catch (error: any) {
    ElMessage.error(error.message || '加载文档列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 文件选择变化
 */
function handleFileChange(file: UploadFile) {
  if (!file.raw) return

  // 验证文件类型
  const fileName = file.name
  if (!fileName.endsWith('.md') && !fileName.endsWith('.markdown')) {
    ElMessage.error('只支持.md或.markdown文件')
    uploadRef.value?.clearFiles()
    selectedFile.value = null
    return
  }

  // 验证文件大小（5MB）
  if (file.size && file.size > 5 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过5MB')
    uploadRef.value?.clearFiles()
    selectedFile.value = null
    return
  }

  selectedFile.value = file.raw
  fileList.value = [file]
}

/**
 * 文件数量超出限制
 */
function handleExceed() {
  ElMessage.warning('只能上传一个文件')
}

/**
 * 创建文档
 */
function handleCreate() {
  Object.assign(form, {
    title: '',
    summary: '',
    category_id: '',
    order: 0,
  })
  selectedFile.value = null
  fileList.value = []
  uploadRef.value?.clearFiles()
  isEdit.value = false
  formRef.value?.clearValidate()
  dialogVisible.value = true
}

/**
 * 编辑文档
 */
function handleEdit(doc: AdminCourseDocumentListItem) {
  Object.assign(form, {
    id: doc.id,
    title: doc.title,
    summary: doc.summary,
    category_id: doc.category_id,
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
      // 更新文档
      const request: UpdateCourseDocumentRequest = {}
      if (form.title) request.title = form.title
      if (form.summary) request.summary = form.summary
      if (form.category_id) request.category_id = form.category_id
      if (form.order !== undefined) request.order = form.order

      await ApiService.updateCourseDocument(form.id, request)
      ElMessage.success('文档更新成功')
    } else {
      // 创建文档
      if (!selectedFile.value) {
        ElMessage.error('请选择Markdown文件')
        return
      }

      await ApiService.createCourseDocument(
        form.title!,
        form.summary!,
        form.category_id!,
        form.order!,
        selectedFile.value
      )
      ElMessage.success('文档创建成功')
    }

    dialogVisible.value = false
    await loadDocuments()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

/**
 * 删除文档
 */
async function handleDelete(doc: AdminCourseDocumentListItem) {
  try {
    await ElMessageBox.confirm(`确定要删除文档"${doc.title}"吗？`, '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }

  try {
    await ApiService.deleteCourseDocument(doc.id)
    ElMessage.success('文档删除成功')
    await loadDocuments()
  } catch (error: any) {
    ElMessage.error(error.message || '删除失败')
  }
}

/**
 * 上移文档
 */
async function handleMoveUp(doc: AdminCourseDocumentListItem) {
  try {
    await ApiService.moveCourseDocumentUp(doc.id)
    ElMessage.success('文档已上移')
    await loadDocuments()
  } catch (error: any) {
    ElMessage.error(error.message || '上移失败')
  }
}

/**
 * 下移文档
 */
async function handleMoveDown(doc: AdminCourseDocumentListItem) {
  try {
    await ApiService.moveCourseDocumentDown(doc.id)
    ElMessage.success('文档已下移')
    await loadDocuments()
  } catch (error: any) {
    ElMessage.error(error.message || '下移失败')
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadCategories()
  loadDocuments()
})
</script>

<style scoped>
.admin-course-documents-page {
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

.header-controls {
  display: flex;
  align-items: center;
}
</style>

