/**
 * PreviewToolbar组件单元测试
 */
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import PreviewToolbar from '@/components/preview/PreviewToolbar.vue';

describe('PreviewToolbar', () => {
  it('should show markdown download buttons for markdown type', () => {
    const wrapper = mount(PreviewToolbar, {
      props: {
        artifactType: 'markdown',
      },
    });

    expect(wrapper.find('[data-testid="btn-download-markdown"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="btn-download-word"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="btn-download-pdf"]').exists()).toBe(true);
  });

  it('should show svg download button for svg type', () => {
    const wrapper = mount(PreviewToolbar, {
      props: {
        artifactType: 'svg',
      },
    });

    expect(wrapper.find('[data-testid="btn-download-svg"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="btn-download-markdown"]').exists()).toBe(false);
  });

  it('should not show any download buttons for html type', () => {
    const wrapper = mount(PreviewToolbar, {
      props: {
        artifactType: 'html',
      },
    });

    expect(wrapper.find('[data-testid="btn-download-markdown"]').exists()).toBe(false);
    expect(wrapper.find('[data-testid="btn-download-svg"]').exists()).toBe(false);
  });

  it('should emit downloadMarkdown when button clicked', async () => {
    const wrapper = mount(PreviewToolbar, {
      props: {
        artifactType: 'markdown',
      },
    });

    await wrapper.find('[data-testid="btn-download-markdown"]').trigger('click');

    expect(wrapper.emitted('downloadMarkdown')).toBeTruthy();
    expect(wrapper.emitted('downloadMarkdown')?.length).toBe(1);
  });

  it('should emit downloadSvg when button clicked', async () => {
    const wrapper = mount(PreviewToolbar, {
      props: {
        artifactType: 'svg',
      },
    });

    await wrapper.find('[data-testid="btn-download-svg"]').trigger('click');

    expect(wrapper.emitted('downloadSvg')).toBeTruthy();
  });

  it('should emit toggleFullscreen when fullscreen button clicked', async () => {
    const wrapper = mount(PreviewToolbar, {
      props: {
        artifactType: 'markdown',
      },
    });

    await wrapper.find('[data-testid="btn-toggle-fullscreen"]').trigger('click');

    expect(wrapper.emitted('toggleFullscreen')).toBeTruthy();
  });

  it('should emit closePreview when close button clicked', async () => {
    const wrapper = mount(PreviewToolbar, {
      props: {
        artifactType: 'markdown',
      },
    });

    await wrapper.find('[data-testid="btn-close-preview"]').trigger('click');

    expect(wrapper.emitted('closePreview')).toBeTruthy();
    expect(wrapper.emitted('closePreview')?.length).toBe(1);
  });

  it('should show expand icon when not in fullscreen', () => {
    const wrapper = mount(PreviewToolbar, {
      props: {
        artifactType: 'markdown',
        isFullscreen: false,
      },
    });

    const html = wrapper.html();
    expect(html).toContain('M8 3H5'); // 展开图标路径
  });

  it('should show collapse icon when in fullscreen', () => {
    const wrapper = mount(PreviewToolbar, {
      props: {
        artifactType: 'markdown',
        isFullscreen: true,
      },
    });

    const html = wrapper.html();
    expect(html).toContain('M8 3v3'); // 收缩图标路径
  });

  describe('Word Download Loading State', () => {
    it('should show loading state when isDownloadingWord is true', () => {
      const wrapper = mount(PreviewToolbar, {
        props: {
          artifactType: 'markdown',
          isDownloadingWord: true,
        },
      });

      const wordButton = wrapper.find('[data-testid="btn-download-word"]');
      expect(wordButton.attributes('disabled')).toBeDefined();
      expect(wordButton.text()).toContain('转换中...');
    });

    it('should not show loading state when isDownloadingWord is false', () => {
      const wrapper = mount(PreviewToolbar, {
        props: {
          artifactType: 'markdown',
          isDownloadingWord: false,
        },
      });

      const wordButton = wrapper.find('[data-testid="btn-download-word"]');
      expect(wordButton.attributes('disabled')).toBeUndefined();
      expect(wordButton.text()).toContain('Word');
    });

    it('should emit downloadWord when download button clicked', async () => {
      const wrapper = mount(PreviewToolbar, {
        props: {
          artifactType: 'markdown',
        },
      });

      await wrapper.find('[data-testid="btn-download-word"]').trigger('click');

      expect(wrapper.emitted('downloadWord')).toBeTruthy();
    });

    it('should emit downloadWord when download button clicked', async () => {
      const wrapper = mount(PreviewToolbar, {
        props: {
          artifactType: 'markdown',
        },
      });

      await wrapper.find('[data-testid="btn-download-word"]').trigger('click');

      expect(wrapper.emitted('downloadWord')).toBeTruthy();
    });
  });

  describe('PDF Download Loading State', () => {
    it('should show loading state when isDownloadingPDF is true', () => {
      const wrapper = mount(PreviewToolbar, {
        props: {
          artifactType: 'markdown',
          isDownloadingPDF: true,
        },
      });

      const pdfButton = wrapper.find('[data-testid="btn-download-pdf"]');
      expect(pdfButton.attributes('disabled')).toBeDefined();
      expect(pdfButton.text()).toContain('生成中...');
    });

    it('should not show loading state when isDownloadingPDF is false', () => {
      const wrapper = mount(PreviewToolbar, {
        props: {
          artifactType: 'markdown',
          isDownloadingPDF: false,
        },
      });

      const pdfButton = wrapper.find('[data-testid="btn-download-pdf"]');
      expect(pdfButton.attributes('disabled')).toBeUndefined();
      expect(pdfButton.text()).toContain('PDF');
    });

    it('should emit downloadPDF when download button clicked', async () => {
      const wrapper = mount(PreviewToolbar, {
        props: {
          artifactType: 'markdown',
        },
      });

      await wrapper.find('[data-testid="btn-download-pdf"]').trigger('click');

      expect(wrapper.emitted('downloadPDF')).toBeTruthy();
      expect(wrapper.emitted('downloadPDF')?.length).toBe(1);
    });
  });
});
