<template>
    <div class="result-wrap">
        <div class="result-header">
            <span class="result-title">🔗 模型链可能组合</span>
            <div class="result-header-right">
                <span class="result-count" v-if="!loading">
                    共 <b>{{ allChains.length }}</b> 种组合
                </span>
                <button class="result-refresh" @click="loadChains" :disabled="loading">
                    {{ loading ? '加载中…' : '🔄 刷新' }}
                </button>
            </div>
        </div>

        <!-- 加载中 -->
        <div v-if="loading" class="result-loading">
            <div class="spinner" />
            <span>正在从数据库加载模型数据并计算组合…</span>
        </div>

        <!-- 错误提示 -->
        <div v-else-if="error" class="result-error">
            <span>⚠ 加载失败：{{ error }}</span>
            <button class="retry-btn" @click="loadChains">重试</button>
        </div>

        <!-- 无数据 -->
        <div v-else-if="allChains.length === 0" class="result-empty">
            暂无可用的模型链组合，请检查各节点是否已有模型数据
        </div>

        <!-- 组合列表 -->
        <div v-else class="result-list">
            <div v-for="(chain, idx) in allChains" :key="idx" class="result-card"
                :class="{ 'result-card--active': activeIdx === idx }" @click="onChainClick(idx)">
                <!-- 卡片头 -->
                <div class="result-card-header">
                    <span class="result-card-index">组合 #{{ idx + 1 }}</span>
                    <button class="result-card-run" @click.stop="onRunChain(chain)">
                        ▶ 运行
                    </button>
                </div>

                <!-- 步骤流 -->
                <div class="result-chain-flow">
                    <div v-for="(step, sIdx) in chain.steps" :key="step.nodeKey" class="result-step">
                        <div class="result-step-node">
                            <span class="result-step-icon" v-text="nodeIcons[step.nodeKey] || '📦'" />
                            <div class="result-step-info">
                                <span class="result-step-label" v-text="step.labelCN" />
                                <span class="result-step-model" v-text="step.model.title" />
                                <span class="result-step-ver" v-text="'v' + (step.model.version || '1.0')" />
                            </div>
                        </div>
                        <span v-if="sIdx < chain.steps.length - 1" class="result-step-arrow">→</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { remoteAlgorithm } from '@/utils/chain-algorithms/index.js'

const props = defineProps({
  nodes: {
    type: Array,
    default: () => [],
  },
  candidateModels: {
    type: Object,
    default: () => ({}),
  },
  nodeIcons: {
    type: Object,
    default: () => ({}),
  },
  // ✅ 不再通过 prop 传递算法，直接在组件内部引用
  // 后续替换算法只需改这一行 import
})

const emit = defineEmits(['run-chain'])

const allChains = ref([])
const activeIdx = ref(null)
const loading   = ref(false)
const error     = ref(null)

async function loadChains() {
  console.log('🚀 loadChains 触发, nodes:', props.nodes)

  if (!props.nodes?.length) {
    console.warn('⚠️ nodes 为空')
    return
  }

  loading.value   = true
  error.value     = null
  activeIdx.value = null

  try {
    // ✅ 直接调用，不通过 prop 传递
    const result = await remoteAlgorithm({
      nodes:           props.nodes,
      candidateModels: props.candidateModels,
    })
    console.log('✅ 算法返回结果:', result)
    allChains.value = result
  } catch (e) {
    console.error('❌ 算法执行失败:', e)
    error.value     = e?.message || '未知错误'
    allChains.value = []
  } finally {
    loading.value = false
  }
}

function onChainClick(idx) {
  activeIdx.value = activeIdx.value === idx ? null : idx
}

function onRunChain(chain) {
  emit('run-chain', chain)
}

watch(() => props.nodes, loadChains, { deep: true, immediate: false })

onMounted(() => {
  console.log('📦 ModelChainResult mounted, nodes长度:', props.nodes?.length)
  loadChains()
})
</script>


<style scoped>
.result-wrap {
    background: #f7fbff;
    border: 1.5px solid #c0d8ee;
    border-radius: 10px;
    padding: 16px;
    margin-top: 16px;
}

.result-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}

.result-title {
    font-size: 15px;
    font-weight: 600;
    color: #2c5f7a;
}

.result-header-right {
    display: flex;
    align-items: center;
    gap: 10px;
}

.result-count {
    font-size: 13px;
    color: #888;
}

.result-count b {
    color: #5a9abf;
    font-size: 15px;
}

.result-refresh {
    font-size: 12px;
    padding: 3px 10px;
    background: #fff;
    border: 1px solid #8bbdd4;
    border-radius: 6px;
    color: #5a9abf;
    cursor: pointer;
    transition: background .2s;
}

.result-refresh:hover:not(:disabled) {
    background: #e8f4fb;
}

.result-refresh:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* 状态区 */
.result-loading {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 40px;
    color: #888;
    font-size: 13px;
}

.result-error {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 24px;
    color: #e07070;
    font-size: 13px;
}

.retry-btn {
    padding: 4px 12px;
    background: #fff;
    border: 1px solid #e07070;
    border-radius: 6px;
    color: #e07070;
    cursor: pointer;
    font-size: 12px;
}

.result-empty {
    text-align: center;
    color: #aaa;
    font-size: 13px;
    padding: 32px 0;
}

/* 组合列表 */
.result-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 520px;
    overflow-y: auto;
}

.result-card {
    background: #fff;
    border: 1.5px solid #dce8f5;
    border-radius: 8px;
    padding: 12px 14px;
    cursor: pointer;
    transition: border-color .2s, box-shadow .2s;
}

.result-card:hover {
    border-color: #5a9abf;
    box-shadow: 0 2px 8px rgba(90, 154, 191, .15);
}

.result-card--active {
    border-color: #5a9abf;
    background: #f0f8ff;
    box-shadow: 0 2px 12px rgba(90, 154, 191, .25);
}

.result-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
}

.result-card-index {
    font-size: 12px;
    font-weight: 600;
    color: #5a9abf;
}

.result-card-run {
    font-size: 12px;
    padding: 3px 12px;
    background: #5a9abf;
    color: #fff;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: background .2s;
}

.result-card-run:hover {
    background: #3a7a9f;
}

/* 步骤流 */
.result-chain-flow {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
}

.result-step {
    display: flex;
    align-items: center;
    gap: 6px;
}

.result-step-node {
    display: flex;
    align-items: center;
    gap: 6px;
    background: #e8f4fb;
    border: 1px solid #b8d8ee;
    border-radius: 8px;
    padding: 5px 10px;
}

.result-step-icon {
    font-size: 14px;
    line-height: 1;
}

.result-step-info {
    display: flex;
    flex-direction: column;
}

.result-step-label {
    font-size: 10px;
    color: #888;
    line-height: 1.3;
}

.result-step-model {
    font-size: 12px;
    font-weight: 600;
    color: #2c5f7a;
    line-height: 1.3;
}

.result-step-ver {
    font-size: 10px;
    color: #aaa;
    line-height: 1.2;
}

.result-step-arrow {
    font-size: 14px;
    color: #5a9abf;
    font-weight: bold;
    flex-shrink: 0;
}

/* Spinner */
.spinner {
    width: 20px;
    height: 20px;
    border: 2px solid #ddd;
    border-top-color: #5a9abf;
    border-radius: 50%;
    animation: spin .8s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}
</style>
