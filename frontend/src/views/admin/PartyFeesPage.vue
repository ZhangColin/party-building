<template>
  <div class="party-fees-page">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/admin' }">管理后台</el-breadcrumb-item>
      <el-breadcrumb-item>党费管理</el-breadcrumb-item>
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
          placeholder="搜索党员姓名"
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
        v-model="filters.status"
        placeholder="状态"
        clearable
        style="width: 120px"
        @change="handleSearch"
      >
        <el-option label="已缴" value="已缴" />
        <el-option label="欠缴" value="欠缴" />
      </el-select>
      <el-date-picker
        v-model="filters.feeMonth"
        type="month"
        placeholder="缴费月份"
        format="YYYY-MM"
        value-format="YYYY-MM"
        style="width: 150px"
        @change="handleSearch"
      />
    </div>

    <!-- 数据表格 -->
    <el-table
      :data="fees"
      :loading="loading"
      stripe
      border
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="member_name" label="党员姓名" width="120" />
      <el-table-column prop="amount" label="缴纳金额" width="120" align="right">
        <template #default="{ row }">
          ¥{{ row.amount.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="fee_month" label="缴费月份" width="110" />
      <el-table-column prop="payment_date" label="缴纳时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.payment_date) }}
        </template>
      </el-table-column>
      <el-table-column prop="payment_method" label="缴纳方式" width="120">
        <template #default="{ row }">
          <el-tag :type="getPaymentMethodTag(row.payment_method)">
            {{ row.payment_method }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === '已缴' ? 'success' : 'danger'">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="collector" label="收款人" width="110" show-overflow-tooltip />
      <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
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
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="党员姓名" prop="member_name">
          <el-input v-model="formData.member_name" placeholder="请输入党员姓名" />
        </el-form-item>
        <el-form-item label="缴纳金额" prop="amount">
          <el-input-number
            v-model="formData.amount"
            :min="0"
            :precision="2"
            :step="0.01"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="缴费月份" prop="fee_month">
          <el-date-picker
            v-model="formData.fee_month"
            type="month"
            placeholder="选择月份"
            format="YYYY-MM"
            value-format="YYYY-MM"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="缴纳时间" prop="payment_date">
          <el-date-picker
            v-model="formData.payment_date"
            type="datetime"
            placeholder="选择日期时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="缴纳方式" prop="payment_method">
          <el-select v-model="formData.payment_method" placeholder="请选择缴纳方式">
            <el-option label="现金" value="现金" />
            <el-option label="微信" value="微信" />
            <el-option label="支付宝" value="支付宝" />
            <el-option label="银行转账" value="银行转账" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio label="已缴">已缴</el-radio>
            <el-radio label="欠缴">欠缴</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="收款人">
          <el-input v-model="formData.collector" placeholder="请输入收款人" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="formData.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看对话框 -->
    <el-dialog v-model="viewDialogVisible" title="记录详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="党员姓名">
          {{ currentFee.member_name }}
        </el-descriptions-item>
        <el-descriptions-item label="缴纳金额">
          ¥{{ currentFee.amount?.toFixed(2) }}
        </el-descriptions-item>
        <el-descriptions-item label="缴费月份">
          {{ currentFee.fee_month }}
        </el-descriptions-item>
        <el-descriptions-item label="缴纳时间">
          {{ formatDateTime(currentFee.payment_date) }}
        </el-descriptions-item>
        <el-descriptions-item label="缴纳方式">
          <el-tag :type="getPaymentMethodTag(currentFee.payment_method)">
            {{ currentFee.payment_method }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentFee.status === '已缴' ? 'success' : 'danger'">
            {{ currentFee.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="收款人">
          {{ currentFee.collector || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDateTime(currentFee.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          <div class="content-text">{{ currentFee.remark || '-' }}</div>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import { ApiService } from '@/services/apiClient'
import type {
  PartyFeeListItem,
  PartyFeeDetail,
  PartyFeeCreateRequest,
  PartyFeeUpdateRequest,
} from '@/types/party'

// 数据
const fees = ref<PartyFeeListItem[]>([])
const loading = ref(false)
const searchKeyword = ref('')
const selectedFees = ref<PartyFeeListItem[]>([])

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

// 筛选条件
const filters = reactive({
  status: '',
  feeMonth: '',
})

// 对话框
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const viewDialogVisible = ref(false)
const currentFee = ref<PartyFeeDetail>({} as PartyFeeDetail)

const dialogTitle = computed(() => {
  return dialogMode.value === 'create' ? '新增党费记录' : '编辑党费记录'
})

// 表单
const formRef = ref<FormInstance>()
const formData = reactive<PartyFeeCreateRequest & { fee_id?: string }>({
  member_name: '',
  amount: 0,
  fee_month: '',
  payment_date: '',
  payment_method: '现金',
  status: '已缴',
  collector: '',
  remark: '',
})

const formRules: FormRules = {
  member_name: [{ required: true, message: '请输入党员姓名', trigger: 'blur' }],
  amount: [{ required: true, message: '请输入缴纳金额', trigger: 'blur' }],
  fee_month: [{ required: true, message: '请选择缴费月份', trigger: 'change' }],
  payment_date: [{ required: true, message: '请选择缴纳时间', trigger: 'change' }],
  payment_method: [{ required: true, message: '请选择缴纳方式', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const response = await ApiService.getPartyFees(
      pagination.page,
      pagination.pageSize,
      undefined,
      filters.feeMonth || undefined,
      filters.status || undefined,
      searchKeyword.value || undefined
    )
    fees.value = response.fees
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
  filters.status = ''
  filters.feeMonth = ''
  pagination.page = 1
  loadData()
}

// 新增
const handleAdd = () => {
  dialogMode.value = 'create'
  resetForm()
  // 默认设置为当前月份
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  formData.fee_month = `${year}-${month}`
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: PartyFeeListItem) => {
  dialogMode.value = 'edit'
  // 获取完整数据
  ApiService.getPartyFee(row.fee_id).then((detail) => {
    currentFee.value = detail
    Object.assign(formData, {
      fee_id: detail.fee_id,
      member_name: detail.member_name,
      amount: detail.amount,
      fee_month: detail.fee_month,
      payment_date: detail.payment_date,
      payment_method: detail.payment_method,
      status: detail.status,
      collector: detail.collector,
      remark: detail.remark,
    })
    dialogVisible.value = true
  })
}

// 查看
const handleView = (row: PartyFeeListItem) => {
  ApiService.getPartyFee(row.fee_id).then((detail) => {
    currentFee.value = detail
    viewDialogVisible.value = true
  })
}

// 删除
const handleDelete = (row: PartyFeeListItem) => {
  ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    ApiService.deletePartyFee(row.fee_id).then(() => {
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
        await ApiService.createPartyFee(formData as PartyFeeCreateRequest)
        ElMessage.success('创建成功')
      } else {
        const updateData: PartyFeeUpdateRequest = { ...formData }
        delete (updateData as any).fee_id
        await ApiService.updatePartyFee(formData.fee_id!, updateData)
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
    fee_id: undefined,
    member_name: '',
    amount: 0,
    fee_month: '',
    payment_date: '',
    payment_method: '现金',
    status: '已缴',
    collector: '',
    remark: '',
  })
  formRef.value?.clearValidate()
}

// 对话框关闭
const handleDialogClose = () => {
  resetForm()
}

// 选择变化
const handleSelectionChange = (selection: PartyFeeListItem[]) => {
  selectedFees.value = selection
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

const getPaymentMethodTag = (method: string) => {
  const methodMap: Record<string, string> = {
    '现金': 'info',
    '微信': 'success',
    '支付宝': 'primary',
    '银行转账': 'warning',
  }
  return methodMap[method] || 'info'
}

// 初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.party-fees-page {
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
