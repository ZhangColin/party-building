<template>
  <div class="agent-detail-view">
    <ChatInterface :agent-id="agentId" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ChatInterface from '../components/ChatInterface.vue'

const route = useRoute()
const agentId = computed(() => route.params.agentId as string)
</script>

<style scoped>
.agent-detail-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>

