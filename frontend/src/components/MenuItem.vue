<template>
  <div class="menu-item">
    <!-- 一级菜单 -->
    <div
      :class="['menu-item-primary', { active: isActive, 'has-children': hasChildren, 'not-clickable': hasChildren }]"
      @click="handlePrimaryClick"
    >
      <span class="menu-label">{{ item.label }}</span>
      <span v-if="hasChildren" class="menu-arrow">›</span>
    </div>
    
    <!-- 二级菜单 -->
    <div v-if="hasChildren && isExpanded" class="menu-item-children">
      <div
        v-for="child in item.children"
        :key="child.id"
        :class="['menu-item-secondary', { active: activeId === child.id }]"
        @click="handleChildClick(child.id)"
      >
        {{ child.label }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface MenuItemData {
  id: string
  label: string
  children?: MenuItemData[]
}

const props = defineProps<{
  item: MenuItemData
  activeId: string | null
}>()

const emit = defineEmits<{
  click: [id: string]
}>()

const isExpanded = ref(true) // 当前迭代固定展开

const hasChildren = computed(() => props.item.children && props.item.children.length > 0)
const isActive = computed(() => {
  if (hasChildren.value) {
    return false // 有二级菜单时，一级菜单不显示激活状态
  }
  return props.activeId === props.item.id
})

function handlePrimaryClick() {
  if (!hasChildren.value) {
    emit('click', props.item.id)
  }
}

function handleChildClick(childId: string) {
  emit('click', childId)
}
</script>

<style scoped>
.menu-item {
  @apply mb-0.5;
}

.menu-item-primary {
  @apply flex items-center justify-between px-4 py-3 rounded-lg cursor-pointer transition-all duration-200 text-gray-700 text-sm;
  /* 添加更柔和的hover效果 */
}

.menu-item-primary:hover:not(.not-clickable) {
  @apply bg-gray-100;
  transform: translateX(2px);
}

.menu-item-primary.not-clickable {
  @apply cursor-default text-gray-600 font-semibold text-xs uppercase tracking-wide;
}

.menu-item-primary.active {
  @apply bg-primary-50 text-primary-600 font-semibold;
  /* 激活状态添加更明显的视觉反馈 */
  box-shadow: inset 0 0 0 1px theme('colors.primary.100');
}

.menu-label {
  @apply flex-1;
}

.menu-arrow {
  @apply text-gray-400 text-base ml-2 transition-transform duration-200;
}

.menu-item-children {
  @apply ml-5 mt-1 pl-2 border-l-2 border-gray-200;
}

.menu-item-secondary {
  @apply px-4 py-2.5 rounded-md cursor-pointer transition-all duration-200 text-gray-500 text-xs;
  /* 添加更柔和的hover效果 */
}

.menu-item-secondary:hover {
  @apply bg-gray-100 text-gray-800;
  transform: translateX(2px);
}

.menu-item-secondary.active {
  @apply bg-primary-50 text-primary-600 font-semibold;
  /* 激活状态添加更明显的视觉反馈 */
  box-shadow: inset 0 0 0 1px theme('colors.primary.100');
}
</style>

