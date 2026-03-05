# -*- coding: utf-8 -*-
<template>
  <el-dialog
    v-model="visible"
    :title="category ? '编辑目录' : '新建目录'"
    :width="500"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="目录名称" prop="name">
        <el-input
          v-model="form.name"
          placeholder="输入目录名称"
          clearable
          maxlength="100"
          show-word-limit
        />
      </el-form-item>

      <el-form-item v-if="!category" label="父目录">
        <el-cascader
          v-model="form.parentId"
          :options="categoryOptions"
          :props="cascaderProps"
          placeholder="选择父目录（可选）"
          clearable
          class="w-full"
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
        {{ category ? '保存' : '创建' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch } from 'vue'
import type { Category } from '@/types/file-manager'
import type { FormInstance, FormRules } from 'element-plus'

interface Props {
  modelValue: boolean
  category: Category | null
  categories: Category[]
  isPartyTheme?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm', data: { categoryId?: string; name: string; parentId?: string | null }): void
}

const props = withDefaults(defineProps<Props>(), {
  isPartyTheme: false
})

const emit = defineEmits<Emits>()

const formRef = ref<FormInstance>()

const form = reactive<{
  name: string
  parentId: string | null
}>({
  name: '',
  parentId: null
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入目录名称', trigger: 'blur' },
    { min: 1, max: 100, message: '目录名称长度为 1-100 个字符', trigger: 'blur' }
  ]
}

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 构建级联选择器选项（排除当前目录及其子目录，防止循环）
const categoryOptions = computed(() => {
  const excludeIds = props.category ? getDescendantIds(props.category, props.categories) : []

  const buildOptions = (categories: Category[]): any[] => {
    return categories
      .filter(cat => !excludeIds.includes(cat.id))
      .map(cat => ({
        value: cat.id,
        label: cat.name,
        children: cat.children?.length ? buildOptions(cat.children) : undefined
      }))
  }
  return buildOptions(props.categories)
})

// 获取目录及其所有子孙目录的 ID
const getDescendantIds = (category: Category, _allCategories: Category[]): string[] => {
  const ids = [category.id]
  const collect = (cat: Category) => {
    if (cat.children?.length) {
      for (const child of cat.children) {
        ids.push(child.id)
        collect(child)
      }
    }
  }
  collect(category)
  return ids
}

const cascaderProps = {
  value: 'value',
  label: 'label',
  children: 'children',
  checkStrictly: true,
  emitPath: false
}

// 监听 category 变化，更新表单
watch(() => props.category, (newCategory) => {
  if (newCategory) {
    form.name = newCategory.name
    form.parentId = newCategory.parent_id
  } else {
    form.name = ''
    form.parentId = null
  }
}, { immediate: true })

const handleConfirm = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    if (props.category) {
      // 编辑模式
      emit('confirm', {
        categoryId: props.category.id,
        name: form.name,
        parentId: form.parentId
      })
    } else {
      // 新建模式
      emit('confirm', {
        name: form.name,
        parentId: form.parentId
      })
    }
  } catch {
    // 验证失败
  }
}

const handleClosed = () => {
  formRef.value?.resetFields()
}
</script>

<style scoped>
</style>
