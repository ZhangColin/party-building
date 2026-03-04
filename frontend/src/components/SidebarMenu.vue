<template>
  <div class="sidebar-menu" :class="{ collapsed: isCollapsed }">
    <div v-if="!isCollapsed" class="menu-list">
      <MenuItem
        v-for="item in menuItems"
        :key="item.id"
        :item="item"
        :active-id="activeMenuItemId"
        @click="handleMenuItemClick"
      />
    </div>
    <button class="collapse-button" @click="toggleCollapse">
      <ChevronLeftIcon v-if="!isCollapsed" class="w-4 h-4" />
      <ChevronRightIcon v-else class="w-4 h-4" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'
import MenuItem from './MenuItem.vue'

const emit = defineEmits<{
  'collapse-change': [collapsed: boolean]
}>()

// 写死的菜单数据
const menuItems = [
  { id: 'text-gen', label: '文生文' },
  { id: 'image-gen', label: '文生图' },
  { id: 'video-gen', label: '文生视频' },
  {
    id: 'agents',
    label: '智能体',
    children: [
      { id: 'prompt-wizard', label: '提示词向导' },
      { id: 'lyar', label: 'Lyar' },
    ],
  },
]

const activeMenuItemId = ref<string | null>('prompt-wizard')
const isCollapsed = ref(false)

function handleMenuItemClick(itemId: string) {
  activeMenuItemId.value = itemId
}

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
  emit('collapse-change', isCollapsed.value)
}
</script>

<style scoped>
.sidebar-menu {
  height: 100%;
  position: relative;
  transition: width 0.3s;
  /* 层级1：容器层 - 继承父容器的浅灰背景 */
}

.sidebar-menu.collapsed {
  width: 0;
  overflow: hidden;
}

.menu-list {
  padding: 16px 12px; /* 从12px 8px增加到16px 12px，更宽松 */
  height: 100%;
  overflow-y: auto;
}

.collapse-button {
  @apply absolute top-3 -right-4 w-8 h-8 bg-white border border-gray-200 rounded-full cursor-pointer flex items-center justify-center text-gray-500 z-10 transition-all duration-200;
  /* 层级3：交互层 - 白色背景，明显阴影 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
}

.collapse-button:hover {
  @apply bg-gray-50 text-gray-800;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>

