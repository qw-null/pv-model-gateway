import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

http.interceptors.response.use(
  res => res.data,
  err => {
    const msg = err.response?.data?.detail?.message
      || err.response?.data?.detail
      || err.message
      || '请求失败'
    ElMessage.error(typeof msg === 'string' ? msg : JSON.stringify(msg))
    return Promise.reject(err)
  }
)

export const modelApi = {
  // 模型 CRUD
  list: (params) => http.get('/models', { params }),
  get: (name) => http.get(`/models/${name}`),
  getByModelId: (modelId) => http.get(`/models/by-model-id/${modelId}`),
  validate: (code) => http.post('/models/validate', { code }),
  upload: (data) => http.post('/models/upload', data),
  delete: (name) => http.delete(`/models/${name}`),
  reload: (name) => http.post(`/models/${name}/reload`),
  run: (name, body) => http.post(`/run/${name}`, body),
  logs: (name, limit) => http.get(`/models/${name}/logs`, { params: { limit } }),

  // 关系管理
  updateRelations: (name, data) => http.put(`/models/${name}/relations`, data),

  // 分类
  categories: () => http.get('/models/categories/list'),
  modelsByCategory: (category) => http.get(`/models/categories/${encodeURIComponent(category)}`),

  // 统计
  statsOverview: () => http.get('/models/stats/overview'),

  getAllNames:()=>http.get('/models/all-names'),
  updateRelations:(name, body)=>http.put(`/models/${name}/relations`, body)

}
