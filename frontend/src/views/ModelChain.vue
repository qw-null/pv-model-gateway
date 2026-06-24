<template>
    <div class="page">
        <h1 class="page-title">光伏系统模型链</h1>

        <div class="canvas-wrap">

            <!-- Input 区 -->
            <div class="input-zone">
                <span class="zone-label">Input:</span>
                <span v-for="inp in inputs" :key="inp" class="input-node" v-text="inp" />
            </div>

            <!-- Model chain 区 -->
            <div class="chain-zone" ref="chainZone">
                <span class="zone-label">Model chain:</span>
                <!-- ✅ 节点加载中 -->
                <div v-if="nodesLoading" class="nodes-loading">
                    <div class="spinner" /><span>加载模型链节点…</span>
                </div>
                <template v-else>
                    <svg class="svg-layer" ref="svgLayer" />
                    <div class="node-grid">
                        <div v-for="node in nodes" :key="node.key" class="chain-node"
                            :class="{ active: activeKey === node.key }"
                            :style="{ gridColumn: node.col, gridRow: node.row }"
                            :ref="el => { if (el) nodeRefs[node.key] = el }" @click="onNodeClick(node)">
                            <span class="node-icon" v-text="NODE_ICON[node.key]" />
                            <span class="node-label">{{ node.labelCN }}</span>
                            <span class="node-label">({{ node.label }})</span>
                        </div>
                    </div>
                </template>
            </div>

            <!-- Output 区 -->
            <div class="output-zone">
                <div class="output-node">PV power output</div>
            </div>
        </div>

        <!-- <ModelChainResult :nodes="nodes" :candidate-models="modelsByCategory" :node-icons="NODE_ICON"
            @run-chain="onRunChain" class="canvas-wrap" /> -->

        <!-- 侧边抽屉 -->
        <Transition name="slide">
            <div v-if="drawerVisible" class="drawer-overlay" @click.self="closeDrawer">
                <div class="drawer">

                    <!-- 抽屉头 -->
                    <div class="drawer-header">
                        <div class="drawer-header-left">
                            <span class="drawer-icon" v-text="NODE_ICON[activeKey] || '📦'" />
                            <div>
                                <div class="drawer-title">{{ activeNode?.labelCN }} - {{ activeNode?.label }} </div>
                                <div class="drawer-sub" v-text="activeNode?.category || ''" />
                            </div>
                        </div>
                        <button class="drawer-close" @click="closeDrawer">&#x2715;</button>
                    </div>

                    <!-- 列表加载中 -->
                    <div v-if="listLoading" class="loading-wrap">
                        <div class="spinner" />
                        <span>加载模型列表…</span>
                    </div>

                    <!-- 模型卡片列表 -->
                    <div v-else class="model-list">
                        <div v-for="model in modelList" :key="model.id" class="model-card"
                            :class="{ 'model-card--active': selectedModel?.name === model.name }"
                            @click="onModelClick(model)">
                            <div class="model-card-top">
                                <span class="model-num" v-text="model.version ? 'v' + model.version : 'v1.0'" />
                                <span class="model-name" v-text="model.title" />
                                <span class="model-tag" v-text="model.category" />
                            </div>
                            <div class="model-card-desc" v-text="model.description" />
                        </div>

                        <div v-if="!listLoading && modelList.length === 0" class="empty-tip">
                            暂无该分类下的模型
                        </div>
                    </div>

                    <!-- 详情面板 -->
                    <Transition name="fade">
                        <div v-if="detailVisible" class="detail-panel">

                            <!-- 详情头 -->
                            <div class="detail-header">
                                <button class="back-btn" @click="closeDetail">&#8592; 返回列表</button>
                                <div class="detail-title-wrap">
                                    <span class="detail-title" v-text="detail?.title || ''" />
                                    <span class="detail-version" v-text="detail ? 'v' + detail.version : ''" />
                                </div>
                            </div>

                            <!-- 详情加载中 -->
                            <div v-if="detailLoading" class="loading-wrap">
                                <div class="spinner" />
                                <span>加载模型详情…</span>
                            </div>

                            <template v-else-if="detail">

                                <!-- 描述 -->
                                <div class="detail-section">
                                    <div class="section-title">模型描述</div>
                                    <div class="detail-desc" v-text="detail.description" />
                                </div>

                                <!-- 基本信息 -->
                                <div class="detail-section">
                                    <div class="section-title">基本信息</div>
                                    <div class="info-grid">
                                        <div class="info-item">
                                            <span class="info-label">作者</span>
                                            <span class="info-value" v-text="detail.author || '-'" />
                                        </div>
                                        <div class="info-item">
                                            <span class="info-label">分类</span>
                                            <span class="info-value" v-text="detail.category || '-'" />
                                        </div>
                                        <div class="info-item">
                                            <span class="info-label">调用次数</span>
                                            <span class="info-value" v-text="(detail.call_count ?? 0) + ' 次'" />
                                        </div>
                                        <div class="info-item">
                                            <span class="info-label">更新时间</span>
                                            <span class="info-value" v-text="detail.updated_at || '-'" />
                                        </div>
                                        <div class="info-item">
                                            <span class="info-label">接口路径</span>
                                            <span class="info-value api-path" v-text="detail.api_path || '-'" />
                                        </div>
                                    </div>
                                </div>

                                <!-- 关联模型 -->
                                <div class="detail-section" v-if="detail.related_models">
                                    <div class="section-title">模型关联</div>
                                    <div class="relation-row">
                                        <div class="relation-item"
                                            v-if="detail.related_models.pre && detail.related_models.pre.length">
                                            <span class="relation-label">前置模型</span>
                                            <span v-for="r in detail.related_models.pre" :key="r"
                                                class="relation-tag relation-tag--pre" v-text="r" />
                                        </div>
                                        <div class="relation-item"
                                            v-if="detail.related_models.post && detail.related_models.post.length">
                                            <span class="relation-label">后续模型</span>
                                            <span v-for="r in detail.related_models.post" :key="r"
                                                class="relation-tag relation-tag--post" v-text="r" />
                                        </div>
                                        <div v-if="!detail.related_models.pre?.length && !detail.related_models.post?.length"
                                            class="empty-tip" style="padding: 8px 0;">
                                            暂无关联模型
                                        </div>
                                    </div>
                                </div>

                                <!-- 标签 -->
                                <div class="detail-section" v-if="detail.tags && detail.tags.length">
                                    <div class="section-title">标签</div>
                                    <div class="tags-wrap">
                                        <span v-for="tag in detail.tags" :key="tag" class="tag" v-text="tag" />
                                    </div>
                                </div>

                                <!-- 运行入口 -->
                                <div class="detail-section">
                                    <button class="run-btn" @click="goToDebug">
                                        &#9654; 运行模型
                                    </button>
                                </div>

                            </template>
                        </div>
                    </Transition>

                </div>
            </div>
        </Transition>
    </div>
</template>

<script setup>
    import { ref, reactive, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAllModels, getModelDetail } from '@/api/modelChain'
import ModelChainResult from '@/components/ModelChainResult.vue'
import { remoteAlgorithm } from '@/utils/chain-algorithms/index.js'

const router = useRouter()
const inputs = ['Time and location', 'GHI', 'Albedo', 'Temperature', 'Wind speed']

const NODE_ICON = {
  '太阳位置': '☀',
  '辐照分离': '⟁',
  '辐照度':   '⬡',
  '电池温度': '🌡',
  '光学修正': '◈',
  '光伏转换': '⚡',
  '直流损失': '▣',
  '交流损失': '▣',
  '逆变器':   '⟳',
}

const NODE_POSITION = {
  '太阳位置': { col: 2, row: 1 },
  '电池温度': { col: 6, row: 1 },
  '辐照分离': { col: 3, row: 2 },
  '辐照度':   { col: 4, row: 2 },
  '直流损失': { col: 1, row: 3 },
  '光学修正': { col: 4, row: 3 },
  '光伏转换': { col: 5, row: 3 },
  '逆变器':   { col: 4, row: 4 },
  '交流损失': { col: 4, row: 5 },
}

const NODE_CONFIG = {
  '太阳位置': { label: 'Solar Position',   labelCN: '太阳位置', icon: '☀️', category: '太阳位置', filterNames: null, multi: false },
  '电池温度': { label: 'Cell Temperature', labelCN: '电池温度', icon: '🌡️', category: '电池温度', filterNames: null, multi: false },
  '辐照分离': { label: 'Irradiance Split', labelCN: '辐照分离', icon: '🌤️', category: '辐照分离', filterNames: null, multi: false },
  '辐照度':   { label: 'Irradiance',       labelCN: '辐照度',   icon: '💡', category: '辐照度',   filterNames: null, multi: false },
  '光学修正': { label: 'IAM',              labelCN: '光学修正', icon: '🔭', category: '光学修正', filterNames: null, multi: false },
  '光伏转换': { label: 'PV Conversion',    labelCN: '光伏转换', icon: '⚡', category: '光伏转换', filterNames: null, multi: false },
  '逆变器':   { label: 'Inverter',         labelCN: '逆变器',   icon: '🔌', category: '逆变器',   filterNames: null, multi: false },
  '直流损失': {
    label: 'DC Loss', labelCN: '直流损失', icon: '🔋',
    category: '损失模型',
    filterNames: ['dc_cable_loss'],
    multi: true,
  },
  '交流损失': {
    label: 'AC Loss', labelCN: '交流损失', icon: '🔁',
    category: '损失模型',
    filterNames: ['ac_cable_loss', 'transformer_oil', 'transformer_dry'],
    multi: true,
  },
}

const allModels    = ref([])
const nodesLoading = ref(false)

// ✅ 修复：nodes 从 NODE_CONFIG 派生，而不是从 allModels category 去重
// 这样直流损失/交流损失等逻辑节点也能正确出现
const nodes = computed(() => {
  return Object.entries(NODE_CONFIG).map(([key, config]) => ({
    key,
    label:    config.label,
    labelCN:  config.labelCN,
    category: config.category,
    icon:     NODE_ICON[key] || '📦',
    col:      NODE_POSITION[key]?.col || 1,
    row:      NODE_POSITION[key]?.row || 1,
    multi:    config.multi || false,
  }))
})

// ✅ 修复：按节点 key 分组，支持 filterNames 过滤
const modelsByCategory = computed(() => {
  const map = {}
  Object.entries(NODE_CONFIG).forEach(([key, config]) => {
    const pool = allModels.value.filter(m => m.category === config.category)
    map[key] = config.filterNames
      ? pool.filter(m => config.filterNames.includes(m.name))
      : pool
  })
  return map
})

// 成链结果
const chainResults = ref([])

async function loadAllModels() {
  nodesLoading.value = true
  try {
    const res = await getAllModels()
    allModels.value = parseList(res)
    console.log('✅ 模型元数据加载完成:', allModels.value.length, '个模型')

    // ✅ 修复：数据加载完成后再执行成链算法
    const results = await remoteAlgorithm({
      nodes:           nodes.value,
      candidateModels: modelsByCategory.value,
      edges,
      multiSelectKeys: ['直流损失', '交流损失'],
    })
    chainResults.value = results
    console.log('🔗 成链结果:', results.length, '种组合')

  } catch (e) {
    console.error('❌ 加载模型元数据失败:', e)
    allModels.value = []
  } finally {
    nodesLoading.value = false
    nextTick(() => setTimeout(drawEdges, 80))
  }
}

const activeKey     = ref(null)
const activeNode    = ref(null)
const drawerVisible = ref(false)
const listLoading   = ref(false)
const modelList     = ref([])
const detailVisible = ref(false)
const detailLoading = ref(false)
const selectedModel = ref(null)
const detail        = ref(null)
const nodeRefs      = reactive({})
const outputRef     = ref(null)
const chainZone     = ref(null)
const svgLayer      = ref(null)

function parseList(res) {
  const raw = res.data
  if (Array.isArray(raw))       return raw
  if (Array.isArray(raw?.data)) return raw.data
  if (Array.isArray(raw?.list)) return raw.list
  return []
}

function parseDetail(res) {
  const raw = res.data
  if (raw?.data && typeof raw.data === 'object') return raw.data
  return raw
}

// ✅ 修复：用 node.key 而不是 node.category 取模型列表
function onNodeClick(node) {
  if (activeKey.value === node.key && drawerVisible.value) {
    closeDrawer()
    return
  }
  activeKey.value     = node.key
  activeNode.value    = node
  drawerVisible.value = true
  detailVisible.value = false
  selectedModel.value = null
  detail.value        = null

  // ✅ 用 node.key 取数据（直流损失/交流损失才能正确匹配）
  modelList.value = modelsByCategory.value[node.key] || []
}

async function onModelClick(model) {
  selectedModel.value = model
  detailVisible.value = true
  detailLoading.value = true
  detail.value        = null
  try {
    const res = await getModelDetail(model.name)
    detail.value = parseDetail(res)
  } catch (e) {
    detail.value = null
  } finally {
    detailLoading.value = false
  }
}

function goToDebug() {
  router.push({ path: '/debug/' + (selectedModel.value?.name || '') })
}

function closeDetail() {
  detailVisible.value = false
  selectedModel.value = null
  detail.value        = null
}

function closeDrawer() {
  drawerVisible.value = false
  activeKey.value     = null
  activeNode.value    = null
  detailVisible.value = false
}

function onRunChain(chain) {
  router.push({ path: '/run-chain', query: { config: JSON.stringify(chain) } })
}

const edges = [
  ['太阳位置', '辐照分离'],
  ['太阳位置', '直流损失'],
  ['辐照分离', '辐照度'  ],
  ['辐照度',   '光学修正'],
  ['光学修正', '光伏转换'],
  ['电池温度', '光伏转换'],
  ['直流损失', '辐照度'  ],
  ['直流损失', '光伏转换'],
  ['光伏转换', '逆变器'  ],
  ['逆变器',   '交流损失'],
]

function getCenter(el, parentRect) {
  const r = el.getBoundingClientRect()
  return {
    x:  r.left - parentRect.left + r.width  / 2,
    y:  r.top  - parentRect.top  + r.height / 2,
    hw: r.width  / 2,
    hh: r.height / 2,
  }
}

function drawEdges() {
  const svg  = svgLayer.value
  const zone = chainZone.value
  if (!svg || !zone) return

  const zoneRect = zone.getBoundingClientRect()
  svg.innerHTML  = ''

  const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs')
  defs.innerHTML = [
    '<marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">',
    '<path d="M0,0 L0,6 L8,3 z" fill="#5a9abf" opacity="0.75"/>',
    '</marker>',
  ].join('')
  svg.appendChild(defs)

  const allRefs = { ...nodeRefs, output: outputRef.value }
  edges.forEach(([fk, tk]) => {
    const fe = allRefs[fk]
    const te = allRefs[tk]
    if (!fe || !te) return

    const f   = getCenter(fe, zoneRect)
    const t   = getCenter(te, zoneRect)
    const dx  = t.x - f.x
    const dy  = t.y - f.y
    const len = Math.sqrt(dx * dx + dy * dy) || 1
    const fx  = f.x + (dx / len) * (Math.max(f.hw, f.hh) + 4)
    const fy  = f.y + (dy / len) * (Math.max(f.hw, f.hh) + 4)
    const tx  = t.x - (dx / len) * (Math.max(t.hw, t.hh) + 8)
    const ty  = t.y - (dy / len) * (Math.max(t.hw, t.hh) + 8)
    const cx  = fx + (tx - fx) * 0.5
    const d   = ['M', fx, fy, 'C', cx, fy, cx, ty, tx, ty].join(' ')

    const p = document.createElementNS('http://www.w3.org/2000/svg', 'path')
    p.setAttribute('d', d)
    p.setAttribute('stroke', '#5a9abf')
    p.setAttribute('stroke-width', '1.8')
    p.setAttribute('fill', 'none')
    p.setAttribute('opacity', '0.65')
    p.setAttribute('marker-end', 'url(#arr)')
    svg.appendChild(p)
  })
}

onMounted(() => {
  loadAllModels()
  window.addEventListener('resize', drawEdges)
})

onUnmounted(() => window.removeEventListener('resize', drawEdges))

</script>

<style scoped>
.page {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 24px 16px 40px;
    min-height: 100vh;
    background: #f0f4f8;
    font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

.page-title {
    font-size: 20px;
    font-weight: 700;
    color: #1a2e4a;
    margin-bottom: 20px;
    letter-spacing: 1px;
}

.canvas-wrap {
    width: 100%;
    max-width: 1100px;
    background: #ddeeff;
    border: 2px dashed #7ab3d4;
    border-radius: 16px;
    overflow: hidden;
}

.input-zone {
    background: #fef3dc;
    border-bottom: 1px dashed #c8a96e;
    padding: 12px 20px 14px;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}

.zone-label {
    font-size: 13px;
    font-weight: 600;
    color: #555;
}

.input-node {
    background: #f5a623;
    color: #fff;
    border-radius: 20px;
    padding: 6px 18px;
    font-size: 13px;
    font-weight: 600;
    white-space: nowrap;
}

.chain-zone {
    padding: 20px 24px 12px;
    position: relative;
}

.svg-layer {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    overflow: visible;
}

.node-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    grid-template-rows: repeat(5, 64px);
    gap: 16px 12px;
    position: relative;
    z-index: 2;
}

.chain-node {
    background: #b8dff0;
    border: 2px solid #7ab3d4;
    border-radius: 22px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    font-size: 12px;
    font-weight: 600;
    color: #1a3a52;
    cursor: pointer;
    transition: background 0.18s, transform 0.15s, box-shadow 0.18s;
    padding: 6px 8px;
    line-height: 1.3;
    user-select: none;
    gap: 2px;
}

.chain-node:hover {
    background: #7fc9e8;
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(100, 180, 220, .35);
}

.chain-node.active {
    background: #3a9fd6;
    color: #fff;
    border-color: #1a6fa0;
    box-shadow: 0 6px 20px rgba(30, 120, 180, .4);
}

.node-icon {
    font-size: 16px;
    line-height: 1;
}

.node-label {
    font-size: 11px;
}

.output-zone {
    background: #e0f2e0;
    border-top: 1px dashed #7abf7a;
    padding: 14px 20px;
    display: flex;
    justify-content: center;
}

.output-node {
    background: #4caf50;
    color: #fff;
    border-radius: 20px;
    padding: 8px 32px;
    font-size: 14px;
    font-weight: 700;
}

.drawer-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, .25);
    z-index: 200;
    display: flex;
    justify-content: flex-end;
}

.drawer {
    width: 480px;
    max-width: 96vw;
    height: 100%;
    background: #fff;
    box-shadow: -8px 0 40px rgba(0, 0, 0, .18);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
}

.drawer-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 20px 14px;
    border-bottom: 1px solid #e8eef4;
    background: #f7fbff;
    flex-shrink: 0;
}

.drawer-header-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.drawer-icon {
    font-size: 26px;
    line-height: 1;
}

.drawer-title {
    font-size: 16px;
    font-weight: 700;
    color: #1a3a52;
}

.drawer-sub {
    font-size: 12px;
    color: #7a9ab8;
    margin-top: 2px;
}

.drawer-close {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    border: none;
    background: #edf2f7;
    cursor: pointer;
    font-size: 15px;
    color: #555;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background .15s;
    flex-shrink: 0;
}

.drawer-close:hover {
    background: #d8e2ec;
}

.model-list {
    flex: 1;
    overflow-y: auto;
    padding: 14px 16px;
}

.empty-tip {
    text-align: center;
    color: #aab8c8;
    font-size: 13px;
    padding: 40px 0;
}

.model-card {
    border: 1.5px solid #e0eaf2;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: box-shadow .15s, border-color .15s, background .15s;
}

.model-card:hover {
    border-color: #7ab3d4;
    box-shadow: 0 4px 14px rgba(58, 159, 214, .15);
    background: #f7fbff;
}

.model-card--active {
    border-color: #3a9fd6;
    background: #edf6fd;
}

.model-card-top {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 5px;
    flex-wrap: wrap;
}

.model-num {
    background: #3a9fd6;
    color: #fff;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    white-space: nowrap;
}

.model-name {
    font-size: 14px;
    font-weight: 600;
    color: #1a3a52;
}

.model-tag {
    font-size: 11px;
    background: #f0f7ff;
    border: 1px solid #c8dff0;
    color: #3a7abf;
    border-radius: 8px;
    padding: 1px 8px;
}

.model-card-desc {
    font-size: 12px;
    color: #6b8099;
    line-height: 1.55;
}

.detail-panel {
    position: absolute;
    inset: 0;
    background: #fff;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    z-index: 10;
}

.detail-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 20px 12px;
    border-bottom: 1px solid #e8eef4;
    background: #f7fbff;
    flex-shrink: 0;
    position: sticky;
    top: 0;
    z-index: 2;
}

.back-btn {
    background: none;
    border: 1.5px solid #b8d4e8;
    border-radius: 8px;
    color: #3a7abf;
    font-size: 13px;
    padding: 5px 12px;
    cursor: pointer;
    white-space: nowrap;
    transition: background .15s;
}

.back-btn:hover {
    background: #edf6fd;
}

.detail-title-wrap {
    flex: 1;
}

.detail-title {
    font-size: 15px;
    font-weight: 700;
    color: #1a3a52;
    display: block;
}

.detail-version {
    font-size: 11px;
    color: #7a9ab8;
}

.detail-section {
    padding: 14px 20px;
    border-bottom: 1px solid #f0f4f8;
}

.section-title {
    font-size: 13px;
    font-weight: 700;
    color: #3a7abf;
    margin-bottom: 10px;
}

.detail-desc {
    font-size: 13px;
    color: #445566;
    line-height: 1.7;
}

.info-grid {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.info-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    font-size: 12px;
}

.info-label {
    color: #7a9ab8;
    width: 60px;
    flex-shrink: 0;
}

.info-value {
    color: #334455;
}

.api-path {
    font-family: monospace;
    font-size: 11px;
    background: #f0f4f8;
    padding: 2px 8px;
    border-radius: 4px;
    color: #3a7abf;
}

.relation-row {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.relation-item {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
}

.relation-label {
    font-size: 12px;
    color: #7a9ab8;
    width: 60px;
    flex-shrink: 0;
}

.relation-tag {
    font-size: 11px;
    border-radius: 6px;
    padding: 2px 10px;
    font-weight: 600;
}

.relation-tag--pre {
    background: #fff3e0;
    color: #e07a00;
    border: 1px solid #f5c07a;
}

.relation-tag--post {
    background: #e8f5e9;
    color: #2e7d32;
    border: 1px solid #81c784;
}

.tags-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.tag {
    background: #edf6fd;
    border: 1px solid #b8d8f0;
    color: #3a7abf;
    border-radius: 20px;
    font-size: 11px;
    padding: 3px 12px;
}

.run-btn {
    width: 100%;
    background: #3a9fd6;
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 11px 0;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: background .15s, transform .12s;
}

.run-btn:hover {
    background: #1a7abf;
    transform: translateY(-1px);
}

.loading-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 48px 20px;
    color: #7a9ab8;
    font-size: 13px;
    flex: 1;
}

.spinner {
    width: 28px;
    height: 28px;
    border: 3px solid #d0e8f4;
    border-top-color: #3a9fd6;
    border-radius: 50%;
    animation: spin .7s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.slide-enter-active,
.slide-leave-active {
    transition: opacity .22s ease;
}

.slide-enter-active .drawer,
.slide-leave-active .drawer {
    transition: transform .25s cubic-bezier(.4, 0, .2, 1);
}

.slide-enter-from .drawer,
.slide-leave-to .drawer {
    transform: translateX(100%);
}

.slide-enter-from,
.slide-leave-to {
    opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity .18s ease, transform .18s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
    transform: translateX(20px);
}
</style>
