// src/api/modelChain.js  ── 改用 service，复用拦截器
import service from '@/utils/request'

export function getAllModels() {
  return service({ url: '/api/models', method: 'GET' })
}

export function getModelsByCategory(category) {
  return service({ url: '/api/models', method: 'GET', params: { category } })
}

export function getModelDetail(modelName) {
  return service({ url: `/api/models/${modelName}`, method: 'GET' })
}
