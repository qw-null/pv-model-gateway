<template>
    <div class="page-container">
        <div class="docs-layout">
            <!-- 左侧导航 -->
            <div class="docs-sidebar">
                <div class="sidebar-title">
                    <el-icon>
                        <Document />
                    </el-icon> 模型 API 列表
                </div>
                <div class="sidebar-search">
                    <el-input v-model="searchKey" placeholder="搜索模型..." prefix-icon="Search" size="small" clearable />
                </div>
                <div class="sidebar-nav">
                    <div v-for="model in filteredModels" :key="model.id"
                        :class="['nav-item', { active: activeId === model.id }]" @click="selectModel(model.id)">
                        <span :class="['tag-category', `tag-${model.category}`]">
                            {{ categoryShort[model.category] || model.category }}
                        </span>
                        <span class="nav-name">{{ model.name }}</span>
                    </div>
                    <div v-if="!filteredModels.length" class="nav-empty">
                        无匹配结果
                    </div>
                </div>
            </div>

            <!-- 右侧文档内容 -->
            <div class="docs-content" v-loading="docLoading">
                <template v-if="currentModel">
                    <!-- 模型标题 -->
                    <div class="doc-header">
                        <div class="doc-title-row">
                            <h2 class="doc-title">{{ currentModel.name }}</h2>
                            <el-tag type="info" size="small">v{{ currentModel.version }}</el-tag>
                            <el-tag v-if="currentModel.isBuiltin" size="small">内置</el-tag>
                        </div>
                        <p class="doc-desc">{{ currentModel.description }}</p>
                        <div class="doc-tags" v-if="currentModel.tags?.length">
                            <el-tag v-for="t in currentModel.tags" :key="t" size="small" effect="plain"
                                class="doc-tag">{{ t }}</el-tag>
                        </div>
                    </div>

                    <!-- 接口地址 -->
                    <div class="doc-section">
                        <div class="section-title">接口地址</div>
                        <div class="endpoint-card">
                            <span class="method-badge post">POST</span>
                            <code class="endpoint-path">/api/execute/{{ currentModel.id }}</code>
                            <el-button size="small" text @click="copyPath">
                                <el-icon>
                                    <CopyDocument />
                                </el-icon> 复制
                            </el-button>
                        </div>
                    </div>

                    <!-- 请求参数 -->
                    <div class="doc-section">
                        <div class="section-title">
                            请求参数（Request Body · application/json）
                        </div>
                        <el-table :data="currentModel.inputs" class="doc-table" size="small">
                            <el-table-column label="参数名" width="160">
                                <template #default="{ row }">
                                    <code class="param-code">{{ row.name }}</code>
                                </template>
                            </el-table-column>
                            <el-table-column prop="label" label="名称" width="100" />
                            <el-table-column label="类型" width="80">
                                <template #default="{ row }">
                                    <el-tag size="small" effect="plain">{{ row.type }}</el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column prop="unit" label="单位" width="70" />
                            <el-table-column label="必填" width="60">
                                <template #default="{ row }">
                                    <el-tag size="small" :type="row.required !== false ? 'danger' : 'info'"
                                        effect="plain">
                                        {{ row.required !== false ? '是' : '否' }}
                                    </el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column label="范围 / 默认值" width="160">
                                <template #default="{ row }">
                                    <span v-if="row.min !== undefined || row.max !== undefined" class="range-text">
                                        {{ row.min ?? '-∞' }} ~ {{ row.max ?? '+∞' }}
                                    </span>
                                    <span v-else-if="row.default !== undefined" class="default-text">
                                        默认: {{ row.default }}
                                    </span>
                                    <span v-else class="text-muted">—</span>
                                </template>
                            </el-table-column>
                            <el-table-column label="说明" min-width="160">
                                <template #default="{ row }">
                                    <span class="text-muted">{{ row.description || '—' }}</span>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>

                    <!-- 响应参数 -->
                    <div class="doc-section">
                        <div class="section-title">
                            响应参数（Response · 200 OK）
                        </div>
                        <el-table :data="currentModel.outputs" class="doc-table" size="small">
                            <el-table-column label="字段名" width="160">
                                <template #default="{ row }">
                                    <code class="param-code">{{ row.name }}</code>
                                </template>
                            </el-table-column>
                            <el-table-column prop="label" label="名称" width="100" />
                            <el-table-column label="类型" width="80">
                                <template #default="{ row }">
                                    <el-tag size="small" effect="plain">{{ row.type }}</el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column prop="unit" label="单位" width="70" />
                            <el-table-column label="说明" min-width="160">
                                <template #default="{ row }">
                                    <span class="text-muted">{{ row.description || '—' }}</span>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>

                    <!-- 请求示例 -->
                    <div class="doc-section">
                        <div class="section-title">请求示例</div>
                        <div class="example-tabs">
                            <div class="example-tab-nav">
                                <span v-for="tab in exampleTabs" :key="tab.key"
                                    :class="['tab-btn', { active: activeExampleTab === tab.key }]"
                                    @click="activeExampleTab = tab.key">{{
                                    tab.label }}</span>
                            </div>
                            <div class="example-block">
                                <div class="example-header">
                                    <span class="lang-badge">
                                        {{exampleTabs.find(t => t.key === activeExampleTab)?.label}}
                                    </span>
                                    <el-button size="small" text @click="copyExample">
                                        <el-icon>
                                            <CopyDocument />
                                        </el-icon> 复制
                                    </el-button>
                                </div>
                                <pre class="example-code">{{ currentExampleCode }}</pre>
                            </div>
                        </div>
                    </div>

                    <!-- 响应示例 -->
                    <div class="doc-section">
                        <div class="section-title">响应示例</div>
                        <div class="example-block">
                            <div class="example-header">
                                <span class="lang-badge">JSON</span>
                                <el-button size="small" text @click="copyResponseExample">
                                    <el-icon>
                                        <CopyDocument />
                                    </el-icon> 复制
                                </el-button>
                            </div>
                            <pre class="example-code">{{ responseExample }}</pre>
                        </div>
                    </div>

                    <!-- 错误码 -->
                    <div class="doc-section">
                        <div class="section-title">错误码说明</div>
                        <el-table :data="errorCodes" class="doc-table" size="small">
                            <el-table-column label="HTTP 状态码" width="120">
                                <template #default="{ row }">
                                    <span :class="['status-code', `status-${row.code}`]">
                                        {{ row.code }}
                                    </span>
                                </template>
                            </el-table-column>
                            <el-table-column prop="name" label="错误类型" width="180" />
                            <el-table-column prop="desc" label="说明" />
                        </el-table>
                    </div>

                    <!-- 在线测试 -->
                    <div class="doc-section">
                        <div class="section-title">在线测试</div>
                        <div class="try-card">
                            <p class="try-desc">
                                在浏览器中直接测试此模型接口，无需任何工具
                            </p>
                            <el-button type="primary" @click="$router.push(`/models/`)">
                                <el-icon>
                                    <VideoPlay />
                                </el-icon> 前往模型详情页测试
                            </el-button>
                        </div>
                    </div>
                </template>

                <!-- 未选中状态 -->
                <div v-else-if="!docLoading" class="docs-empty">
                    <el-icon size="48" color="#1e2d4f">
                        <Document />
                    </el-icon>
                    <p>从左侧选择一个模型查看 API 文档</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { modelApi } from '../api/index.js'

const allModels = ref([])
const searchKey = ref('')
const activeId = ref('')
const currentModel = ref(null)
const docLoading = ref(false)
const activeExampleTab = ref('curl')

const categoryLabels = {
    conversion: '转换',
    separation: '分离',
    solar_position: '太阳位置',
    reflection: '反射',
    thermal: '温度',
    electrical: '电气',
    custom: '自定义'
}

const exampleTabs = [
    { key: 'curl', label: 'cURL' },
    { key: 'python', label: 'Python' },
    { key: 'js', label: 'JavaScript' }
]

const errorCodes = [
    { code: 200, name: 'Success', desc: '执行成功，返回 outputs 结果对象' },
    { code: 400, name: 'Bad Request', desc: '输入参数校验失败，检查字段类型和范围' },
    { code: 401, name: 'Unauthorized', desc: '未提供或令牌无效，请重新登录' },
    { code: 404, name: 'Not Found', desc: '模型 ID 不存在或已被停用' },
    { code: 422, name: 'Execution Error', desc: 'Python 模型执行错误或超时' },
    { code: 429, name: 'Too Many Requests', desc: '请求频率超限，默认每分钟 120 次' },
    { code: 500, name: 'Internal Server Error', desc: '服务器内部错误，请查看后端日志' }
]

// ─── 过滤模型列表
const filteredModels = computed(() => {
    if (!searchKey.value) return allModels.value
    const kw = searchKey.value.toLowerCase()
    return allModels.value.filter(m =>
        m.name.toLowerCase().includes(kw) ||
        m.id.toLowerCase().includes(kw) ||
        (m.tags || []).some(t => t.toLowerCase().includes(kw))
    )
})

// ─── 构建请求示例
function buildRequestExample(model) {
    if (!model) return '{}'
    const example = {}
    for (const f of model.inputs || []) {
        if (f.default !== undefined) example[f.name] = f.default
        else if (f.type === 'number') example[f.name] = f.min ?? 0
        else if (f.type === 'string') example[f.name] = ''
        else if (f.type === 'boolean') example[f.name] = true
        else example[f.name] = null
    }
    return JSON.stringify(example, null, 2)
}

// ─── 构建响应示例
function buildResponseExample(model) {
    if (!model) return '{}'
    const outputs = {}
    for (const f of model.outputs || []) {
        outputs[f.name] = f.type === 'number' ? 0.0
            : f.type === 'string' ? ''
                : f.type === 'boolean' ? true
                    : null
    }
    return JSON.stringify({
        code: 200,
        data: {
            modelId: model.id,
            modelName: model.name,
            version: model.version,
            executionTime: 18,
            outputs
        }
    }, null, 2)
}

// ─── 构建 cURL 示例
function buildCurlExample(model) {
    if (!model) return ''
    return `curl -X POST \\
  http://localhost:3000/api/execute/ \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer <your_token>" \\
  -d ''`
}

// ─── 构建 Python 示例
function buildPythonExample(model) {
    if (!model) return ''
    return `import requests

url = "http://localhost:3000/api/execute/"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer <your_token>"
}
payload = 

response = requests.post(url, json=payload, headers=headers)
result = response.json()
print(result["data"]["outputs"])`
}

// ─── 构建 JavaScript 示例
function buildJsExample(model) {
    if (!model) return ''
    return `const response = await fetch(
  "http://localhost:3000/api/execute/",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer <your_token>"
    },
    body: JSON.stringify()
  }
);
const result = await response.json();
console.log(result.data.outputs);`
}

// ─── 当前示例代码（响应式）
const currentExampleCode = computed(() => {
    if (!currentModel.value) return ''
    const m = currentModel.value
    if (activeExampleTab.value === 'curl') return buildCurlExample(m)
    if (activeExampleTab.value === 'python') return buildPythonExample(m)
    if (activeExampleTab.value === 'js') return buildJsExample(m)
    return ''
})

const currentExampleLang = computed(() => {
    return exampleTabs.find(t => t.key === activeExampleTab.value)?.label || ''
})

// ─── 响应示例（响应式）
const responseExample = computed(() =>
    buildResponseExample(currentModel.value)
)

// ─── 请求示例（响应式）
const requestExample = computed(() =>
    buildRequestExample(currentModel.value)
)

// ─── 选中模型
async function selectModel(id) {
    activeId.value = id
    docLoading.value = true
    currentModel.value = null

    try {
        const res = await modelApi.get(id)
        if (res.code === 200) {
            currentModel.value = res.data
        }
    } catch (err) {
        ElMessage.error('获取模型详情失败')
    } finally {
        docLoading.value = false
    }
}

// ─── 复制操作
async function copyPath() {
    await navigator.clipboard.writeText(
        `/api/execute/`
    )
    ElMessage.success('接口路径已复制')
}

async function copyExample() {
    await navigator.clipboard.writeText(currentExampleCode.value)
    ElMessage.success('示例代码已复制')
}

async function copyResponseExample() {
    await navigator.clipboard.writeText(responseExample.value)
    ElMessage.success('响应示例已复制')
}

onMounted(async () => {
    try {
        const res = await modelApi.list({ limit: 200 })
        if (res.code === 200) {
            allModels.value = res.data.list || []
            // 默认选中第一个
            if (allModels.value.length) {
                selectModel(allModels.value[0].id)
            }
        }
    } catch { }
})
</script>

<style scoped>
.page-container {
    padding: 0;
    height: calc(100vh - 60px);
    overflow: hidden;
}

/* ─── 整体布局 ───────────────────────────────── */
.docs-layout {
    display: grid;
    grid-template-columns: 240px 1fr;
    height: 100%;
    overflow: hidden;
}

/* ─── 左侧导航 ───────────────────────────────── */
.docs-sidebar {
    border-right: 1px solid #1e2d4f;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.sidebar-title {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 16px;
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid #1e2d4f;
    flex-shrink: 0;
}

.sidebar-search {
    padding: 10px 12px;
    border-bottom: 1px solid #1e2d4f;
    flex-shrink: 0;
}

.sidebar-nav {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.15s;
    margin-bottom: 2px;
}

.nav-item:hover {
    background: #1e2d4f;
}

.nav-item.active {
    background: #1a3a6e;
    border-left: 2px solid #60a5fa;
    padding-left: 8px;
}

.nav-name {
    font-size: 13px;
    color: #94a3b8;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex: 1;
}

.nav-item.active .nav-name {
    color: #e2e8f0;
}

.nav-empty {
    text-align: center;
    color: #334155;
    font-size: 13px;
    padding: 20px;
}

/* ─── 右侧文档内容 ───────────────────────────── */
.docs-content {
    overflow-y: auto;
    padding: 28px 32px;
}

.docs-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 16px;
    height: 60%;
    color: #334155;
    font-size: 14px;
}

/* ─── 文档头部 ───────────────────────────────── */
.doc-header {
    margin-bottom: 28px;
    padding-bottom: 20px;
    border-bottom: 1px solid #1e2d4f;
}

.doc-title-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
    flex-wrap: wrap;
}

.doc-title {
    font-size: 22px;
    font-weight: 700;
    color: #e2e8f0;
    margin: 0;
}

.doc-desc {
    font-size: 14px;
    color: #64748b;
    line-height: 1.7;
    margin: 0 0 10px;
}

.doc-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.doc-tag {
    font-size: 12px !important;
    border-color: #1e2d4f !important;
    color: #64748b !important;
    background: transparent !important;
}

/* ─── 文档章节 ───────────────────────────────── */
.doc-section {
    margin-bottom: 32px;
}

.section-title {
    font-size: 12px;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #1e2d4f;
}

/* ─── 接口地址 ───────────────────────────────── */
.endpoint-card {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    background: #131c35;
    border: 1px solid #1e2d4f;
    border-radius: 8px;
}

.method-badge {
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 4px;
    letter-spacing: 0.5px;
    flex-shrink: 0;
}

.method-badge.post {
    background: rgba(96, 165, 250, 0.15);
    color: #60a5fa;
    border: 1px solid rgba(96, 165, 250, 0.3);
}

.endpoint-path {
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    color: #e2e8f0;
    flex: 1;
    word-break: break-all;
}

/* ─── 参数表格 ───────────────────────────────── */
.doc-table {
    background: transparent !important;
    border: 1px solid #1e2d4f;
    border-radius: 8px;
    overflow: hidden;
}

.param-code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #60a5fa;
    background: rgba(96, 165, 250, 0.1);
    padding: 2px 6px;
    border-radius: 4px;
}

.range-text {
    font-size: 12px;
    color: #64748b;
    font-family: monospace;
}

.default-text {
    font-size: 12px;
    color: #fb923c;
    font-family: monospace;
}

.text-muted {
    font-size: 12px;
    color: #475569;
}

/* ─── 示例代码 ───────────────────────────────── */
.example-tab-nav {
    display: flex;
    gap: 2px;
    border-bottom: 1px solid #1e2d4f;
}

.tab-btn {
    padding: 6px 16px;
    font-size: 12px;
    color: #64748b;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    transition: all 0.15s;
    user-select: none;
}

.tab-btn:hover {
    color: #94a3b8;
}

.tab-btn.active {
    color: #60a5fa;
    border-bottom-color: #60a5fa;
}

.example-block {
    background: #0a0f1e;
    border: 1px solid #1e2d4f;
    border-top: none;
    border-radius: 0 0 8px 8px;
    overflow: hidden;
}

.example-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 12px;
    background: #131c35;
    border-bottom: 1px solid #1e2d4f;
}

.lang-badge {
    font-size: 11px;
    font-weight: 600;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.example-code {
    padding: 14px 16px;
    font-size: 12px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    color: #94a3b8;
    white-space: pre;
    overflow-x: auto;
    margin: 0;
    line-height: 1.7;
}

/* ─── 错误码 ─────────────────────────────────── */
.status-code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 4px;
}

.status-200 {
    color: #4ade80;
    background: rgba(74, 222, 128, 0.1);
}

.status-400 {
    color: #fb923c;
    background: rgba(251, 146, 60, 0.1);
}

.status-401 {
    color: #f87171;
    background: rgba(248, 113, 113, 0.1);
}

.status-404 {
    color: #fb923c;
    background: rgba(251, 146, 60, 0.1);
}

.status-422 {
    color: #f87171;
    background: rgba(248, 113, 113, 0.1);
}

.status-429 {
    color: #facc15;
    background: rgba(250, 204, 21, 0.1);
}

.status-500 {
    color: #f87171;
    background: rgba(248, 113, 113, 0.1);
}

/* ─── 在线测试 ───────────────────────────────── */
.try-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    background: #131c35;
    border: 1px solid #1e2d4f;
    border-radius: 8px;
    gap: 16px;
}

.try-desc {
    font-size: 13px;
    color: #64748b;
    margin: 0;
}

/* ─── 分类标签 ───────────────────────────────── */
.tag-category {
    padding: 2px 6px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 500;
    white-space: nowrap;
    flex-shrink: 0;
}

.tag-conversion {
    background: #1a3a5c;
    color: #60a5fa;
}

.tag-separation {
    background: #1a3a2c;
    color: #4ade80;
}

.tag-solar_position {
    background: #3a2a1a;
    color: #fb923c;
}

.tag-reflection {
    background: #3a1a3a;
    color: #c084fc;
}

.tag-thermal {
    background: #3a1a1a;
    color: #f87171;
}

.tag-electrical {
    background: #1a3a3a;
    color: #34d399;
}

.tag-custom {
    background: #2a2a1a;
    color: #facc15;
}

/* ─── Element Plus 暗色覆盖 ──────────────────── */
:deep(.el-input__wrapper) {
    background: #131c35 !important;
    border-color: #1e2d4f !important;
    box-shadow: 0 0 0 1px #1e2d4f inset !important;
}

:deep(.el-input__inner) {
    color: #e2e8f0 !important;
    font-size: 13px !important;
}

:deep(.el-table) {
    background: transparent !important;
    color: #94a3b8 !important;
}

:deep(.el-table tr),
:deep(.el-table th.el-table__cell) {
    background: transparent !important;
}

:deep(.el-table th.el-table__cell) {
    color: #475569 !important;
    font-size: 12px !important;
    border-bottom-color: #1e2d4f !important;
    font-weight: 600;
    background: #131c35 !important;
}

:deep(.el-table td.el-table__cell) {
    border-bottom-color: #1a2744 !important;
    color: #94a3b8 !important;
    font-size: 13px !important;
}

:deep(.el-table__row:hover > td) {
    background: #1a2744 !important;
}

:deep(.el-loading-mask) {
    background: rgba(15, 22, 41, 0.85) !important;
}
</style>
