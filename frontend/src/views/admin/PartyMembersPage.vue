<template>
  <div class="party-members-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>管理后台</el-breadcrumb-item>
            <el-breadcrumb-item>党员管理</el-breadcrumb-item>
          </el-breadcrumb>
          <div class="header-actions">
            <el-button type="primary" @click="handleAdd">新增党员</el-button>
            <el-button @click="handleBatchImport">批量导入</el-button>
            <el-button @click="handleExport">导出</el-button>
          </div>
        </div>
      </template>

      <!-- 筛选器 -->
      <div class="filter-bar">
        <el-input
          v-model="filters.name"
          placeholder="姓名"
          clearable
          style="width: 150px"
          @keyup.enter="handleSearch"
        />
        <el-select
          v-model="filters.party_branch"
          placeholder="党支部"
          clearable
          style="width: 180px"
        >
          <el-option label="第一党支部" value="第一党支部" />
          <el-option label="第二党支部" value="第二党支部" />
          <el-option label="第三党支部" value="第三党支部" />
        </el-select>
        <el-select
          v-model="filters.member_type"
          placeholder="党员类型"
          clearable
          style="width: 150px"
        >
          <el-option label="正式党员" value="正式党员" />
          <el-option label="预备党员" value="预备党员" />
        </el-select>
        <el-select
          v-model="filters.status"
          placeholder="状态"
          clearable
          style="width: 120px"
        >
          <el-option label="正常" value="正常" />
          <el-option label="停止党籍" value="停止党籍" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>

      <!-- 党员列表表格 -->
      <el-table
        :data="members"
        v-loading="loading"
        style="width: 100%; margin-top: 16px"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column prop="member_type" label="党员类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.member_type === '正式党员'" type="success">正式党员</el-tag>
            <el-tag v-else type="warning">预备党员</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="party_branch" label="所属党支部" width="150" />
        <el-table-column prop="phone" label="联系电话" width="130">
          <template #default="{ row }">
            {{ row.phone || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="fee_standard" label="党费标准" width="100">
          <template #default="{ row }">
            {{ row.fee_standard ? `¥${row.fee_standard}` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.status === '正常'" type="success">正常</el-tag>
            <el-tag v-else type="danger">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="210" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleView(row)">查看</el-button>
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row)"
            >
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
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
        style="margin-top: 16px; justify-content: flex-end"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="formData.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="formData.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="身份证号" prop="id_card">
              <el-input v-model="formData.id_card" placeholder="请输入身份证号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出生日期" prop="birth_date">
              <el-date-picker
                v-model="formData.birth_date"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学历" prop="education">
              <el-select v-model="formData.education" placeholder="请选择学历" clearable style="width: 100%">
                <el-option label="博士" value="博士" />
                <el-option label="硕士" value="硕士" />
                <el-option label="本科" value="本科" />
                <el-option label="大专" value="大专" />
                <el-option label="高中" value="高中" />
                <el-option label="初中" value="初中" />
                <el-option label="小学" value="小学" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="formData.phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="formData.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工作单位" prop="work_unit">
              <el-input v-model="formData.work_unit" placeholder="请输入工作单位" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="职务/职称" prop="job_title">
          <el-input v-model="formData.job_title" placeholder="请输入职务/职称" />
        </el-form-item>
        <el-form-item label="现居住地址" prop="address">
          <el-input v-model="formData.address" placeholder="请输入现居住地址" />
        </el-form-item>

        <!-- 党务信息 -->
        <el-divider content-position="left">党务信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="所属党支部" prop="party_branch">
              <el-select v-model="formData.party_branch" placeholder="请选择党支部" style="width: 100%">
                <el-option label="第一党支部" value="第一党支部" />
                <el-option label="第二党支部" value="第二党支部" />
                <el-option label="第三党支部" value="第三党支部" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="党员类型" prop="member_type">
              <el-radio-group v-model="formData.member_type">
                <el-radio label="正式党员">正式党员</el-radio>
                <el-radio label="预备党员">预备党员</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="入党时间" prop="join_date">
              <el-date-picker
                v-model="formData.join_date"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="党内职务" prop="party_position">
              <el-input v-model="formData.party_position" placeholder="请输入党内职务" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="入党申请书提交时间" prop="application_date">
              <el-date-picker
                v-model="formData.application_date"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="确定为积极分子时间" prop="activist_date">
              <el-date-picker
                v-model="formData.activist_date"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="确定为发展对象时间" prop="candidate_date">
              <el-date-picker
                v-model="formData.candidate_date"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="接收为预备党员时间" prop="provisional_date">
              <el-date-picker
                v-model="formData.provisional_date"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="转正时间" prop="full_member_date">
              <el-date-picker
                v-model="formData.full_member_date"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="介绍人1" prop="introducer_1">
              <el-input v-model="formData.introducer_1" placeholder="请输入介绍人1" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="介绍人2" prop="introducer_2">
              <el-input v-model="formData.introducer_2" placeholder="请输入介绍人2" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 流动党员 -->
        <el-divider content-position="left">流动党员</el-divider>
        <el-form-item label="是否流动党员">
          <el-checkbox v-model="formData.is_mobile">是流动党员</el-checkbox>
        </el-form-item>
        <el-row v-if="formData.is_mobile" :gutter="20">
          <el-col :span="12">
            <el-form-item label="流动类型">
              <el-radio-group v-model="formData.mobile_type">
                <el-radio label="流出">流出</el-radio>
                <el-radio label="流入">流入</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="流动原因">
              <el-input v-model="formData.mobile_reason" placeholder="请输入流动原因" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 党费 -->
        <el-divider content-position="left">党费</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="月收入" prop="monthly_income">
              <el-input-number
                v-model="formData.monthly_income"
                :min="0"
                :precision="2"
                placeholder="请输入月收入"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="党费标准" prop="fee_standard">
              <el-input-number
                v-model="formData.fee_standard"
                :min="0"
                :precision="2"
                placeholder="请输入月缴金额"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 状态 -->
        <el-divider content-position="left">状态</el-divider>
        <el-form-item label="状态" prop="status">
          <el-select v-model="formData.status" placeholder="请选择状态" style="width: 200px">
            <el-option label="正常" value="正常" />
            <el-option label="停止党籍" value="停止党籍" />
            <el-option label="出党" value="出党" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="党员详情"
      width="800px"
    >
      <div v-if="currentMember" class="member-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="姓名">{{ currentMember.name }}</el-descriptions-item>
          <el-descriptions-item label="性别">{{ currentMember.gender }}</el-descriptions-item>
          <el-descriptions-item label="身份证号">{{ currentMember.id_card || '-' }}</el-descriptions-item>
          <el-descriptions-item label="出生日期">{{ currentMember.birth_date }}</el-descriptions-item>
          <el-descriptions-item label="学历">{{ currentMember.education || '-' }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ currentMember.phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ currentMember.email || '-' }}</el-descriptions-item>
          <el-descriptions-item label="工作单位">{{ currentMember.work_unit || '-' }}</el-descriptions-item>
          <el-descriptions-item label="职务/职称">{{ currentMember.job_title || '-' }}</el-descriptions-item>
          <el-descriptions-item label="所属党支部">{{ currentMember.party_branch }}</el-descriptions-item>
          <el-descriptions-item label="党员类型">{{ currentMember.member_type }}</el-descriptions-item>
          <el-descriptions-item label="入党时间">{{ currentMember.join_date }}</el-descriptions-item>
          <el-descriptions-item label="党内职务">{{ currentMember.party_position || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag v-if="currentMember.status === '正常'" type="success">正常</el-tag>
            <el-tag v-else type="danger">{{ currentMember.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="月收入">{{ currentMember.monthly_income ? `¥${currentMember.monthly_income}` : '-' }}</el-descriptions-item>
          <el-descriptions-item label="党费标准">{{ currentMember.fee_standard ? `¥${currentMember.fee_standard}` : '-' }}</el-descriptions-item>
          <el-descriptions-item label="是否流动党员">
            <el-tag v-if="currentMember.is_mobile" type="warning">是</el-tag>
            <el-tag v-else type="info">否</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="批量导入党员"
      width="600px"
    >
      <el-alert
        title="请上传Excel文件，文件格式要求："
        type="info"
        :closable="false"
        style="margin-bottom: 16px"
      >
        <template #default>
          <ul style="margin: 8px 0; padding-left: 20px">
            <li>文件格式：.xlsx 或 .xls</li>
            <li>必填字段：姓名、性别、出生日期、入党时间、所属党支部</li>
            <li>可选字段：身份证号、学历、联系电话、邮箱、工作单位、职务/职称等</li>
          </ul>
        </template>
      </el-alert>
      <el-upload
        ref="uploadRef"
        class="upload-demo"
        drag
        action=""
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        accept=".xlsx,.xls"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只支持 .xlsx 或 .xls 格式的Excel文件
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleImportSubmit" :loading="submitting">
          开始导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules, type UploadFile } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { ApiService } from '../../services/apiClient'
import type {
  PartyMemberListItem,
  PartyMemberDetail,
  PartyMemberCreateRequest,
  PartyMemberUpdateRequest,
} from '../../types/party'

// 党员列表数据
const members = ref<PartyMemberListItem[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const selectedMembers = ref<PartyMemberListItem[]>([])

// 筛选器
const filters = reactive({
  name: '',
  party_branch: '',
  member_type: '',
  status: '',
})

// 新增/编辑对话框
const dialogVisible = ref(false)
const dialogTitle = computed(() => (isEditMode.value ? '编辑党员' : '新增党员'))
const isEditMode = ref(false)
const formRef = ref<FormInstance>()
const formData = reactive<PartyMemberCreateRequest & { member_id?: string }>({
  name: '',
  gender: '男',
  id_card: '',
  birth_date: '',
  education: '',
  phone: '',
  email: '',
  address: '',
  work_unit: '',
  job_title: '',
  join_date: '',
  party_branch: '',
  member_type: '正式党员',
  application_date: '',
  activist_date: '',
  candidate_date: '',
  provisional_date: '',
  full_member_date: '',
  party_position: '',
  introducer_1: '',
  introducer_2: '',
  is_mobile: false,
  mobile_type: '',
  mobile_reason: '',
  monthly_income: undefined,
  fee_standard: undefined,
  status: '正常',
})

// 查看详情对话框
const viewDialogVisible = ref(false)
const currentMember = ref<PartyMemberDetail | null>(null)

// 批量导入对话框
const importDialogVisible = ref(false)
const uploadRef = ref()
const importFile = ref<File | null>(null)

// 提交状态
const submitting = ref(false)

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 1, max: 50, message: '姓名长度为1-50个字符', trigger: 'blur' },
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' },
  ],
  birth_date: [
    { required: true, message: '请选择出生日期', trigger: 'change' },
  ],
  party_branch: [
    { required: true, message: '请选择所属党支部', trigger: 'change' },
  ],
  member_type: [
    { required: true, message: '请选择党员类型', trigger: 'change' },
  ],
  join_date: [
    { required: true, message: '请选择入党时间', trigger: 'change' },
  ],
  phone: [
    {
      pattern: /^1[3-9]\d{9}$/,
      message: '请输入正确的手机号格式',
      trigger: 'blur',
    },
  ],
  email: [
    {
      pattern: /^[^@]+@[^@]+\.[^@]+$/,
      message: '请输入正确的邮箱格式',
      trigger: 'blur',
    },
  ],
  id_card: [
    {
      pattern: /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/,
      message: '请输入正确的身份证号格式',
      trigger: 'blur',
    },
  ],
}

/**
 * 格式化日期
 */
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * 加载党员列表
 */
async function loadMembers() {
  loading.value = true
  try {
    const response = await ApiService.getPartyMembers(
      currentPage.value,
      pageSize.value,
      filters.name || undefined,
      filters.party_branch || undefined,
      filters.member_type || undefined,
      filters.status || undefined
    )
    members.value = response.members
    total.value = response.total
  } catch (error: any) {
    ElMessage.error(error.message || '加载党员列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 查询按钮
 */
function handleSearch() {
  currentPage.value = 1
  loadMembers()
}

/**
 * 重置按钮
 */
function handleReset() {
  filters.name = ''
  filters.party_branch = ''
  filters.member_type = ''
  filters.status = ''
  currentPage.value = 1
  loadMembers()
}

/**
 * 页码变化
 */
function handlePageChange() {
  loadMembers()
}

/**
 * 每页数量变化
 */
function handleSizeChange() {
  currentPage.value = 1
  loadMembers()
}

/**
 * 表格选择变化
 */
function handleSelectionChange(selection: PartyMemberListItem[]) {
  selectedMembers.value = selection
}

/**
 * 新增党员
 */
function handleAdd() {
  isEditMode.value = false
  // 重置表单
  Object.assign(formData, {
    member_id: undefined,
    name: '',
    gender: '男',
    id_card: '',
    birth_date: '',
    education: '',
    phone: '',
    email: '',
    address: '',
    work_unit: '',
    job_title: '',
    join_date: '',
    party_branch: '',
    member_type: '正式党员',
    application_date: '',
    activist_date: '',
    candidate_date: '',
    provisional_date: '',
    full_member_date: '',
    party_position: '',
    introducer_1: '',
    introducer_2: '',
    is_mobile: false,
    mobile_type: '',
    mobile_reason: '',
    monthly_income: undefined,
    fee_standard: undefined,
    status: '正常',
  })
  formRef.value?.clearValidate()
  dialogVisible.value = true
}

/**
 * 查看详情
 */
async function handleView(member: PartyMemberListItem) {
  try {
    const detail = await ApiService.getPartyMember(member.member_id)
    currentMember.value = detail
    viewDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取党员详情失败')
  }
}

/**
 * 编辑党员
 */
async function handleEdit(member: PartyMemberListItem) {
  try {
    const detail = await ApiService.getPartyMember(member.member_id)
    isEditMode.value = true
    Object.assign(formData, {
      member_id: detail.member_id,
      name: detail.name,
      gender: detail.gender,
      id_card: detail.id_card,
      birth_date: detail.birth_date,
      education: detail.education,
      phone: detail.phone,
      email: detail.email,
      address: detail.address,
      work_unit: detail.work_unit,
      job_title: detail.job_title,
      join_date: detail.join_date,
      party_branch: detail.party_branch,
      member_type: detail.member_type,
      application_date: detail.application_date,
      activist_date: detail.activist_date,
      candidate_date: detail.candidate_date,
      provisional_date: detail.provisional_date,
      full_member_date: detail.full_member_date,
      party_position: detail.party_position,
      introducer_1: detail.introducer_1,
      introducer_2: detail.introducer_2,
      is_mobile: detail.is_mobile,
      mobile_type: detail.mobile_type,
      mobile_reason: detail.mobile_reason,
      monthly_income: detail.monthly_income ? parseFloat(detail.monthly_income) : undefined,
      fee_standard: detail.fee_standard ? parseFloat(detail.fee_standard) : undefined,
      status: detail.status,
    })
    formRef.value?.clearValidate()
    dialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取党员详情失败')
  }
}

/**
 * 提交表单
 */
async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEditMode.value && formData.member_id) {
        // 编辑模式
        const { member_id, ...requestData } = formData
        const updateData: PartyMemberUpdateRequest = {
          ...requestData,
          monthly_income: requestData.monthly_income?.toString(),
          fee_standard: requestData.fee_standard?.toString(),
        }
        await ApiService.updatePartyMember(member_id, updateData)
        ElMessage.success('更新党员成功')
      } else {
        // 新增模式
        const createData: PartyMemberCreateRequest = {
          ...formData,
          monthly_income: formData.monthly_income?.toString(),
          fee_standard: formData.fee_standard?.toString(),
        }
        await ApiService.createPartyMember(createData)
        ElMessage.success('创建党员成功')
      }
      dialogVisible.value = false
      loadMembers()
    } catch (error: any) {
      ElMessage.error(error.message || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

/**
 * 删除党员
 */
async function handleDelete(member: PartyMemberListItem) {
  try {
    await ElMessageBox.confirm(
      `确定要删除党员 ${member.name} 吗？删除后无法恢复。`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    loading.value = true
    try {
      await ApiService.deletePartyMember(member.member_id)
      ElMessage.success('删除党员成功')
      loadMembers()
    } catch (error: any) {
      ElMessage.error(error.message || '删除党员失败')
    } finally {
      loading.value = false
    }
  } catch {
    // 用户取消
  }
}

/**
 * 批量导入按钮
 */
function handleBatchImport() {
  importFile.value = null
  importDialogVisible.value = true
}

/**
 * 文件选择变化
 */
function handleFileChange(file: UploadFile) {
  if (file.raw) {
    importFile.value = file.raw
  }
}

/**
 * 提交批量导入
 */
async function handleImportSubmit() {
  if (!importFile.value) {
    ElMessage.warning('请选择要导入的文件')
    return
  }

  submitting.value = true
  try {
    // TODO: 实现Excel文件解析和批量导入逻辑
    // 这里需要使用 xlsx 库解析Excel文件
    ElMessage.info('批量导入功能开发中，请先使用新增党员功能')
    importDialogVisible.value = false
  } catch (error: any) {
    ElMessage.error(error.message || '批量导入失败')
  } finally {
    submitting.value = false
  }
}

/**
 * 导出按钮
 */
function handleExport() {
  ElMessage.info('导出功能开发中')
}

// 组件挂载时加载数据
onMounted(() => {
  loadMembers()
})
</script>

<style scoped>
.party-members-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.member-detail {
  padding: 16px 0;
}

:deep(.el-divider__text) {
  font-weight: 600;
  color: #409eff;
}
</style>
