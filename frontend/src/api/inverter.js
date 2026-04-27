// src/api/inverter.js
import service from '@/utils/request'

export const inverterApi = {
  upload(file) {
    const form = new FormData()
    form.append('file', file)
    return service.post('/api/inverters/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  list:          (params) => service.get('/api/inverters', { params }),
  manufacturers: ()       => service.get('/api/inverters/manufacturers'),
  get:           (id)     => service.get(`/api/inverters/`),
  update:        (id, data) => service.put(`/api/inverters/`, data),
  delete:        (id)     => service.delete(`/api/inverters/`),
}
