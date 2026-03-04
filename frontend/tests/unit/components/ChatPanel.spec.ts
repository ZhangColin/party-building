/**
 * ChatPanel组件单元测试
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { ref } from 'vue';
import { useSessionStore } from '@/stores/sessionStore';
import ChatPanel from '@/components/ChatPanel.vue';
import type { Message } from '@/types';

// Mock sessionStore
vi.mock('@/stores/sessionStore', () => ({
  useSessionStore: vi.fn(),
}));

// 辅助函数：创建默认的 mock sessionStore
// 注意：Pinia stores 会自动解包 refs，所以 mock 应该返回普通值而非 ref 对象
function createMockSessionStore() {
  return {
    sessionId: null,
    toolId: null,
    messages: [],
    loading: false,  // 返回普通值，而不是 ref
    error: null,
    titleGenerated: false,
    initTool: vi.fn(),
    sendMessage: vi.fn(),
    restoreSession: vi.fn().mockResolvedValue(undefined),
    clearSession: vi.fn(),
    setPreviewArtifact: vi.fn(),
    reset: vi.fn(),
    hasSession: false,
    messageCount: 0,
    showPreview: false,
    currentPreviewArtifact: null,
  };
}

describe('ChatPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // 设置默认 mock
    vi.mocked(useSessionStore).mockReturnValue(createMockSessionStore());
  });
  // 测试修复：messages属性应该有默认值，避免"Cannot read properties of undefined"错误
  it('should have default messages prop as empty array', () => {
    const wrapper = mount(ChatPanel, {
      props: {
        toolId: 'test-tool'
      }
    })

    // 验证messages属性有默认值，不会抛出undefined错误
    expect(wrapper.props()).toHaveProperty('messages')
    expect(wrapper.vm.messages).toEqual([])
  })

  // 测试修复：ChatPanel可以在不传递messages prop的情况下正常渲染
  it('should render without errors when messages not provided', () => {
    // 修复前：会因为messages为undefined而导致子组件错误
    const wrapper = mount(ChatPanel, {
      props: {
        toolId: 'test-tool'
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('[data-testid="chat-panel"]').exists()).toBe(true)
  })

  it('should render MessageList and ChatInput', () => {
    const wrapper = mount(ChatPanel, {
      props: {
        messages: [],
      },
    });

    expect(wrapper.findComponent({ name: 'MessageList' }).exists()).toBe(true);
    expect(wrapper.findComponent({ name: 'ChatInput' }).exists()).toBe(true);
  });

  it('should pass messages to MessageList', () => {
    const messages: Message[] = [
      {
        message_id: '1',
        session_id: '1',
        role: 'user',
        content: 'Hello',
        created_at: '2024-01-01T12:00:00Z',
      },
    ];

    const wrapper = mount(ChatPanel, {
      props: {
        messages,
      },
    });

    const messageList = wrapper.findComponent({ name: 'MessageList' });
    expect(messageList.props('messages')).toEqual(messages);
  });

  it('should pass streamingContent to MessageList', () => {
    const wrapper = mount(ChatPanel, {
      props: {
        messages: [],
        streamingContent: 'Streaming...',
      },
    });

    const messageList = wrapper.findComponent({ name: 'MessageList' });
    expect(messageList.props('streamingContent')).toBe('Streaming...');
  });

  it('should emit send event when ChatInput sends', async () => {
    const wrapper = mount(ChatPanel, {
      props: {
        messages: [],
      },
    });

    const chatInput = wrapper.findComponent({ name: 'ChatInput' });
    await chatInput.vm.$emit('send', 'Hello');

    expect(wrapper.emitted('send')).toBeTruthy();
    expect(wrapper.emitted('send')?.[0]).toEqual(['Hello']);
  });

  it('should pass disabled to ChatInput', () => {
    const wrapper = mount(ChatPanel, {
      props: {
        messages: [],
        disabled: true,
      },
    });

    const chatInput = wrapper.findComponent({ name: 'ChatInput' });
    expect(chatInput.props('disabled')).toBe(true);
  });

  it('should pass isLoading to ChatInput', () => {
    const wrapper = mount(ChatPanel, {
      props: {
        messages: [],
        isLoading: true,
      },
    });

    const chatInput = wrapper.findComponent({ name: 'ChatInput' });
    expect(chatInput.props('isLoading')).toBe(true);
  });

  it('should expose focusInput method', () => {
    const wrapper = mount(ChatPanel, {
      props: {
        messages: [],
      },
    });

    expect(typeof (wrapper.vm as any).focusInput).toBe('function');
  });

  it('should expose scrollToBottom method', () => {
    const wrapper = mount(ChatPanel, {
      props: {
        messages: [],
      },
    });

    expect(typeof (wrapper.vm as any).scrollToBottom).toBe('function');
  });

  // ========== 测试错误处理 UI ==========
  describe('Error Handling', () => {
    it('should show error message when error exists', () => {
      const wrapper = mount(ChatPanel, {
        props: {
          messages: [],
          error: '网络错误'
        }
      })

      expect(wrapper.text()).toContain('网络错误')
      expect(wrapper.find('.error-message').exists()).toBe(true)
    })

    it('should not show error when no error', () => {
      const wrapper = mount(ChatPanel, {
        props: {
          messages: [],
          error: undefined
        }
      })

      expect(wrapper.find('.error-message').exists()).toBe(false)
    })

    it('should emit retry event when retry button clicked', async () => {
      const wrapper = mount(ChatPanel, {
        props: {
          messages: [],
          error: '网络错误'
        }
      })

      await wrapper.find('.retry-button').trigger('click')

      expect(wrapper.emitted('retry')).toBeTruthy()
      expect(wrapper.emitted('retry')?.[0]).toEqual([])
    })

    it('should display error icon and title', () => {
      const wrapper = mount(ChatPanel, {
        props: {
          messages: [],
          error: '连接失败'
        }
      })

      expect(wrapper.find('.error-icon').exists()).toBe(true)
      expect(wrapper.text()).toContain('出错了')
      expect(wrapper.text()).toContain('连接失败')
    })
  });

  // ========== 测试会话恢复功能（防止回归） ==========
  describe('Session Restoration', () => {
    it('should call sessionStore.restoreSession when sessionId prop changes', async () => {
      const mockRestoreSession = vi.fn().mockResolvedValue(undefined);
      const mockStore = createMockSessionStore();
      mockStore.restoreSession = mockRestoreSession;

      vi.mocked(useSessionStore).mockReturnValue(mockStore);

      const wrapper = mount(ChatPanel, {
        props: {
          toolId: 'test-tool',
          sessionId: undefined,
        },
      });

      // 设置 sessionId
      await wrapper.setProps({ sessionId: 'session-123' });

      // 等待 watch 执行
      await wrapper.vm.$nextTick();
      await new Promise(resolve => setTimeout(resolve, 0));

      // 验证 restoreSession 被调用
      expect(mockRestoreSession).toHaveBeenCalledWith('session-123');
      expect(mockRestoreSession).toHaveBeenCalledTimes(1);
    });

    it('should not call restoreSession when loading is true', async () => {
      const mockRestoreSession = vi.fn().mockResolvedValue(undefined);
      const mockStore = createMockSessionStore();
      mockStore.loading = ref(true); // 正在加载
      mockStore.restoreSession = mockRestoreSession;

      vi.mocked(useSessionStore).mockReturnValue(mockStore);

      const wrapper = mount(ChatPanel, {
        props: {
          toolId: 'test-tool',
        },
      });

      // 设置 sessionId
      await wrapper.setProps({ sessionId: 'session-456' });

      // 等待 watch 执行
      await wrapper.vm.$nextTick();
      await new Promise(resolve => setTimeout(resolve, 0));

      // 验证 restoreSession 没有被调用（因为 loading=true）
      expect(mockRestoreSession).not.toHaveBeenCalled();
    });

    it('should call sessionStore.initTool when toolId prop changes', async () => {
      const mockInitTool = vi.fn();
      const mockStore = createMockSessionStore();
      mockStore.initTool = mockInitTool;

      vi.mocked(useSessionStore).mockReturnValue(mockStore);

      const wrapper = mount(ChatPanel, {
        props: {
          toolId: 'tool-a',
        },
      });

      // 等待 watch 执行（immediate: true）
      await wrapper.vm.$nextTick();

      // 验证 initTool 被调用
      expect(mockInitTool).toHaveBeenCalledWith('tool-a');
    });

    it('should handle restoreSession errors gracefully', async () => {
      const mockError = new Error('Network error');
      const mockRestoreSession = vi.fn().mockRejectedValue(mockError);
      const mockStore = createMockSessionStore();
      mockStore.restoreSession = mockRestoreSession;

      vi.mocked(useSessionStore).mockReturnValue(mockStore);

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      const wrapper = mount(ChatPanel, {
        props: {
          toolId: 'test-tool',
        },
      });

      // 设置 sessionId
      await wrapper.setProps({ sessionId: 'session-789' });

      // 等待 watch 执行
      await wrapper.vm.$nextTick();
      await new Promise(resolve => setTimeout(resolve, 0));

      // 验证错误被记录
      expect(consoleSpy).toHaveBeenCalledWith(
        '[ChatPanel] Failed to restore session:',
        mockError
      );

      consoleSpy.mockRestore();
    });
  });
});
