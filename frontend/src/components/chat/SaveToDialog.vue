# -*- coding: utf-8 -*-
<template>
  <CreateFileDialog
    v-model="visible"
    mode="save"
    :target="target"
    :categories="categories"
    :default-filename="defaultFilename"
    :content="content"
    :is-party-theme="true"
    @confirm="handleConfirm"
    @update:model-value="handleDialogVisibleChange"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import CreateFileDialog from '../file-manager/CreateFileDialog.vue'
import * as knowledgeApi from '@/services/knowledgeApi'
import * as partyActivityApi from '@/services/partyActivityApi'
import type { Category } from '@/types/file-manager'
import { extractDefaultFilename, generateUniqueFilename } from '@/utils/filenameExtractor'

interface Props {
  modelValue: boolean
  target: 'knowledge' | 'party'
  content: string
  categories: Category[]
  sessionTitle?: string
  forceRefresh?: (target: 'knowledge' | 'party') => Promise<void>
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'saved', path: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 对话框显示状态变化时刷新目录
async function handleDialogVisibleChange(value: boolean) {
  if (value && props.forceRefresh) {
    await props.forceRefresh(props.target)
  }
}

// 从内容中提取默认文件名
const defaultFilename = computed(() => {
  return extractDefaultFilename(props.content, props.sessionTitle)
})

// 递归深度计数器，防止栈溢出
let recursionDepth = 0
const MAX_RECURSION_DEPTH = 3

const handleConfirm = async (data: { categoryId: string; filename: string; content?: string }) => {
  // 递归深度保护
  if (recursionDepth > MAX_RECURSION_DEPTH) {
    ElMessage.error('文件名冲突过多，请手动重命名文件')
    return
  }
  recursionDepth++

  try {
    const { categoryId, filename, content } = data

    // 获取目录下现有文件列表，检查冲突
    const existingFiles = props.target === 'knowledge'
      ? await knowledgeApi.getDocuments(categoryId)
      : await partyActivityApi.getDocuments(categoryId)

    const existingNames = existingFiles.map(f => f.original_filename)

    // 检查文件名是否已存在
    if (existingNames.includes(filename)) {
      // 使用 ElMessageBox 询问用户
      const { ElMessageBox } = await import('element-plus')
      try {
        await ElMessageBox.confirm(
          `文件 "${filename}" 已存在，是否覆盖？`,
          '文件名冲突',
          {
            confirmButtonText: '覆盖',
            cancelButtonText: '重命名',
            distinguishCancelAndClose: true,
            type: 'warning',
          }
        )
        // 用户选择覆盖，继续保存
      } catch (action) {
        if (action === 'cancel') {
          // 用户选择重命名，生成新文件名
          const uniqueName = generateUniqueFilename(
            filename.replace('.md', ''),
            existingNames
          )
          // 递归调用，使用新文件名
          await handleConfirm({ categoryId, filename: uniqueName + '.md', content })
          return
        } else {
          // 用户取消，关闭对话框
          recursionDepth = 0
          return
        }
      }
    }

    // 调用 API 保存
    if (props.target === 'knowledge') {
      await knowledgeApi.createDocument({
        category_id: categoryId,
        filename: filename,
        content: content || ''
      })
    } else {
      await partyActivityApi.createDocument({
        category_id: categoryId,
        filename: filename,
        content: content || ''
      })
    }

    // 获取目录名称用于提示
    const findCategoryName = (cats: Category[], id: string): string => {
      for (const cat of cats) {
        if (cat.id === id) return cat.name
        if (cat.children) {
          const found = findCategoryName(cat.children, id)
          if (found) return found
        }
      }
      return '未知目录'
    }

    const categoryName = findCategoryName(props.categories, categoryId)
    const targetName = props.target === 'knowledge' ? '知识库' : '党建活动'

    ElMessage.success(`已保存到 ${targetName}/${categoryName}/${filename}`)
    emit('saved', `${targetName}/${categoryName}/${filename}`)
    visible.value = false
    recursionDepth = 0
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败，请重试')
    recursionDepth = 0
  }
}
</script>
