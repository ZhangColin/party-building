# -*- coding: utf-8 -*-
<template>
  <el-dialog
    v-model="visible"
    title="上传文件"
    :width="500"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <el-form :model="form" label-width="80px">
      <el-form-item label="目标目录">
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

      <el-form-item label="选择文件">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :show-file-list="true"
          :limit="1"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          drag
          class="w-full"
        >
          <div class="upload-content">
            <CloudArrowUpIcon class="w-12 h-12 text-gray-400 mx-auto mb-2" />
            <p class="text-gray-600">拖拽文件到此处或点击上传</p>
            <p class="text-gray-400 text-sm mt-1">支持 Word、Excel、PDF、Markdown、文本、图片</p>
          </div>
        </el-upload>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button
        type="primary"
        :class="isPartyTheme ? 'party-btn-primary' : ''"
        :disabled="!form.file"
        :loading="uploading"
        @click="handleConfirm"
      >
        {{ uploading ? '上传中...' : '上传' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { CloudArrowUpIcon } from '@heroicons/vue/24/outline'
import { ElMessage } from 'element-plus'
import type { Category } from '@/types/file-manager'
import type { UploadFile } from 'element-plus'

interface Props {
  modelValue: boolean
  categories: Category[]
  defaultCategoryId?: string | null
  isPartyTheme?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm', data: { file: File; categoryId: string }): void
}

const props = withDefaults(defineProps<Props>(), {
  defaultCategoryId: null,
  isPartyTheme: false
})

const emit = defineEmits<Emits>()

const uploadRef = ref()
const cascaderRef = ref()
const uploading = ref(false)

const form = ref<{
  file: File | null
  categoryId: string | null
}>({
  file: null,
  categoryId: props.defaultCategoryId
})

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

const handleCascaderChange = () => {
  // 选择后关闭面板
  cascaderRef.value?.blur()
}

const handleFileChange = (file: UploadFile) => {
  if (file.raw) {
    form.value.file = file.raw
  }
}

const handleFileRemove = () => {
  form.value.file = null
}

const handleConfirm = () => {
  if (!form.value.file) {
    ElMessage.warning('请选择要上传的文件')
    return
  }

  if (!form.value.categoryId) {
    ElMessage.warning('请选择目标目录')
    return
  }

  emit('confirm', {
    file: form.value.file,
    categoryId: form.value.categoryId
  })
}

const handleClosed = () => {
  form.value = {
    file: null,
    categoryId: props.defaultCategoryId
  }
  uploadRef.value?.clearFiles()
}
</script>

<style scoped>
.upload-content {
  @apply p-6;
}

:deep(.el-upload-dragger) {
  @apply border-dashed;
}
</style>
