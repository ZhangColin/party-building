/**
 * Word 下载功能单元测试
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { downloadWord } from '@/utils/documentDownloader';

// Mock fetch
global.fetch = vi.fn();

describe('downloadWord - 认证功能', () => {
  const mockFilename = 'test-document.docx';

  beforeEach(() => {
    // 重置 fetch mock
    vi.mocked(fetch).mockReset();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('应该在请求头中包含 Authorization token', async () => {
    // Mock localStorage with auth token
    vi.stubGlobal('localStorage', {
      getItem: (key: string) => {
        if (key === 'auth_token') {
          return 'mock-jwt-token-12345';
        }
        return null;
      },
      setItem: vi.fn(),
      removeItem: vi.fn(),
    });

    // Mock successful response
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      blob: async () => new Blob(['mock word content'], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' }),
    } as Response);

    // Mock URL.createObjectURL and URL.revokeObjectURL
    global.URL.createObjectURL = vi.fn(() => 'mock-url');
    global.URL.revokeObjectURL = vi.fn();

    const mockBlob = vi.fn();
    vi.mock('@/composables/useFileDownload', () => ({
      useFileDownload: () => ({
        downloadBlob: mockBlob,
      }),
    }));

    await downloadWord('# Test', mockFilename);

    // 验证 fetch 被调用
    expect(fetch).toHaveBeenCalled();

    // 获取 fetch 的调用参数
    const fetchCall = vi.mocked(fetch).mock.calls[0];
    const fetchOptions = fetchCall[1] as RequestInit;

    // 验证请求头包含 Authorization
    expect(fetchOptions?.headers).toHaveProperty('Authorization');
    expect(fetchOptions?.headers).toMatchObject({
      Authorization: 'Bearer mock-jwt-token-12345',
    });
  });

  it('应该优先从 localStorage 获取 token，然后是 sessionStorage', async () => {
    // Mock both storages
    vi.stubGlobal('localStorage', {
      getItem: (key: string) => {
        if (key === 'auth_token') {
          return 'localstorage-token';
        }
        return null;
      },
      setItem: vi.fn(),
      removeItem: vi.fn(),
    });

    vi.stubGlobal('sessionStorage', {
      getItem: (key: string) => {
        if (key === 'auth_token') {
          return 'sessionstorage-token';
        }
        return null;
      },
      setItem: vi.fn(),
      removeItem: vi.fn(),
    });

    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      blob: async () => new Blob(['mock word content'], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' }),
    } as Response);

    global.URL.createObjectURL = vi.fn(() => 'mock-url');
    global.URL.revokeObjectURL = vi.fn();

    const mockBlob = vi.fn();
    vi.mock('@/composables/useFileDownload', () => ({
      useFileDownload: () => ({
        downloadBlob: mockBlob,
      }),
    }));

    await downloadWord('# Test', mockFilename);

    const fetchCall = vi.mocked(fetch).mock.calls[0];
    const fetchOptions = fetchCall[1] as RequestInit;

    // 应该使用 localStorage 的 token（优先级更高）
    expect(fetchOptions?.headers).toMatchObject({
      Authorization: 'Bearer localstorage-token',
    });
  });

  it('应该在没有 token 时不发送 Authorization 头', async () => {
    // Mock 没有 token 的情况
    vi.stubGlobal('localStorage', {
      getItem: () => null,
      setItem: vi.fn(),
      removeItem: vi.fn(),
    });

    vi.stubGlobal('sessionStorage', {
      getItem: () => null,
      setItem: vi.fn(),
      removeItem: vi.fn(),
    });

    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      blob: async () => new Blob(['mock word content'], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' }),
    } as Response);

    global.URL.createObjectURL = vi.fn(() => 'mock-url');
    global.URL.revokeObjectURL = vi.fn();

    const mockBlob = vi.fn();
    vi.mock('@/composables/useFileDownload', () => ({
      useFileDownload: () => ({
        downloadBlob: mockBlob,
      }),
    }));

    await downloadWord('# Test', mockFilename);

    const fetchCall = vi.mocked(fetch).mock.calls[0];
    const fetchOptions = fetchCall[1] as RequestInit;

    // 不应该有 Authorization 头
    expect(fetchOptions?.headers).not.toHaveProperty('Authorization');
  });
});
