<template>
    <div class="apidocs-root">
        <div class="apidocs-layout">

            <!-- ══ 左侧导航 ══ -->
            <aside class="apidocs-nav">
                <div class="nav-header">
                    <el-icon>
                        <Document />
                    </el-icon>
                    <span>API 文档</span>
                </div>

                <div class="nav-search">
                    <el-input v-model="searchKey" placeholder="搜索模型..." :prefix-icon="Search" size="small" clearable />
                </div>

                <div class="nav-body" v-loading="listLoading">
                    <template v-for="(docs, group) in groupedApiDocs" :key="group">

                        <!-- 分组标题 -->
                        <div class="nav-group-label">
                            <el-icon v-if="group === '模型链'">
                                <Connection />
                            </el-icon>
                            <el-icon v-else-if="group === '单模型运行'">
                                <VideoPlay />
                            </el-icon>
                            <el-icon v-else>
                                <List />
                            </el-icon>
                            <span>{{ group }}</span>
                        </div>

                        <template v-for="doc in docs" :key="doc.key">

                            <!-- 单模型运行：可展开子列表 -->
                            <template v-if="doc.isRunApi">
                                <div :class="['nav-item', 'nav-item-run', {
                                    active: activeKey === doc.key || activeKey.startsWith('model:')
                                }]" @click="selectDoc(doc.key)">
                                    <span :class="['method-tag', doc.method.toLowerCase()]">
                                        {{ doc.method }}
                                    </span>
                                    <span class="nav-item-title">{{ doc.title }}</span>
                                </div>

                                <!-- 模型子列表 -->
                                <div class="nav-model-list"
                                    v-if="activeKey.startsWith('model:') || activeKey === doc.key">
                                    <div v-for="model in filteredModels" :key="model.name"
                                        :class="['nav-model-item', { active: activeKey === `model:${model.name}` }]"
                                        @click="selectModel(model)">
                                        <span class="model-dot"></span>
                                        <span class="nav-model-name">{{ model.title || model.name }}</span>
                                        <span class="nav-model-cat">{{ model.category }}</span>
                                    </div>
                                    <div v-if="!filteredModels.length" class="nav-model-empty">
                                        <el-icon>
                                            <InfoFilled />
                                        </el-icon> 暂无模型
                                    </div>
                                </div>
                            </template>

                            <!-- 普通接口 -->
                            <div v-else :class="['nav-item', { active: activeKey === doc.key }]"
                                @click="selectDoc(doc.key)">
                                <span :class="['method-tag', doc.method.toLowerCase()]">
                                    {{ doc.method }}
                                </span>
                                <span class="nav-item-title">{{ doc.title }}</span>
                            </div>

                        </template>
                    </template>
                </div>
            </aside>

            <!-- ══ 右侧内容区 ══ -->
            <main class="apidocs-main">

                <!-- ── 单模型运行：跳转调试 ── -->
                <template v-if="currentModelName && currentModelInfo">
                    <div class="doc-page">

                        <div class="doc-hero">
                            <div class="doc-hero-title">
                                <span class="method-badge post">POST</span>
                                <h2>{{ currentModelInfo.title || currentModelInfo.name }}</h2>
                                <el-tag type="info" size="small">
                                    v{{ currentModelInfo.version || '1.0.0' }}
                                </el-tag>
                                <el-tag v-if="currentModelInfo.category" type="warning" size="small" effect="plain">
                                    {{ currentModelInfo.category }}
                                </el-tag>
                            </div>
                            <div class="doc-hero-path">
                                <code>/api/run/{{ currentModelName }}</code>
                                <el-button size="small" text @click="copyText(`/api/run/${currentModelName}`)">
                                    <el-icon>
                                        <CopyDocument />
                                    </el-icon>
                                </el-button>
                            </div>
                            <p class="doc-hero-desc" v-if="currentModelInfo.description">
                                {{ currentModelInfo.description }}
                            </p>
                        </div>

                        <!-- 调试入口卡片 -->
                        <div class="doc-section">
                            <div class="debug-card" @click="goToDebug(currentModelName)">
                                <div class="debug-card-left">
                                    <el-icon size="36" color="#409eff">
                                        <VideoPlay />
                                    </el-icon>
                                    <div>
                                        <div class="debug-card-title">前往调试页面运行此模型</div>
                                        <div class="debug-card-desc">
                                            在调试页面填写参数、实时运行并查看输出结果，支持历史记录查询与结果对比。
                                        </div>
                                    </div>
                                </div>
                                <el-button type="primary" size="large">
                                    <el-icon>
                                        <Right />
                                    </el-icon> 打开调试页面
                                </el-button>
                            </div>
                        </div>

                        <!-- 输入参数预览 -->
                        <div class="doc-section" v-if="currentModelInfo.inputs?.length">
                            <div class="section-title">输入参数</div>
                            <el-table :data="currentModelInfo.inputs" class="doc-table" size="small" border>
                                <el-table-column label="参数名" min-width="140">
                                    <template #default="{ row }">
                                        <code class="param-code">{{ row.name }}</code>
                                    </template>
                                </el-table-column>
                                <el-table-column label="类型" width="90">
                                    <template #default="{ row }">
                                        <el-tag size="small" effect="plain">{{ row.type }}</el-tag>
                                    </template>
                                </el-table-column>
                                <el-table-column label="单位" width="70">
                                    <template #default="{ row }">
                                        <span class="muted">{{ row.unit || '—' }}</span>
                                    </template>
                                </el-table-column>
                                <el-table-column label="必填" width="60">
                                    <template #default="{ row }">
                                        <el-tag size="small" :type="row.required !== false ? 'danger' : 'info'"
                                            effect="plain">
                                            {{ row.required !== false ? '是' : '否' }}
                                        </el-tag>
                                    </template>
                                </el-table-column>
                                <el-table-column label="说明" min-width="160">
                                    <template #default="{ row }">
                                        <span class="muted">{{ row.description || row.desc || '—' }}</span>
                                    </template>
                                </el-table-column>
                            </el-table>
                        </div>

                        <!-- 输出参数预览 -->
                        <div class="doc-section" v-if="currentModelInfo.outputs?.length">
                            <div class="section-title">输出参数</div>
                            <el-table :data="currentModelInfo.outputs" class="doc-table" size="small" border>
                                <el-table-column label="字段名" min-width="140">
                                    <template #default="{ row }">
                                        <code class="param-code">{{ row.name }}</code>
                                    </template>
                                </el-table-column>
                                <el-table-column label="类型" width="90">
                                    <template #default="{ row }">
                                        <el-tag size="small" effect="plain">{{ row.type }}</el-tag>
                                    </template>
                                </el-table-column>
                                <el-table-column label="单位" width="70">
                                    <template #default="{ row }">
                                        <span class="muted">{{ row.unit || '—' }}</span>
                                    </template>
                                </el-table-column>
                                <el-table-column label="说明" min-width="160">
                                    <template #default="{ row }">
                                        <span class="muted">{{ row.description || row.desc || '—' }}</span>
                                    </template>
                                </el-table-column>
                            </el-table>
                        </div>

                    </div>
                </template>

                <!-- ── 普通接口文档 ── -->
                <template v-else-if="currentDoc">
                    <div class="doc-page">

                        <!-- 标题区 -->
                        <div class="doc-hero">
                            <div class="doc-hero-title">
                                <span :class="['method-badge', currentDoc.method.toLowerCase()]">
                                    {{ currentDoc.method }}
                                </span>
                                <h2>{{ currentDoc.title }}</h2>
                            </div>
                            <div class="doc-hero-path">
                                <code>{{ currentDoc.path }}</code>
                                <el-button size="small" text @click="copyText(currentDoc.path)">
                                    <el-icon>
                                        <CopyDocument />
                                    </el-icon>
                                </el-button>
                            </div>
                            <p class="doc-hero-desc">{{ currentDoc.description }}</p>
                        </div>

                        <!-- WORKFLOW 专属：四步调用流程卡片 -->
                        <template v-if="currentDoc.method === 'WORKFLOW'">
                            <div class="doc-section workflow-steps">
                                <div class="section-title">调用流程</div>

                                <!-- ── Step 1：获取厂家列表 ── -->
                                <div class="workflow-step-card">
                                    <div class="step-header">
                                        <span class="step-badge">Step 1</span>
                                        <span class="step-method-tag get">GET</span>
                                        <code class="step-path">/api/panels/manufacturers</code>
                                        <span class="step-desc-inline">获取所有组件厂家名称列表</span>
                                    </div>
                                    <div class="step-body">
                                        <p class="step-note">
                                            首先调用此接口获取系统中已录入的所有组件厂家名称，
                                            用于在 Step 2 中按厂家筛选组件型号。无需任何请求参数，直接调用即可。
                                        </p>
                                        <div class="step-example">
                                            <div class="step-example-label">响应示例</div>
                                            <CodeBlock lang="JSON" :code="step1ResponseExample" @copy="copyText" />
                                        </div>
                                    </div>
                                </div>

                                <!-- ── Step 2：按厂家+型号查询，获取组件 ID ── -->
                                <div class="workflow-step-card">
                                    <div class="step-header">
                                        <span class="step-badge">Step 2</span>
                                        <span class="step-method-tag get">GET</span>
                                        <code class="step-path">/api/panels</code>
                                        <span class="step-desc-inline">根据厂家和型号获取组件 ID</span>
                                    </div>
                                    <div class="step-body">
                                        <p class="step-note">
                                            使用 Step 1 返回的厂家名称作为 <code>manufacturer</code> 参数进行精确过滤，
                                            配合 <code>model_name</code> 关键字模糊搜索，
                                            从返回列表中取目标组件的 <code>data[].id</code> 字段，作为 Step 3 的路径参数。
                                        </p>
                                        <ParamTable :data="step2QueryParams" />
                                        <div class="step-example">
                                            <div class="step-example-label">响应示例（取 data[].id）</div>
                                            <CodeBlock lang="JSON" :code="step2ResponseExample" @copy="copyText" />
                                        </div>
                                    </div>
                                </div>

                                <!-- ── Step 3：根据 ID 查询组件详情 ── -->
                                <div class="workflow-step-card">
                                    <div class="step-header">
                                        <span class="step-badge">Step 3</span>
                                        <span class="step-method-tag get">GET</span>
                                        <code class="step-path">/api/panels/{panel_id}</code>
                                        <span class="step-desc-inline">根据组件 ID 查询完整电学参数</span>
                                    </div>
                                    <div class="step-body">
                                        <p class="step-note">
                                            使用 Step 2 获取的 <code>id</code> 作为路径参数，返回该组件的完整电学数据，
                                            将 <code>isc / voc / imp / vmp / temp_coeff / g_ref / t_ref</code>
                                            用于填充 Step 4 的请求体。
                                        </p>
                                        <ParamTable :data="step3PathParams" />
                                        <div class="step-example">
                                            <div class="step-example-label">响应示例（取电学参数）</div>
                                            <CodeBlock lang="JSON" :code="step3ResponseExample" @copy="copyText" />
                                        </div>
                                    </div>
                                </div>

                                <!-- ── Step 4：调用二极管模型 ── -->
                                <div class="workflow-step-card">
                                    <div class="step-header">
                                        <span class="step-badge">Step 4</span>
                                        <span class="step-method-tag post">POST</span>
                                        <code class="step-path">/api/run/pv_diode</code>
                                        <span class="step-desc-inline">调用二极管模型计算输出功率</span>
                                    </div>
                                    <div class="step-body">
                                        <p class="step-note">
                                            将 Step 3 获取的组件电学参数与用户手动输入的工况参数一起发送。<br />
                                            <b>方式一</b>：仅传 <code>panel_id + g_poa + t_cell</code>，后端自动从数据库补全组件参数；<br />
                                            <b>方式二</b>：传入全部参数（isc / voc / imp / vmp / temp_coeff / g_ref / t_ref / g_poa
                                            / t_cell）。
                                        </p>
                                        <div class="section-title" style="font-size:13px;margin:12px 0 6px">
                                            Request Body
                                        </div>
                                        <ParamTable :data="currentDoc.bodyParams" />
                                        <div class="step-example">
                                            <div class="step-example-label">请求示例</div>
                                            <CodeBlock lang="JSON" :code="currentDoc.requestExample" @copy="copyText" />
                                        </div>
                                        <div class="step-example" style="margin-top:12px">
                                            <div class="step-example-label">响应示例</div>
                                            <CodeBlock lang="JSON" :code="currentDoc.responseExample"
                                                @copy="copyText" />
                                        </div>
                                    </div>
                                </div>

                            </div>

                            <!-- 错误码 -->
                            <div class="doc-section" style="margin-bottom:40px">
                                <div class="section-title">错误码说明</div>
                                <ErrorCodeTable :data="errorCodes" />
                            </div>
                        </template>

                        <!-- 非 WORKFLOW 的普通文档，保持原有渲染逻辑不变 -->
                        <template v-else>
                            <!-- Path 参数 -->
                            <div class="doc-section" v-if="currentDoc.pathParams?.length">
                                <div class="section-title">Path 参数</div>
                                <ParamTable :data="currentDoc.pathParams" />
                            </div>

                            <!-- Query 参数 -->
                            <div class="doc-section" v-if="currentDoc.queryParams?.length">
                                <div class="section-title">Query 参数</div>
                                <ParamTable :data="currentDoc.queryParams" />
                            </div>

                            <!-- Body 参数 -->
                            <div class="doc-section" v-if="currentDoc.bodyParams?.length">
                                <div class="section-title">
                                    Request Body
                                    <span class="muted" style="font-weight:400;margin-left:6px">application/json</span>
                                </div>
                                <ParamTable :data="currentDoc.bodyParams" />
                            </div>

                            <!-- 请求示例 -->
                            <div class="doc-section" v-if="currentDoc.requestExample">
                                <div class="section-title">请求示例</div>
                                <CodeBlock lang="JSON" :code="currentDoc.requestExample" @copy="copyText" />
                            </div>

                            <!-- 响应示例 -->
                            <div class="doc-section" v-if="currentDoc.responseExample">
                                <div class="section-title">响应示例</div>
                                <CodeBlock lang="JSON" :code="currentDoc.responseExample" @copy="copyText" />
                            </div>

                            <!-- 错误码 -->
                            <div class="doc-section" style="margin-bottom:40px">
                                <div class="section-title">错误码说明</div>
                                <ErrorCodeTable :data="errorCodes" />
                            </div>
                        </template>
                    </div>
                </template>

                <!-- ── 未选中 ── -->
                <div v-else class="doc-empty">
                    <el-icon size="52" color="#c0c4cc">
                        <Document />
                    </el-icon>
                    <p>从左侧选择接口查看文档</p>
                </div>

            </main>
        </div>
    </div>
</template>


<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElTable, ElTableColumn, ElTag, ElButton, ElIcon } from 'element-plus'
import {
    Document, Connection, List, Search, Check, Share,
    CopyDocument, VideoPlay, Right, InfoFilled
} from '@element-plus/icons-vue'
import { getAllModels } from '@/api/modelChain.js'

const router = useRouter()

// ── 状态 ──────────────────────────────────────────────────────
const allModels = ref([])
const searchKey = ref('')
const activeKey = ref('')   // 当前选中的导航 key
const listLoading = ref(false)

// ══════════════════════════════════════════════════════════════
// 静态接口文档数据
// ══════════════════════════════════════════════════════════════

// ── 错误码（公用）─────────────────────────────────────────────
const errorCodes = [
    { code: 200, name: 'Success', desc: '请求成功' },
    { code: 400, name: 'Bad Request', desc: '参数校验失败，检查字段类型和范围' },
    { code: 401, name: 'Unauthorized', desc: '未提供或令牌无效，请重新登录' },
    { code: 404, name: 'Not Found', desc: '资源不存在或已被停用' },
    { code: 422, name: 'Execution Error', desc: 'Python 模型执行错误或超时' },
    { code: 500, name: 'Internal Server Error', desc: '服务器内部错误，请查看后端日志' },
]

// 光伏组件二极管模型 — 三步调用说明
// ── WORKFLOW pv_diode 四步静态数据 ──────────────────────────

// Step 1：GET /api/panels/manufacturers 响应示例
const step1ResponseExample = JSON.stringify({
    success: true,
    data: ['JA Solar', 'LONGi', 'Trina Solar', 'Canadian Solar', 'Risen Energy']
}, null, 2)

// Step 2：GET /api/panels  Query 参数
const step2QueryParams = [
    {
        name: 'manufacturer', type: 'string', required: false,
        desc: '厂家名称（精确匹配），来自 Step 1 返回的列表'
    },
    {
        name: 'model_name', type: 'string', required: false,
        desc: '型号关键字（模糊匹配），返回 data[].id 即为组件 ID'
    },
    {
        name: 'page', type: 'integer', required: false,
        desc: '页码，默认 1'
    },
    {
        name: 'page_size', type: 'integer', required: false,
        desc: '每页数量，默认 100'
    },
]

// Step 2：GET /api/panels 响应示例
const step2ResponseExample = JSON.stringify({
    success: true,
    data: [
        { id: 3, manufacturer: 'JA Solar', model_name: 'JAM72S30-545/MR', pmp_calc: 545.0 },
        { id: 4, manufacturer: 'JA Solar', model_name: 'JAM72S30-530/MR', pmp_calc: 530.0 },
    ],
    total: 2, page: 1, page_size: 100
}, null, 2)

// Step 3：GET /api/panels/{panel_id}  Path 参数
const step3PathParams = [
    {
        name: 'panel_id', type: 'integer', required: true,
        desc: '组件 ID，来自 Step 2 返回的 data[].id'
    },
]

// Step 3：GET /api/panels/{panel_id} 响应示例
const step3ResponseExample = JSON.stringify({
    success: true,
    data: {
        id: 3,
        manufacturer: 'JA Solar',
        model_name: 'JAM72S30-545/MR',
        isc: 13.96, voc: 49.8, imp: 13.14, vmp: 41.5,
        temp_coeff: 6.22, g_ref: 1000.0, t_ref: 25.0,
        pmp_calc: 545.0, efficiency: 21.2
    }
}, null, 2)



// ── 接口文档定义 ───────────────────────────────────────────────
const apiDocs = [
    // ────────────────────────────────────────────────────────────
    // 分组：模型管理
    // ────────────────────────────────────────────────────────────
    {
        key: 'model-list',
        group: '模型管理',
        method: 'GET',
        path: '/api/models',
        title: '获取模型列表',
        description: '获取平台中所有已注册的活跃模型列表，支持按分类过滤和关键词搜索。每条记录已内嵌 related_models 关系字段，无需额外请求。',
        queryParams: [
            { name: 'category', type: 'string', required: false, desc: '按模型分类过滤，如"太阳位置"、"温度模型"' },
            { name: 'keyword', type: 'string', required: false, desc: '按模型 name 或 title 模糊搜索' },
        ],
        responseExample: JSON.stringify({
            success: true,
            total: 2,
            data: [
                {
                    id: 1,
                    name: 'solar_position',
                    title: '太阳位置计算',
                    version: '1.0.0',
                    description: '基于 pvlib 计算太阳高度角、方位角等参数',
                    author: 'pvlib',
                    category: '太阳位置',
                    call_count: 128,
                    api_path: '/api/run/solar_position',
                    inputs: [
                        { name: 'latitude', type: 'float', unit: '°', required: true, description: '纬度' },
                        { name: 'longitude', type: 'float', unit: '°', required: true, description: '经度' },
                        { name: 'datetime_str', type: 'string', unit: null, required: true, description: 'ISO 8601 时间字符串' },
                    ],
                    outputs: [
                        { name: 'solar_zenith', type: 'float', unit: '°', description: '太阳天顶角' },
                        { name: 'solar_azimuth', type: 'float', unit: '°', description: '太阳方位角' },
                        { name: 'solar_elevation', type: 'float', unit: '°', description: '太阳高度角' },
                    ],
                    related_models: { pre: [], post: ['perez_separation'], depends_on: [], conflicts_with: [] },
                },
            ],
        }, null, 2),
    },
    {
        key: 'model-allnames',
        group: '模型管理',
        method: 'GET',
        path: '/api/models/all-names',
        title: '获取所有模型名称',
        description: '获取平台中所有活跃模型的 name、title、category 轻量列表，适用于下拉选择、自动补全等场景，无需加载完整字段。',
        responseExample: JSON.stringify({
            success: true,
            data: [
                { name: 'solar_position', title: '太阳位置计算', category: '太阳位置' },
                { name: 'perez_separation', title: 'Perez 辐照分离', category: '辐照分离' },
            ],
        }, null, 2),
    },
    {
        key: 'model-categories',
        group: '模型管理',
        method: 'GET',
        path: '/api/models/categories/list',
        title: '获取模型分类列表',
        description: '获取平台中所有模型分类及各分类下的模型数量，可用于分类导航、筛选面板等。',
        responseExample: JSON.stringify({
            success: true,
            total: 3,
            data: [
                { category: '太阳位置', count: 2 },
                { category: '辐照分离', count: 3 },
                { category: '温度模型', count: 1 },
            ],
        }, null, 2),
    },
    {
        key: 'model-stats',
        group: '模型管理',
        method: 'GET',
        path: '/api/models/stats/overview',
        title: '模型统计概览',
        description: '获取平台整体统计数据，包括模型总数、分类数、总调用次数、调用最多的 Top5 模型，以及最近 10 条执行日志。',
        responseExample: JSON.stringify({
            success: true,
            data: {
                total_models: 12,
                total_categories: 5,
                total_calls: 3842,
                top_models: [
                    { id: 1, name: 'solar_position', title: '太阳位置计算', category: '太阳位置', call_count: 980 },
                ],
                recent_logs: [
                    { model_name: 'solar_position', success: true, execution_time_ms: 18, created_at: '2026-04-14T10:00:00' },
                ],
            },
        }, null, 2),
    },
    {
        key: 'model-detail',
        group: '模型管理',
        method: 'GET',
        path: '/api/models/{name}',
        title: '获取模型详情',
        description: '根据模型 name 获取完整详情，包含 inputs/outputs 字段定义、模型关系（pre/post/depends_on/conflicts_with），以及 meta.py 和 model.py 完整源码内容。',
        pathParams: [
            { name: 'name', type: 'string', required: true, desc: '模型唯一标识名，如 solar_position' },
        ],
        responseExample: JSON.stringify({
            success: true,
            data: {
                id: 1,
                name: 'solar_position',
                title: '太阳位置计算',
                version: '1.0.0',
                description: '基于 pvlib 计算太阳位置参数',
                author: 'pvlib',
                category: '太阳位置',
                call_count: 128,
                api_path: '/api/run/solar_position',
                inputs: [{ name: 'latitude', type: 'float', unit: '°', required: true, description: '纬度，范围 -90 ~ 90' }],
                outputs: [{ name: 'solar_zenith', type: 'float', unit: '°', description: '太阳天顶角' }],
                execution: { timeout: 30, engine: 'pvlib' },
                related_models: { pre: [], post: ['perez_separation'], depends_on: [], conflicts_with: [] },
                meta_code: 'MODEL_META = { "name": "solar_position", ... }',
                model_code: 'def run(inputs):\n    ...',
            },
        }, null, 2),
    },
    {
        key: 'model-logs',
        group: '模型管理',
        method: 'GET',
        path: '/api/models/{name}/logs',
        title: '获取模型执行日志',
        description: '获取指定模型最近的执行日志，包含每次调用的输入输出快照、执行耗时和错误信息。',
        pathParams: [
            { name: 'name', type: 'string', required: true, desc: '模型唯一标识名' },
        ],
        queryParams: [
            { name: 'limit', type: 'integer', required: false, desc: '返回条数，默认 20，最大 100' },
        ],
        responseExample: JSON.stringify({
            success: true,
            total: 2,
            data: [
                {
                    id: 101,
                    success: true,
                    inputs: { latitude: 39.9, longitude: 116.4, datetime_str: '2026-04-14T04:00:00Z' },
                    outputs: { solar_zenith: 22.48, solar_azimuth: 175.64 },
                    error_msg: null,
                    execution_time_ms: 18,
                    created_at: '2026-04-14T10:00:00',
                },
            ],
        }, null, 2),
    },
    {
        key: 'model-validate',
        group: '模型管理',
        method: 'POST',
        path: '/api/models/validate',
        title: '模型代码校验',
        description: '在上传模型前对 meta.py 代码进行静态校验，检查 MODEL_META 字典结构完整性和字段类型合法性，不会实际执行代码，安全无副作用。',
        bodyParams: [
            { name: 'code', type: 'string', required: true, desc: 'meta.py 的完整代码字符串' },
        ],
        requestExample: `MODEL_META = {\n  "name": "solar_position",\n  "title": "太阳位置计算",\n  "version": "1.0.0",\n  "inputs": [\n    { "name": "latitude", "type": "float", "required": true, "description": "纬度" }\n  ],\n  "outputs": [\n    { "name": "solar_zenith", "type": "float", "description": "太阳天顶角" }\n  ]\n}`,
        responseExample: JSON.stringify({
            success: true,
            data: {
                valid: true,
                errors: [],
                warnings: ['建议填写 execution.timeout 字段以避免超时'],
                meta: { name: 'solar_position', title: '太阳位置计算', version: '1.0.0' },
            },
        }, null, 2),
    },
    {
        key: 'model-upload',
        group: '模型管理',
        method: 'POST',
        path: '/api/models/upload',
        title: '上传并发布模型',
        description: '上传 meta.py 和 model.py 代码发布新模型，系统会自动校验代码合法性、写入文件、注册到运行时并持久化到数据库。若同名模型已存在则执行覆盖更新。',
        bodyParams: [
            { name: 'meta_code', type: 'string', required: true, desc: 'meta.py 完整代码，必须包含合法的 MODEL_META 字典' },
            { name: 'model_code', type: 'string', required: true, desc: 'model.py 完整代码，必须包含 run(inputs) 函数' },
        ],
        requestExample:
            `meta_code: 'MODEL_META = {\n  "name": "my_model",\n  "title": "我的模型",\n  "version": "1.0.0",\n  "inputs": [],\n  "outputs": []\n}',\nmodel_code: \n'def run(inputs):\n    return {}'`,
        responseExample: JSON.stringify({
            success: true,
            message: "模型 'my_model' 已发布",
            data: { id: 5, name: 'my_model', title: '我的模型', category: '未分类', api_path: '/api/run/my_model' },
        }, null, 2),
    },
    {
        key: 'model-relations',
        group: '模型管理',
        method: 'PUT',
        path: '/api/models/{name}/relations',
        title: '更新模型关系',
        description: '覆盖更新指定模型的前置/后置/依赖/冲突关系。调用后会先清除该模型所有已有关系记录，再按请求体重新写入。所有目标模型必须存在且处于活跃状态。',
        pathParams: [
            { name: 'name', type: 'string', required: true, desc: '要更新关系的模型 name' },
        ],
        bodyParams: [
            { name: 'related_models', type: 'Object', required: true, desc: '关系对象，包含四类关系数组' },
            { name: 'related_models.pre', type: 'string[]', required: false, desc: '前置模型列表，本模型需在这些模型之后运行' },
            { name: 'related_models.post', type: 'string[]', required: false, desc: '后置模型列表，这些模型需在本模型之后运行' },
            { name: 'related_models.depends_on', type: 'string[]', required: false, desc: '依赖模型列表，强依赖关系' },
            { name: 'related_models.conflicts_with', type: 'string[]', required: false, desc: '冲突模型列表，不能与这些模型同时在链中使用' },
        ],
        requestExample: JSON.stringify({
            related_models: { pre: ['solar_position'], post: ['poa_irradiance'], depends_on: [], conflicts_with: [] },
        }, null, 2),
        responseExample: JSON.stringify({
            success: true,
            message: "模型 'perez_separation' 关系已更新",
            data: { pre: ['solar_position'], post: ['poa_irradiance'], depends_on: [], conflicts_with: [] },
        }, null, 2),
    },
    {
        key: 'model-delete',
        group: '模型管理',
        method: 'DELETE',
        path: '/api/models/{name}',
        title: '删除模型',
        description: '软删除指定模型（将 is_active 置为 false），同时删除磁盘上的模型文件并从运行时注册表中移除。删除后该模型不再出现在列表中，但历史日志仍保留。',
        pathParams: [
            { name: 'name', type: 'string', required: true, desc: '要删除的模型 name' },
        ],
        responseExample: JSON.stringify({
            success: true,
            message: "模型 'my_model' 已删除",
        }, null, 2),
    },
    {
        key: 'model-reload',
        group: '模型管理',
        method: 'POST',
        path: '/api/models/{name}/reload',
        title: '热重载模型',
        description: '从磁盘重新加载指定模型的代码到运行时注册表，无需重启服务器。适用于直接修改了模型文件后需要立即生效的场景。',
        pathParams: [
            { name: 'name', type: 'string', required: true, desc: '要热重载的模型 name' },
        ],
        responseExample: JSON.stringify({
            success: true,
            message: "模型 'solar_position' 已重新加载",
        }, null, 2),
    },

    // ────────────────────────────────────────────────────────────
    // 分组：单模型运行（跳转调试）
    // ────────────────────────────────────────────────────────────
    {
        key: 'model-run',
        group: '单模型运行',
        method: 'POST',
        path: '/api/run/{name}',
        title: '运行单个模型',
        isRunApi: true,   // 标记为运行接口，点击跳转调试页
        description: '直接调用指定模型的 run() 函数，传入 inputs 参数对象，返回模型计算结果。',
    },

    // ────────────────────────────────────────────────────────────
    // 分组：光伏组件二极管模型调用方法
    // ────────────────────────────────────────────────────────────
    {
        key: 'pv-diode-workflow',
        group: '单模型运行',
        method: 'WORKFLOW',
        path: '/api/run/pv_diode',
        title: '光伏组件二极管模型 — 四步调用说明',       // 改为"四步"
        description: 'pv_diode 模型依赖组件库电学参数，推荐按以下四步顺序完成完整调用流程。',
        bodyParams: [
            {
                name: 'panel_id', type: 'integer', required: false,
                desc: '可选。传入后后端自动从数据库补全缺失的组件电学参数（方式一）'
            },
            {
                name: 'isc', type: 'float', required: true,
                desc: '短路电流 (A)，来自 Step 3 组件详情'
            },
            {
                name: 'voc', type: 'float', required: true,
                desc: '开路电压 (V)，来自 Step 3 组件详情'
            },
            {
                name: 'imp', type: 'float', required: true,
                desc: '最大功率点电流 (A)，来自 Step 3 组件详情'
            },
            {
                name: 'vmp', type: 'float', required: true,
                desc: '最大功率点电压 (V)，来自 Step 3 组件详情'
            },
            {
                name: 'temp_coeff', type: 'float', required: true,
                desc: '温度系数 (mA/℃)，来自 Step 3 组件详情'
            },
            {
                name: 'g_ref', type: 'float', required: true,
                desc: '参考辐照度 (W/m²)，来自 Step 3，通常为 1000.0'
            },
            {
                name: 't_ref', type: 'float', required: true,
                desc: '参考温度 (℃)，来自 Step 3，通常为 25.0'
            },
            {
                name: 'g_poa', type: 'float', required: true,
                desc: '【用户输入】实际平面辐照度 (W/m²)，范围 0 ~ 1500'
            },
            {
                name: 't_cell', type: 'float', required: true,
                desc: '【用户输入】电池温度 (℃)，范围 -40 ~ 100'
            },
        ],
        requestExample: JSON.stringify({
            panel_id: 3,
            isc: 13.96, voc: 49.8, imp: 13.14, vmp: 41.5,
            temp_coeff: 6.22, g_ref: 1000.0, t_ref: 25.0,
            g_poa: 800.0, t_cell: 35.0,
        }, null, 2),
        responseExample: JSON.stringify({
            success: true,
            model: 'pv_diode',
            panel_id: 3,
            outputs: {
                current: 12.81, power: 516.40,
                voc: 48.23, isc: 11.17,
                vmpp: 40.31, impp: 12.81,
                pmpp: 516.40, ff: 0.9587,
            },
            execution_time_ms: 12.5,
        }, null, 2),
    },

    // ────────────────────────────────────────────────────────────
    // 分组：组件管理  ★ 新增
    // ────────────────────────────────────────────────────────────
    {
        key: 'panel-list',
        group: '组件管理',
        method: 'GET',
        path: '/api/panels',
        title: '获取组件列表',
        description: '分页查询已入库的光伏组件，支持按**厂家**精确筛选和按**型号**模糊搜索。返回字段包含三项温度系数（temp_coeff / mu_voc_spec / mu_pmp）及全部电气参数。',
        queryParams: [
            { name: 'manufacturer', type: 'string', required: false, desc: '厂家精确匹配，如 "Canadian Solar"' },
            { name: 'model_name', type: 'string', required: false, desc: '型号模糊搜索' },
            { name: 'page', type: 'integer', required: false, desc: '页码，默认 1' },
            { name: 'page_size', type: 'integer', required: false, desc: '每页条数，默认 100' },
        ],
        responseExample: JSON.stringify({
            success: true,
            total: 2,
            page: 1,
            page_size: 100,
            data: [
                {
                    id: 1,
                    filename: 'CS6W-550MS.pan',
                    manufacturer: 'Canadian Solar',
                    model_name: 'CS6W-550MS',
                    is_bifacial: false,
                    bifacial_factor: 0,
                    isc: 13.93, voc: 49.3, imp: 13.16, vmp: 41.8,
                    temp_coeff: 6.22,    // 短路电流温度系数 muISC (mA/℃)
                    mu_voc_spec: -138.4,  // 开路电压温度系数 muVocSpec (mV/℃)
                    mu_pmp: -0.35,   // 功率温度系数 muPmpReq (%/℃)
                    pmp_calc: 550.1, efficiency: 21.2,
                    length: 2278, width: 1134, thickness: 35, weight: 28.2, area: 2.583,
                    created_at: '2026-04-24T10:00:00',
                },
            ],
        }, null, 2),
    },
    {
        key: 'panel-manufacturers',
        group: '组件管理',
        method: 'GET',
        path: '/api/panels/manufacturers',
        title: '获取厂家列表',
        description: '返回数据库中所有已入库组件的**厂家名称去重列表**，按字母顺序排列，常用于前端下拉筛选框的选项数据源。',
        responseExample: JSON.stringify({
            success: true,
            data: ['Canadian Solar', 'JA Solar', 'LONGi Solar', 'Trina Solar'],
        }, null, 2),
    },
    {
        key: 'panel-detail',
        group: '组件管理',
        method: 'GET',
        path: '/api/panels/{panel_id}',
        title: '获取组件详情',
        description: '根据组件 ID 获取完整信息，在列表字段基础上额外返回三项温度系数及原始 `.pan` 文件文本内容（`raw_content`）。',
        pathParams: [
            { name: 'panel_id', type: 'integer', required: true, desc: '组件 ID' },
        ],
        responseExample: JSON.stringify({
            success: true,
            data: {
                id: 1,
                filename: 'CS6W-550MS.pan',
                manufacturer: 'Canadian Solar',
                model_name: 'CS6W-550MS',
                isc: 13.93, voc: 49.3, imp: 13.16, vmp: 41.8,
                temp_coeff: 6.22,
                mu_voc_spec: -138.4,
                mu_pmp: -0.35,
                g_ref: 1000, t_ref: 25,
                isc_calc: 13.93, voc_calc: 49.3, imp_calc: 13.16, vmp_calc: 41.8, pmp_calc: 550.1,
                efficiency: 21.2,
                length: 2278, width: 1134, thickness: 35, weight: 28.2, area: 2.583,
                r_series: 0.037, r_shunt: 1000, gamma: 1.255,
                iam_angles: [0, 20, 40, 60, 70, 80, 85, 90],
                iam_values: [1.0, 1.0, 0.997, 0.977, 0.947, 0.856, 0.721, 0.0],
                raw_content: 'PVObject_=pvModule\nVersion=8.4.1\n...',
                created_at: '2026-04-24T10:00:00',
                updated_at: null,
            },
        }, null, 2),
    },
    {
        key: 'panel-curves',
        group: '组件管理',
        method: 'POST',
        path: '/api/panels/{panel_id}/curves',
        title: '计算 IV/PV 电学曲线（getCurves）',
        description: '基于单二极管模型计算组件在不同工况下的 IV 及 PV 曲线。`mode=irradiance` 时固定温度，对多辐照度求解；`mode=temperature` 时固定辐照度，对多温度求解。计算过程使用 `temp_coeff`（muISC）和 `mu_voc_spec`（muVocSpec）两项温度系数。返回的每条曲线含 `voltages`、`currents`、`powers` 三组数据点，可直接用于图表渲染。',
        pathParams: [
            { name: 'panel_id', type: 'integer', required: true, desc: '组件 ID' },
        ],
        bodyParams: [
            { name: 'mode', type: 'string', required: false, desc: '"irradiance"（默认）或 "temperature"' },
            { name: 'irradiances', type: 'number[]', required: false, desc: '辐照度列表 W/m²，mode=irradiance 时生效，默认 [1000,800,600,400,200]' },
            { name: 'temperatures', type: 'number[]', required: false, desc: '温度列表 ℃，mode=temperature 时生效，默认 [0,10,25,35,45]' },
            { name: 'base_temp', type: 'number', required: false, desc: '基准温度 ℃，mode=irradiance 时使用，默认 45' },
            { name: 'base_irradiance', type: 'number', required: false, desc: '基准辐照度 W/m²，mode=temperature 时使用，默认 1000' },
        ],
        requestExample: JSON.stringify({
            mode: 'irradiance',
            irradiances: [1000, 800, 600, 400, 200],
            base_temp: 25,
        }, null, 2),
        responseExample: JSON.stringify({
            success: true,
            mode: 'irradiance',
            data: [
                {
                    label: '1000 W/m²',
                    voltages: [0, 5.12, 10.24, '...', 49.3],
                    currents: [13.93, 13.91, 13.87, '...', 0],
                    powers: [0, 71.2, 141.9, '...', 0],
                },
                {
                    label: '800 W/m²',
                    voltages: [0, 5.10, '...'],
                    currents: [11.14, '...'],
                    powers: [0, '...'],
                },
            ],
        }, null, 2),
    },


    // ────────────────────────────────────────────────────────────
    // 分组：模型链
    // ────────────────────────────────────────────────────────────
    // {
    //     key: 'chain-run',
    //     group: '模型链',
    //     method: 'POST',
    //     path: '/api/chain/run',
    //     title: '执行模型链',
    //     description: '按顺序串联执行多个模型，前一个模型的输出字段可通过 input_mapping 自动映射为下一个模型的输入，最终返回每个节点的执行结果和总耗时。',
    //     bodyParams: [
    //         { name: 'chain', type: 'Array', required: true, desc: '模型链节点数组，按执行顺序排列' },
    //         { name: 'chain[].model_id', type: 'string', required: true, desc: '节点使用的模型 name，必须是已注册的有效模型' },
    //         { name: 'chain[].inputs', type: 'Object', required: true, desc: '该节点的直接输入参数，无法从上游映射的参数在此提供' },
    //         { name: 'chain[].input_mapping', type: 'Object', required: false, desc: '字段映射规则，格式：{ "本节点字段": "上游节点ID.输出字段" }' },
    //         { name: 'chain[].alias', type: 'string', required: false, desc: '节点别名，用于在 input_mapping 中引用，默认使用 model_id' },
    //         { name: 'chain[].skip_on_error', type: 'boolean', required: false, desc: '当前节点出错时是否跳过继续执行，默认 false' },
    //     ],
    //     requestExample: JSON.stringify({
    //         chain: [
    //             {
    //                 model_id: 'solar_position',
    //                 inputs: { latitude: 39.9042, longitude: 116.4074, datetime_str: '2026-06-21T04:00:00Z' },
    //             },
    //             {
    //                 model_id: 'perez_separation',
    //                 inputs: { ghi: 800 },
    //                 input_mapping: {
    //                     solar_zenith: 'solar_position.solar_zenith',
    //                     datetime_str: 'solar_position.datetime_str',
    //                 },
    //             },
    //             {
    //                 model_id: 'pv_conversion',
    //                 inputs: { temp_air: 25.0 },
    //                 input_mapping: { poa_irradiance: 'perez_separation.dni' },
    //             },
    //         ],
    //     }, null, 2),
    //     responseExample: JSON.stringify({
    //         code: 200,
    //         data: {
    //             total_execution_time: 680,
    //             results: [
    //                 { step: 1, model_id: 'solar_position', status: 'success', execution_time: 210, outputs: { solar_zenith: 22.48, solar_azimuth: 175.64, solar_elevation: 67.52 } },
    //                 { step: 2, model_id: 'perez_separation', status: 'success', execution_time: 195, outputs: { dni: 683.42, dhi: 116.58, kt: 0.782 } },
    //                 { step: 3, model_id: 'pv_conversion', status: 'success', execution_time: 275, outputs: { p_mp: 312.5, v_mp: 38.2, efficiency: 0.458 } },
    //             ],
    //         },
    //     }, null, 2),
    // },
    // {
    //     key: 'chain-validate',
    //     group: '模型链',
    //     method: 'POST',
    //     path: '/api/chain/validate',
    //     title: '验证模型链配置',
    //     description: '在执行前验证模型链配置是否合法，检查各节点模型是否存在、字段映射引用是否有效、输入输出类型是否匹配，不会实际执行模型。',
    //     bodyParams: [
    //         { name: 'chain', type: 'Array', required: true, desc: '与执行接口相同的模型链节点数组' },
    //     ],
    //     requestExample: JSON.stringify({
    //         chain: [
    //             { model_id: 'solar_position', inputs: {} },
    //             { model_id: 'perez_separation', inputs: {}, input_mapping: { solar_zenith: 'solar_position.solar_zenith' } },
    //         ],
    //     }, null, 2),
    //     responseExample: JSON.stringify({
    //         code: 200,
    //         data: {
    //             valid: true,
    //             errors: [],
    //             warnings: ['步骤 2 的 datetime_str 未映射，将使用默认值'],
    //         },
    //     }, null, 2),
    // },
    // {
    //     key: 'chain-templates',
    //     group: '模型链',
    //     method: 'GET',
    //     path: '/api/chain/templates',
    //     title: '获取预置模型链模板',
    //     description: '获取平台内置的常用模型链模板，如完整光伏发电量计算链、辐照分析链等，可直接使用或基于模板修改后提交执行。',
    //     responseExample: JSON.stringify({
    //         code: 200,
    //         data: [
    //             {
    //                 id: 'full_pv_chain',
    //                 name: '完整光伏发电量计算链',
    //                 description: '太阳位置 → 辐照分离 → 平面辐照转换 → 温度模型 → 功率转换',
    //                 steps: ['solar_position', 'perez_separation', 'poa_irradiance', 'temperature_model', 'pv_conversion'],
    //             },
    //             {
    //                 id: 'irradiance_chain',
    //                 name: '辐照分析链',
    //                 description: '太阳位置 → 辐照分离 → 平面辐照转换',
    //                 steps: ['solar_position', 'perez_separation', 'poa_irradiance'],
    //             },
    //         ],
    //     }, null, 2),
    // },
]

// ── 按分组聚合 ────────────────────────────────────────────────
const groupedApiDocs = computed(() => {
    const groups = {}
    for (const doc of apiDocs) {
        if (!groups[doc.group]) groups[doc.group] = []
        groups[doc.group].push(doc)
    }
    return groups
})


// ── 动态模型列表导航（单模型运行分组下） ──────────────────────
const filteredModels = computed(() => {
    const kw = searchKey.value.trim().toLowerCase()
    if (!kw) return allModels.value
    return allModels.value.filter(m =>
        (m.name || '').toLowerCase().includes(kw) ||
        (m.title || '').toLowerCase().includes(kw)
    )
})

// ── 当前选中的接口文档 ────────────────────────────────────────
const currentDoc = computed(() =>
    apiDocs.find(d => d.key === activeKey.value) || null
)

// ── 当前选中的是否为某个具体模型（动态 key: model:xxx）────────
const currentModelName = computed(() => {
    if (!activeKey.value.startsWith('model:')) return null
    return activeKey.value.replace('model:', '')
})

const currentModelInfo = computed(() =>
    allModels.value.find(m => m.name === currentModelName.value) || null
)

// ── 导航选中 ──────────────────────────────────────────────────
function selectDoc(key) {
    activeKey.value = key
}

function selectModel(model) {
    activeKey.value = `model:${model.name}`
}

function goToDebug(modelName) {
    router.push({ path: `/debug/${modelName}` })
}

// ── 复制 ──────────────────────────────────────────────────────
async function copyText(text) {
    if (!text) return
    try {
        await navigator.clipboard.writeText(text)
        ElMessage.success('已复制到剪贴板')
    } catch {
        ElMessage.error('复制失败，请手动复制')
    }
}

// ── 初始化 ────────────────────────────────────────────────────
onMounted(async () => {
    listLoading.value = true
    try {
        const res = await getAllModels()
        const data = res?.data?.data || res?.data || res
        allModels.value = data?.list || data?.items || data?.models
            || data?.results || (Array.isArray(data) ? data : [])
    } catch {
        ElMessage.error('获取模型列表失败')
    } finally {
        listLoading.value = false
    }
    // 默认选中第一个接口
    activeKey.value = apiDocs[0].key
})

// ══════════════════════════════════════════════════════════════
// h() 渲染函数子组件（避免运行时模板编译）
// ══════════════════════════════════════════════════════════════

// ── 参数表格 ──────────────────────────────────────────────────
const ParamTable = (props) =>
    h(ElTable, { data: props.data, class: 'doc-table', size: 'small', border: true }, {
        default: () => [
            h(ElTableColumn, { label: '参数名', minWidth: 180 }, {
                default: ({ row }) => h('code', { class: 'param-code' }, row.name)
            }),
            h(ElTableColumn, { prop: 'type', label: '类型', width: 110 }),
            h(ElTableColumn, { label: '必填', width: 65 }, {
                default: ({ row }) =>
                    h(ElTag, { size: 'small', type: row.required ? 'danger' : 'info', effect: 'plain' },
                        () => row.required ? '是' : '否')
            }),
            h(ElTableColumn, { prop: 'desc', label: '说明', minWidth: 200 }),
        ]
    })
ParamTable.props = ['data']

// ── 错误码表格 ────────────────────────────────────────────────
const ErrorCodeTable = (props) =>
    h(ElTable, { data: props.data, class: 'doc-table', size: 'small', border: true }, {
        default: () => [
            h(ElTableColumn, { label: 'HTTP 状态码', width: 130 }, {
                default: ({ row }) =>
                    h('span', { class: `status-code status-${row.code}` }, String(row.code))
            }),
            h(ElTableColumn, { prop: 'name', label: '类型', width: 200 }),
            h(ElTableColumn, { prop: 'desc', label: '说明' }),
        ]
    })
ErrorCodeTable.props = ['data']

// ── 代码块 ────────────────────────────────────────────────────
const CodeBlock = (props, { emit }) =>
    h('div', { class: 'code-block' }, [
        h('div', { class: 'code-header' }, [
            h('span', { class: 'code-lang' }, props.lang || 'JSON'),
            h(ElButton, {
                size: 'small', text: true,
                onClick: () => emit('copy', props.code)
            }, { default: () => [h(ElIcon, {}, () => h(CopyDocument)), ' 复制'] }),
        ]),
        h('pre', { class: 'code-body' }, props.code),
    ])
CodeBlock.props = ['lang', 'code']
CodeBlock.emits = ['copy']
</script>

<style scoped>
/* ── 根布局 ─────────────────────────────────────────────────── */
.apidocs-root {
    height: 100%;
    overflow: hidden;
    background: #f4f6f9;
}

.apidocs-layout {
    display: flex;
    height: 100%;
}

/* ── 左侧导航 ───────────────────────────────────────────────── */
.apidocs-nav {
    width: 248px;
    min-width: 248px;
    background: #fff;
    border-right: 1px solid #e4e7ed;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.nav-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 16px;
    font-size: 15px;
    font-weight: 600;
    color: #1a2332;
    border-bottom: 1px solid #e4e7ed;
    flex-shrink: 0;
}

.nav-search {
    padding: 10px 12px;
    border-bottom: 1px solid #f0f2f5;
    flex-shrink: 0;
}

.nav-body {
    flex: 1;
    overflow-y: auto;
    padding: 6px 0 16px;
}

/* 分组标签 */
.nav-group-label {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 12px 14px 4px;
    font-size: 11px;
    font-weight: 600;
    color: #909399;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}

/* 导航项 */
.nav-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 7px 14px;
    cursor: pointer;
    font-size: 13px;
    color: #4a5568;
    transition: background 0.12s;
    border-left: 3px solid transparent;
}

.nav-item:hover {
    background: #f5f7ff;
    color: #409eff;
}

.nav-item.active {
    background: #ecf0fd;
    color: #2563eb;
    font-weight: 500;
    border-left-color: #2563eb;
}

.nav-item-title {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* 单模型子列表 */
.nav-model-list {
    background: #fafbfc;
    border-bottom: 1px solid #f0f2f5;
}

.nav-model-item {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 5px 14px 5px 28px;
    cursor: pointer;
    font-size: 12.5px;
    color: #606878;
    transition: background 0.12s;
}

.nav-model-item:hover {
    background: #f0f4ff;
    color: #409eff;
}

.nav-model-item.active {
    background: #e8f0fe;
    color: #2563eb;
    font-weight: 500;
}

.model-dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #c0c4cc;
    flex-shrink: 0;
}

.nav-model-item.active .model-dot {
    background: #2563eb;
}

.nav-model-name {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.nav-model-cat {
    font-size: 11px;
    color: #b0b8c4;
    flex-shrink: 0;
}

.nav-model-empty {
    padding: 8px 28px;
    font-size: 12px;
    color: #c0c4cc;
}

/* Method Tag（导航内小标签）*/
.method-tag {
    font-size: 10px;
    font-weight: 700;
    padding: 1px 5px;
    border-radius: 3px;
    letter-spacing: 0.3px;
    flex-shrink: 0;
}

.method-tag.get {
    background: #e6f4ea;
    color: #1e7e34;
}

.method-tag.post {
    background: #e8f0fe;
    color: #1a56db;
}

.method-tag.put {
    background: #fff3cd;
    color: #856404;
}

.method-tag.delete {
    background: #fde8e8;
    color: #c81e1e;
}

/* ── 右侧主内容 ─────────────────────────────────────────────── */
.apidocs-main {
    flex: 1;
    overflow-y: auto;
    padding: 32px 40px;
    background: #f4f6f9;
}

.doc-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 60%;
    gap: 12px;
    color: #c0c4cc;
    font-size: 14px;
}

/* ── 文档页面 ───────────────────────────────────────────────── */
.doc-page {
    max-width: 900px;
}

/* 标题区 */
.doc-hero {
    margin-bottom: 24px;
}

.doc-hero-title {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
    flex-wrap: wrap;
}

.doc-hero-title h2 {
    margin: 0;
    font-size: 22px;
    font-weight: 700;
    color: #1a2332;
}

.doc-hero-path {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
}

.doc-hero-path code {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 14px;
    color: #2d3748;
    background: #f0f2f5;
    padding: 4px 10px;
    border-radius: 5px;
}

.doc-hero-desc {
    margin: 0;
    color: #606878;
    font-size: 14px;
    line-height: 1.75;
}

/* Method Badge（内容区大标签）*/
.method-badge {
    font-size: 12px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 5px;
    letter-spacing: 0.5px;
    flex-shrink: 0;
}

.method-badge.get {
    background: #e6f4ea;
    color: #1e7e34;
}

.method-badge.post {
    background: #e8f0fe;
    color: #1a56db;
}

.method-badge.put {
    background: #fff3cd;
    color: #856404;
}

.method-badge.delete {
    background: #fde8e8;
    color: #c81e1e;
}

/* 区块卡片 */
.doc-section {
    background: #fff;
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, .06);
}

.section-title {
    font-size: 14px;
    font-weight: 600;
    color: #1a2332;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid #f0f2f5;
}

/* 参数表 */
.doc-table {
    width: 100%;
}

.param-code {
    font-family: monospace;
    font-size: 12.5px;
    color: #c7254e;
    background: #f9f2f4;
    padding: 1px 5px;
    border-radius: 3px;
}

.muted {
    color: #909399;
    font-size: 12.5px;
}

/* ── 代码块（亮色主题，替换原有深色版本）─────────────────────── */
/* ── 代码块（完整重设计）────────────────────────────────────── */
.code-block {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    margin-top: 4px;
}

.code-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 16px;
    background: #1e2433;
    border-bottom: 1px solid #2d3548;
}

.code-lang {
    display: inline-flex;
    align-items: center;
    font-size: 11px;
    font-weight: 700;
    color: #7dd3fc;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 1px;
    text-transform: uppercase;
    background: rgba(125, 211, 252, 0.1);
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid rgba(125, 211, 252, 0.2);
}

.code-body {
    margin: 0;
    padding: 20px 20px;
    /* VSCode One Dark 风格配色 */
    background: #282c34;
    color: #abb2bf;
    font-size: 13px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
    line-height: 1.75;
    overflow-x: auto;
    white-space: pre;
    /* 滚动条美化 */
    scrollbar-width: thin;
    scrollbar-color: #4a5568 transparent;
}

.code-body::-webkit-scrollbar {
    height: 6px;
}

.code-body::-webkit-scrollbar-track {
    background: transparent;
}

.code-body::-webkit-scrollbar-thumb {
    background: #4a5568;
    border-radius: 3px;
}



/* 错误码 */
.status-code {
    font-family: monospace;
    font-size: 13px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
}

.status-200 {
    background: #e6f4ea;
    color: #1e7e34;
}

.status-400,
.status-401,
.status-404 {
    background: #fff3cd;
    color: #856404;
}

.status-422,
.status-500 {
    background: #fde8e8;
    color: #c81e1e;
}

/* 调试跳转卡片 */
.debug-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: linear-gradient(135deg, #e8f0fe 0%, #f0f5ff 100%);
    border: 1px solid #c7d9f8;
    border-radius: 10px;
    padding: 20px 24px;
    gap: 16px;
    cursor: pointer;
    transition: box-shadow 0.15s;
}

.debug-card:hover {
    box-shadow: 0 4px 16px rgba(37, 99, 235, .15);
}

.debug-card-left {
    display: flex;
    align-items: center;
    gap: 16px;
    flex: 1;
}

.debug-card-title {
    font-size: 15px;
    font-weight: 600;
    color: #1a2332;
    margin-bottom: 5px;
}

.debug-card-desc {
    font-size: 13px;
    color: #606878;
    line-height: 1.5;
}

.method-tag.workflow {
    background: #f0f4ff;
    color: #6d28d9;
}

/* WORKFLOW 三步流程卡片 */
.workflow-steps {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.workflow-step-card {
    border: 1px solid #e4e7ed;
    border-radius: 10px;
    overflow: hidden;
    background: #fff;
}

.step-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 18px;
    background: #f8fafc;
    border-bottom: 1px solid #e4e7ed;
}

.step-badge {
    font-size: 11px;
    font-weight: 700;
    background: #2563eb;
    color: #fff;
    padding: 2px 8px;
    border-radius: 20px;
    letter-spacing: 0.5px;
}

.step-method-tag {
    font-size: 11px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 4px;
}

.step-method-tag.get {
    background: #e6f4ea;
    color: #1e7e34;
}

.step-method-tag.post {
    background: #e8f0fe;
    color: #1a56db;
}

.step-path {
    font-size: 13px;
    font-weight: 600;
    color: #1a2332;
    background: transparent;
}

.step-desc-inline {
    font-size: 13px;
    color: #64748b;
    margin-left: 4px;
}

.step-body {
    padding: 16px 18px;
}

.step-note {
    font-size: 13px;
    color: #4a5568;
    margin: 0 0 12px;
    line-height: 1.7;
}

.step-example {
    margin-top: 14px;
}

.step-example-label {
    font-size: 12px;
    font-weight: 600;
    color: #909399;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* WORKFLOW 导航标签颜色 */
.method-tag.workflow {
    background: #f3f0ff;
    color: #6d28d9;
}
</style>
