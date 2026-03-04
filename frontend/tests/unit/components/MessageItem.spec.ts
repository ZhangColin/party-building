/**
 * MessageItem组件单元测试
 */
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import MessageItem from '@/components/chat/MessageItem.vue';
import type { Message } from '@/types';

describe('MessageItem', () => {
  it('should render user message correctly', () => {
    const message: Message = {
      id: 1,
      session_id: 1,
      role: 'user',
      content: 'Hello AI',
      created_at: '2024-01-01T12:00:00Z',
    };

    const wrapper = mount(MessageItem, {
      props: {
        message,
      },
    });

    expect(wrapper.find('.message-user').exists()).toBe(true);
    expect(wrapper.text()).toContain('Hello AI');
  });

  it('should render assistant message correctly', () => {
    const message: Message = {
      id: 2,
      session_id: 1,
      role: 'assistant',
      content: 'Hello User',
      created_at: '2024-01-01T12:00:00Z',
    };

    const wrapper = mount(MessageItem, {
      props: {
        message,
      },
    });

    expect(wrapper.find('.message-assistant').exists()).toBe(true);
    expect(wrapper.text()).toContain('Hello User');
  });

  it('should render markdown for assistant message', () => {
    const message: Message = {
      id: 1,
      session_id: 1,
      role: 'assistant',
      content: '# Heading',
      created_at: '2024-01-01T12:00:00Z',
    };

    const wrapper = mount(MessageItem, {
      props: {
        message,
      },
    });

    const html = wrapper.find('[data-testid="message-text"]').html();
    expect(html).toContain('<h1>');
  });

  it('should not render markdown for user message', () => {
    const message: Message = {
      id: 1,
      session_id: 1,
      role: 'user',
      content: '# Heading',
      created_at: '2024-01-01T12:00:00Z',
    };

    const wrapper = mount(MessageItem, {
      props: {
        message,
      },
    });

    const html = wrapper.find('[data-testid="message-text"]').html();
    // 用户消息不应该被渲染为markdown
    expect(html).not.toContain('<h1>');
    expect(wrapper.text()).toContain('# Heading');
  });

  it('should format timestamp', () => {
    const message: Message = {
      id: 1,
      session_id: 1,
      role: 'user',
      content: 'Test',
      created_at: '2024-01-01T14:30:00Z',
    };

    const wrapper = mount(MessageItem, {
      props: {
        message,
      },
    });

    const timeElement = wrapper.find('[data-testid="message-time"]');
    expect(timeElement.exists()).toBe(true);
    expect(timeElement.text()).toMatch(/\d{2}:\d{2}/);
  });

  it('should display correct avatar for user', () => {
    const message: Message = {
      id: 1,
      session_id: 1,
      role: 'user',
      content: 'Test',
      created_at: '2024-01-01T12:00:00Z',
    };

    const wrapper = mount(MessageItem, {
      props: {
        message,
      },
    });

    const avatar = wrapper.find('.avatar-image');
    expect(avatar.attributes('src')).toContain('user-avatar');
  });

  it('should display correct avatar for assistant', () => {
    const message: Message = {
      id: 1,
      session_id: 1,
      role: 'assistant',
      content: 'Test',
      created_at: '2024-01-01T12:00:00Z',
    };

    const wrapper = mount(MessageItem, {
      props: {
        message,
      },
    });

    const avatar = wrapper.find('.avatar-image');
    expect(avatar.attributes('src')).toContain('ai-avatar');
  });

  it('should not show copy button initially', () => {
    const message: Message = {
      id: 1,
      session_id: 1,
      role: 'user',
      content: 'test message',
      created_at: '2024-01-01T12:00:00Z',
    };

    const wrapper = mount(MessageItem, {
      props: {
        message,
      },
    });

    // toolbar 不应该有 toolbar-visible 类
    expect(wrapper.find('.message-toolbar').classes()).not.toContain('toolbar-visible');
  });

  it('should show copy button on hover', async () => {
    const message: Message = {
      id: 1,
      session_id: 1,
      role: 'user',
      content: 'test message',
      created_at: '2024-01-01T12:00:00Z',
    };

    const wrapper = mount(MessageItem, {
      props: {
        message,
      },
    });

    // 初始状态不应该有 toolbar-visible 类
    expect(wrapper.find('.message-toolbar').classes()).not.toContain('toolbar-visible');

    await wrapper.trigger('mouseenter');
    await wrapper.vm.$nextTick();

    // hover 后 toolbar 应该有 toolbar-visible 类
    expect(wrapper.find('.message-toolbar').classes()).toContain('toolbar-visible');
  });

  it('should hide copy button when mouse leaves', async () => {
    const message: Message = {
      id: 1,
      session_id: 1,
      role: 'user',
      content: 'test message',
      created_at: '2024-01-01T12:00:00Z',
    };

    const wrapper = mount(MessageItem, {
      props: {
        message,
      },
    });

    await wrapper.trigger('mouseenter');
    await wrapper.vm.$nextTick();

    // hover 后 toolbar 应该有 toolbar-visible 类
    expect(wrapper.find('.message-toolbar').classes()).toContain('toolbar-visible');

    await wrapper.trigger('mouseleave');
    await wrapper.vm.$nextTick();

    // mouseleave 后 toolbar 不应该有 toolbar-visible 类
    expect(wrapper.find('.message-toolbar').classes()).not.toContain('toolbar-visible');
  });

  it('should copy message content when copy button clicked', async () => {
    const message: Message = {
      id: 1,
      session_id: 1,
      role: 'user',
      content: 'test message',
      created_at: '2024-01-01T12:00:00Z',
    };

    // Mock the clipboard API
    const mockClipboard = {
      writeText: vi.fn().mockResolvedValue(undefined),
    };

    // Store original clipboard
    const originalClipboard = global.navigator.clipboard;

    // Set mock clipboard
    Object.defineProperty(global.navigator, 'clipboard', {
      value: mockClipboard,
      writable: true,
      configurable: true,
    });

    const wrapper = mount(MessageItem, {
      props: {
        message,
      },
      global: {
        stubs: {
          Transition: false,
        },
      },
    });

    await wrapper.trigger('mouseenter');
    await wrapper.vm.$nextTick();

    await wrapper.find('[data-testid="copy-button"]').trigger('click');

    expect(mockClipboard.writeText).toHaveBeenCalledWith('test message');

    // Restore original clipboard
    if (originalClipboard) {
      Object.defineProperty(global.navigator, 'clipboard', {
        value: originalClipboard,
        writable: true,
        configurable: true,
      });
    }
  });
});
