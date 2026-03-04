/**
 * SidebarMenu组件单元测试
 */
import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import SidebarMenu from '@/components/SidebarMenu.vue';

// Mock MenuItem组件
vi.mock('@/components/MenuItem.vue', () => ({
  default: {
    name: 'MenuItem',
    props: ['item', 'activeId'],
    emits: ['click'],
    template: `
      <div class="menu-item-mock">
        <span class="item-label">{{ item.label }}</span>
        <span class="item-id">{{ item.id }}</span>
        <span class="active-id">{{ activeId }}</span>
        <button @click="$emit('click', item.id)">Click</button>
      </div>
    `,
  },
}));

describe('SidebarMenu', () => {
  it('should render menu list when not collapsed', () => {
    const wrapper = mount(SidebarMenu);

    expect(wrapper.find('.menu-list').exists()).toBe(true);
    expect(wrapper.find('.sidebar-menu').classes()).not.toContain('collapsed');
  });

  it('should not render menu list when collapsed', async () => {
    const wrapper = mount(SidebarMenu);

    // 初始状态未折叠
    expect(wrapper.find('.menu-list').exists()).toBe(true);

    // 切换到折叠状态
    await wrapper.find('.collapse-button').trigger('click');
    await wrapper.vm.$nextTick();

    // 折叠后不应该显示菜单列表
    expect(wrapper.find('.menu-list').exists()).toBe(false);
    expect(wrapper.find('.sidebar-menu').classes()).toContain('collapsed');
  });

  it('should render all menu items', () => {
    const wrapper = mount(SidebarMenu);

    const menuItems = wrapper.findAll('.menu-item-mock');
    // 应该有4个菜单项：text-gen, image-gen, video-gen, agents
    expect(menuItems.length).toBe(4);
  });

  it('should render chevron left icon when not collapsed', () => {
    const wrapper = mount(SidebarMenu);

    // 未折叠状态应该显示左箭头
    expect(wrapper.find('.collapse-button').exists()).toBe(true);
  });

  it('should toggle collapse state on button click', async () => {
    const wrapper = mount(SidebarMenu);

    // 初始状态
    expect(wrapper.vm.isCollapsed).toBe(false);

    // 点击按钮
    await wrapper.find('.collapse-button').trigger('click');
    await wrapper.vm.$nextTick();

    // 应该切换到折叠状态
    expect(wrapper.vm.isCollapsed).toBe(true);
  });

  it('should emit collapse-change event with true when collapsed', async () => {
    const wrapper = mount(SidebarMenu);

    await wrapper.find('.collapse-button').trigger('click');
    await wrapper.vm.$nextTick();

    expect(wrapper.emitted('collapse-change')).toBeTruthy();
    expect(wrapper.emitted('collapse-change')![0]).toEqual([true]);
  });

  it('should emit collapse-change event with false when expanded', async () => {
    const wrapper = mount(SidebarMenu);

    // 第一次点击：折叠
    await wrapper.find('.collapse-button').trigger('click');
    await wrapper.vm.$nextTick();

    // 第二次点击：展开
    await wrapper.find('.collapse-button').trigger('click');
    await wrapper.vm.$nextTick();

    // 应该有两个事件
    expect(wrapper.emitted('collapse-change')!.length).toBe(2);

    // 第二个事件应该是false（展开）
    expect(wrapper.emitted('collapse-change')![1]).toEqual([false]);
  });

  it('should have default active menu item', () => {
    const wrapper = mount(SidebarMenu);

    expect(wrapper.vm.activeMenuItemId).toBe('prompt-wizard');
  });

  it('should update active menu item when clicked', async () => {
    const wrapper = mount(SidebarMenu);

    // 初始激活项
    expect(wrapper.vm.activeMenuItemId).toBe('prompt-wizard');

    // 点击第一个菜单项
    const firstMenuItem = wrapper.findAll('.menu-item-mock')[0];
    await firstMenuItem.find('button').trigger('click');

    // 激活项应该更新
    expect(wrapper.vm.activeMenuItemId).toBe('text-gen');
  });

  it('should pass correct activeId to MenuItem components', () => {
    const wrapper = mount(SidebarMenu);

    const menuItems = wrapper.findAll('.menu-item-mock');

    // 所有MenuItem组件都应该接收到activeId
    menuItems.forEach(item => {
      expect(item.find('.active-id').text()).toBe('prompt-wizard');
    });
  });

  it('should render menu items in correct order', () => {
    const wrapper = mount(SidebarMenu);

    const menuItems = wrapper.findAll('.menu-item-mock');

    expect(menuItems[0].find('.item-label').text()).toBe('文生文');
    expect(menuItems[1].find('.item-label').text()).toBe('文生图');
    expect(menuItems[2].find('.item-label').text()).toBe('文生视频');
    expect(menuItems[3].find('.item-label').text()).toBe('智能体');
  });

  it('should have correct menu item IDs', () => {
    const wrapper = mount(SidebarMenu);

    const menuItems = wrapper.findAll('.menu-item-mock');

    expect(menuItems[0].find('.item-id').text()).toBe('text-gen');
    expect(menuItems[1].find('.item-id').text()).toBe('image-gen');
    expect(menuItems[2].find('.item-id').text()).toBe('video-gen');
    expect(menuItems[3].find('.item-id').text()).toBe('agents');
  });

  it('should handle multiple menu item clicks correctly', async () => {
    const wrapper = mount(SidebarMenu);

    const menuItems = wrapper.findAll('.menu-item-mock');

    // 点击第一个
    await menuItems[0].find('button').trigger('click');
    expect(wrapper.vm.activeMenuItemId).toBe('text-gen');

    // 点击第二个
    await menuItems[1].find('button').trigger('click');
    expect(wrapper.vm.activeMenuItemId).toBe('image-gen');

    // 点击第四个
    await menuItems[3].find('button').trigger('click');
    expect(wrapper.vm.activeMenuItemId).toBe('agents');
  });

  it('should toggle collapse state multiple times', async () => {
    const wrapper = mount(SidebarMenu);

    // 初始状态
    expect(wrapper.vm.isCollapsed).toBe(false);

    // 第一次点击
    await wrapper.find('.collapse-button').trigger('click');
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.isCollapsed).toBe(true);

    // 第二次点击
    await wrapper.find('.collapse-button').trigger('click');
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.isCollapsed).toBe(false);

    // 第三次点击
    await wrapper.find('.collapse-button').trigger('click');
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.isCollapsed).toBe(true);
  });

  it('should emit collapse-change event on each toggle', async () => {
    const wrapper = mount(SidebarMenu);

    // 点击3次
    await wrapper.find('.collapse-button').trigger('click');
    await wrapper.vm.$nextTick();

    await wrapper.find('.collapse-button').trigger('click');
    await wrapper.vm.$nextTick();

    await wrapper.find('.collapse-button').trigger('click');
    await wrapper.vm.$nextTick();

    // 应该有3个事件
    expect(wrapper.emitted('collapse-change')!.length).toBe(3);

    // 事件值应该交替
    expect(wrapper.emitted('collapse-change')![0]).toEqual([true]);
    expect(wrapper.emitted('collapse-change')![1]).toEqual([false]);
    expect(wrapper.emitted('collapse-change')![2]).toEqual([true]);
  });

  it('should apply collapsed class correctly', async () => {
    const wrapper = mount(SidebarMenu);

    // 初始状态
    expect(wrapper.find('.sidebar-menu').classes()).not.toContain('collapsed');

    // 折叠
    await wrapper.find('.collapse-button').trigger('click');
    await wrapper.vm.$nextTick();
    expect(wrapper.find('.sidebar-menu').classes()).toContain('collapsed');

    // 展开
    await wrapper.find('.collapse-button').trigger('click');
    await wrapper.vm.$nextTick();
    expect(wrapper.find('.sidebar-menu').classes()).not.toContain('collapsed');
  });

  it('should not show menu list in DOM when collapsed', async () => {
    const wrapper = mount(SidebarMenu);

    // 初始状态应该显示
    expect(wrapper.find('.menu-list').exists()).toBe(true);

    // 折叠后不应该存在（因为v-if）
    await wrapper.find('.collapse-button').trigger('click');
    await wrapper.vm.$nextTick();

    expect(wrapper.find('.menu-list').exists()).toBe(false);

    // 展开后应该重新显示
    await wrapper.find('.collapse-button').trigger('click');
    await wrapper.vm.$nextTick();

    expect(wrapper.find('.menu-list').exists()).toBe(true);
  });

  it('should always render collapse button', async () => {
    const wrapper = mount(SidebarMenu);

    // 未折叠状态
    expect(wrapper.find('.collapse-button').exists()).toBe(true);

    // 折叠状态
    await wrapper.find('.collapse-button').trigger('click');
    await wrapper.vm.$nextTick();

    expect(wrapper.find('.collapse-button').exists()).toBe(true);

    // 展开状态
    await wrapper.find('.collapse-button').trigger('click');
    await wrapper.vm.$nextTick();

    expect(wrapper.find('.collapse-button').exists()).toBe(true);
  });
});
