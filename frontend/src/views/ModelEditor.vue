<!-- frontend/src/views/ModelEditor.vue -->
<template>
  <div>

    <!-- 页头 -->
    <el-page-header @back="$router.push('/')" style="margin-bottom:24px;">
      <template #content>
        <span style="font-size:18px; font-weight:700;">
          {{ pageTitle }}
        </span>
      </template>
    </el-page-header>

    <el-row :gutter="20">

      <!-- 左侧：双编辑器 -->
      <el-col :span="16">
        <el-tabs v-model="activeTab" type="card">

          <!-- meta.py -->
          <el-tab-pane label="meta.py（模型元数据）" name="meta">
            <div style="margin-bottom:8px; color:#64748b; font-size:13px;">
              定义 MODEL_META 字典，描述模型名称、输入输出参数等信息
            </div>
            <CodeEditor v-model="metaCode" height="520px" @update:modelValue="onMetaChange" />
          </el-tab-pane>

          <!-- model.py -->
          <el-tab-pane label="model.py（执行逻辑）" name="model">
            <div style="margin-bottom:8px; color:#64748b; font-size:13px;">
              实现 run(inputs: dict) -> dict 函数，包含模型计算逻辑
            </div>
            <CodeEditor v-model="modelCode" height="520px" />
          </el-tab-pane>

        </el-tabs>
      </el-col>

      <!-- 右侧：操作面板 -->
      <el-col :span="8">

        <!-- 操作按钮 -->
        <el-card header="操作" style="margin-bottom:16px;">
          <el-space direction="vertical" style="width:100%;">

            <el-button type="warning" style="width:100%;" :loading="validating" @click="handleValidate">
              校验 meta.py
            </el-button>

            <el-button type="primary" style="width:100%;" :loading="saving" :disabled="!validatePassed"
              @click="handleSave">
              <!-- saveButtonText：新增模型时显示"发布模型"，编辑时显示"保存并更新" -->
              {{ saveButtonText }}
            </el-button>

            <el-button style="width:100%;" @click="loadTemplate">
              加载模板代码
            </el-button>

          </el-space>

          <el-divider style="margin:12px 0;" />

          <div style="font-size:12px; color:#94a3b8; line-height:2;">
            <div style="display:flex; align-items:center; gap:6px;">
              <el-icon :style="{ color: validatePassed ? '#22c55e' : '#f87171' }">
                <CircleCheck v-if="validatePassed" />
                <CircleClose v-else />
              </el-icon>
              <!-- validateStatusText：显示"未校验" / "校验通过" / "校验失败" -->
              <span>meta.py — {{ validateStatusText }}</span>
            </div>
            <div style="display:flex; align-items:center; gap:6px;">
              <el-icon style="color:#94a3b8;">
                <InfoFilled />
              </el-icon>
              <span>model.py — 发布时自动校验</span>
            </div>
          </div>
        </el-card>

        <!-- 校验结果 -->
        <el-card header="校验结果" style="margin-bottom:16px;" v-if="validateResult">
          <el-result :icon="validateResult.valid ? 'success' : 'error'"
            :title="validateResult.valid ? '校验通过，可以发布' : '校验失败，请修正后重试'" style="padding:12px 0;">
            <template #extra>
              <div v-if="validateResult.errors?.length">
                <el-tag v-for="err in validateResult.errors" :key="err" type="danger"
                  style="display:block; margin-bottom:6px; white-space:normal; height:auto; line-height:1.6;">
                  <!-- err：每条错误信息 -->
                  {{ err }}
                </el-tag>
              </div>
              <div v-if="validateResult.warnings?.length" style="margin-top:8px;">
                <el-tag v-for="w in validateResult.warnings" :key="w" type="warning"
                  style="display:block; margin-bottom:6px; white-space:normal; height:auto; line-height:1.6;">
                  <!-- w：每条警告信息 -->
                  {{ w }}
                </el-tag>
              </div>
            </template>
          </el-result>
        </el-card>

        <!-- 模型信息预览 -->
        <el-card header="模型信息预览" v-if="parsedMeta">
          <el-descriptions :column="1" size="small" label-width="80px" border>

            <el-descriptions-item label="模型标识">
              <!-- parsedMeta.name：模型唯一标识符 -->
              <code style="color:#0369a1;">{{ parsedMeta.name }}</code>
            </el-descriptions-item>

            <el-descriptions-item label="标题">
              <!-- parsedMeta.title：模型中文标题 -->
              {{ parsedMeta.title }}
            </el-descriptions-item>

            <el-descriptions-item label="版本">
              <!-- parsedMeta.version：版本号 -->
              {{ parsedMeta.version }}
            </el-descriptions-item>

            <el-descriptions-item label="输入参数">
              <!-- parsedMeta.inputCount：输入参数个数 -->
              {{ parsedMeta.inputCount }} 个
            </el-descriptions-item>

            <el-descriptions-item label="输出参数">
              <!-- parsedMeta.outputCount：输出参数个数 -->
              {{ parsedMeta.outputCount }} 个
            </el-descriptions-item>

            <el-descriptions-item label="API 路径">
              <!-- parsedMeta.name：拼接 API 路径 -->
              <code style="color:#059669;">POST /api/run/{{ parsedMeta.name }}</code>
            </el-descriptions-item>

          </el-descriptions>
        </el-card>

      </el-col>

    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { CircleCheck, CircleClose, InfoFilled } from '@element-plus/icons-vue'
import CodeEditor from '../components/CodeEditor.vue'
import { modelApi } from '../api/index.js'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.name)
const activeTab = ref('meta')
const metaCode = ref('')
const modelCode = ref('')
const validating = ref(false)
const saving = ref(false)
const validateResult = ref(null)
const validatePassed = ref(false)
const parsedMeta = ref(null)

// ✅ 页面标题
const pageTitle = computed(() =>
  isEdit.value ? `编辑模型：${route.params.name}` : '新增模型'
)

// ✅ 按钮文字
const saveButtonText = computed(() =>
  isEdit.value ? '保存并更新' : '发布模型'
)

// ✅ meta.py 校验状态文字
const validateStatusText = computed(() => {
  if (validatePassed.value) return '校验通过'
  if (validateResult.value && !validateResult.value.valid) return '校验失败'
  return '未校验'
})

// ── 生命周期：编辑模式加载已有代码 ──────────────────────────────

onMounted(async () => {
  if (isEdit.value) {
    try {
      const res = await modelApi.get(route.params.name)
      const data = res.data

      // ✅ 正确读取后端返回的源码字段
      metaCode.value = data.meta_code || ''
      modelCode.value = data.model_code || ''

      if (metaCode.value) {
        onMetaChange(metaCode.value)
      }
    } catch (e) {
      ElMessage.error('加载模型数据失败')
    }
  } else {
    loadTemplate()
  }
})

// ── meta 代码变化时实时解析预览 ──────────────────────────────────

function onMetaChange(code) {
  validatePassed.value = false
  validateResult.value = null

  try {
    const nameMatch = code.match(/"name"\s*:\s*"([^"]+)"/)
    const titleMatch = code.match(/"title"\s*:\s*"([^"]+)"/)
    const versionMatch = code.match(/"version"\s*:\s*"([^"]+)"/)

    const inputsBlock = code.match(/"inputs"\s*:\s*$$([\s\S]*?)$$/)?.[1] || ''
    const outputsBlock = code.match(/"outputs"\s*:\s*$$([\s\S]*?)$$/)?.[1] || ''

    const inputCount = (inputsBlock.match(/"name"\s*:/g) || []).length
    const outputCount = (outputsBlock.match(/"name"\s*:/g) || []).length

    if (nameMatch) {
      parsedMeta.value = {
        name: nameMatch[1],
        title: titleMatch?.[1] || '',
        version: versionMatch?.[1] || '1.0.0',
        inputCount,
        outputCount,
      }
    } else {
      parsedMeta.value = null
    }
  } catch {
    parsedMeta.value = null
  }
}

// ── 校验 meta.py ─────────────────────────────────────────────────

async function handleValidate() {
  if (!metaCode.value.trim()) {
    ElMessage.warning('meta.py 内容不能为空')
    return
  }

  validating.value = true
  try {
    const res = await modelApi.validate(metaCode.value)
    validateResult.value = res.data
    validatePassed.value = res.data.valid

    if (res.data.valid) {
      ElMessage.success('meta.py 校验通过，可以发布')
    } else {
      const firstErr = res.data.errors?.[0] || '请检查代码'
      ElMessage.error(`校验失败：${firstErr}`)
    }
  } catch {
    ElMessage.error('校验请求失败，请检查后端服务')
  } finally {
    validating.value = false
  }
}

// ── 保存并发布 ───────────────────────────────────────────────────

async function handleSave() {
  if (!validatePassed.value) {
    ElMessage.warning('请先通过 meta.py 校验')
    return
  }

  if (!modelCode.value.trim()) {
    ElMessage.warning('model.py 内容不能为空')
    activeTab.value = 'model'
    return
  }

  saving.value = true
  try {
    const res = await modelApi.upload({
      meta_code: metaCode.value,
      model_code: modelCode.value,
    })

    ElMessage.success(res.message || '模型已发布，API 已自动注册！')
    router.push('/')
  } catch (e) {
    const detail = e.response?.data?.detail

    if (detail?.message === 'model.py 校验失败') {
      const firstErr = detail.errors?.[0] || ''
      ElMessage.error(`model.py 校验失败：${firstErr}`)
      activeTab.value = 'model'
    } else if (detail?.message === 'meta.py 校验失败') {
      const firstErr = detail.errors?.[0] || ''
      ElMessage.error(`meta.py 校验失败：${firstErr}`)
      activeTab.value = 'meta'
      validatePassed.value = false
    } else {
      ElMessage.error(typeof detail === 'string' ? detail : '发布失败，请检查代码')
    }
  } finally {
    saving.value = false
  }
}

// ── 加载模板代码 ─────────────────────────────────────────────────

function loadTemplate() {
  metaCode.value = `MODEL_META = {
    "name": "my_model",
    "title": "我的光伏模型",
    "version": "1.0.0",
    "description": "模型描述",
    "author": "PV Team",
    "category": "未分类",
    "related_models": {
        "pre": [],
        "post": [],
        "depends_on": [],
        "conflicts_with": []
    },
    "inputs": [
        {
            "name": "param1",
            "type": "float",
            "required": True,
            "min": 0.0,
            "description": "参数1说明"
        },
    ],
    "outputs": [
        {
            "name": "result",
            "type": "float",
            "unit": "",
            "description": "计算结果"
        },
    ],
    "tags": ["custom"],
    "execution": {
        "timeout": 30,
        "cacheable": False,
    },
}`

  modelCode.value = `def run(inputs: dict) -> dict:
    """
    模型执行入口，禁止修改函数签名。
    inputs: 由网关根据 MODEL_META.inputs 注入并校验后的参数字典
    return: 必须为 dict，key 与 MODEL_META.outputs 对应
    """
    param1 = inputs["param1"]

    # ====== 在此编写模型计算逻辑 ======
    result = param1 * 2.0
    # ==================================

    return {
        "result": result,
    }
`

  validateResult.value = null
  validatePassed.value = false
  parsedMeta.value = null
  activeTab.value = 'meta'

  onMetaChange(metaCode.value)
}
</script>
