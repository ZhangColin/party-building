/**
 * SvgPreview组件单元测试
 */
import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import SvgPreview from '@/components/preview/SvgPreview.vue';

// Mock DOMPurify
vi.mock('dompurify', () => ({
  default: {
    sanitize: (html: string, config: any) => {
      // 简单模拟DOMPurify的清理行为：移除script标签
      return html.replace(/<script\b[^>]*>([\s\S]*?)<\/script>/gim, '');
    },
  },
}));

// Mock URL and document methods
global.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
global.URL.revokeObjectURL = vi.fn();

describe('SvgPreview', () => {
  it('should render SVG content', () => {
    const svgContent = '<svg width="100" height="100"><circle cx="50" cy="50" r="40" /></svg>';

    const wrapper = mount(SvgPreview, {
      props: {
        content: svgContent,
      },
    });

    expect(wrapper.find('[data-testid="svg-preview-content"]').exists()).toBe(true);
    expect(wrapper.html()).toContain('<svg');
  });

  it('should show empty message when content is not valid SVG', () => {
    const wrapper = mount(SvgPreview, {
      props: {
        content: 'This is not SVG',
      },
    });

    expect(wrapper.find('[data-testid="svg-preview-empty"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('No SVG content');
  });

  it('should download SVG when clicked', async () => {
    const svgContent = '<svg width="100" height="100"><circle cx="50" cy="50" r="40" /></svg>';

    const wrapper = mount(SvgPreview, {
      props: {
        content: svgContent,
        filename: 'test.svg',
      },
    });

    const content = wrapper.find('[data-testid="svg-preview-content"]');
    await content.trigger('click');

    expect(URL.createObjectURL).toHaveBeenCalled();
    expect(URL.revokeObjectURL).toHaveBeenCalled();
  });

  it('should use custom filename when downloading', () => {
    const svgContent = '<svg width="100" height="100"><circle cx="50" cy="50" r="40" /></svg>';

    const wrapper = mount(SvgPreview, {
      props: {
        content: svgContent,
        filename: 'custom-name.svg',
      },
    });

    expect(wrapper.props('filename')).toBe('custom-name.svg');
  });

  it('should sanitize SVG content', () => {
    const svgWithScript = '<svg><script>alert("xss")</script><circle cx="50" cy="50" r="40" /></svg>';

    const wrapper = mount(SvgPreview, {
      props: {
        content: svgWithScript,
      },
    });

    const html = wrapper.html();
    // 应该保留svg标签
    expect(html).toContain('<svg');
    // 应该移除script标签（由DOMPurify处理）
    expect(html).not.toContain('<script>');
  });
});
