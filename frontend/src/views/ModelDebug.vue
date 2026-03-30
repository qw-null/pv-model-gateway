<template>
  <div>
    <!-- 页头 -->
    <el-page-header @back="$router.push('/')" style="margin-bottom:24px;">
      <template #content>
        <span style="font-size:18px; font-weight:700;">
          调试模型：{{ modelMeta?.title || route.params.name }}
        </span>
        <el-tag type="success" style="margin-left:12px;" v-if="modelMeta">
          v{{ modelMeta.version }}
        </el-tag>
      </template>
    </el-page-header>

    <div v-if="modelMeta" v-loading="pageLoading">
      <el-row :gutter="24">
        <!-- 左侧：参数输入 -->
        <el-col :span="10">
          <el-card>
            <template #header>
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:600;">输入参数</span>
                <el-tag>POST /api/run/{{ route.params.name }}</el-tag>
              </div>
            </template>

            <ParamForm
              :inputs="modelMeta.inputs"
              @update:formData="formData = $event"
            />

            <el-divider />

            <el-button
              type="primary"
              size="large"
              style="width:100%;"
              :loading="running"
              @click="handleRun"
            >
              执行模型
            </el-button>

            <!-- 请求体预览 -->
            <el-collapse style="margin-top:16px;">
              <el-collapse-item title="查看请求体 JSON">
                <pre style="background:#f8fafc; padding:12px; border-radius:6px;
                            font-size:13px; overflow:auto;">{{ JSON.stringify(formData, null, 2) }}</pre>
              </el-collapse-item>
            </el-collapse>
          </el-card>
        </el-col>

        <!-- 右侧：执行结果 -->
        <el-col :span="14">
          <el-card>
            <template #header>
              <span style="font-weight:600;">执行结果</span>
            </template>
            <ResultDisplay
              :result="runResult"
              :error="runError"
              :outputs="modelMeta.outputs"
            />
          </el-card>

          <!-- 模型说明 -->
          <el-card style="margin-top:16px;">
            <template #header>
              <span style="font-weight:600;">模型说明</span>
            </template>
            <p style="color:#64748b;">{{ modelMeta.description }}</p>
            <el-divider />
            <el-descriptions :column="2" size="small">
              <el-descriptions-item label="作者">{{ modelMeta.author || '—' }}</el-descriptions-item>
              <el-descriptions-item label="版本">{{ modelMeta.version }}</el-descriptions-item>
              <el-descriptions-item label="标签">
                <el-tag
                  v-for="tag in modelMeta.tags"
                  :key="tag"
                  size="small"
                  style="margin-right:4px;"
                >{{ tag }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="超时">
                {{ modelMeta.execution?.timeout ?? 30 }}s
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <el-skeleton v-else :rows="8" animated />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import ParamForm      from '../components/ParamForm.vue'
import ResultDisplay  from '../components/ResultDisplay.vue'
import { modelApi }   from '../api/index.js'

const route       = useRoute()
const modelMeta   = ref(null)
const formData    = ref({})
const runResult   = ref(null)
const runError    = ref('')
const running     = ref(false)
const pageLoading = ref(false)

onMounted(async () => {
  pageLoading.value = true
  try {
    const res   = await modelApi.get(route.params.name)
    modelMeta.value = res.data
  } finally {
    pageLoading.value = false
  }
})

async function handleRun() {
  running.value  = true
  runResult.value = null
  runError.value  = ''
  try {
    const res     = await modelApi.run(route.params.name, formData.value)
    runResult.value = res
  } catch (e) {
    runError.value = e.response?.data?.detail || e.message || '执行失败'
    ElMessage.error(runError.value)
  } finally {
    running.value = false
  }
}
</script>
