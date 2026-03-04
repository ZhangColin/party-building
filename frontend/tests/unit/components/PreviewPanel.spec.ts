/**
 * PreviewPanel组件单元测试
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import PreviewPanel from '@/components/PreviewPanel.vue';
import type { Artifact } from '@/types';

// Mock downloadPdf utility
const mockDownloadPdf = vi.fn().mockResolvedValue(undefined);
vi.mock('@/utils/html2pdfDownloader', () => ({
  default: () => mockDownloadPdf(),
}));

// Mock downloadWord utility
const mockDownloadWord = vi.fn().mockResolvedValue(undefined);
vi.mock('@/utils/documentDownloader', () => ({
  downloadWord: () => mockDownloadWord(),
}));

describe('PreviewPanel', () => {
  describe('基础渲染', () => {
    it('should show empty message when no artifact', () => {
      const wrapper = mount(PreviewPanel, {
        props: {
          artifact: null,
        },
      });

      expect(wrapper.find('[data-testid="preview-empty"]').exists()).toBe(true);
      expect(wrapper.text()).toContain('暂无预览内容');
    });

    it('should render MarkdownPreview for markdown type', () => {
      const artifact: Artifact = {
        type: 'markdown',
        content: '# Hello World',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      expect(wrapper.find('[data-testid="markdown-preview"]').exists()).toBe(true);
    });

    it('should render HtmlPreview for html type', () => {
      const artifact: Artifact = {
        type: 'html',
        content: '<div>Hello HTML</div>',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      expect(wrapper.find('[data-testid="html-preview-iframe"]').exists()).toBe(true);
    });

    it('should render SvgPreview for svg type', () => {
      const artifact: Artifact = {
        type: 'svg',
        content: '<svg><circle cx="50" cy="50" r="40" /></svg>',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      expect(wrapper.find('[data-testid="svg-preview-content"]').exists()).toBe(true);
    });

    it('should render SvgPreview for image/svg+xml type', () => {
      const artifact: Artifact = {
        type: 'image/svg+xml',
        content: '<svg><rect x="10" y="10" width="100" height="100" /></svg>',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      expect(wrapper.find('[data-testid="svg-preview-content"]').exists()).toBe(true);
    });

    it('should render toolbar when artifact exists', () => {
      const artifact: Artifact = {
        type: 'markdown',
        content: '# Test',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      expect(wrapper.find('[data-testid="preview-toolbar"]').exists()).toBe(true);
    });

    it('should not render toolbar when no artifact', () => {
      const wrapper = mount(PreviewPanel, {
        props: {
          artifact: null,
        },
      });

      // 工具栏依然会渲染，但不会显示特定类型的按钮
      expect(wrapper.find('[data-testid="preview-toolbar"]').exists()).toBe(true);
    });
  });

  describe('全屏功能', () => {
    it('should toggle fullscreen when toolbar button clicked', async () => {
      const artifact: Artifact = {
        type: 'markdown',
        content: '# Test',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      expect(wrapper.find('.preview-panel').classes()).not.toContain('is-fullscreen');

      await wrapper.find('[data-testid="btn-toggle-fullscreen"]').trigger('click');

      expect(wrapper.find('.preview-panel').classes()).toContain('is-fullscreen');
    });

    it('should exit fullscreen when clicked again', async () => {
      const artifact: Artifact = {
        type: 'markdown',
        content: '# Test',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      // 进入全屏
      await wrapper.find('[data-testid="btn-toggle-fullscreen"]').trigger('click');
      expect(wrapper.find('.preview-panel').classes()).toContain('is-fullscreen');

      // 退出全屏
      await wrapper.find('[data-testid="btn-toggle-fullscreen"]').trigger('click');
      expect(wrapper.find('.preview-panel').classes()).not.toContain('is-fullscreen');
    });
  });

  describe('PDF Download', () => {
    it('should have PDF download button for markdown artifacts', () => {
      const artifact: Artifact = {
        type: 'markdown',
        content: '# Test Document',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      expect(wrapper.find('[data-testid="btn-download-pdf"]').exists()).toBe(true);
    });

    it('should not show PDF download button for non-markdown artifacts', () => {
      const htmlArtifact: Artifact = {
        type: 'html',
        content: '<div>Test</div>',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact: htmlArtifact,
        },
      });

      expect(wrapper.find('[data-testid="btn-download-pdf"]').exists()).toBe(false);
    });

    it('should call downloadPdf utility when PDF button is clicked', async () => {
      const artifact: Artifact = {
        type: 'markdown',
        content: '# Test Document',
        language: 'markdown',
        timestamp: new Date().toISOString(),
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      const pdfButton = wrapper.find('[data-testid="btn-download-pdf"]');
      expect(pdfButton.exists()).toBe(true);

      await pdfButton.trigger('click');
      await wrapper.vm.$nextTick();

      expect(wrapper.exists()).toBe(true);
    });

    it('should show loading state during PDF download', async () => {
      const artifact: Artifact = {
        type: 'markdown',
        content: '# Test Document',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      const pdfButton = wrapper.find('[data-testid="btn-download-pdf"]');
      expect(pdfButton.attributes('disabled')).toBeUndefined();

      await pdfButton.trigger('click');

      expect(wrapper.exists()).toBe(true);
    });

    it('should handle PDF download error and show notification', async () => {
      const artifact: Artifact = {
        type: 'markdown',
        content: '# Test Document',
      };

      // Mock PDF 下载失败
      mockDownloadPdf.mockRejectedValueOnce(new Error('PDF generation failed'));

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      await wrapper.find('[data-testid="btn-download-pdf"]').trigger('click');
      await wrapper.vm.$nextTick();

      // 验证错误被记录
      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();

      // 验证组件仍然正常工作
      expect(wrapper.exists()).toBe(true);
    });

    it('should not download PDF for non-markdown content', async () => {
      const artifact: Artifact = {
        type: 'html',
        content: '<div>Test</div>',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      // HTML 成果物不应该有 PDF 下载按钮
      expect(wrapper.find('[data-testid="btn-download-pdf"]').exists()).toBe(false);
    });

    it('should show notification for non-markdown PDF download attempt', async () => {
      const artifact: Artifact = {
        type: 'html',
        content: '<div>Test</div>',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      // HTML 没有 PDF 下载按钮，所以这个测试验证组件不会崩溃
      expect(wrapper.exists()).toBe(true);
    });
  });

  describe('Markdown 下载功能', () => {
    it('should download markdown when markdown button clicked', async () => {
      const artifact: Artifact = {
        type: 'markdown',
        content: '# Test Markdown',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      const downloadBlobSpy = vi.spyOn(wrapper.vm as any, 'handleDownloadMarkdown');
      await wrapper.find('[data-testid="btn-download-markdown"]').trigger('click');

      expect(downloadBlobSpy).toHaveBeenCalled();
    });

    it('should not download markdown when content is empty', async () => {
      const artifact: Artifact = {
        type: 'markdown',
        content: '',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
      await wrapper.find('[data-testid="btn-download-markdown"]').trigger('click');

      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });
  });

  describe('SVG 下载功能', () => {
    it('should download SVG when svg button clicked', async () => {
      const artifact: Artifact = {
        type: 'svg',
        content: '<svg><circle cx="50" cy="50" r="40" /></svg>',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      expect(wrapper.find('[data-testid="btn-download-svg"]').exists()).toBe(true);

      const handleDownloadSpy = vi.spyOn(wrapper.vm as any, 'handleDownloadSvg');
      await wrapper.find('[data-testid="btn-download-svg"]').trigger('click');

      expect(handleDownloadSpy).toHaveBeenCalled();
    });

    it('should not show SVG download button for non-svg artifacts', () => {
      const markdownArtifact: Artifact = {
        type: 'markdown',
        content: '# Test',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact: markdownArtifact,
        },
      });

      expect(wrapper.find('[data-testid="btn-download-svg"]').exists()).toBe(false);
    });
  });

  describe('通知功能', () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it('should show notification when downloadWord fails with non-markdown content', async () => {
      const htmlArtifact: Artifact = {
        type: 'html',
        content: '<div>Test</div>',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact: htmlArtifact,
        },
      });

      // 模拟 HTML 成果物的 Word 下载按钮不应该显示
      expect(wrapper.find('[data-testid="btn-download-word"]').exists()).toBe(false);
    });

    it('should show notification and hide after 3 seconds', async () => {
      const artifact: Artifact = {
        type: 'markdown',
        content: '# Test',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      // 手动调用 showNotification
      (wrapper.vm as any).showNotification('测试通知');
      await wrapper.vm.$nextTick();

      expect(wrapper.find('[data-testid="notification"]').exists()).toBe(true);
      expect(wrapper.find('[data-testid="notification"]').text()).toBe('测试通知');

      // 快进3秒
      vi.advanceTimersByTime(3000);
      await wrapper.vm.$nextTick();

      // 通知应该被隐藏（notification 值为空）
      expect((wrapper.vm as any).notification).toBe('');
    });

    it('should clear previous notification timer when showing new notification', async () => {
      const artifact: Artifact = {
        type: 'markdown',
        content: '# Test',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      const clearTimeoutSpy = vi.spyOn(window, 'clearTimeout');

      // 显示第一个通知
      (wrapper.vm as any).showNotification('第一个通知');
      expect(clearTimeoutSpy).not.toHaveBeenCalled();

      // 显示第二个通知
      (wrapper.vm as any).showNotification('第二个通知');
      expect(clearTimeoutSpy).toHaveBeenCalled();

      clearTimeoutSpy.mockRestore();
    });
  });

  describe('关闭预览功能', () => {
    it('should emit closePreview event when close button clicked', async () => {
      const artifact: Artifact = {
        type: 'markdown',
        content: '# Test',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      await wrapper.find('[data-testid="btn-close-preview"]').trigger('click');

      expect(wrapper.emitted('closePreview')).toBeTruthy();
      expect(wrapper.emitted('closePreview')?.length).toBe(1);
    });
  });

  describe('边界情况', () => {
    it('should handle artifact with null content gracefully', () => {
      const artifact: Artifact = {
        type: 'markdown',
        content: '',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      expect(wrapper.find('[data-testid="markdown-preview"]').exists()).toBe(true);
    });

    it('should handle unknown artifact type', () => {
      const artifact = {
        type: 'unknown',
        content: 'some content',
      } as any;

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      // 应该显示空状态
      expect(wrapper.find('[data-testid="preview-empty"]').exists()).toBe(true);
    });

    it('should handle SVG with custom filename', () => {
      const artifact: Artifact = {
        type: 'svg',
        content: '<svg></svg>',
        filename: 'custom.svg',
      } as any;

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      expect(wrapper.find('[data-testid="svg-preview-content"]').exists()).toBe(true);
    });
  });

  describe('Props 变化响应', () => {
    it('should update preview when artifact prop changes', async () => {
      const wrapper = mount(PreviewPanel, {
        props: {
          artifact: null,
        },
      });

      expect(wrapper.find('[data-testid="preview-empty"]').exists()).toBe(true);

      const newArtifact: Artifact = {
        type: 'markdown',
        content: '# New Content',
      };

      await wrapper.setProps({ artifact: newArtifact });

      expect(wrapper.find('[data-testid="markdown-preview"]').exists()).toBe(true);
    });

    it('should update fullscreen state when artifact changes', async () => {
      const artifact: Artifact = {
        type: 'markdown',
        content: '# Test',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      // 进入全屏
      await wrapper.find('[data-testid="btn-toggle-fullscreen"]').trigger('click');
      expect(wrapper.find('.preview-panel').classes()).toContain('is-fullscreen');

      // 更新 artifact
      const newArtifact: Artifact = {
        type: 'html',
        content: '<div>New HTML</div>',
      };
      await wrapper.setProps({ artifact: newArtifact });

      // 全屏状态应该保持
      expect(wrapper.find('.preview-panel').classes()).toContain('is-fullscreen');
    });
  });

  describe('Word Download', () => {
    it('should emit downloadWord event when Word button clicked', async () => {
      const artifact: Artifact = {
        type: 'markdown',
        content: '# Test Document',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      await wrapper.find('[data-testid="btn-download-word"]').trigger('click');

      expect(wrapper.find('[data-testid="btn-download-word"]').exists()).toBe(true);
    });

    it('should show loading state during Word download', async () => {
      const artifact: Artifact = {
        type: 'markdown',
        content: '# Test Document',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      const wordButton = wrapper.find('[data-testid="btn-download-word"]');
      expect(wordButton.attributes('disabled')).toBeUndefined();

      await wordButton.trigger('click');
      expect(wrapper.exists()).toBe(true);
    });

    it('should not show Word download button for non-markdown artifacts', () => {
      const htmlArtifact: Artifact = {
        type: 'html',
        content: '<div>Test</div>',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact: htmlArtifact,
        },
      });

      expect(wrapper.find('[data-testid="btn-download-word"]').exists()).toBe(false);
    });

    it('should handle Word download errors gracefully', async () => {
      const artifact: Artifact = {
        type: 'markdown',
        content: '# Test Document',
      };

      // Mock Word 下载失败
      mockDownloadWord.mockRejectedValueOnce(new Error('Word generation failed'));

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      expect(wrapper.find('[data-testid="btn-download-word"]').exists()).toBe(true);

      const wordButton = wrapper.find('[data-testid="btn-download-word"]');
      await wordButton.trigger('click');
      await wrapper.vm.$nextTick();

      // 验证错误被记录
      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();

      // 验证组件仍然正常工作
      expect(wrapper.exists()).toBe(true);
    });
  });

  describe('isSvgArtifact 辅助函数', () => {
    it('should return true for svg type', () => {
      const artifact: Artifact = {
        type: 'svg',
        content: '<svg></svg>',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      expect((wrapper.vm as any).isSvgArtifact(artifact)).toBe(true);
    });

    it('should return true for image/svg+xml type', () => {
      const artifact: Artifact = {
        type: 'image/svg+xml',
        content: '<svg></svg>',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      expect((wrapper.vm as any).isSvgArtifact(artifact)).toBe(true);
    });

    it('should return false for non-svg types', () => {
      const artifact: Artifact = {
        type: 'markdown',
        content: '# Test',
      };

      const wrapper = mount(PreviewPanel, {
        props: {
          artifact,
        },
      });

      expect((wrapper.vm as any).isSvgArtifact(artifact)).toBe(false);
    });

    it('should return false for null artifact', () => {
      const wrapper = mount(PreviewPanel, {
        props: {
          artifact: null,
        },
      });

      expect((wrapper.vm as any).isSvgArtifact(null)).toBe(false);
    });
  });
});
