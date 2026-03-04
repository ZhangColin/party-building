/**
 * ChatInput组件单元测试
 */
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import ChatInput from '@/components/chat/ChatInput.vue';

describe('ChatInput', () => {
  it('should render input and button', () => {
    const wrapper = mount(ChatInput);

    expect(wrapper.find('[data-testid="chat-input"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="send-button"]').exists()).toBe(true);
  });

  it('should emit send event with content when button clicked', async () => {
    const wrapper = mount(ChatInput);

    const input = wrapper.find('[data-testid="chat-input"]') as any;
    await input.setValue('Hello World');

    await wrapper.find('[data-testid="send-button"]').trigger('click');

    expect(wrapper.emitted('send')).toBeTruthy();
    expect(wrapper.emitted('send')?.[0]).toEqual(['Hello World']);
  });

  it('should emit send event when Enter pressed', async () => {
    const wrapper = mount(ChatInput);

    const input = wrapper.find('[data-testid="chat-input"]') as any;
    await input.setValue('Test');

    await input.trigger('keydown', { key: 'Enter' });

    expect(wrapper.emitted('send')).toBeTruthy();
  });

  it('should not send on Shift+Enter', async () => {
    const wrapper = mount(ChatInput);

    const input = wrapper.find('[data-testid="chat-input"]') as any;
    await input.setValue('Test');

    await input.trigger('keydown', { key: 'Enter', shiftKey: true });

    expect(wrapper.emitted('send')).toBeFalsy();
  });

  it('should disable send button when content is empty', async () => {
    const wrapper = mount(ChatInput);

    const button = wrapper.find('[data-testid="send-button"]');
    expect(button.attributes('disabled')).toBeDefined();
  });

  it('should enable send button when content exists', async () => {
    const wrapper = mount(ChatInput);

    const input = wrapper.find('[data-testid="chat-input"]') as any;
    await input.setValue('Hello');

    const button = wrapper.find('[data-testid="send-button"]');
    expect(button.attributes('disabled')).toBeUndefined();
  });

  it('should disable when isLoading prop is true', async () => {
    const wrapper = mount(ChatInput, {
      props: {
        isLoading: true,
      },
    });

    const button = wrapper.find('[data-testid="send-button"]');
    expect(button.attributes('disabled')).toBeDefined();
    expect(wrapper.find('[data-testid="loading-spinner"]').exists()).toBe(true);
  });

  /**
   * 中文输入法测试
   * Bug: 在中文状态下输入英文时，回车不应该发送消息，而是选择输入的英文字母
   */
  describe('Chinese IME Composition', () => {
    it('should not send message when Enter pressed during composition', async () => {
      const wrapper = mount(ChatInput);

      const input = wrapper.find('[data-testid="chat-input"]') as any;
      await input.setValue('Test');

      // 模拟composition开始（用户正在使用输入法选择候选词）
      await input.trigger('compositionstart');

      // 在composition期间按Enter，不应该发送
      await input.trigger('keydown', { key: 'Enter' });

      expect(wrapper.emitted('send')).toBeFalsy();
    });

    it('should send message when Enter pressed after composition ends', async () => {
      const wrapper = mount(ChatInput);

      const input = wrapper.find('[data-testid="chat-input"]') as any;
      await input.setValue('Test');

      // 模拟composition开始和结束
      await input.trigger('compositionstart');
      await input.trigger('compositionend');

      // composition结束后按Enter，应该发送
      await input.trigger('keydown', { key: 'Enter' });

      expect(wrapper.emitted('send')).toBeTruthy();
      expect(wrapper.emitted('send')?.[0]).toEqual(['Test']);
    });

    it('should send message when Enter pressed without composition', async () => {
      const wrapper = mount(ChatInput);

      const input = wrapper.find('[data-testid="chat-input"]') as any;
      await input.setValue('Hello');

      // 没有composition，直接按Enter，应该发送
      await input.trigger('keydown', { key: 'Enter' });

      expect(wrapper.emitted('send')).toBeTruthy();
      expect(wrapper.emitted('send')?.[0]).toEqual(['Hello']);
    });

    it('should handle multiple composition cycles correctly', async () => {
      const wrapper = mount(ChatInput);

      const input = wrapper.find('[data-testid="chat-input"]') as any;
      await input.setValue('Test');

      // 第一次composition
      await input.trigger('compositionstart');
      await input.trigger('keydown', { key: 'Enter' });
      expect(wrapper.emitted('send')).toBeFalsy();

      await input.trigger('compositionend');
      await input.trigger('keydown', { key: 'Enter' });
      expect(wrapper.emitted('send')).toBeTruthy();
      expect(wrapper.emitted('send')?.length).toBe(1);

      // 重置
      await input.setValue('Test2');

      // 第二次composition
      await input.trigger('compositionstart');
      await input.trigger('keydown', { key: 'Enter' });
      expect(wrapper.emitted('send')?.length).toBe(1); // 仍然是1，没有增加

      await input.trigger('compositionend');
      await input.trigger('keydown', { key: 'Enter' });
      expect(wrapper.emitted('send')?.length).toBe(2); // 现在是2
    });
  });
});
