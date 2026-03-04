/**
 * @vitest-environment jsdom
 * MarkdownEditorView 组件测试
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import MarkdownEditorView from '../../src/views/MarkdownEditorView.vue'
import PreviewPanel from '../../src/components/PreviewPanel.vue'

// Mock window.confirm
const mockConfirm = vi.spyOn(window, 'confirm')

// Mock vue-router
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

describe('MarkdownEditorView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('应该正确渲染工具栏和编辑器', () => {
    const wrapper = mount(MarkdownEditorView, {
      global: {
        stubs: {
          PreviewPanel: true, // Stub PreviewPanel to simplify testing
        },
      },
    })

    // 验证工具栏
    expect(wrapper.find('.toolbar').exists()).toBe(true)
    expect(wrapper.find('.toolbar-title').exists()).toBe(true)
    expect(wrapper.find('.toolbar-title').text()).toContain('Markdown 编辑器')

    // 验证清空按钮存在
    expect(wrapper.find('.toolbar-btn').exists()).toBe(true)

    // 验证编辑器内容区域
    expect(wrapper.find('.editor-content').exists()).toBe(true)

    // 验证编辑器容器
    expect(wrapper.find('.editor-container').exists()).toBe(true)

    // 验证预览容器
    expect(wrapper.find('.preview-container').exists()).toBe(true)
  })

  it('应该包含PreviewPanel组件', () => {
    const wrapper = mount(MarkdownEditorView)

    // 验证PreviewPanel组件存在
    const previewPanel = wrapper.findComponent(PreviewPanel)
    expect(previewPanel.exists()).toBe(true)
  })

  it('应该将编辑器内容传递给PreviewPanel', () => {
    const wrapper = mount(MarkdownEditorView)

    const previewPanel = wrapper.findComponent(PreviewPanel)
    const artifact = previewPanel.props('artifact')

    // 验证artifact存在并且是Markdown类型
    expect(artifact).toBeTruthy()
    expect(artifact.type).toBe('markdown')
    expect(artifact.language).toBe('markdown')
    expect(artifact.content).toContain('# 欢迎使用 Markdown 编辑器')
  })

  it('清空按钮应该弹出确认对话框', async () => {
    mockConfirm.mockReturnValue(false) // 用户取消

    const wrapper = mount(MarkdownEditorView, {
      global: {
        stubs: {
          PreviewPanel: true,
        },
      },
    })

    // 找到清空按钮（通过title属性）
    const clearButtons = wrapper.findAll('.toolbar-btn')
    const clearButton = clearButtons.find(btn => btn.text().includes('清空'))

    expect(clearButton).toBeDefined()
    if (clearButton) {
      await clearButton.trigger('click')

      // 验证confirm被调用
      expect(mockConfirm).toHaveBeenCalledWith('确定要清空所有内容吗？此操作不可撤销。')
    }
  })

  it('应该有默认的欢迎内容', () => {
    const wrapper = mount(MarkdownEditorView)

    const previewPanel = wrapper.findComponent(PreviewPanel)
    const artifact = previewPanel.props('artifact')

    // 验证默认内容
    expect(artifact.content).toContain('# 欢迎使用 Markdown 编辑器')
    expect(artifact.content).toContain('## 功能特性')
    expect(artifact.content).toContain('实时预览')
    expect(artifact.content).toContain('数学公式')
  })

  it('应该有响应式布局类名', () => {
    const wrapper = mount(MarkdownEditorView, {
      global: {
        stubs: {
          PreviewPanel: true,
        },
      },
    })

    // 验证响应式容器类名
    expect(wrapper.find('.editor-container').exists()).toBe(true)
    expect(wrapper.find('.editor-panel').exists()).toBe(true)
    expect(wrapper.find('.preview-container').exists()).toBe(true)
  })

  it('返回按钮应该导航到/common-tools', async () => {
    const wrapper = mount(MarkdownEditorView, {
      global: {
        stubs: {
          PreviewPanel: true,
        },
      },
    })

    // 找到返回按钮
    const backButtons = wrapper.findAll('.toolbar-btn')
    const backButton = backButtons.find(btn => btn.text().includes('返回'))

    expect(backButton).toBeDefined()
    if (backButton) {
      await backButton.trigger('click')

      // 验证路由跳转
      expect(mockPush).toHaveBeenCalledWith('/common-tools')
    }
  })

  it('清空按钮确认后应该清空内容', async () => {
    mockConfirm.mockReturnValue(true) // 用户确认

    const wrapper = mount(MarkdownEditorView, {
      global: {
        stubs: {
          PreviewPanel: true,
        },
      },
    })

    // 等待编辑器初始化
    await nextTick()
    await nextTick()

    // 找到清空按钮
    const clearButtons = wrapper.findAll('.toolbar-btn')
    const clearButton = clearButtons.find(btn => btn.text().includes('清空'))

    expect(clearButton).toBeDefined()
    if (clearButton) {
      await clearButton.trigger('click')

      // 验证confirm被调用
      expect(mockConfirm).toHaveBeenCalledWith('确定要清空所有内容吗？此操作不可撤销。')

      // 等待清空操作完成
      await nextTick()

      // 验证内容被清空（previewArtifact应该是空内容）
      const previewPanel = wrapper.findComponent(PreviewPanel)
      const artifact = previewPanel.props('artifact')
      // 内容应该被清空
      expect(artifact.content).toBe('')
    }
  })

  it('PreviewPanel关闭事件应该被处理', async () => {
    const wrapper = mount(MarkdownEditorView)

    const previewPanel = wrapper.findComponent(PreviewPanel)

    // 触发close事件（不应该抛出错误）
    await previewPanel.vm.$emit('close')

    // Markdown编辑器的预览始终显示，所以close不做任何操作
    // 只要没有抛出错误就说明测试通过
    expect(true).toBe(true)
  })

  it('应该有可拖动分隔条', () => {
    const wrapper = mount(MarkdownEditorView, {
      global: {
        stubs: {
          PreviewPanel: true,
        },
      },
    })

    // 验证分隔条存在
    const resizer = wrapper.find('.resizer')
    expect(resizer.exists()).toBe(true)

    // 验证分隔条有正确的类名
    expect(resizer.classes()).toContain('resizer')

    // 验证分隔条内有线条
    const resizerLine = wrapper.find('.resizer-line')
    expect(resizerLine.exists()).toBe(true)
  })

  it('应该正确计算编辑器和预览宽度', () => {
    const wrapper = mount(MarkdownEditorView, {
      global: {
        stubs: {
          PreviewPanel: true,
        },
      },
    })

    // 验证默认宽度是50%
    const editorPanel = wrapper.find('.editor-panel')
    const previewContainer = wrapper.find('.preview-container')

    // 初始宽度应该是50%和50%
    // 注意：由于使用了计算属性，我们需要检查实际的style
    expect(editorPanel.attributes('style')).toContain('width: 50%')
    expect(previewContainer.attributes('style')).toContain('width: 50%')
  })

  it('handleClosePreview应该是一个空函数', () => {
    // 这个测试验证handleClosePreview存在且不会抛出错误
    const wrapper = mount(MarkdownEditorView, {
      global: {
        stubs: {
          PreviewPanel: true,
        },
      },
    })

    // 通过vm访问组件方法
    const vm = wrapper.vm as any
    expect(typeof vm.handleClosePreview).toBe('function')

    // 调用不应该抛出错误
    expect(() => vm.handleClosePreview()).not.toThrow()
  })

  describe('分隔条拖动功能', () => {
    it('应该开始拖动并设置isResizing为true', async () => {
      const wrapper = mount(MarkdownEditorView, {
        global: {
          stubs: {
            PreviewPanel: true,
          },
        },
      })

      const resizer = wrapper.find('.resizer')
      const vm = wrapper.vm as any

      // 初始状态不是拖动中
      expect(vm.isResizing).toBe(false)

      // 触发mousedown
      await resizer.trigger('mousedown')

      // 应该进入拖动状态
      expect(vm.isResizing).toBe(true)
    })

    it('应该支持触摸事件开始拖动', async () => {
      const wrapper = mount(MarkdownEditorView, {
        global: {
          stubs: {
            PreviewPanel: true,
          },
        },
      })

      const resizer = wrapper.find('.resizer')
      const vm = wrapper.vm as any

      // 触发touchstart
      await resizer.trigger('touchstart')

      // 应该进入拖动状态
      expect(vm.isResizing).toBe(true)
    })

    it('拖动应该防止默认行为', async () => {
      const wrapper = mount(MarkdownEditorView, {
        global: {
          stubs: {
            PreviewPanel: true,
          },
        },
      })

      const resizer = wrapper.find('.resizer')
      const event = new MouseEvent('mousedown', { cancelable: true })
      const preventDefaultSpy = vi.spyOn(event, 'preventDefault')

      // 手动触发事件
      resizer.element.addEventListener('mousedown', (e: Event) => {
        const vm = wrapper.vm as any
        vm.startResize(e)
      })
      resizer.element.dispatchEvent(event)

      expect(preventDefaultSpy).toHaveBeenCalled()
    })

    it('拖动开始时应该设置body样式', async () => {
      const wrapper = mount(MarkdownEditorView, {
        global: {
          stubs: {
            PreviewPanel: true,
          },
        },
      })

      const resizer = wrapper.find('.resizer')
      const vm = wrapper.vm as any

      await resizer.trigger('mousedown')

      // 验证body样式被设置
      expect(document.body.style.cursor).toBe('col-resize')
      expect(document.body.style.userSelect).toBe('none')
    })

    it('拖动结束后应该恢复body样式', async () => {
      const wrapper = mount(MarkdownEditorView, {
        global: {
          stubs: {
            PreviewPanel: true,
          },
        },
      })

      const vm = wrapper.vm as any

      // 模拟拖动开始
      await vm.startResize(new MouseEvent('mousedown'))

      // 验证样式被设置
      expect(document.body.style.cursor).toBe('col-resize')

      // 直接调用stopResize
      await vm.stopResize()

      // 验证样式被恢复
      expect(document.body.style.cursor).toBe('')
      expect(document.body.style.userSelect).toBe('')
    })

    it('拖动时应该更新编辑器宽度', async () => {
      const wrapper = mount(MarkdownEditorView, {
        global: {
          stubs: {
            PreviewPanel: true,
          },
        },
        attachTo: document.body,
      })

      const vm = wrapper.vm as any

      // 模拟拖动开始
      await vm.startResize(new MouseEvent('mousedown'))

      // 创建一个容器元素用于计算
      const container = wrapper.find('.editor-container').element as HTMLElement
      vi.spyOn(container, 'getBoundingClientRect').mockReturnValue({
        left: 0,
        width: 1000,
        top: 0,
        height: 500,
        right: 1000,
        bottom: 500,
        toJSON: () => ({}),
      })

      // 触发mousemove事件（模拟在600px位置）
      const moveEvent = new MouseEvent('mousemove', { clientX: 600 })
      await vm.handleResize(moveEvent)

      // 等待更新
      await nextTick()

      // 验证宽度被更新（60%）
      expect(vm.editorWidth).toBe(60)

      // 清理
      wrapper.unmount()
    })

    it('拖动宽度应该限制在30%-70%之间', async () => {
      const wrapper = mount(MarkdownEditorView, {
        global: {
          stubs: {
            PreviewPanel: true,
          },
        },
        attachTo: document.body,
      })

      const vm = wrapper.vm as any

      // 模拟拖动开始
      await vm.startResize(new MouseEvent('mousedown'))

      // 创建容器mock
      const container = wrapper.find('.editor-container').element as HTMLElement
      vi.spyOn(container, 'getBoundingClientRect').mockReturnValue({
        left: 0,
        width: 1000,
        top: 0,
        height: 500,
        right: 1000,
        bottom: 500,
        toJSON: () => ({}),
      })

      // 测试下限（10%应该被限制为30%）
      const moveEvent1 = new MouseEvent('mousemove', { clientX: 100 })
      await vm.handleResize(moveEvent1)
      await nextTick()
      expect(vm.editorWidth).toBe(30)

      // 测试上限（90%应该被限制为70%）
      const moveEvent2 = new MouseEvent('mousemove', { clientX: 900 })
      await vm.handleResize(moveEvent2)
      await nextTick()
      expect(vm.editorWidth).toBe(70)

      // 清理
      wrapper.unmount()
    })

    it('非拖动状态下handleResize不应该更新宽度', async () => {
      const wrapper = mount(MarkdownEditorView, {
        global: {
          stubs: {
            PreviewPanel: true,
          },
        },
      })

      const vm = wrapper.vm as any
      const initialWidth = vm.editorWidth

      // 不触发startResize，直接触发mousemove
      await window.dispatchEvent(new MouseEvent('mousemove'))

      // 宽度不应该改变
      expect(vm.editorWidth).toBe(initialWidth)
    })

    it('触摸拖动应该正确更新宽度', async () => {
      const wrapper = mount(MarkdownEditorView, {
        global: {
          stubs: {
            PreviewPanel: true,
          },
        },
        attachTo: document.body,
      })

      const vm = wrapper.vm as any

      // 模拟触摸开始
      await vm.startResize(new TouchEvent('touchstart'))

      // 创建容器mock
      const container = wrapper.find('.editor-container').element as HTMLElement
      vi.spyOn(container, 'getBoundingClientRect').mockReturnValue({
        left: 0,
        width: 1000,
        top: 0,
        height: 500,
        right: 1000,
        bottom: 500,
        toJSON: () => ({}),
      })

      // 触发touchmove
      const touchEvent = new TouchEvent('touchmove', {
        touches: [{ clientX: 400 } as Touch],
      })
      await vm.handleResize(touchEvent)
      await nextTick()

      // 验证宽度被更新（40%）
      expect(vm.editorWidth).toBe(40)

      // 清理
      wrapper.unmount()
    })

    it('触摸结束应该停止拖动', async () => {
      const wrapper = mount(MarkdownEditorView, {
        global: {
          stubs: {
            PreviewPanel: true,
          },
        },
      })

      const vm = wrapper.vm as any

      // 模拟触摸开始
      await vm.startResize(new TouchEvent('touchstart'))
      expect(vm.isResizing).toBe(true)

      // 触发touchend
      await vm.stopResize()

      // 应该停止拖动
      expect(vm.isResizing).toBe(false)
    })
  })

  describe('组件生命周期', () => {
    it('组件挂载时应该初始化编辑器', async () => {
      const wrapper = mount(MarkdownEditorView, {
        global: {
          stubs: {
            PreviewPanel: true,
          },
        },
      })

      await nextTick()

      const vm = wrapper.vm as any
      // 验证编辑器引用被设置
      expect(vm.editorRef).toBeTruthy()
    })

    it('组件卸载时应该清理编辑器', async () => {
      const wrapper = mount(MarkdownEditorView, {
        global: {
          stubs: {
            PreviewPanel: true,
          },
        },
      })

      await nextTick()

      const vm = wrapper.vm as any

      // 验证editorView存在
      expect(vm.editorView).toBeTruthy()

      // 卸载组件
      wrapper.unmount()

      // editorView应该被清理
      expect(vm.editorView).toBe(null)
    })
  })

  describe('边界情况', () => {
    it('清空时如果没有editorView不应该报错', async () => {
      mockConfirm.mockReturnValue(true)

      const wrapper = mount(MarkdownEditorView, {
        global: {
          stubs: {
            PreviewPanel: true,
          },
        },
      })

      const vm = wrapper.vm as any

      // 手动设置editorView为null
      vm.editorView = null

      // 找到清空按钮
      const clearButtons = wrapper.findAll('.toolbar-btn')
      const clearButton = clearButtons.find(btn => btn.text().includes('清空'))

      if (clearButton) {
        // 不应该抛出错误
        await expect(async () => {
          await clearButton.trigger('click')
        }).not.toThrow()
      }
    })

    it('拖动时如果没有容器不应该更新宽度', async () => {
      const wrapper = mount(MarkdownEditorView, {
        global: {
          stubs: {
            PreviewPanel: true,
          },
        },
      })

      const resizer = wrapper.find('.resizer')
      const vm = wrapper.vm as any

      await resizer.trigger('mousedown')

      // 确保没有.editor-container元素
      const existingContainer = document.querySelector('.editor-container')
      if (existingContainer) {
        existingContainer.remove()
      }

      const initialWidth = vm.editorWidth

      // 触发mousemove
      await window.dispatchEvent(new MouseEvent('mousemove'))

      // 宽度不应该改变
      expect(vm.editorWidth).toBe(initialWidth)
    })
  })
})
