/** Agent Store - 管理 Agent 列表状态 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ApiService } from '../services/apiClient'
import type { AgentListItem } from '../types'

export const useAgentStore = defineStore('agent', () => {
  // 状态
  const agents = ref<AgentListItem[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const agentCount = computed(() => agents.value.length)
  const hasAgents = computed(() => agents.value.length > 0)

  /**
   * 获取 Agent 列表
   */
  async function fetchAgents() {
    loading.value = true
    error.value = null
    try {
      const response = await ApiService.getAgents()
      agents.value = response.agents
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取 Agent 列表失败'
      agents.value = []
    } finally {
      loading.value = false
    }
  }

  /**
   * 根据 agent_id 获取 Agent
   */
  function getAgentById(agentId: string): AgentListItem | undefined {
    return agents.value.find((agent) => agent.agent_id === agentId)
  }

  /**
   * 重置状态
   */
  function reset() {
    agents.value = []
    loading.value = false
    error.value = null
  }

  return {
    // 状态
    agents,
    loading,
    error,
    // 计算属性
    agentCount,
    hasAgents,
    // 方法
    fetchAgents,
    getAgentById,
    reset,
  }
})

