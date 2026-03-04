<template>
  <div class="media-chat-view">
    <MediaChatInterface
      v-if="tool"
      :tool-id="tool.tool_id"
      :tool-name="tool.name"
      :welcome-message="tool.welcome_message || '你好！'"
    />
    <div v-else class="loading-view">
      <p>加载中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import MediaChatInterface from '../components/media/MediaChatInterface.vue'
import type { ToolListItem } from '../types'
import apiClient from '../services/apiClient'

const route = useRoute()
const tool = ref<ToolListItem | null>(null)

onMounted(async () => {
  const toolId = route.params.toolId as string
  
  try {
    // 获取工具信息
    // TODO: 优化为从store获取，避免重复请求
    const response = await apiClient.get('/tools')
    const data = response.data
    
    // 从所有工具中查找
    for (const category of data.categories) {
      const found = category.tools.find((t: ToolListItem) => t.tool_id === toolId)
      if (found) {
        tool.value = found
        break
      }
    }
    
    if (!tool.value) {
      console.error('工具不存在:', toolId)
      // TODO: 跳转到404或工具列表
    }
    
  } catch (error) {
    console.error('加载工具信息失败:', error)
  }
})
</script>

<style scoped>
.media-chat-view {
  height: 100vh;
  background: #f9fafb;
}

.loading-view {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  font-size: 16px;
  color: #6b7280;
}
</style>
