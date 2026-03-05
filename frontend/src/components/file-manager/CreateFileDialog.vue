# -*- coding: utf-8 -*-
<template>
  <el-dialog
    v-model="visible"
    title="新建 Markdown 文件"
    :width="500"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="目标目录" prop="categoryId">
        <el-cascader
          v-model="form.categoryId"
          :options="categoryOptions"
          :props="cascaderProps"
          placeholder="选择目录"
          clearable
          class="w-full"
        />
      </el-form-item>

      <el-form-item label="文件名" prop="filename">
        <el-input
          v-model="form.filename"
          placeholder="输入文件名（不含扩展名）"
          clearable
        >
          <template #suffix>.md</template>
        </el-input>
      </el-form-item>

      <el-form-item label="初始内容">
        <el-input
          v-model="form.content"
          type="textarea"
          :rows="6"
          placeholder="可选：输入初始内容（支持 Markdown 语法）"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button
        type="primary"
        :class="isPartyTheme ? 'party-btn-primary' : ''"
        @click="handleConfirm"
      >
        创建
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import type { Category } from '@/types/file-manager'
import type { FormInstance, FormRules } from 'element-plus'

interface Props {
  modelValue: boolean
  categories: Category[]
  defaultCategoryId?: string | null
  isPartyTheme?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm', data: { categoryId: string; filename: string; content: string }): void
}

const props = withDefaults(defineProps<Props>(), {
  defaultCategoryId: null,
  isPartyTheme: false
})

const emit = defineEmits<Emits>()

const formRef = ref<FormInstance>()

const form = reactive<{
  categoryId: string | null
  filename: string
  content: string
}>({
  categoryId: props.defaultCategoryId,
  filename: '',
  content: ''
})

const rules: FormRules = {
  categoryId: [
    { required: true, message: '请选择目标目录', trigger: 'change' }
  ],
  filename: [
    { required: true, message: '请输入文件名', trigger: 'blur' },
    {
      pattern: /^[^<>:"/\\|?*]+$/,
      message: '文件名不能包含特殊字符',
      trigger: 'blur'
    },
    { max: 100, message: '文件名不能超过 100 个字符', trigger: 'blur' }
  ]
}

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 构建级联选择器选项
const categoryOptions = computed(() => {
  const buildOptions = (categories: Category[]): any[] => {
    return categories.map(cat => ({
      value: cat.id,
      label: cat.name,
      children: cat.children?.length ? buildOptions(cat.children) : undefined
    }))
  }
  return buildOptions(props.categories)
})

const cascaderProps = {
  value: 'value',
  label: 'label',
  children: 'children',
  checkStrictly: true,
  emitPath: false
}

const handleConfirm = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    emit('confirm', {
      categoryId: form.categoryId!,
      filename: form.filename + '.md',
      content: form.content
    })
    // 关闭对话框
    visible.value = false
  } catch {
    // 验证失败
  }
}

const handleClosed = () => {
  formRef.value?.resetFields()
  form.content = ''
}
</script>

<style scoped>
:deep(.el-input__suffix) {
  @apply text-gray-400;
}
</style>
