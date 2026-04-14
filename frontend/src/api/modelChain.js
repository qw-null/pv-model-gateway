import request from '@/utils/request'

export function getAllModels() {
  return request({
    url: '/api/models',
    method: 'GET'
  })
}

// 获取某分类下的模型列表
export function getModelsByCategory(category) {
  return request({
    url: '/api/models',
    method: 'get',
    params: { category }
  })
}

// 获取单个模型详情（含 meta 完整信息）
export function getModelDetail(modelName) {
  return request({
    url: `/api/models/${modelName}`,
    method: 'get'
  })
}



