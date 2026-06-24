// frontend/src/api/inverter.js
import service from '@/utils/request'

export const inverterApi = {
  // 厂家列表
  manufacturers: () => service.get('/api/inverters/manufacturers'),

  // 列表（支持厂家筛选 + 型号模糊搜索）
  list: (params) => service.get('/api/inverters', { params }),

  // 详情（含 Sandia 拟合参数）
  get: (id) => service.get(`/api/inverters/${id}`),

  // 修改
  update: (id, data) => service.put(`/api/inverters/${id}`, data),

  // 删除
  delete: (id) => service.delete(`/api/inverters/${id}`),

  // 上传 .OND 文件
  upload(file) {
    const form = new FormData()
    form.append('file', file)
    return service.post('/api/inverters/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}
