<template>
  <div>
    <el-page-header @back="$router.push('/')" style="margin-bottom:24px">
      <template #content>
        <span style="font-size:18px; font-weight:700">
          调试模型：{{ modelMeta?.title || route.params.name }}
        </span>
        <el-tag type="success" style="margin-left:12px" v-if="modelMeta">
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
              <div style="display:flex; justify-content:space-between; align-items:center">
                <span style="font-weight:600">输入参数</span>
                <el-tag>POST /api/run/{{ route.params.name }}</el-tag>
              </div>
            </template>

            <!-- 组件选择器（仅含 panel 字段的模型显示） -->
            <template v-if="hasPanelInputs">
              <div class="panel-selector-block">
                <div class="panel-selector-title">
                  <el-icon style="color:#f5a623">
                    <Connection />
                  </el-icon>
                  光伏组件选择
                </div>
                <div class="panel-selector-row">
                  <el-select v-model="selectedManufacturer" placeholder="选择厂家" clearable style="width:130px"
                    @change="onManufacturerChange">
                    <el-option v-for="m in manufacturerOptions" :key="m" :label="m" :value="m" />
                  </el-select>

                  <el-select v-model="selectedPanelId" placeholder="选择型号" clearable filterable style="flex:1"
                    :disabled="!selectedManufacturer" @change="onPanelChange">
                    <el-option v-for="p in panelOptions" :key="p.id" :label="p.model_name" :value="p.id" />
                  </el-select>

                  <el-button :disabled="!selectedPanelId" :type="selectedPanelId ? 'warning' : 'default'"
                    @click="openPanelDetail">详情</el-button>
                </div>

                <!-- 已选信息条 -->
                <div v-if="selectedPanel" class="panel-info-bar">
                  <el-icon>
                    <CircleCheck />
                  </el-icon> 已选：
                  <strong>{{ selectedPanel.manufacturer }}</strong> 
                  · 
                  <strong>{{ selectedPanel.model_name}}</strong> 
                  <span class="panel-info-meta"> 
                    Pmp 
                    <strong>{{ selectedPanel.pmp_calc }}</strong> 
                    W &nbsp;|&nbsp; Vmp 
                    <strong>{{ selectedPanel.vmp_calc }}</strong> 
                    V &nbsp;|&nbsp; Imp 
                    <strong>{{selectedPanel.imp_calc }}</strong> 
                    A 
                  </span>
                  <el-button link type="danger" size="small" style="margin-left:auto" @click="clearPanel">清除</el-button>
                </div>
              </div>
              <el-divider style="margin:12px 0" />
            </template>

            <ParamForm :inputs="modelMeta.inputs" :overrides="panelOverrides" @update:formData="formData = $event" />

            <el-divider />
            <el-button type="primary" size="large" style="width:100%" :loading="running" @click="handleRun">
              执行模型
            </el-button>

            <el-collapse style="margin-top:16px">
              <el-collapse-item title="查看请求体 JSON">
                <pre style="background:#f8fafc; padding:12px; border-radius:6px;
                  font-size:13px; overflow:auto">{{ JSON.stringify(formData, null, 2) }}</pre>
              </el-collapse-item>
            </el-collapse>
          </el-card>
        </el-col>

        <!-- 右侧：执行结果 -->
        <el-col :span="14">
          <el-card>
            <template #header><span style="font-weight:600">执行结果</span></template>
            <ResultDisplay :result="runResult" :error="runError" :outputs="modelMeta.outputs" />
          </el-card>

          <el-card style="margin-top:16px">
            <template #header><span style="font-weight:600">模型说明</span></template>
            <p style="color:#64748b">{{ modelMeta.description }}</p>
            <el-divider />
            <el-descriptions :column="2" size="small">
              <el-descriptions-item label="作者">{{ modelMeta.author || '—' }}</el-descriptions-item>
              <el-descriptions-item label="版本">
                <el-tag type="success">{{ modelMeta.version }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="分类">
                <el-tag>{{ modelMeta.category }}</el-tag>
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

    <!-- 组件详情抽屉 -->
    <el-drawer v-model="detailDrawerVisible" title="组件详情" size="720px" destroy-on-close>
      <PanelDetail v-if="selectedPanel" :panel="selectedPanel" @updated="onPanelUpdated" />
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Connection, CircleCheck } from '@element-plus/icons-vue'
import ParamForm from '../components/ParamForm.vue'
import ResultDisplay from '../components/ResultDisplay.vue'
import PanelDetail from '../components/PanelDetail.vue'
import { modelApi } from '../api/index.js'
import { panelApi } from '../api/panel.js'

const route = useRoute()
const modelMeta = ref(null)
const formData = ref({})
const runResult = ref(null)
const runError = ref('')
const running = ref(false)
const pageLoading = ref(false)

// 是否含有 source=panel 字段 → 控制选择器显示
const hasPanelInputs = computed(() =>
  (modelMeta.value?.inputs || []).some(inp => inp.source === 'panel')
)

// panel 字段映射表：formFieldName → panelFieldName
const panelFieldMap = computed(() => {
  const map = {}
    ; (modelMeta.value?.inputs || [])
      .filter(inp => inp.source === 'panel')
      .forEach(inp => { map[inp.name] = inp.panel_field || inp.name })
  return map
})

const manufacturerOptions = ref([])
const panelOptions = ref([])
const selectedManufacturer = ref('')
const selectedPanelId = ref(null)
const selectedPanel = ref(null)
const detailDrawerVisible = ref(false)

// 注入 ParamForm 的覆盖值（来自选中组件）
const panelOverrides = computed(() => {
  if (!selectedPanel.value) return {}
  const overrides = {}
  Object.entries(panelFieldMap.value).forEach(([formKey, panelKey]) => {
    const val = selectedPanel.value[panelKey]
    if (val !== undefined && val !== null) overrides[formKey] = val
  })
  return overrides
})

onMounted(async () => {
  pageLoading.value = true
  try {
    const res = await modelApi.get(route.params.name)
    modelMeta.value = res.data
  } finally {
    pageLoading.value = false
  }
})

// 懒加载厂家列表
async function ensureManufacturers() {
  if (manufacturerOptions.value.length > 0) return
  try {
    const res = await panelApi.manufacturers()
    manufacturerOptions.value = res.data?.data ?? res.data ?? []
  } catch { }
}
watch(hasPanelInputs, val => { if (val) ensureManufacturers() }, { immediate: true })

async function onManufacturerChange(manufacturer) {
  selectedPanelId.value = null
  selectedPanel.value = null
  panelOptions.value = []
  if (!manufacturer) return
  try {
    const res = await panelApi.list({ manufacturer, page: 1, page_size: 200 })
    panelOptions.value = res.data
  } catch { }
}

async function onPanelChange(panelId) {
  selectedPanel.value = null
  if (!panelId) return
  try {
    const res = await panelApi.get(panelId)
    selectedPanel.value = res.data
    console.log('Selected panel details:', selectedPanel.value)
  } catch { ElMessage.error('获取组件详情失败') }
}

function clearPanel() {
  selectedManufacturer.value = ''
  selectedPanelId.value = null
  selectedPanel.value = null
  panelOptions.value = []
  
}

function openPanelDetail() {
  if (selectedPanel.value) detailDrawerVisible.value = true
}

function onPanelUpdated(updated) {
  selectedPanel.value = updated
  detailDrawerVisible.value = false
}

// ── 执行：直接发送 formData，后端接收完整参数 ──
async function handleRun() {
  running.value = true
  runResult.value = null
  runError.value = ''
  try {
    const res = await modelApi.run(route.params.name, formData.value)
    runResult.value = res
  } catch (e) {
    runError.value = e.response?.data?.detail || e.message || '执行失败'
    ElMessage.error(runError.value)
  } finally {
    running.value = false
  }
}
</script>

<style scoped>
.panel-selector-block {
  background: #fffdf5;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 12px 14px;
  margin-bottom: 4px;
}

.panel-selector-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  font-size: 13px;
  color: #92400e;
  margin-bottom: 10px;
}

.panel-selector-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.panel-info-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  font-size: 12px;
  color: #92400e;
  background: #fef9c3;
  border-radius: 4px;
  padding: 5px 8px;
}

.panel-info-meta {
  margin-left: 8px;
  color: #b45309;
  font-size: 11px;
}
</style>
