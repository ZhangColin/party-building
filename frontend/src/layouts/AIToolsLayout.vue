<template>
  <div class="ai-tools-layout">
    <!-- 左侧：AI工具选择器 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <AIToolSelector 
        :collapsed="sidebarCollapsed"
        @collapse-change="handleSidebarCollapse" 
        @tool-change="handleToolChange" 
      />
    </aside>
    
    <!-- 收起/展开按钮 - 始终显示在布局层级 -->
    <button 
      class="collapse-button" 
      :class="{ 'collapsed': sidebarCollapsed }"
      @click="toggleSidebar"
    >
      <ChevronLeftIcon v-if="!sidebarCollapsed" class="w-4 h-4" />
      <SparklesIcon v-else class="w-4 h-4" />
    </button>
    
    <!-- 右侧：聊天区域或敬请期待页面 -->
    <!-- 文本工具：使用 ChatArea -->
    <ChatArea 
      v-if="currentTool && currentTool.type === 'normal' && currentTool.content_type === 'text'" 
      :tool-id="currentTool.tool_id"
      :welcome-message="currentTool.welcome_message"
      class="chat-area" 
    />
    
    <!-- 多模态工具：使用 MediaChatArea -->
    <MediaChatArea
      v-else-if="currentTool && currentTool.type === 'normal' && currentTool.content_type === 'multimodal'"
      :tool-id="currentTool.tool_id"
      :tool-name="currentTool.name"
      :welcome-message="currentTool.welcome_message || '你好！'"
      class="chat-area"
    />
    
    <!-- 占位工具：显示敬请期待 -->
    <ComingSoon 
      v-else-if="currentTool && currentTool.type === 'placeholder'"
      :tool-name="currentTool.name"
      :welcome-message="currentTool.welcome_message"
      :icon="currentTool.icon"
      class="chat-area"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ChevronLeftIcon, SparklesIcon } from '@heroicons/vue/24/outline'
import AIToolSelector from '../components/AIToolSelector.vue'
import ChatArea from '../components/ChatArea.vue'
import MediaChatArea from '../components/MediaChatArea.vue'
import ComingSoon from '../components/ComingSoon.vue'
import type { ToolListItem } from '../types'

const sidebarCollapsed = ref(false)
const currentTool = ref<ToolListItem | null>(null)

function handleSidebarCollapse(collapsed: boolean) {
  sidebarCollapsed.value = collapsed
}

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

function handleToolChange(tool: ToolListItem) {
  // 所有工具都在当前Layout中显示
  currentTool.value = tool
}
</script>

<style scoped>
.ai-tools-layout {
  @apply flex h-full overflow-hidden;
  position: relative; /* 为按钮提供定位上下文 */
}

.sidebar {
  @apply flex-shrink-0 border-r border-gray-200 overflow-y-auto transition-all duration-300 ease-in-out;
  /* 层级1：容器层 - 浅灰背景，右侧阴影，工具选择器区域 */
  width: 260px; /* 恢复原来的宽度 */
  background-color: theme('colors.gray.50');
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.04);
}

.sidebar.collapsed {
  @apply w-0 border-r-0;
  overflow-x: visible; /* 允许按钮显示 */
  overflow-y: hidden;
}

.chat-area {
  @apply flex-1 min-w-0 bg-white;
}

/* 收起/展开按钮 - 在布局层级，不受 sidebar overflow 影响 */
.collapse-button {
  @apply absolute top-3 w-8 h-8 bg-white border border-gray-200 rounded-full cursor-pointer flex items-center justify-center text-gray-500 z-30 transition-all duration-200;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  left: 244px; /* 展开时：sidebar宽度260px - 按钮宽度的一半 */
}

.collapse-button.collapsed {
  left: 8px; /* 收起时在左侧边缘 */
}

.collapse-button:hover {
  @apply bg-gray-50 text-gray-800;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 平板端响应式（768px - 1023px） */
@media (min-width: 768px) and (max-width: 1023px) {
  .sidebar {
    width: 260px; /* 平板端保持较宽，确保卡片布局舒适 */
  }
  
  .sidebar.collapsed {
    width: 0;
  }
}

/* 移动端响应式（<768px） */
@media (max-width: 767px) {
  .sidebar {
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    z-index: 40;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
  
  .sidebar.collapsed {
    width: 240px;
    transform: translateX(-100%);
  }
}
</style>

