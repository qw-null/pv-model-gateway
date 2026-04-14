import { defineStore } from 'pinia'
import { ref } from 'vue'
import { modelApi } from '../api/index.js'

export const useModelStore = defineStore('model', () => {
  const models = ref([])
  const loading = ref(false)

  async function fetchModels() {
    loading.value = true
    try {
      const res = await modelApi.list()
      models.value = res.data
      console.log('数据来了',res);
      
    } finally {
      loading.value = false
    }
  }

  return { models, loading, fetchModels }
})
