<template>
  <div class="agent-list" data-testid="agent-list">
    <!-- 加载状态 -->
    <div v-if="agentStore.loading" class="loading" data-testid="loading">
      加载中...
    </div>

    <!-- 错误状态 -->
    <div v-else-if="agentStore.error" class="error" data-testid="error">
      {{ agentStore.error }}
      <button @click="handleRetry">重试</button>
    </div>

    <!-- 空列表 -->
    <div v-else-if="!agentStore.hasAgents" class="empty" data-testid="empty">
      暂无 Agent
    </div>

    <!-- Agent 列表 -->
    <div v-else class="agent-items">
      <div
        v-for="agent in agentStore.agents"
        :key="agent.agent_id"
        :data-testid="`agent-item-${agent.agent_id}`"
        class="agent-item"
        @click="handleAgentClick(agent.agent_id)"
      >
        <h3 class="agent-name">{{ agent.name }}</h3>
        <p v-if="agent.description" class="agent-description">
          {{ agent.description }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAgentStore } from '../stores/agentStore'

const router = useRouter()
const agentStore = useAgentStore()

/**
 * 处理 Agent 点击
 */
function handleAgentClick(agentId: string) {
  router.push({
    name: 'agent-detail',
    params: { agentId },
  })
}

/**
 * 处理重试
 */
function handleRetry() {
  agentStore.fetchAgents()
}

/**
 * 组件挂载时获取 Agent 列表
 */
onMounted(() => {
  agentStore.fetchAgents()
})
</script>

<style scoped>
.agent-list {
  padding: 1rem;
}

.loading,
.error,
.empty {
  text-align: center;
  padding: 2rem;
}

.error {
  color: red;
}

.agent-items {
  display: grid;
  gap: 1rem;
}

.agent-item {
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.agent-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.agent-name {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.agent-description {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}
</style>

