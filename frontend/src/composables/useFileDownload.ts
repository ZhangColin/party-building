/**
 * 文件下载 composable
 * 提供统一的文件下载功能，支持多种文件类型
 */
import { ref } from 'vue';

export interface DownloadOptions {
  filename: string;
  mimeType?: string;
}

/**
 * 文件下载 hook
 */
export function useFileDownload() {
  const isDownloading = ref(false);

  /**
   * 下载文件
   * @param content 文件内容
   * @param options 下载选项
   */
  const download = (content: string, options: DownloadOptions) => {
    try {
      isDownloading.value = true;

      const { filename, mimeType = 'text/plain' } = options;

      // 创建 Blob 对象
      const blob = new Blob([content], { type: mimeType });

      // 创建下载链接
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();

      // 清理
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      return { success: true };
    } catch (error) {
      console.error('Download failed:', error);
      return { success: false, error };
    } finally {
      isDownloading.value = false;
    }
  };

  /**
   * 下载 Blob 对象
   * @param blob Blob 对象
   * @param filename 文件名
   */
  const downloadBlob = (blob: Blob, filename: string) => {
    try {
      isDownloading.value = true;

      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();

      // 清理
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      return { success: true };
    } catch (error) {
      console.error('Blob download failed:', error);
      return { success: false, error };
    } finally {
      isDownloading.value = false;
    }
  };

  return {
    isDownloading,
    download,
    downloadBlob,
  };
}
