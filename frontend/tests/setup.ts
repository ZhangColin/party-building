/**
 * Vitest测试设置文件
 */
import { vi } from 'vitest';
import { config } from '@vue/test-utils';

// 全局mock Vue Router
vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal<typeof import('vue-router')>()
  return {
    ...actual,
    useRoute: () => ({ params: {}, query: {} }),
    useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  }
})

// 全局mock Pinia stores
config.global.mocks = {
  $store: {
    state: {},
  },
};
