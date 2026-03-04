<template>
  <el-dialog
    v-model="dialogVisible"
    :title="title"
    width="500px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="名称" prop="name">
        <el-input
          v-model="form.name"
          placeholder="请输入名称"
          maxlength="100"
          show-word-limit
        />
      </el-form-item>
      
      <el-form-item label="描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="请输入描述"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>
      
      <el-form-item label="HTML文件" prop="htmlFile">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          accept=".html"
          :file-list="fileList"
        >
          <el-button size="default">选择文件</el-button>
          <template #tip>
            <div class="el-upload__tip">
              只能上传 .html 文件，且不超过 {{ maxFileSizeMB }}MB
            </div>
          </template>
        </el-upload>
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitting">
        {{ submitText }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules, type UploadUserFile } from 'element-plus'

interface Props {
  modelValue: boolean
  title?: string
  submitText?: string
  maxFileSizeMB?: number
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'submit', data: { name: string; description: string; htmlFile: File }): void
}

const props = withDefaults(defineProps<Props>(), {
  title: '添加内容',
  submitText: '提交',
  maxFileSizeMB: 5,
})

const emit = defineEmits<Emits>()

// 表单引用
const formRef = ref<FormInstance>()
const uploadRef = ref()

// 对话框显示状态
const dialogVisible = ref(false)

// 表单数据
const form = reactive({
  name: '',
  description: '',
  htmlFile: null as File | null,
})

// 文件列表
const fileList = ref<UploadUserFile[]>([])

// 提交中状态
const submitting = ref(false)

// 表单验证规则
const rules: FormRules = {
  name: [
    { required: true, message: '请输入名称', trigger: 'blur' },
    { min: 1, max: 100, message: '名称长度为 1-100 个字符', trigger: 'blur' },
  ],
  description: [
    { required: true, message: '请输入描述', trigger: 'blur' },
    { min: 1, max: 200, message: '描述长度为 1-200 个字符', trigger: 'blur' },
  ],
  htmlFile: [
    { 
      required: true, 
      validator: (_rule, _value, callback) => {
        if (!form.htmlFile) {
          callback(new Error('请上传 HTML 文件'))
        } else {
          callback()
        }
      },
      trigger: 'change',
    },
  ],
}

// 监听 modelValue 变化
watch(() => props.modelValue, (newVal) => {
  dialogVisible.value = newVal
})

// 监听 dialogVisible 变化
watch(dialogVisible, (newVal) => {
  emit('update:modelValue', newVal)
})

/**
 * 处理文件选择
 */
const handleFileChange = (file: any) => {
  // 验证文件类型
  if (!file.name.endsWith('.html')) {
    ElMessage.error('只能上传 HTML 文件')
    uploadRef.value?.clearFiles()
    form.htmlFile = null
    return
  }
  
  // 验证文件大小
  const maxSize = props.maxFileSizeMB * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error(`文件大小不能超过 ${props.maxFileSizeMB}MB`)
    uploadRef.value?.clearFiles()
    form.htmlFile = null
    return
  }
  
  form.htmlFile = file.raw
}

/**
 * 处理文件移除
 */
const handleFileRemove = () => {
  form.htmlFile = null
}

/**
 * 处理提交
 */
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    // 验证表单
    await formRef.value.validate()
    
    if (!form.htmlFile) {
      ElMessage.error('请上传 HTML 文件')
      return
    }
    
    submitting.value = true
    
    // 触发提交事件
    emit('submit', {
      name: form.name,
      description: form.description,
      htmlFile: form.htmlFile,
    })
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    submitting.value = false
  }
}

/**
 * 处理关闭
 */
const handleClose = () => {
  // 重置表单
  formRef.value?.resetFields()
  form.htmlFile = null
  fileList.value = []
  uploadRef.value?.clearFiles()
  submitting.value = false
  
  emit('update:modelValue', false)
}

/**
 * 暴露重置方法（供父组件调用）
 */
const reset = () => {
  handleClose()
}

defineExpose({
  reset,
})
</script>

<style scoped>
.el-upload__tip {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}
</style>
