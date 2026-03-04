<template>
  <div class="agent-list-view">
    <h1 class="page-title">AI Agent 列表</h1>
    <AgentList />
  </div>
</template>

<script setup lang="ts">
import AgentList from '../components/AgentList.vue'
</script>

<style scoped>
.agent-list-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-title {
  margin-bottom: 2rem;
  font-size: 2rem;
  font-weight: 700;
}
</style>

