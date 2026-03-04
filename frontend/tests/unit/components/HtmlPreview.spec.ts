/**
 * HtmlPreview组件单元测试
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import HtmlPreview from '@/components/preview/HtmlPreview.vue';

// Mock URL.createObjectURL 和 URL.revokeObjectURL
const mockBlobUrls: string[] = [];
let blobUrlCounter = 0;

global.URL.createObjectURL = vi.fn((blob: Blob) => {
  const url = `blob:${mockBlobUrls.length}:${blobUrlCounter++}`;
  mockBlobUrls.push(url);
  return url;
});

global.URL.revokeObjectURL = vi.fn((url: string) => {
  const index = mockBlobUrls.indexOf(url);
  if (index > -1) {
    mockBlobUrls.splice(index, 1);
  }
});

describe('HtmlPreview', () => {
  beforeEach(() => {
    blobUrlCounter = 0;
    mockBlobUrls.length = 0;
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should render iframe with blob URL', () => {
    const wrapper = mount(HtmlPreview, {
      props: {
        content: '<div>Hello HTML</div>',
      },
    });

    const iframe = wrapper.find('[data-testid="html-preview-iframe"]');
    expect(iframe.exists()).toBe(true);
    expect(iframe.attributes('src')).toMatch(/^blob:/);
    expect(global.URL.createObjectURL).toHaveBeenCalled();
  });

  it('should show empty message when content is empty', () => {
    const wrapper = mount(HtmlPreview, {
      props: {
        content: '',
      },
    });

    expect(wrapper.find('[data-testid="html-preview-iframe"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="html-preview-empty"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('No HTML content');
  });

  it('should preserve script tags in HTML content', () => {
    const content = '<div><script>alert("test")</script>Hello</div>';

    const wrapper = mount(HtmlPreview, {
      props: {
        content,
      },
    });

    // 验证 URL.createObjectURL 被调用
    expect(global.URL.createObjectURL).toHaveBeenCalled();
    const blob = (global.URL.createObjectURL as any).mock.calls[0][0] as Blob;
    expect(blob).toBeInstanceOf(Blob);

    // 读取 blob 内容验证 script 标签被保留
    const reader = new FileReader();
    const blobText = new Promise<string>((resolve) => {
      reader.onload = (e) => resolve(e.target?.result as string);
      reader.readAsText(blob);
    });

    return blobText.then((text) => {
      expect(text).toContain('<script>');
      expect(text).toContain('alert("test")');
    });
  });

  it('should preserve style tags in HTML content', () => {
    const content = '<html><head><style>body { color: red; }</style></head><body>Test</body></html>';

    const wrapper = mount(HtmlPreview, {
      props: {
        content,
      },
    });

    expect(global.URL.createObjectURL).toHaveBeenCalled();
    const blob = (global.URL.createObjectURL as any).mock.calls[0][0] as Blob;

    const reader = new FileReader();
    const blobText = new Promise<string>((resolve) => {
      reader.onload = (e) => resolve(e.target?.result as string);
      reader.readAsText(blob);
    });

    return blobText.then((text) => {
      expect(text).toContain('<style>');
      expect(text).toContain('body { color: red; }');
    });
  });

  it('should set sandbox attribute on iframe', () => {
    const wrapper = mount(HtmlPreview, {
      props: {
        content: '<div>Test</div>',
      },
    });

    const iframe = wrapper.find('[data-testid="html-preview-iframe"]');
    expect(iframe.attributes('sandbox')).toBe('allow-scripts allow-same-origin allow-forms allow-modals');
  });

  it('should update blob URL when content changes', async () => {
    const wrapper = mount(HtmlPreview, {
      props: {
        content: '<div>Initial</div>',
      },
    });

    const initialCallCount = (global.URL.createObjectURL as any).mock.calls.length;
    expect(initialCallCount).toBe(1);

    await wrapper.setProps({ content: '<div>Updated</div>' });

    // 应该调用 createObjectURL 两次（初始 + 更新）
    // 同时也应该调用 revokeObjectURL 来清理旧的 URL
    expect((global.URL.createObjectURL as any).mock.calls.length).toBe(2);
    expect((global.URL.revokeObjectURL as any).mock.calls.length).toBe(1);
  });

  it('should cleanup blob URL on unmount', async () => {
    const wrapper = mount(HtmlPreview, {
      props: {
        content: '<div>Test</div>',
      },
    });

    // 等待组件挂载和 blob URL 创建
    await wrapper.vm.$nextTick();

    expect(mockBlobUrls.length).toBe(1);

    const revokeCallsBefore = (global.URL.revokeObjectURL as any).mock.calls.length;

    wrapper.unmount();

    // unmount 后应该清理 blob URL
    expect((global.URL.revokeObjectURL as any).mock.calls.length).toBe(revokeCallsBefore + 1);
    expect(global.URL.revokeObjectURL).toHaveBeenCalledWith(expect.stringMatching(/^blob:/));
  });

  it('should support Vue applications with CDN links', () => {
    const vueApp = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
</head>
<body>
  <div id="app">{{ message }}</div>
  <script>
    const { createApp } = Vue;
    createApp({
      data() {
        return { message: 'Hello Vue!' };
      }
    }).mount('#app');
  </script>
</body>
</html>`;

    const wrapper = mount(HtmlPreview, {
      props: {
        content: vueApp,
      },
    });

    expect(global.URL.createObjectURL).toHaveBeenCalled();
    const blob = (global.URL.createObjectURL as any).mock.calls[0][0] as Blob;

    const reader = new FileReader();
    const blobText = new Promise<string>((resolve) => {
      reader.onload = (e) => resolve(e.target?.result as string);
      reader.readAsText(blob);
    });

    return blobText.then((text) => {
      expect(text).toContain('https://unpkg.com/vue@3/dist/vue.global.js');
      expect(text).toContain('{{ message }}');
      expect(text).toContain('Hello Vue!');
    });
  });
});
