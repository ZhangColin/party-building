/** 路由配置 */
import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import { useNavigationStore } from '../stores/navigationStore'

// 扩展路由meta类型
declare module 'vue-router' {
  interface RouteMeta {
    requiresAdmin?: boolean
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    redirect: '/modules/party-ai',
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginPage.vue'),
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('../layouts/AdminLayout.vue'),
    redirect: '/admin/users',
    meta: { requiresAdmin: true },
    children: [
      {
        path: 'users',
        name: 'admin-users',
        component: () => import('../views/admin/AdminUsersPage.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: 'tool-categories',
        name: 'admin-tool-categories',
        component: () => import('../views/admin/AdminToolCategoriesPage.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: 'common-tools',
        name: 'admin-common-tools',
        component: () => import('../views/admin/AdminCommonToolsPage.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: 'work-categories',
        name: 'admin-work-categories',
        component: () => import('../views/admin/AdminWorkCategoriesPage.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: 'works',
        name: 'admin-works',
        component: () => import('../views/admin/AdminWorksPage.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: 'course-categories',
        name: 'admin-course-categories',
        component: () => import('../views/admin/AdminCourseCategoriesPage.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: 'course-documents',
        name: 'admin-course-documents',
        component: () => import('../views/admin/AdminCourseDocumentsPage.vue'),
        meta: { requiresAdmin: true },
      },
      // 党建业务管理模块
      {
        path: 'party-members',
        name: 'admin-party-members',
        component: () => import('../views/admin/PartyMembersPage.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: 'organization-life',
        name: 'admin-organization-life',
        component: () => import('../views/admin/OrganizationLifePage.vue'),
        meta: { requiresAdmin: true },
      },
      {
        path: 'party-fees',
        name: 'admin-party-fees',
        component: () => import('../views/admin/PartyFeesPage.vue'),
        meta: { requiresAdmin: true },
      },
    ],
  },
  {
    path: '/modules/:moduleId',
    name: 'module',
    component: () => import('../layouts/MainLayout.vue'),
    props: true,
  },
  {
    path: '/media/:toolId',
    name: 'media-chat',
    component: () => import('../views/MediaChatView.vue'),
    props: true,
  },
  {
    path: '/common-tools',
    name: 'common-tools',
    component: () => import('../layouts/CommonToolsLayout.vue'),
    children: [
      {
        path: '',
        name: 'common-tools-home',
        component: () => import('../views/CommonToolsView.vue'),
      },
      {
        path: 'markdown-editor',
        name: 'markdown-editor',
        component: () => import('../views/MarkdownEditorView.vue'),
      },
      {
        path: 'html/:toolId',
        name: 'html-tool',
        component: () => import('../views/HtmlToolView.vue'),
        props: true,
      },
    ],
  },
  {
    path: '/works',
    name: 'works',
    component: () => import('../layouts/WorksLayout.vue'),
    children: [
      {
        path: '',
        name: 'works-display',
        component: () => import('../views/WorksDisplayPage.vue'),
      },
      {
        path: ':workId',
        name: 'work-detail',
        component: () => import('../views/WorkDetailPage.vue'),
        props: true,
      },
    ],
  },
  {
    path: '/documents',
    name: 'documents',
    component: () => import('../layouts/DocumentsLayout.vue'),
    children: [
      {
        path: '',
        name: 'documents-page',
        component: () => import('../views/DocumentsPage.vue'),
      },
    ],
  },
  // 保留原有路由（后续处理）
  {
    path: '/agents',
    name: 'agent-list',
    component: () => import('../views/AgentListView.vue'),
  },
  {
    path: '/agent/:agentId',
    name: 'agent-detail',
    component: () => import('../views/AgentDetailView.vue'),
    props: true,
  },
]

const router = createRouter({
  history: createWebHashHistory(), // 使用 Hash 模式，刷新页面不会 404
  routes,
})

// 公开路由（不需要登录即可访问）
const publicRoutes = ['/login']

// 路由守卫
router.beforeEach(async (to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const authStore = useAuthStore()
  const navigationStore = useNavigationStore()

  // 如果是登录页
  if (to.path === '/login') {
    // 如果已登录，直接跳转到首页（不验证token，让后续请求自动处理）
    if (authStore.isAuthenticated) {
      next('/modules/party-ai')
      return
    }
    next()
    return
  }

  // 检查是否为公开路由
  if (publicRoutes.includes(to.path)) {
    next()
    return
  }

  // 需要登录的路由
  if (!authStore.isAuthenticated) {
    // 未登录，跳转到登录页，并记录原访问页面
    next({
      path: '/login',
      query: { redirect: to.fullPath },
    })
    return
  }

  // 预加载导航配置（避免刷新时白屏）
  // 如果是 /modules/* 路由，确保导航配置已加载
  if (to.path.startsWith('/modules/') && !navigationStore.isLoaded) {
    try {
      await navigationStore.loadNavigation()
    } catch (error) {
      console.error('加载导航配置失败:', error)
      // 即使失败也继续导航（navigationStore 会使用默认配置）
    }
  }

  // 检查是否需要管理员权限
  if (to.meta.requiresAdmin) {
    // 如果用户信息不存在，先获取用户信息
    if (!authStore.user) {
      try {
        await authStore.fetchUserInfo()
      } catch (error) {
        // 获取用户信息失败，跳转到登录页
        next('/login')
        return
      }
    }

    // 检查是否为管理员
    if (!authStore.user?.is_admin) {
      // 非管理员，跳转到首页
      next('/modules/party-ai')
      return
    }
  }

  // 已登录，直接放行（token验证交给API响应拦截器处理）
  // 如果token无效，响应拦截器会自动清除并跳转到登录页
  next()
})

export default router

