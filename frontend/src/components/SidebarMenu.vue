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
  /* 党建主题：淡红色背景 */
  background: linear-gradient(180deg, rgba(200, 16, 46, 0.03) 0%, rgba(139, 0, 0, 0.05) 100%);
  border-right: 1px solid rgba(200, 16, 46, 0.1);
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
  @apply absolute top-3 -right-4 w-8 h-8 rounded-full cursor-pointer flex items-center justify-center z-10 transition-all duration-200;
  /* 党建主题：白色背景 + 金色边框 */
  background: white;
  border: 1px solid #FFD700;
  color: #C8102E;
  box-shadow: 0 2px 8px rgba(200, 16, 46, 0.15);
}

.collapse-button:hover {
  background: #FFF5E6;
  border-color: #C8102E;
  box-shadow: 0 4px 12px rgba(200, 16, 46, 0.25);
}
</style>

