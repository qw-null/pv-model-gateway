// src/api/index.js
import service from '@/utils/request'
import { ElMessage } from 'element-plus'

// ── 统一错误提示（复用原有逻辑）────────────────────────────────
// 注意：utils/request.js 的响应拦截器已处理 401 跳转
// 此处仅保留业务层的 ElMessage 提示兜底
service.interceptors.response.use(
  res => res,
  err => {
    const msg = err.response?.data?.detail?.message
      || err.response?.data?.detail
      || err.message
      || '请求失败'
    ElMessage.error(typeof msg === 'string' ? msg : JSON.stringify(msg))
    return Promise.reject(err)
  }
)

// ── 模型接口 ───────────────────────────────────────────────────
export const modelApi = {
  // 模型 CRUD
  list: (params) => service.get('/api/models', { params }),
  get: (name) => service.get(`/api/models/${name}`),
  getByModelId: (modelId) => service.get(`/api/models/by-model-id/${modelId}`),
  validate: (code) => service.post('/api/models/validate', { code }),
  upload: (data) => service.post('/api/models/upload', data),
  delete: (name) => service.delete(`/api/models/${name}`),
  reload: (name) => service.post(`/api/models/${name}/reload`),
  run: (name, body) => service.post(`/api/run/${name}`, body),
  logs: (name, limit) => service.get(`/api/models/${name}/logs`, { params: { limit } }),

  // 关系管理
  updateRelations: (name, body) => service.put(`/api/models/${name}/relations`, body),

  // 分类
  categories: () => service.get('/api/models/categories/list'),
  modelsByCategory: (category) => service.get(`/api/models/categories/${category}`),

  // 统计
  statsOverview: () => service.get('/api/models/stats/overview'),
  getAllNames: () => service.get('/api/models/all-names'),

  

}
