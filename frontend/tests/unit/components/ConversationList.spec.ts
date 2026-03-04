/**
 * ConversationList组件单元测试
 * 测试聊天记录点击和预览功能
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { ref } from 'vue';
import ConversationList from '@/components/ConversationList.vue';
import { ApiService } from '@/services/apiClient';

// Mock ApiService
vi.mock('@/services/apiClient', () => ({
  ApiService: {
    getConversations: vi.fn(),
    updateSessionTitle: vi.fn(),
    deleteSession: vi.fn(),
  },
}));

describe('ConversationList', () => {
  const mockConversations = [
    {
      session_id: 'session-1',
      title: 'First Conversation',
      updated_at: '2024-01-01T12:00:00Z',
    },
    {
      session_id: 'session-2',
      title: 'Second Conversation',
      updated_at: '2024-01-02T14:30:00Z',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(ApiService.getConversations).mockResolvedValue({
      conversations: mockConversations,
    });
  });

  it('should load conversations on mount with toolId', async () => {
    const wrapper = mount(ConversationList, {
      props: {
        toolId: 'test-tool',
      },
    });

    // 等待异步操作完成
    await new Promise(resolve => setTimeout(resolve, 0));
    await wrapper.vm.$nextTick();

    expect(ApiService.getConversations).toHaveBeenCalledWith('test-tool');
  });

  it('should emit conversation-change when clicking on a conversation', async () => {
    const wrapper = mount(ConversationList, {
      props: {
        toolId: 'test-tool',
      },
    });

    // 等待加载完成
    await new Promise(resolve => setTimeout(resolve, 0));
    await wrapper.vm.$nextTick();

    // 点击第一个对话
    const firstConversation = wrapper.findAll('.conversation-content')[0];
    await firstConversation.trigger('click');

    // 验证事件被触发
    expect(wrapper.emitted('conversation-change')).toBeTruthy();
    expect(wrapper.emitted('conversation-change')?.[0]).toEqual(['session-1']);
  });

  it('should emit new-conversation when clicking new conversation button', async () => {
    const wrapper = mount(ConversationList, {
      props: {
        toolId: 'test-tool',
      },
    });

    const newButton = wrapper.find('.new-conversation-btn');
    await newButton.trigger('click');

    expect(wrapper.emitted('new-conversation')).toBeTruthy();
  });

  it('should show conversation actions on hover', async () => {
    const wrapper = mount(ConversationList, {
      props: {
        toolId: 'test-tool',
      },
    });

    // 等待加载完成
    await new Promise(resolve => setTimeout(resolve, 0));
    await wrapper.vm.$nextTick();

    const firstItem = wrapper.find('.conversation-item');
    expect(firstItem.find('.conversation-actions').exists()).toBe(false);

    // 触发 hover
    await firstItem.trigger('mouseenter');
    await wrapper.vm.$nextTick();

    expect(firstItem.find('.conversation-actions').exists()).toBe(true);
  });

  it('should enter edit mode when clicking edit button', async () => {
    const wrapper = mount(ConversationList, {
      props: {
        toolId: 'test-tool',
      },
    });

    // 等待加载完成
    await new Promise(resolve => setTimeout(resolve, 0));
    await wrapper.vm.$nextTick();

    const firstItem = wrapper.find('.conversation-item');
    await firstItem.trigger('mouseenter');
    await wrapper.vm.$nextTick();

    const editButton = firstItem.find('.edit-btn');
    await editButton.trigger('click');
    await wrapper.vm.$nextTick();

    // 应该显示输入框而不是标题
    expect(firstItem.find('.conversation-title-input').exists()).toBe(true);
    expect(firstItem.find('.conversation-title').exists()).toBe(false);
  });

  it('should show delete confirmation when clicking delete button', async () => {
    const wrapper = mount(ConversationList, {
      props: {
        toolId: 'test-tool',
      },
    });

    // 等待加载完成
    await new Promise(resolve => setTimeout(resolve, 0));
    await wrapper.vm.$nextTick();

    const firstItem = wrapper.find('.conversation-item');
    await firstItem.trigger('mouseenter');
    await wrapper.vm.$nextTick();

    const deleteButton = firstItem.find('.delete-btn');
    await deleteButton.trigger('click');
    await wrapper.vm.$nextTick();

    // 应该显示删除确认对话框
    expect(wrapper.find('.delete-confirm-overlay').exists()).toBe(true);
    expect(wrapper.text()).toContain('确认删除');
    expect(wrapper.text()).toContain('First Conversation');
  });

  it('should call deleteSession when confirming delete', async () => {
    vi.mocked(ApiService.deleteSession).mockResolvedValue(undefined);

    const wrapper = mount(ConversationList, {
      props: {
        toolId: 'test-tool',
      },
    });

    // 等待加载完成
    await new Promise(resolve => setTimeout(resolve, 0));
    await wrapper.vm.$nextTick();

    // 触发删除流程
    const firstItem = wrapper.find('.conversation-item');
    await firstItem.trigger('mouseenter');
    await wrapper.vm.$nextTick();

    await firstItem.find('.delete-btn').trigger('click');
    await wrapper.vm.$nextTick();

    // 点击确认删除
    const confirmButton = wrapper.find('.delete-confirm-btn');
    await confirmButton.trigger('click');
    await new Promise(resolve => setTimeout(resolve, 0));
    await wrapper.vm.$nextTick();

    expect(ApiService.deleteSession).toHaveBeenCalledWith('session-1');
  });

  it('should format time correctly for today', () => {
    const wrapper = mount(ConversationList, {
      props: {
        toolId: 'test-tool',
      },
    });

    const today = new Date();
    const timestamp = today.toISOString();

    // 调用内部方法测试时间格式化
    const formattedTime = (wrapper.vm as any).formatTime(timestamp);

    // 今天应该显示时间，格式为 HH:MM
    expect(formattedTime).toMatch(/\d{2}:\d{2}/);
  });

  it('should reload conversations when toolId changes', async () => {
    const wrapper = mount(ConversationList, {
      props: {
        toolId: 'tool-a',
      },
    });

    // 等待首次加载
    await new Promise(resolve => setTimeout(resolve, 0));
    await wrapper.vm.$nextTick();

    expect(ApiService.getConversations).toHaveBeenCalledWith('tool-a');
    expect(ApiService.getConversations).toHaveBeenCalledTimes(1);

    // 切换工具
    await wrapper.setProps({ toolId: 'tool-b' });
    await new Promise(resolve => setTimeout(resolve, 0));
    await wrapper.vm.$nextTick();

    expect(ApiService.getConversations).toHaveBeenCalledWith('tool-b');
    expect(ApiService.getConversations).toHaveBeenCalledTimes(2);
  });

  describe('active state', () => {
    it('should mark conversation as active when clicked', async () => {
      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      // 等待加载完成
      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      const conversations = wrapper.findAll('.conversation-item');

      // 初始状态：没有激活的对话
      expect(conversations[0].classes()).not.toContain('active');
      expect(conversations[1].classes()).not.toContain('active');

      // 点击第一个对话
      await conversations[0].find('.conversation-content').trigger('click');
      await wrapper.vm.$nextTick();

      // 第一个对话应该被激活
      const updatedConversations = wrapper.findAll('.conversation-item');
      expect(updatedConversations[0].classes()).toContain('active');
      expect(updatedConversations[1].classes()).not.toContain('active');
    });

    it('should switch active conversation when clicking another', async () => {
      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      // 等待加载完成
      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      const conversations = wrapper.findAll('.conversation-item');

      // 点击第一个对话
      await conversations[0].find('.conversation-content').trigger('click');
      await wrapper.vm.$nextTick();

      // 点击第二个对话
      await conversations[1].find('.conversation-content').trigger('click');
      await wrapper.vm.$nextTick();

      // 第二个对话应该被激活
      const updatedConversations = wrapper.findAll('.conversation-item');
      expect(updatedConversations[0].classes()).not.toContain('active');
      expect(updatedConversations[1].classes()).toContain('active');
    });
  });

  describe('collapsed state', () => {
    it('should be collapsible when collapsed prop is true', () => {
      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
          collapsed: true,
        },
      });

      expect(wrapper.find('.conversation-list').classes()).toContain('collapsed');
    });

    it('should toggle collapse when clicking collapse button', async () => {
      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
          collapsed: false,
        },
      });

      const collapseButton = wrapper.find('.collapse-button');
      expect(collapseButton.exists()).toBe(true);

      // 点击收起按钮
      await collapseButton.trigger('click');
      await wrapper.vm.$nextTick();

      expect(wrapper.find('.conversation-list').classes()).toContain('collapsed');

      // 再次点击展开
      await collapseButton.trigger('click');
      await wrapper.vm.$nextTick();

      expect(wrapper.find('.conversation-list').classes()).not.toContain('collapsed');
    });

    it('should sync with external collapsed prop changes', async () => {
      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
          collapsed: false,
        },
      });

      expect(wrapper.find('.conversation-list').classes()).not.toContain('collapsed');

      // 外部改变collapsed prop
      await wrapper.setProps({ collapsed: true });
      await wrapper.vm.$nextTick();

      expect(wrapper.find('.conversation-list').classes()).toContain('collapsed');
    });
  });

  describe('error handling', () => {
    it('should handle loading conversations error', async () => {
      vi.mocked(ApiService.getConversations).mockRejectedValueOnce(
        new Error('网络错误')
      );

      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      // 等待异步操作完成
      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      // 应该显示错误状态
      expect(wrapper.find('.error-state').exists()).toBe(true);
      expect(wrapper.text()).toContain('网络错误');
    });

    it('should handle invalid response', async () => {
      vi.mocked(ApiService.getConversations).mockResolvedValueOnce({} as any);

      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      // 应该显示空状态
      expect(wrapper.find('.empty-state').exists()).toBe(true);
      expect(wrapper.text()).toContain('暂无对话');
    });

    it('should handle delete conversation error', async () => {
      vi.mocked(ApiService.deleteSession).mockRejectedValueOnce(
        new Error('删除失败')
      );

      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      // 触发删除流程
      const firstItem = wrapper.find('.conversation-item');
      await firstItem.trigger('mouseenter');
      await wrapper.vm.$nextTick();

      await firstItem.find('.delete-btn').trigger('click');
      await wrapper.vm.$nextTick();

      // 点击确认删除
      const confirmButton = wrapper.find('.delete-confirm-btn');
      await confirmButton.trigger('click');
      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      // 应该显示错误状态
      expect(wrapper.find('.error-state').exists()).toBe(true);
      expect(wrapper.text()).toContain('删除失败');
    });

    it('should handle update title error', async () => {
      vi.mocked(ApiService.updateSessionTitle).mockRejectedValueOnce(
        new Error('更新失败')
      );

      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      // 进入编辑模式
      const firstItem = wrapper.find('.conversation-item');
      await firstItem.trigger('mouseenter');
      await wrapper.vm.$nextTick();

      await firstItem.find('.edit-btn').trigger('click');
      await wrapper.vm.$nextTick();

      // 修改标题并保存
      const input = firstItem.find('.conversation-title-input');
      await input.setValue('New Title');
      await input.trigger('blur');
      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      // 应该显示错误状态
      expect(wrapper.find('.error-state').exists()).toBe(true);
      expect(wrapper.text()).toContain('更新失败');
    });
  });

  describe('edit functionality', () => {
    it('should save title when pressing Enter', async () => {
      vi.mocked(ApiService.updateSessionTitle).mockResolvedValueOnce(undefined);

      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      const firstItem = wrapper.find('.conversation-item');
      await firstItem.trigger('mouseenter');
      await wrapper.vm.$nextTick();

      await firstItem.find('.edit-btn').trigger('click');
      await wrapper.vm.$nextTick();

      const input = firstItem.find('.conversation-title-input');
      await input.setValue('Updated Title');
      await input.trigger('keyup', { key: 'Enter' });
      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      expect(ApiService.updateSessionTitle).toHaveBeenCalledWith('session-1', {
        title: 'Updated Title',
      });
    });

    it('should cancel edit when pressing Escape', async () => {
      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      const firstItem = wrapper.find('.conversation-item');
      await firstItem.trigger('mouseenter');
      await wrapper.vm.$nextTick();

      await firstItem.find('.edit-btn').trigger('click');
      await wrapper.vm.$nextTick();

      const input = firstItem.find('.conversation-title-input');
      await input.setValue('New Title');
      await input.trigger('keyup', { key: 'Escape' });
      await wrapper.vm.$nextTick();

      // 应该退出编辑模式
      expect(firstItem.find('.conversation-title').exists()).toBe(true);
      expect(firstItem.find('.conversation-title-input').exists()).toBe(false);
    });

    it('should cancel edit when title is empty', async () => {
      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      const firstItem = wrapper.find('.conversation-item');
      await firstItem.trigger('mouseenter');
      await wrapper.vm.$nextTick();

      await firstItem.find('.edit-btn').trigger('click');
      await wrapper.vm.$nextTick();

      const input = firstItem.find('.conversation-title-input');
      await input.setValue('   '); // 只有空格
      await input.trigger('blur');
      await wrapper.vm.$nextTick();

      // 应该退出编辑模式
      expect(firstItem.find('.conversation-title').exists()).toBe(true);
    });

    it('should cancel edit when title has not changed', async () => {
      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      const firstItem = wrapper.find('.conversation-item');
      await firstItem.trigger('mouseenter');
      await wrapper.vm.$nextTick();

      await firstItem.find('.edit-btn').trigger('click');
      await wrapper.vm.$nextTick();

      const input = firstItem.find('.conversation-title-input');
      // 保持原标题不变
      await input.trigger('blur');
      await wrapper.vm.$nextTick();

      // 应该退出编辑模式，不调用API
      expect(ApiService.updateSessionTitle).not.toHaveBeenCalled();
      expect(firstItem.find('.conversation-title').exists()).toBe(true);
    });
  });

  describe('delete functionality', () => {
    it('should cancel delete when clicking cancel button', async () => {
      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      const firstItem = wrapper.find('.conversation-item');
      await firstItem.trigger('mouseenter');
      await wrapper.vm.$nextTick();

      await firstItem.find('.delete-btn').trigger('click');
      await wrapper.vm.$nextTick();

      // 点击取消按钮
      const cancelButton = wrapper.find('.cancel-btn');
      await cancelButton.trigger('click');
      await wrapper.vm.$nextTick();

      // 对话框应该消失
      expect(wrapper.find('.delete-confirm-overlay').exists()).toBe(false);
    });

    it('should cancel delete when clicking overlay', async () => {
      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      const firstItem = wrapper.find('.conversation-item');
      await firstItem.trigger('mouseenter');
      await wrapper.vm.$nextTick();

      await firstItem.find('.delete-btn').trigger('click');
      await wrapper.vm.$nextTick();

      // 点击遮罩层
      const overlay = wrapper.find('.delete-confirm-overlay');
      await overlay.trigger('click');
      await wrapper.vm.$nextTick();

      // 对话框应该消失
      expect(wrapper.find('.delete-confirm-overlay').exists()).toBe(false);
    });

    it('should emit new-conversation when deleting active conversation', async () => {
      vi.mocked(ApiService.deleteSession).mockResolvedValueOnce(undefined);

      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      // 先选中第一个对话
      const firstItem = wrapper.find('.conversation-item');
      await firstItem.find('.conversation-content').trigger('click');
      await wrapper.vm.$nextTick();

      // 记录之前的事件数量
      const eventsBeforeDelete = wrapper.emitted('new-conversation')?.length || 0;

      // 删除该对话
      await firstItem.trigger('mouseenter');
      await wrapper.vm.$nextTick();

      await firstItem.find('.delete-btn').trigger('click');
      await wrapper.vm.$nextTick();

      const confirmButton = wrapper.find('.delete-confirm-btn');
      await confirmButton.trigger('click');
      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      // 应该触发新的 new-conversation 事件
      const eventsAfterDelete = wrapper.emitted('new-conversation')?.length || 0;
      expect(eventsAfterDelete).toBeGreaterThan(eventsBeforeDelete);
    });
  });

  describe('time formatting', () => {
    it('should format time for yesterday', () => {
      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      const timestamp = yesterday.toISOString();

      const formattedTime = (wrapper.vm as any).formatTime(timestamp);

      expect(formattedTime).toBe('昨天');
    });

    it('should format time for this week', () => {
      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      const threeDaysAgo = new Date();
      threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);
      const timestamp = threeDaysAgo.toISOString();

      const formattedTime = (wrapper.vm as any).formatTime(timestamp);

      // 应该显示星期几
      expect(formattedTime).toMatch(/周[一二三四五六七]/);
    });

    it('should format time for older dates', () => {
      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      const tenDaysAgo = new Date();
      tenDaysAgo.setDate(tenDaysAgo.getDate() - 10);
      const timestamp = tenDaysAgo.toISOString();

      const formattedTime = (wrapper.vm as any).formatTime(timestamp);

      // 应该显示月-日格式
      expect(formattedTime).toMatch(/\d+[月日]/);
    });
  });

  describe('loading and empty states', () => {
    it('should show loading state', async () => {
      // 让getConversations延迟返回
      vi.mocked(ApiService.getConversations).mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            setTimeout(
              () =>
                resolve({
                  conversations: mockConversations,
                }),
              100
            );
          })
      );

      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      // 立即检查，应该显示加载状态
      await wrapper.vm.$nextTick();
      expect(wrapper.find('.loading-state').exists()).toBe(true);
      expect(wrapper.text()).toContain('加载对话列表');
    });

    it('should show empty state when no conversations', async () => {
      vi.mocked(ApiService.getConversations).mockResolvedValueOnce({
        conversations: [],
      });

      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      expect(wrapper.find('.empty-state').exists()).toBe(true);
      expect(wrapper.text()).toContain('暂无对话');
    });

    it('should not load conversations when toolId is empty', async () => {
      const wrapper = mount(ConversationList, {
        props: {
          toolId: undefined,
        },
      });

      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      expect(ApiService.getConversations).not.toHaveBeenCalled();
    });
  });

  describe('exposed methods', () => {
    it('should expose loadConversations method', async () => {
      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      await new Promise(resolve => setTimeout(resolve, 0));
      await wrapper.vm.$nextTick();

      // 清除之前的调用
      vi.mocked(ApiService.getConversations).mockClear();

      // 调用暴露的方法
      await (wrapper.vm as any).loadConversations();

      expect(ApiService.getConversations).toHaveBeenCalledWith('test-tool');
    });

    it('should expose setCurrentConversation method', () => {
      const wrapper = mount(ConversationList, {
        props: {
          toolId: 'test-tool',
        },
      });

      // 调用暴露的方法
      (wrapper.vm as any).setCurrentConversation('session-1');

      // 应该更新当前会话ID
      expect((wrapper.vm as any).currentConversationId).toBe('session-1');
    });
  });
});
