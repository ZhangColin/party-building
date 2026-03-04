/**
 * MessageList组件单元测试
 */
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import MessageList from '@/components/chat/MessageList.vue';
import type { Message } from '@/types';

describe('MessageList', () => {
  it('should render list of messages', () => {
    const messages: Message[] = [
      {
        id: 1,
        session_id: 1,
        role: 'user',
        content: 'Hello',
        created_at: '2024-01-01T12:00:00Z',
      },
      {
        id: 2,
        session_id: 1,
        role: 'assistant',
        content: 'Hi there!',
        created_at: '2024-01-01T12:00:01Z',
      },
    ];

    const wrapper = mount(MessageList, {
      props: {
        messages,
      },
    });

    const messageItems = wrapper.findAll('[data-testid="message-item"]');
    expect(messageItems.length).toBe(2);
  });

  it('should render streaming message when content provided', () => {
    const wrapper = mount(MessageList, {
      props: {
        messages: [],
        streamingContent: 'Streaming...',
      },
    });

    expect(wrapper.find('[data-testid="streaming-message-wrapper"]').exists()).toBe(true);
  });

  it('should not render streaming message when no content', () => {
    const wrapper = mount(MessageList, {
      props: {
        messages: [],
        streamingContent: '',
      },
    });

    expect(wrapper.find('[data-testid="streaming-message-wrapper"]').exists()).toBe(false);
  });

  it('should expose scrollToBottom method', () => {
    const wrapper = mount(MessageList, {
      props: {
        messages: [],
      },
    });

    expect(typeof (wrapper.vm as any).scrollToBottom).toBe('function');
  });
});

/**
 * 智能自动滚动测试
 * Bug: 内容输出时滚动条应该自动滚动，但现在需要用户手动滚动
 */
describe('MessageList - 智能自动滚动', () => {
  /**
   * 测试1：isNearBottom 正确判断在底部
   */
  it('should detect when near bottom', async () => {
    const wrapper = mount(MessageList, {
      props: {
        messages: [],
        autoScroll: true
      },
      global: {
        stubs: {
          MessageItem: { template: '<div />' },
          StreamingMessage: { template: '<div />' }
        }
      }
    })

    const scrollContainer = wrapper.find('.message-list').element as HTMLElement
    const messageList = wrapper.vm as any

    // 验证 isNearBottom 暴露了
    expect(typeof messageList.isNearBottom).toBe('function')

    // 模拟在底部的状态（距离底部0）
    Object.defineProperty(scrollContainer, 'scrollHeight', {
      writable: true,
      configurable: true,
      value: 1000
    })
    Object.defineProperty(scrollContainer, 'clientHeight', {
      writable: true,
      configurable: true,
      value: 500
    })
    Object.defineProperty(scrollContainer, 'scrollTop', {
      writable: true,
      configurable: true,
      value: 500 // 在底部
    })

    // 验证 isNearBottom 返回 true
    expect(messageList.isNearBottom()).toBe(true)
  })

  /**
   * 测试2：isNearBottom 正确判断不在底部
   */
  it('should detect when not near bottom', async () => {
    const wrapper = mount(MessageList, {
      props: {
        messages: [],
        autoScroll: true
      },
      global: {
        stubs: {
          MessageItem: { template: '<div />' },
          StreamingMessage: { template: '<div />' }
        }
      }
    })

    const scrollContainer = wrapper.find('.message-list').element as HTMLElement
    const messageList = wrapper.vm as any

    // 模拟不在底部的状态（距离底部200px，大于阈值100px）
    Object.defineProperty(scrollContainer, 'scrollHeight', {
      writable: true,
      configurable: true,
      value: 1000
    })
    Object.defineProperty(scrollContainer, 'clientHeight', {
      writable: true,
      configurable: true,
      value: 500
    })
    Object.defineProperty(scrollContainer, 'scrollTop', {
      writable: true,
      configurable: true,
      value: 300 // 距离底部 1000 - 500 - 300 = 200
    })

    // 验证 isNearBottom 返回 false
    expect(messageList.isNearBottom()).toBe(false)
  })

  /**
   * 测试3：isNearBottom 正确判断接近底部
   */
  it('should detect when near bottom threshold', async () => {
    const wrapper = mount(MessageList, {
      props: {
        messages: [],
        autoScroll: true
      },
      global: {
        stubs: {
          MessageItem: { template: '<div />' },
          StreamingMessage: { template: '<div />' }
        }
      }
    })

    const scrollContainer = wrapper.find('.message-list').element as HTMLElement
    const messageList = wrapper.vm as any

    // 模拟接近底部的状态（距离底部50px，小于阈值100px）
    Object.defineProperty(scrollContainer, 'scrollHeight', {
      writable: true,
      configurable: true,
      value: 1000
    })
    Object.defineProperty(scrollContainer, 'clientHeight', {
      writable: true,
      configurable: true,
      value: 500
    })
    Object.defineProperty(scrollContainer, 'scrollTop', {
      writable: true,
      configurable: true,
      value: 450 // 距离底部 1000 - 500 - 450 = 50
    })

    // 验证 isNearBottom 返回 true
    expect(messageList.isNearBottom()).toBe(true)
  })

  /**
   * 测试3：用户手动向上滚动后应该停止自动滚动
   */
  it('should stop auto-scroll when user scrolls up', async () => {
    const wrapper = mount(MessageList, {
      props: {
        messages: [],
        autoScroll: true
      },
      global: {
        stubs: {
          MessageItem: { template: '<div />' },
          StreamingMessage: { template: '<div />' }
        }
      }
    })

    const scrollContainer = wrapper.find('.message-list').element as HTMLElement

    // 模拟用户手动向上滚动（不是在底部）
    Object.defineProperty(scrollContainer, 'scrollTop', {
      writable: true,
      configurable: true,
      value: 100 // 不在底部
    })
    Object.defineProperty(scrollContainer, 'scrollHeight', {
      writable: true,
      configurable: true,
      value: 1000
    })
    Object.defineProperty(scrollContainer, 'clientHeight', {
      writable: true,
      configurable: true,
      value: 500
    })

    // 触发滚动事件，让组件知道用户手动滚动
    scrollContainer.dispatchEvent(new Event('scroll'))

    const scrollSpy = vi.spyOn(scrollContainer, 'scrollTop', 'set').mockImplementation(() => {})

    // 添加新消息
    await wrapper.setProps({ messages: [{ role: 'user', content: 'New message' }] })
    await wrapper.vm.$nextTick()

    // 由于用户不在底部，不应该自动滚动
    expect(scrollSpy).not.toHaveBeenCalled()
    scrollSpy.mockRestore()
  })

  /**
   * 测试4：用户滚动到底部附近时应该恢复自动滚动
   */
  it('should resume auto-scroll when user scrolls near bottom', async () => {
    const wrapper = mount(MessageList, {
      props: {
        messages: [],
        autoScroll: true
      },
      global: {
        stubs: {
          MessageItem: { template: '<div />' },
          StreamingMessage: { template: '<div />' }
        }
      }
    })

    const scrollContainer = wrapper.find('.message-list').element as HTMLElement
    const messageList = wrapper.vm as any

    // 模拟用户滚动到接近底部（距离底部50px，小于阈值100px）
    Object.defineProperty(scrollContainer, 'scrollHeight', {
      writable: true,
      configurable: true,
      value: 1000
    })
    Object.defineProperty(scrollContainer, 'clientHeight', {
      writable: true,
      configurable: true,
      value: 500
    })
    Object.defineProperty(scrollContainer, 'scrollTop', {
      writable: true,
      configurable: true,
      value: 450 // 距离底部 1000 - 500 - 450 = 50
    })

    // 验证 isNearBottom 返回 true（接近底部）
    expect(messageList.isNearBottom()).toBe(true)
  })
})

