// frontend/src/stores/modelStore.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { modelApi } from '../api/index.js'

export const useModelStore = defineStore('model', () => {
  const models  = ref([])
  const loading = ref(false)

  // 保持原有签名兼容，支持传入 params（其他页面无感知）
  async function fetchModels(params = {}) {
    loading.value = true
    try {
      const res = await modelApi.list(params)
      // 兼容新旧两种返回结构
      models.value = res.data?.data ?? res.data ?? []
    } finally {
      loading.value = false
    }
  }

  return { models, loading, fetchModels }
})
