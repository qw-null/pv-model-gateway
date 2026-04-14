// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

import ModelList from '../views/ModelList.vue'
import ModelEditor from '../views/ModelEditor.vue'
import ModelDebug from '../views/ModelDebug.vue'
import ModelStats from '../views/ModelStats.vue'
import ModelChain from '../views/ModelChain.vue'

const routes = [

  // ── 独立页面（无侧边栏）──────────────────────────────────────
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false },
  },

  // ── 主布局页面（含侧边栏 + 顶部导航）────────────────────────
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'ModelList',
        component: ModelList,
        meta: { title: '模型列表', requiresAuth: true },
      },
      {
        path: 'editor',
        name: 'ModelCreate',
        component: ModelEditor,
        meta: { title: '新增模型', requiresAuth: true },
      },
      {
        path: 'editor/:name',
        name: 'ModelEdit',
        component: ModelEditor,
        meta: { title: '编辑模型', requiresAuth: true },
      },
      {
        path: 'debug/:name',
        name: 'ModelDebug',
        component: ModelDebug,
        meta: { title: '调试模型', requiresAuth: true },
      },
      {
        path: 'stats',
        name: 'ModelStats',
        component: ModelStats,
        meta: { title: '模型统计', requiresAuth: true },
      },
      {
        path: 'model-chain',
        name: 'ModelChain',
        component: ModelChain,
        meta: { title: '模型链', requiresAuth: true },
      },
      {
        path: 'profile',
        name: 'UserProfile',
        component: () => import('@/views/UserProfile.vue'),
        meta: { title: '个人信息', requiresAuth: true },
      }
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// ── 全局前置守卫 ──────────────────────────────────────────────
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const requiresAuth = to.matched.some(r => r.meta.requiresAuth !== false)

  if (requiresAuth && !token) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router
