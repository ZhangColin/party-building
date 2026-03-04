/**
 * 集成测试：测试点击对话列表加载对话的完整流程
 * 从 ConversationList 点击到 ChatPanel 恢复会话
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { ref } from 'vue';
import { useSessionStore } from '@/stores/sessionStore';
import ConversationList from '@/components/ConversationList.vue';
import ChatPanel from '@/components/ChatPanel.vue';

// Mock sessionStore
vi.mock('@/stores/sessionStore', () => ({
  useSessionStore: vi.fn(),
}));

// Mock ApiService
vi.mock('@/services/apiClient', () => ({
  ApiService: {
    getConversations: vi.fn(),
    updateSessionTitle: vi.fn(),
    deleteSession: vi.fn(),
  },
}));

import { ApiService } from '@/services/apiClient';

describe('Conversation Click Flow Integration', () => {
  const mockConversations = [
    {
      session_id: 'session-1',
      title: 'First Conversation',
      updated_at: '2024-01-01T12:00:00Z',
    },
  ];

  const mockMessages = [
    {
      message_id: 'msg-1',
      session_id: 'session-1',
      role: 'user',
      content: 'Hello',
      created_at: '2024-01-01T12:00:00Z',
    },
    {
      message_id: 'msg-2',
      session_id: 'session-1',
      role: 'assistant',
      content: 'Hi there!',
      created_at: '2024-01-01T12:00:01Z',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(ApiService.getConversations).mockResolvedValue({
      conversations: mockConversations,
    });
  });

  it('should restore session when clicking on a conversation', async () => {
    // 创建 mock sessionStore
    // Pinia stores 自动解包 refs，所以 mock 应该返回普通值
    const mockRestoreSession = vi.fn().mockResolvedValue(undefined);
    const mockStore = {
      sessionId: null,
      toolId: null,
      messages: [],
      loading: false,
      error: null,
      titleGenerated: false,
      initTool: vi.fn(),
      sendMessage: vi.fn(),
      restoreSession: mockRestoreSession,
      clearSession: vi.fn(),
      setPreviewArtifact: vi.fn(),
      reset: vi.fn(),
      hasSession: false,
      messageCount: 0,
      showPreview: false,
      currentPreviewArtifact: null,
    };

    vi.mocked(useSessionStore).mockReturnValue(mockStore);

    // 挂载 ConversationList
    const conversationList = mount(ConversationList, {
      props: {
        toolId: 'test-tool',
      },
    });

    // 等待对话列表加载完成
    await new Promise(resolve => setTimeout(resolve, 0));
    await conversationList.vm.$nextTick();

    // 点击第一个对话
    const conversations = conversationList.findAll('.conversation-content');
    await conversations[0].trigger('click');

    // 验证 conversation-change 事件被触发
    expect(conversationList.emitted('conversation-change')).toBeTruthy();
    expect(conversationList.emitted('conversation-change')?.[0]).toEqual(['session-1']);

    // 现在挂载 ChatPanel 并传入 sessionId
    const chatPanel = mount(ChatPanel, {
      props: {
        toolId: 'test-tool',
        sessionId: 'session-1',
        messages: [],
      },
    });

    // 等待 watch 执行
    await new Promise(resolve => setTimeout(resolve, 0));
    await chatPanel.vm.$nextTick();

    // 验证 restoreSession 被调用
    expect(mockRestoreSession).toHaveBeenCalledWith('session-1');
  });

  it('should not restore session when already loading', async () => {
    // 创建 mock sessionStore，loading 为 true
    const mockRestoreSession = vi.fn().mockResolvedValue(undefined);
    const mockStore = {
      sessionId: null,
      toolId: null,
      messages: [],
      loading: true, // 正在加载
      error: null,
      titleGenerated: false,
      initTool: vi.fn(),
      sendMessage: vi.fn(),
      restoreSession: mockRestoreSession,
      clearSession: vi.fn(),
      setPreviewArtifact: vi.fn(),
      reset: vi.fn(),
      hasSession: false,
      messageCount: 0,
      showPreview: false,
      currentPreviewArtifact: null,
    };

    vi.mocked(useSessionStore).mockReturnValue(mockStore);

    // 挂载 ChatPanel 并传入 sessionId
    const chatPanel = mount(ChatPanel, {
      props: {
        toolId: 'test-tool',
        sessionId: 'session-1',
        messages: [],
      },
    });

    // 等待 watch 执行
    await new Promise(resolve => setTimeout(resolve, 0));
    await chatPanel.vm.$nextTick();

    // 验证 restoreSession 没有被调用（因为 loading=true）
    expect(mockRestoreSession).not.toHaveBeenCalled();
  });

  it('should update messages after session restore', async () => {
    // 创建 mock sessionStore
    const mockStore = {
      sessionId: 'session-1',
      toolId: 'test-tool',
      messages: [], // 初始为空
      loading: false,
      error: null,
      titleGenerated: false,
      initTool: vi.fn(),
      sendMessage: vi.fn(),
      restoreSession: vi.fn().mockImplementation(async (sessionId: string) => {
        // 模拟恢复会话后更新消息
        mockStore.messages = mockMessages;
        mockStore.sessionId = sessionId;
      }),
      clearSession: vi.fn(),
      setPreviewArtifact: vi.fn(),
      reset: vi.fn(),
      hasSession: false,
      messageCount: 0,
      showPreview: false,
      currentPreviewArtifact: null,
    };

    vi.mocked(useSessionStore).mockReturnValue(mockStore);

    // 挂载 ChatPanel
    const chatPanel = mount(ChatPanel, {
      props: {
        toolId: 'test-tool',
        sessionId: 'session-1',
        messages: [],
      },
    });

    // 等待 restoreSession 完成
    await new Promise(resolve => setTimeout(resolve, 0));
    await chatPanel.vm.$nextTick();

    // 验证 restoreSession 被调用
    expect(mockStore.restoreSession).toHaveBeenCalledWith('session-1');

    // 验证 messages 被更新
    expect(mockStore.messages).toEqual(mockMessages);
  });
});
