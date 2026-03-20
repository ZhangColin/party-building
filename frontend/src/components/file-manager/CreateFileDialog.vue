# -*- coding: utf-8 -*-
<template>
  <el-dialog
    v-model="visible"
    :title="dialogTitle"
    :width="500"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="目标目录" prop="categoryId">
        <el-cascader
          ref="cascaderRef"
          v-model="form.categoryId"
          :options="categoryOptions"
          :props="cascaderProps"
          placeholder="选择目录"
          clearable
          filterable
          @change="handleCascaderChange"
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

      <!-- 新建模式下显示内容输入框 -->
      <el-form-item v-if="mode === 'create'" label="初始内容">
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
        {{ confirmButtonText }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch } from 'vue'
import type { Category } from '@/types/file-manager'
import type { FormInstance, FormRules } from 'element-plus'

/** 对话框模式 */
type DialogMode = 'create' | 'save'

/** 目标类型 */
type TargetType = 'knowledge' | 'party'

interface Props {
  /** 对话框显示状态 */
  modelValue: boolean
  /** 可选目录列表 */
  categories: Category[]
  /** 默认目录 ID */
  defaultCategoryId?: string | null
  /** 是否使用党建主题 */
  isPartyTheme?: boolean
  /** 对话框模式：create（新建）或 save（保存） */
  mode?: DialogMode
  /** 保存模式下传入的内容 */
  content?: string
  /** 目标类型：knowledge（知识库）或 party（党建活动） */
  target?: TargetType
  /** 默认文件名 */
  defaultFilename?: string
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (
    e: 'confirm',
    data: { categoryId: string; filename: string; content?: string }
  ): void
}

const props = withDefaults(defineProps<Props>(), {
  defaultCategoryId: null,
  isPartyTheme: false,
  mode: 'create',
  content: '',
  target: 'knowledge',
  defaultFilename: ''
})

const emit = defineEmits<Emits>()

const formRef = ref<FormInstance>()
const cascaderRef = ref()

const form = reactive<{
  categoryId: string | null
  filename: string
  content: string
}>({
  categoryId: props.defaultCategoryId,
  filename: props.defaultFilename,
  content: props.content
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

/** 对话框显示状态 */
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

/** 当前模式 */
const mode = computed<DialogMode>(() => props.mode)

/** 当前目标类型 */
const target = computed<TargetType>(() => props.target)

/** 对话框标题 */
const dialogTitle = computed(() => {
  if (mode.value === 'create') {
    return '新建 Markdown 文件'
  }
  // 保存模式
  if (target.value === 'party') {
    return '保存到党建活动'
  }
  return '保存到知识库'
})

/** 确认按钮文本 */
const confirmButtonText = computed(() => {
  return mode.value === 'create' ? '创建' : '保存'
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

const handleCascaderChange = () => {
  // 选择后关闭面板
  cascaderRef.value?.blur()
}

/** 监听 props 变化，更新表单 */
watch(
  () => [props.defaultCategoryId, props.defaultFilename, props.content] as const,
  ([categoryId, filename, content]) => {
    if (categoryId !== null) {
      form.categoryId = categoryId
    }
    if (filename) {
      form.filename = filename
    }
    if (content) {
      form.content = content
    }
  }
)

const handleConfirm = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    // 保存模式下传递 content，新建模式下传递表单中的 content
    const emitContent = mode.value === 'save' ? props.content : form.content
    emit('confirm', {
      categoryId: form.categoryId!,
      filename: form.filename + '.md',
      content: emitContent
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
  // 保存模式下保留文件名，方便下次使用
  if (mode.value === 'save' && props.defaultFilename) {
    form.filename = props.defaultFilename
  }
}
</script>

<style scoped>
:deep(.el-input__suffix) {
  @apply text-gray-400;
}
</style>
