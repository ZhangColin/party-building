<template>
  <div
    class="message-item"
    :class="messageClass"
    data-testid="message-item"
    :data-role="message.role"
    @mouseenter="showToolbar = true"
    @mouseleave="showToolbar = false"
  >
    <!-- 隐藏头像，保持简洁 -->
    <div class="message-avatar" style="display: none;">
      <img
        :src="avatarUrl"
        :alt="message.role"
        class="avatar-image"
        data-testid="message-avatar"
      />
    </div>

    <div class="message-content">
      <!-- 消息附件展示 -->
      <div
        v-if="message.attachments && message.attachments.length > 0"
        class="message-attachments"
      >
        <div
          v-for="attachment in message.attachments"
          :key="attachment.id"
          class="message-attachment"
        >
          <DocumentIcon class="attachment-icon" />
          <span class="attachment-name">{{ attachment.name }}</span>
          <span class="attachment-type">{{ getAttachmentTypeLabel(attachment.type) }}</span>
        </div>
      </div>

      <div
        class="message-text"
        :class="{ 'markdown-content': message.role === 'assistant', 'user-text': message.role === 'user' }"
        v-html="renderedContent"
        data-testid="message-text"
      />
      <div class="message-footer">
        <div
          class="message-toolbar"
          :class="{ 'toolbar-visible': showToolbar }"
        >
          <button
            class="copy-button"
            @click="handleCopy"
            title="复制"
            data-testid="copy-button"
          >
            <DocumentDuplicateIcon />
          </button>

          <!-- 只在 AI 消息时显示保存按钮 -->
          <template v-if="message.role === 'assistant'">
            <button
              class="save-button"
              @click="handleSaveToKnowledge"
              title="保存到知识库"
            >
              <FolderIcon />
            </button>
            <button
              class="save-button"
              @click="handleSaveToParty"
              title="保存到党建活动"
            >
              <FlagIcon />
            </button>
          </template>
        </div>
        <div class="message-time" data-testid="message-time">
          {{ formattedTime }}
        </div>
      </div>
    </div>

    <!-- 保存对话框 -->
    <SaveToDialog
      v-model="showSaveToKnowledge"
      target="knowledge"
      :content="message.content"
      :categories="knowledgeCategories"
      :session-title="sessionTitle"
      :force-refresh="forceRefreshCategories"
      @saved="handleSaved"
    />
    <SaveToDialog
      v-model="showSaveToParty"
      target="party"
      :content="message.content"
      :categories="partyCategories"
      :session-title="sessionTitle"
      :force-refresh="forceRefreshCategories"
      @saved="handleSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import {
  DocumentDuplicateIcon,
  DocumentIcon,
  FolderIcon,
  FlagIcon
} from '@heroicons/vue/24/outline';
import { renderMarkdown } from '@/utils/markdownRenderer';
import { useClipboard } from '@/composables/useClipboard';
import type { Message, MessageAttachment } from '@/types';
import SaveToDialog from './SaveToDialog.vue';
import * as knowledgeApi from '@/services/knowledgeApi';
import * as partyActivityApi from '@/services/partyActivityApi';
import type { Category } from '@/types/file-manager';

interface Props {
  message: Message;
  sessionTitle?: string;
}

const props = defineProps<Props>();

const showToolbar = ref(false);
const { copy } = useClipboard();

// 保存对话框状态
const showSaveToKnowledge = ref(false);
const showSaveToParty = ref(false);
const knowledgeCategories = ref<Category[]>([]);
const partyCategories = ref<Category[]>([]);

// 强制刷新目录缓存的函数
async function forceRefreshCategories(target: 'knowledge' | 'party') {
  if (target === 'knowledge') {
    knowledgeCategories.value = await knowledgeApi.getCategoryTree();
  } else {
    partyCategories.value = await partyActivityApi.getCategoryTree();
  }
}

const messageClass = computed(() => {
  return `message-${props.message.role}`;
});

const avatarUrl = computed(() => {
  return props.message.role === 'user'
    ? '/images/user-avatar.png'
    : '/images/ai-avatar.png';
});

const renderedContent = computed(() => {
  if (props.message.role === 'assistant') {
    return renderMarkdown(props.message.content);
  }
  return props.message.content;
});

const formattedTime = computed(() => {
  if (!props.message.created_at) return '';
  const date = new Date(props.message.created_at);
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  });
});

/**
 * 获取附件类型标签
 */
const getAttachmentTypeLabel = (type: MessageAttachment['type']): string => {
  const labels: Record<MessageAttachment['type'], string> = {
    temp: '本地文件',
    knowledge: '知识库',
    party: '党建活动'
  };
  return labels[type];
};

async function handleCopy() {
  await copy(props.message.content);
}

// 加载知识库目录树
async function loadKnowledgeCategories() {
  if (knowledgeCategories.value.length > 0) return;
  try {
    knowledgeCategories.value = await knowledgeApi.getCategoryTree();
  } catch (error) {
    console.error('加载知识库目录失败:', error);
  }
}

// 加载党建活动目录树
async function loadPartyCategories() {
  if (partyCategories.value.length > 0) return;
  try {
    partyCategories.value = await partyActivityApi.getCategoryTree();
  } catch (error) {
    console.error('加载党建活动目录失败:', error);
  }
}

// 保存到知识库
async function handleSaveToKnowledge() {
  await loadKnowledgeCategories();
  showSaveToKnowledge.value = true;
}

// 保存到党建活动
async function handleSaveToParty() {
  await loadPartyCategories();
  showSaveToParty.value = true;
}

// 保存成功回调
function handleSaved(path: string) {
  console.log('已保存到:', path);
}
</script>

<style scoped>
@import '@/styles/markdown.css';

.message-item {
  display: flex;
  gap: 0;
  margin-bottom: 16px;
  animation: fadeIn 0.3s ease-in;
  position: relative;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.avatar-image {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  /* 默认（AI消息）使用完整宽度 */
  max-width: 100%;
}

.message-user .message-content {
  align-items: flex-end;
  /* 用户消息限制宽度 */
  max-width: 70%;
}

/* 消息附件样式 */
.message-attachments {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 6px;
}

.message-attachment {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background-color: rgba(255, 255, 255, 0.9);
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 13px;
}

.message-user .message-attachment {
  background-color: rgba(255, 255, 255, 0.95);
  border-color: rgba(200, 16, 46, 0.3);
  color: #333;
}

.attachment-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

.message-user .attachment-icon {
  color: #C8102E;
}

.attachment-name {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attachment-type {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  background-color: #f0f0f0;
  color: #666;
}

.message-user .attachment-type {
  background-color: #f0f0f0;
  color: #C8102E;
  font-weight: 500;
}

.message-text {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
}

.message-user .message-text {
  /* 党建主题：用户消息气泡样式 */
  background: linear-gradient(135deg, #C8102E 0%, #8B0000 100%);
  color: white;
}

.message-assistant .message-text {
  background-color: #f5f5f5;
  color: #333;
}

/* 用户消息保留原始换行 */
.user-text {
  white-space: pre-wrap;
}

/* Assistant messages use markdown-content class for rich formatting */
/* 移除 overflow-x: auto，使代码块的 sticky 定位能够相对于整个页面工作 */
.message-assistant .message-text {
  /* overflow-x: auto; - 已移除 */
}

.message-time {
  font-size: 12px;
  color: #999;
  padding: 0 4px;
}

.message-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  min-height: 20px;
}

.message-assistant .message-footer {
  flex-direction: row;
}

.message-user .message-footer {
  flex-direction: row-reverse;
}

.message-toolbar {
  display: flex;
  gap: 4px;
  /* 固定高度，避免显示时抖动 */
  height: 28px;
  min-height: 28px;
  /* 默认隐藏但保持占位 */
  visibility: hidden;
  opacity: 0;
  transition: opacity 0.2s;
}

.message-toolbar.toolbar-visible {
  visibility: visible;
  opacity: 1;
}

.copy-button {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: #999;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  padding: 0;
}

.copy-button:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #666;
}

.copy-button svg {
  width: 16px;
  height: 16px;
}

.save-button {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: #999;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  padding: 0;
}

.save-button:hover {
  background: rgba(200, 16, 46, 0.1);
  color: #C8102E;
}

.save-button svg {
  width: 16px;
  height: 16px;
}
</style>
