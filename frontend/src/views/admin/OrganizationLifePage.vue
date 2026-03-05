<template>
  <div class="organization-life-page">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/admin' }">管理后台</el-breadcrumb-item>
      <el-breadcrumb-item>组织生活管理</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 工具栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增记录
      </el-button>
      <el-button @click="handleRefresh">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
      <div class="toolbar-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索主题或内容"
          clearable
          style="width: 250px"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-select
        v-model="filters.activityType"
        placeholder="活动类型"
        clearable
        style="width: 180px"
        @change="handleSearch"
      >
        <el-option label="三会一课" value="三会一课" />
        <el-option label="民主评议" value="民主评议" />
        <el-option label="主题党日" value="主题党日" />
        <el-option label="组织生活会" value="组织生活会" />
        <el-option label="其他" value="其他" />
      </el-select>
    </div>

    <!-- 数据表格 -->
    <el-table
      :data="records"
      :loading="loading"
      stripe
      border
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="title" label="活动主题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="activity_type" label="活动类型" width="120">
        <template #default="{ row }">
          <el-tag :type="getActivityTypeTag(row.activity_type)">
            {{ row.activity_type }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="activity_date" label="活动时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.activity_date) }}
        </template>
      </el-table-column>
      <el-table-column prop="location" label="活动地点" width="150" show-overflow-tooltip />
      <el-table-column prop="participants_count" label="参与人数" width="100" align="center" />
      <el-table-column prop="organizer" label="组织者" width="120" show-overflow-tooltip />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="handleView(row)">
            查看
          </el-button>
          <el-button type="primary" link size="small" @click="handleEdit(row)">
            编辑
          </el-button>
          <el-button type="danger" link size="small" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.pageSize"
      :page-sizes="[10, 20, 50, 100]"
      :total="pagination.total"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
    />

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>
        <el-form-item label="活动类型" prop="activity_type">
          <el-select v-model="formData.activity_type" placeholder="请选择活动类型">
            <el-option label="三会一课" value="三会一课" />
            <el-option label="民主评议" value="民主评议" />
            <el-option label="主题党日" value="主题党日" />
            <el-option label="组织生活会" value="组织生活会" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="formData.activity_type === '三会一课'" label="会议类型" prop="meeting_type">
          <el-select v-model="formData.meeting_type" placeholder="请选择会议类型">
            <el-option label="支部党员大会" value="支部党员大会" />
            <el-option label="支部委员会" value="支部委员会" />
            <el-option label="党小组会" value="党小组会" />
            <el-option label="党课" value="党课" />
          </el-select>
        </el-form-item>
        <el-form-item label="活动主题" prop="title">
          <el-input v-model="formData.title" placeholder="请输入活动主题" />
        </el-form-item>
        <el-form-item label="活动时间" prop="activity_date">
          <el-date-picker
            v-model="formData.activity_date"
            type="datetime"
            placeholder="选择日期时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="活动地点">
          <el-input v-model="formData.location" placeholder="请输入活动地点" />
        </el-form-item>

        <!-- 人员信息 -->
        <el-divider content-position="left">人员信息</el-divider>
        <el-form-item label="主持人">
          <el-input v-model="formData.host" placeholder="请输入主持人" />
        </el-form-item>
        <el-form-item label="记录人">
          <el-input v-model="formData.recorder" placeholder="请输入记录人" />
        </el-form-item>
        <el-form-item label="应到人数">
          <el-input-number v-model="formData.expected_count" :min="0" />
        </el-form-item>
        <el-form-item label="实到人数" prop="participants_count">
          <el-input-number v-model="formData.participants_count" :min="0" />
        </el-form-item>

        <!-- 活动内容 -->
        <el-divider content-position="left">活动内容</el-divider>
        <el-form-item label="活动内容">
          <el-input
            v-model="formData.content"
            type="textarea"
            :rows="4"
            placeholder="请输入活动内容摘要"
          />
        </el-form-item>
        <el-form-item label="决议事项">
          <el-input
            v-model="formData.resolutions"
            type="textarea"
            :rows="3"
            placeholder="请输入决议事项"
          />
        </el-form-item>

        <!-- 其他信息 -->
        <el-divider content-position="left">其他信息</el-divider>
        <el-form-item label="组织者">
          <el-input v-model="formData.organizer" placeholder="请输入组织者" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看对话框 -->
    <el-dialog v-model="viewDialogVisible" title="记录详情" width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="活动类型">
          <el-tag :type="getActivityTypeTag(currentRecord.activity_type)">
            {{ currentRecord.activity_type }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="会议类型">
          {{ currentRecord.meeting_type || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="活动主题" :span="2">
          {{ currentRecord.title }}
        </el-descriptions-item>
        <el-descriptions-item label="活动时间">
          {{ formatDateTime(currentRecord.activity_date) }}
        </el-descriptions-item>
        <el-descriptions-item label="活动地点">
          {{ currentRecord.location || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="主持人">
          {{ currentRecord.host || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="记录人">
          {{ currentRecord.recorder || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="应到人数">
          {{ currentRecord.expected_count || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="实到人数">
          {{ currentRecord.participants_count }}
        </el-descriptions-item>
        <el-descriptions-item label="组织者">
          {{ currentRecord.organizer || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDateTime(currentRecord.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="活动内容" :span="2">
          <div class="content-text">{{ currentRecord.content || '-' }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="决议事项" :span="2">
          <div class="content-text">{{ currentRecord.resolutions || '-' }}</div>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import APIService from '@/services/apiClient'
import type {
  OrganizationLifeListItem,
  OrganizationLifeDetail,
  OrganizationLifeCreateRequest,
  OrganizationLifeUpdateRequest,
} from '@/types/party'

// 数据
const records = ref<OrganizationLifeListItem[]>([])
const loading = ref(false)
const searchKeyword = ref('')
const selectedRecords = ref<OrganizationLifeListItem[]>([])

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

// 筛选条件
const filters = reactive({
  activityType: '',
})

// 对话框
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const viewDialogVisible = ref(false)
const currentRecord = ref<OrganizationLifeDetail>({} as OrganizationLifeDetail)

const dialogTitle = computed(() => {
  return dialogMode.value === 'create' ? '新增组织生活记录' : '编辑组织生活记录'
})

// 表单
const formRef = ref<FormInstance>()
const formData = reactive<OrganizationLifeCreateRequest & { life_id?: string }>({
  activity_type: '',
  meeting_type: '',
  title: '',
  activity_date: '',
  location: '',
  host: '',
  recorder: '',
  expected_count: undefined,
  participants_count: 0,
  content: '',
  resolutions: '',
  organizer: '',
})

const formRules: FormRules = {
  activity_type: [{ required: true, message: '请选择活动类型', trigger: 'change' }],
  title: [{ required: true, message: '请输入活动主题', trigger: 'blur' }],
  activity_date: [{ required: true, message: '请选择活动时间', trigger: 'change' }],
  participants_count: [{ required: true, message: '请输入实到人数', trigger: 'blur' }],
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const response = await APIService.getOrganizationLives(
      pagination.page,
      pagination.pageSize,
      filters.activityType || undefined,
      searchKeyword.value || undefined
    )
    records.value = response.records
    pagination.total = response.total
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 刷新
const handleRefresh = () => {
  searchKeyword.value = ''
  filters.activityType = ''
  pagination.page = 1
  loadData()
}

// 新增
const handleAdd = () => {
  dialogMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: OrganizationLifeListItem) => {
  dialogMode.value = 'edit'
  // 获取完整数据
  APIService.getOrganizationLife(row.life_id).then((detail) => {
    currentRecord.value = detail
    Object.assign(formData, {
      life_id: detail.life_id,
      activity_type: detail.activity_type,
      meeting_type: detail.meeting_type,
      title: detail.title,
      activity_date: detail.activity_date,
      location: detail.location,
      host: detail.host,
      recorder: detail.recorder,
      expected_count: detail.expected_count,
      participants_count: detail.participants_count,
      content: detail.content,
      resolutions: detail.resolutions,
      organizer: detail.organizer,
    })
    dialogVisible.value = true
  })
}

// 查看
const handleView = (row: OrganizationLifeListItem) => {
  APIService.getOrganizationLife(row.life_id).then((detail) => {
    currentRecord.value = detail
    viewDialogVisible.value = true
  })
}

// 删除
const handleDelete = (row: OrganizationLifeListItem) => {
  ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    APIService.deleteOrganizationLife(row.life_id).then(() => {
      ElMessage.success('删除成功')
      loadData()
    })
  })
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      if (dialogMode.value === 'create') {
        await APIService.createOrganizationLife(formData as OrganizationLifeCreateRequest)
        ElMessage.success('创建成功')
      } else {
        const updateData: OrganizationLifeUpdateRequest = { ...formData }
        delete (updateData as any).life_id
        await APIService.updateOrganizationLife(formData.life_id!, updateData)
        ElMessage.success('更新成功')
      }
      dialogVisible.value = false
      loadData()
    } catch (error) {
      console.error('提交失败:', error)
      ElMessage.error('操作失败')
    }
  })
}

// 重置表单
const resetForm = () => {
  Object.assign(formData, {
    life_id: undefined,
    activity_type: '',
    meeting_type: '',
    title: '',
    activity_date: '',
    location: '',
    host: '',
    recorder: '',
    expected_count: undefined,
    participants_count: 0,
    content: '',
    resolutions: '',
    organizer: '',
  })
  formRef.value?.clearValidate()
}

// 对话框关闭
const handleDialogClose = () => {
  resetForm()
}

// 选择变化
const handleSelectionChange = (selection: OrganizationLifeListItem[]) => {
  selectedRecords.value = selection
}

// 分页变化
const handlePageChange = (page: number) => {
  pagination.page = page
  loadData()
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.page = 1
  loadData()
}

// 工具函数
const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getActivityTypeTag = (type: string) => {
  const typeMap: Record<string, string> = {
    '三会一课': 'danger',
    '民主评议': 'warning',
    '主题党日': 'success',
    '组织生活会': 'primary',
  }
  return typeMap[type] || 'info'
}

// 初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.organization-life-page {
  padding: 20px;
}

.breadcrumb {
  margin-bottom: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.toolbar-right {
  display: flex;
  gap: 10px;
}

.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.content-text {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}

.el-pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
