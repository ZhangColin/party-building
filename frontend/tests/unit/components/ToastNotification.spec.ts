import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ToastNotification from '@/components/ToastNotification.vue'

describe('ToastNotification', () => {
  it('should show toast message', () => {
    const wrapper = mount(ToastNotification, {
      props: {
        show: true,
        message: '已复制到剪贴板'
      }
    })

    expect(wrapper.text()).toContain('已复制到剪贴板')
    expect(wrapper.find('.toast-notification').exists()).toBe(true)
  })

  it('should not show toast when show is false', () => {
    const wrapper = mount(ToastNotification, {
      props: {
        show: false,
        message: '已复制到剪贴板'
      }
    })

    expect(wrapper.find('.toast-notification').exists()).toBe(false)
  })
})
