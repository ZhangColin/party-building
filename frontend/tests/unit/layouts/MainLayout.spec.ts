import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import { useNavigationStore } from '@/stores/navigationStore'

describe('MainLayout.vue', () => {
  let pinia: any
  let router: any
  let navigationStore: any

  beforeEach(async () => {
    // 创建新的 Pinia 实例
    pinia = createPinia()
    setActivePinia(pinia)

    // 创建路由
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/modules/:moduleId',
          component: MainLayout
        }
      ]
    })

    // 获取 navigationStore 并设置初始状态
    navigationStore = useNavigationStore()

    // 重置 store 状态
    navigationStore.modules = []
    navigationStore.loading = false
    navigationStore.isLoaded = false
    navigationStore.currentModuleId = 'ai-tools'
  })

  describe('基础渲染', () => {
    it('应该正确渲染布局结构', async () => {
      navigationStore.loading = false
      navigationStore.isLoaded = true

      const wrapper = mount(MainLayout, {
        global: {
          plugins: [pinia, router],
          stubs: {
            Header: { template: '<div class="mock-header">Header</div>' },
            AIToolsLayout: { template: '<div class="mock-ai-tools">AIToolsLayout</div>' },
            ToolsetModuleLayout: { template: '<div class="mock-toolset">ToolsetModuleLayout</div>' },
            CommonToolsLayout: { template: '<div class="mock-common-tools">CommonToolsLayout</div>' },
            WorksLayout: { template: '<div class="mock-works">WorksLayout</div>' }
          }
        }
      })

      expect(wrapper.find('.main-layout').exists()).toBe(true)
      expect(wrapper.find('.main-content').exists()).toBe(true)
    })

    it('应该渲染 Header 组件', async () => {
      navigationStore.loading = false
      navigationStore.isLoaded = true

      const wrapper = mount(MainLayout, {
        global: {
          plugins: [pinia, router],
          stubs: {
            Header: { template: '<div class="mock-header">Header</div>' },
            AIToolsLayout: true,
            ToolsetModuleLayout: true,
            CommonToolsLayout: true,
            WorksLayout: true
          }
        }
      })

      expect(wrapper.find('.mock-header').exists()).toBe(true)
    })
  })

  describe('加载状态', () => {
    it('loading 为 true 时显示加载指示器', async () => {
      navigationStore.loading = true
      navigationStore.isLoaded = false

      const wrapper = mount(MainLayout, {
        global: {
          plugins: [pinia, router],
          stubs: {
            Header: { template: '<div class="mock-header">Header</div>' },
            AIToolsLayout: true,
            ToolsetModuleLayout: true,
            CommonToolsLayout: true,
            WorksLayout: true
          }
        }
      })

      expect(wrapper.find('.loading-container').exists()).toBe(true)
      expect(wrapper.find('.loading-spinner').exists()).toBe(true)
      expect(wrapper.find('.loading-text').exists()).toBe(true)
      expect(wrapper.find('.loading-text').text()).toBe('加载中...')
    })

    it('loading 为 false 时不显示加载指示器', async () => {
      navigationStore.loading = false
      navigationStore.isLoaded = true

      const wrapper = mount(MainLayout, {
        global: {
          plugins: [pinia, router],
          stubs: {
            Header: { template: '<div class="mock-header">Header</div>' },
            AIToolsLayout: true,
            ToolsetModuleLayout: true,
            CommonToolsLayout: true,
            WorksLayout: true
          }
        }
      })

      expect(wrapper.find('.loading-container').exists()).toBe(false)
      expect(wrapper.find('.loading-spinner').exists()).toBe(false)
    })
  })

  describe('动态组件渲染 - 兜底逻辑', () => {
    it('找不到模块时应该渲染 AIToolsLayout（兜底）', async () => {
      navigationStore.modules = []
      navigationStore.loading = false
      navigationStore.isLoaded = true

      const wrapper = mount(MainLayout, {
        global: {
          plugins: [pinia, router],
          stubs: {
            Header: { template: '<div class="mock-header">Header</div>' },
            AIToolsLayout: {
              name: 'AIToolsLayout',
              template: '<div class="mock-ai-tools">AIToolsLayout</div>'
            },
            ToolsetModuleLayout: { template: '<div class="mock-toolset">ToolsetModuleLayout</div>' },
            CommonToolsLayout: { template: '<div class="mock-common-tools">CommonToolsLayout</div>' },
            WorksLayout: { template: '<div class="mock-works">WorksLayout</div>' }
          }
        }
      })

      await wrapper.vm.$nextTick()

      expect(wrapper.find('.mock-ai-tools').exists()).toBe(true)
    })

    it('page 类型但无匹配路由时应该渲染 AIToolsLayout（兜底）', async () => {
      navigationStore.modules = [
        {
          name: '某个页面',
          type: 'page',
          page_path: '/some-page',
          icon: 'document',
          order: 1
        }
      ]
      navigationStore.loading = false
      navigationStore.isLoaded = true

      const wrapper = mount(MainLayout, {
        global: {
          plugins: [pinia, router],
          stubs: {
            Header: { template: '<div class="mock-header">Header</div>' },
            AIToolsLayout: {
              name: 'AIToolsLayout',
              template: '<div class="mock-ai-tools">AIToolsLayout</div>'
            },
            ToolsetModuleLayout: { template: '<div class="mock-toolset">ToolsetModuleLayout</div>' },
            CommonToolsLayout: { template: '<div class="mock-common-tools">CommonToolsLayout</div>' },
            WorksLayout: { template: '<div class="mock-works">WorksLayout</div>' }
          }
        }
      })

      await wrapper.vm.$nextTick()

      expect(wrapper.find('.mock-ai-tools').exists()).toBe(true)
    })
  })

  describe('Props 传递逻辑', () => {
    it('非 toolset 模块不应该传递 toolsetId', async () => {
      navigationStore.modules = [
        {
          name: '某个页面',
          type: 'page',
          page_path: '/some-page',
          icon: 'document',
          order: 1
        }
      ]
      navigationStore.loading = false
      navigationStore.isLoaded = true

      const wrapper = mount(MainLayout, {
        global: {
          plugins: [pinia, router],
          stubs: {
            Header: { template: '<div class="mock-header">Header</div>' },
            AIToolsLayout: {
              name: 'AIToolsLayout',
              props: ['toolsetId'],
              template: '<div class="mock-ai-tools">AIToolsLayout</div>'
            },
            ToolsetModuleLayout: { template: '<div class="mock-toolset">ToolsetModuleLayout</div>' },
            CommonToolsLayout: { template: '<div class="mock-common-tools">CommonToolsLayout</div>' },
            WorksLayout: { template: '<div class="mock-works">WorksLayout</div>' }
          }
        }
      })

      await wrapper.vm.$nextTick()

      // AIToolsLayout 被渲染，但不会有 toolsetId
      const aiToolsLayout = wrapper.findComponent({ name: 'AIToolsLayout' })
      expect(aiToolsLayout.exists()).toBe(true)
      expect(aiToolsLayout.props('toolsetId')).toBeUndefined()
    })
  })

  describe('生命周期', () => {
    it('onMounted 时如果导航未加载应该调用 loadNavigation', async () => {
      navigationStore.isLoaded = false
      navigationStore.loadNavigation = vi.fn().mockResolvedValue(undefined)

      mount(MainLayout, {
        global: {
          plugins: [pinia, router],
          stubs: {
            Header: { template: '<div class="mock-header">Header</div>' },
            AIToolsLayout: { template: '<div class="mock-ai-tools">AIToolsLayout</div>' },
            ToolsetModuleLayout: { template: '<div class="mock-toolset">ToolsetModuleLayout</div>' },
            CommonToolsLayout: { template: '<div class="mock-common-tools">CommonToolsLayout</div>' },
            WorksLayout: { template: '<div class="mock-works">WorksLayout</div>' }
          }
        }
      })

      // onMounted 是异步的，需要等待
      await new Promise(resolve => setTimeout(resolve, 0))

      expect(navigationStore.loadNavigation).toHaveBeenCalledTimes(1)
    })

    it('onMounted 时如果导航已加载不应该调用 loadNavigation', async () => {
      navigationStore.isLoaded = true
      navigationStore.loadNavigation = vi.fn().mockResolvedValue(undefined)

      mount(MainLayout, {
        global: {
          plugins: [pinia, router],
          stubs: {
            Header: { template: '<div class="mock-header">Header</div>' },
            AIToolsLayout: { template: '<div class="mock-ai-tools">AIToolsLayout</div>' },
            ToolsetModuleLayout: { template: '<div class="mock-toolset">ToolsetModuleLayout</div>' },
            CommonToolsLayout: { template: '<div class="mock-common-tools">CommonToolsLayout</div>' },
            WorksLayout: { template: '<div class="mock-works">WorksLayout</div>' }
          }
        }
      })

      // onMounted 是异步的，需要等待
      await new Promise(resolve => setTimeout(resolve, 0))

      expect(navigationStore.loadNavigation).not.toHaveBeenCalled()
    })
  })

  describe('路由监听', () => {
    it('应该设置 setCurrentModule 方法到 watch', async () => {
      navigationStore.isLoaded = true
      navigationStore.setCurrentModule = vi.fn()

      mount(MainLayout, {
        global: {
          plugins: [pinia, router],
          stubs: {
            Header: { template: '<div class="mock-header">Header</div>' },
            AIToolsLayout: { template: '<div class="mock-ai-tools">AIToolsLayout</div>' },
            ToolsetModuleLayout: { template: '<div class="mock-toolset">ToolsetModuleLayout</div>' },
            CommonToolsLayout: { template: '<div class="mock-common-tools">CommonToolsLayout</div>' },
            WorksLayout: { template: '<div class="mock-works">WorksLayout</div>' }
          }
        }
      })

      await new Promise(resolve => setTimeout(resolve, 0))

      // watch 设置了 immediate: true，所以应该调用
      expect(navigationStore.setCurrentModule).toHaveBeenCalled()
    })
  })
})
