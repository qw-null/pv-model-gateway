// src/utils/request.js
import axios from 'axios'
import router from '@/router'

// ── 基础配置 ──────────────────────────────────────────────────

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// ── 请求拦截器 ────────────────────────────────────────────────

service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('[request error]', error)
    return Promise.reject(error)
  }
)

// ── 响应拦截器 ────────────────────────────────────────────────

service.interceptors.response.use(
  response => {
    const res = response.data

    if (response.status === 200) {
      // 统一包装格式 → { code: 0, data: {...}, message: "ok" }
      if (res !== null && typeof res === 'object' && 'code' in res) {
        if (res.code === 0 || res.code === 200) {
          return res.data        // ✅ 直接返回 res.data，调用方用 res.data 取值
        } else {
          const msg = res.message || res.detail || '请求失败'
          console.error('[business error]', msg)
          return Promise.reject(new Error(msg))
        }
      }

      // FastAPI 直接返回数据对象，直接透传
      return res               // ✅ 直接返回 res，调用方用 res.data 取值
    }

    return Promise.reject(new Error(`HTTP 请求异常`))
  },
  error => {
    const status  = error.response?.status
    const detail  = error.response?.data?.detail
    const message = error.response?.data?.message

    const errMap = {
      400: '请求参数错误',
      401: '未授权，请重新登录',
      403: '无访问权限',
      404: '请求的资源不存在',
      422: `参数校验失败`,
      500: '服务器内部错误',
      502: '网关错误',
      503: '服务暂不可用',
    }

    const errMsg = detail || message || errMap[status] || `请求失败（${status}）`
    console.error(`[response error] HTTP ${status} -`, errMsg)

    // 401 自动清除 token 并跳转登录页
    if (status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('role')
      localStorage.removeItem('nickname')
      router.push({ path: '/login', query: { redirect: router.currentRoute.value.fullPath } })
    }

    return Promise.reject({
      status,
      message: errMsg,
      response: error.response
    })
  }
)

export default service
