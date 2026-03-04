/**
 * MarkdownPreview组件单元测试
 */
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import MarkdownPreview from '@/components/preview/MarkdownPreview.vue';

describe('MarkdownPreview', () => {
  it('should render markdown headers', () => {
    const wrapper = mount(MarkdownPreview, {
      props: {
        content: '# Hello World',
      },
    });

    const html = wrapper.html();
    expect(html).toContain('<h1>');
    expect(html).toContain('Hello World');
  });

  it('should render markdown paragraphs', () => {
    const wrapper = mount(MarkdownPreview, {
      props: {
        content: 'This is a paragraph.',
      },
    });

    const html = wrapper.html();
    expect(html).toContain('<p>');
    expect(html).toContain('This is a paragraph');
  });

  it('should render markdown code blocks', () => {
    const wrapper = mount(MarkdownPreview, {
      props: {
        content: '```javascript\nconsole.log("Hello");\n```',
      },
    });

    const html = wrapper.html();
    expect(html).toContain('<pre');
    expect(html).toContain('<code');
    expect(html).toContain('console.log');
  });

  it('should render inline code', () => {
    const wrapper = mount(MarkdownPreview, {
      props: {
        content: 'Use `console.log()` for debugging.',
      },
    });

    const html = wrapper.html();
    expect(html).toContain('<code>');
    expect(html).toContain('console.log()');
  });

  it('should render empty string when content is empty', () => {
    const wrapper = mount(MarkdownPreview, {
      props: {
        content: '',
      },
    });

    expect(wrapper.find('.markdown-preview').exists()).toBe(true);
  });

  it('should have data-testid for testing', () => {
    const wrapper = mount(MarkdownPreview, {
      props: {
        content: '# Test',
      },
    });

    expect(wrapper.find('[data-testid="markdown-preview"]').exists()).toBe(true);
  });
});
