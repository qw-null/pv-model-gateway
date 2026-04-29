// src/api/panel.js
import service from '@/utils/request'

export const panelApi = {
  // 上传 .pan 文件
  upload(file) {
    const form = new FormData()
    form.append('file', file)
    return service.post('/api/panels/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // 列表
  list:   (params)           => service.get('/api/panels', { params }),

  // 厂家列表
  manufacturers: () => service.get('/api/panels/manufacturers'),

  // 详情
  get:    (id)         => service.get(`/api/panels/${id}`),

  // 修改
  update: (id, data)   => service.put(`/api/panels/${id}`, data),

  // 删除
  delete: (id)         => service.delete(`/api/panels/${id}`),

  // 新增
  getCurves: (id, data) => service.post(`/api/panels/${id}/curves`, data),

}
