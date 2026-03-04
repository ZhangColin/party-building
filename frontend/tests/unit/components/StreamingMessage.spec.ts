/**
 * StreamingMessage组件单元测试
 */
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import StreamingMessage from '@/components/chat/StreamingMessage.vue';

describe('StreamingMessage', () => {
  it('should render streaming content', () => {
    const wrapper = mount(StreamingMessage, {
      props: {
        content: 'Streaming text',
      },
    });

    expect(wrapper.find('[data-testid="streaming-message"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('Streaming text');
  });

  it('should render markdown content', () => {
    const wrapper = mount(StreamingMessage, {
      props: {
        content: '# Heading',
      },
    });

    const html = wrapper.find('[data-testid="streaming-text"]').html();
    expect(html).toContain('<h1>');
  });

  it('should show streaming indicator', () => {
    const wrapper = mount(StreamingMessage, {
      props: {
        content: 'Test',
      },
    });

    expect(wrapper.find('[data-testid="streaming-indicator"]').exists()).toBe(true);
    expect(wrapper.findAll('.dot').length).toBe(3);
  });

  it('should have streaming class', () => {
    const wrapper = mount(StreamingMessage, {
      props: {
        content: 'Test',
      },
    });

    expect(wrapper.find('.message-item').classes()).toContain('streaming');
  });

  it('should handle empty content', () => {
    const wrapper = mount(StreamingMessage, {
      props: {
        content: '',
      },
    });

    expect(wrapper.find('[data-testid="streaming-message"]').exists()).toBe(true);
  });
});
