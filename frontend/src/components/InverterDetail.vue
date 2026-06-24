<template>
  <div class="inverter-detail">
    <div class="tab-nav">
      <span
        v-for="tab in tabs"
        :key="tab.name"
        class="tab-item"
        :class="{ active: activeTab === tab.name }"
        @click="activeTab = tab.name"
      >{{ tab.label }}</span>
    </div>
    <div class="tab-divider" />

    <!-- ── Tab 1：基本数据 ────────────────────────────────────── -->
    <div v-show="activeTab === 'basic'" class="tab-content">
      <div class="section-title">基本信息</div>
      <el-form :model="form" label-position="right" size="default">
        <el-row :gutter="40">
          <el-col :span="12">
            <el-form-item label="厂家">
              <span class="readonly-text">{{ form.manufacturer }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="* 型号">
              <span class="readonly-text">{{ form.model_name }}</span>
            </el-form-item>
          </el-col>
        </el-row>

        <div class="section-title">输入侧</div>
        <el-row :gutter="40">
          <el-col :span="12">
            <el-form-item label="* 最小mpp电压">
              <el-input v-model.number="form.vmp_min">
                <template #append>V</template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="* 标称mpp电压">
              <el-input v-model.number="form.vmp_nom">
                <template #append>V</template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="* 最大mpp电压">
              <el-input v-model.number="form.vmp_max">
                <template #append>V</template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="* 绝对最大直流电压">
              <el-input v-model.number="form.vdc_max">
                <template #append>V</template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <div class="section-title">输出侧</div>
        <el-row :gutter="40">
          <el-col :span="12">
            <el-form-item label="* 输出电压">
              <el-input v-model.number="form.vac_out" @input="recalcCurrent">
                <template #append>V</template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="* 标称交流功率">
              <el-input v-model.number="form.pac_nom" @input="recalcCurrent">
                <template #append>kW</template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="* 最大交流功率">
              <el-input v-model.number="form.pac_max" @input="recalcCurrent">
                <template #append>kW</template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="标称输出电流">
              <span class="readonly-text">{{ calcIacNom }} A</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最大输出电流">
              <span class="readonly-text">{{ calcIacMax }} A</span>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>

    <!-- ── Tab 2：效率曲线 ────────────────────────────────────── -->
    <div v-show="activeTab === 'curve'" class="tab-content">
      <div class="curve-control-row">
        <span class="control-label">输入电压：</span>
        <el-radio-group v-model="curveVoltage" @change="renderCurveChart">
          <el-radio
            v-for="opt in voltageOptions"
            :key="opt.value"
            :value="opt.value"
          >{{ opt.label }}</el-radio>
        </el-radio-group>
      </div>
      <div class="curve-control-row" style="margin-top:16px">
        <span class="control-label">显示模式：</span>
        <el-radio-group v-model="curveMode" @change="renderCurveChart">
          <el-radio value="pin_eta">输入功率vs效率</el-radio>
          <el-radio value="pout_eta">输出功率vs效率</el-radio>
          <el-radio value="pin_pout">输入功率vs输出功率</el-radio>
        </el-radio-group>
      </div>

      <div class="curve-data-block" v-if="activeCurve">
        <div class="data-row">
          <div class="data-label">{{ xAxisLabel }}(kW)</div>
          <div
            v-for="(val, i) in xDataList"
            :key="'x'+i"
            class="data-cell"
            :class="{ 'cell-disabled': val === 0 && i === 0 }"
          >{{ formatNum(val) }}</div>
        </div>
        <div class="data-row">
          <div class="data-label">{{ yAxisLabel }}{{ curveMode === 'pin_pout' ? '(kW)' : '(%)' }}</div>
          <div
            v-for="(val, i) in yDataList"
            :key="'y'+i"
            class="data-cell"
            :class="{ 'cell-disabled': val === 0 && i === 0 }"
          >{{ formatNum(val) }}</div>
        </div>
      </div>

      <div ref="curveChartEl" class="echarts-box" />
    </div>

    <!-- ── Tab 3：输出参数 ────────────────────────────────────── -->
    <div v-show="activeTab === 'output'" class="tab-content">
      <div class="section-title">最大交流功率f（温度）</div>
      <el-form :model="form" label-position="right" size="default">
        <el-row :gutter="40" align="middle" class="temp-row">
          <el-col :span="8">
            <el-form-item label="标称交流功率" class="no-margin">
              <span class="readonly-text">{{ form.pac_nom }} kW</span>
            </el-form-item>
          </el-col>
          <el-col :span="8" class="up-to-col">
            <span class="up-to-label">up to</span>
            <el-input v-model.number="form.temp_pac_nom" style="width:100px" @change="renderTempChart">
              <template #append>℃</template>
            </el-input>
          </el-col>
        </el-row>
        <el-row :gutter="40" align="middle" class="temp-row">
          <el-col :span="8">
            <el-form-item label="最大交流功率" class="no-margin">
              <span class="readonly-text">{{ form.pac_max }} kW</span>
            </el-form-item>
          </el-col>
          <el-col :span="8" class="up-to-col">
            <span class="up-to-label">at</span>
            <el-input v-model.number="form.temp_pac_max" style="width:100px" @change="renderTempChart">
              <template #append>℃</template>
            </el-input>
          </el-col>
        </el-row>
        <el-row :gutter="40" align="middle" class="temp-row">
          <el-col :span="8">
            <el-form-item label="高温功率限制" class="no-margin">
              <el-input v-model.number="form.pac_derating" style="width:160px" @change="renderTempChart">
                <template #append>kW</template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="8" class="up-to-col">
            <span class="up-to-label">at</span>
            <el-input v-model.number="form.temp_derating" style="width:100px" @change="renderTempChart">
              <template #append>℃</template>
            </el-input>
          </el-col>
        </el-row>
        <el-row :gutter="40" align="middle" class="temp-row">
          <el-col :span="8">
            <el-form-item label="高温功率限制极限" class="no-margin">
              <span class="readonly-text">{{ form.pac_derating }} kW</span>
            </el-form-item>
          </el-col>
          <el-col :span="8" class="up-to-col">
            <span class="up-to-label">at</span>
            <el-input v-model.number="form.temp_derating_limit" style="width:100px" @change="renderTempChart">
              <template #append>℃</template>
            </el-input>
          </el-col>
        </el-row>
      </el-form>
      <div ref="tempChartEl" class="echarts-box" style="margin-top:24px" />
    </div>

    <!-- ── 底部按钮 ─────────────────────────────────────────── -->
    <!-- <div class="drawer-footer">
      <el-button @click="$emit('cancel')">取 消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
    </div> -->
  </div>
</template>

<script setup>
import {
  ref, reactive, computed, watch,
  nextTick, onMounted, onBeforeUnmount,
} from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { inverterApi } from '@/api/inverter'

// ── Props / Emits ─────────────────────────────────────────────
const props = defineProps({
  inverter: {
    type: Object,
    required: true
  }
})
const emit = defineEmits(['updated', 'cancel'])

// ── Tab 配置 ──────────────────────────────────────────────────
const tabs = [
  { name: 'basic',  label: '1.基本数据' },
  { name: 'curve',  label: '2.效率曲线' },
  { name: 'output', label: '3.输出参数' },
]
const activeTab = ref('basic')

// ── 表单数据（深拷贝，避免直接修改 props）────────────────────
const form = reactive(JSON.parse(JSON.stringify(props.inverter)))

// ── 只读电流计算 ───────────────────────────────────────────────
const calcIacNom = computed(() => {
  if (!form.vac_out || form.vac_out === 0) return form.iac_nom ?? 0
  return (form.pac_nom * 1000 / form.vac_out).toFixed(1)
})
const calcIacMax = computed(() => {
  if (!form.vac_out || form.vac_out === 0) return form.iac_max ?? 0
  return (form.pac_max * 1000 / form.vac_out).toFixed(1)
})
function recalcCurrent() { /* computed 自动响应，无需额外逻辑 */ }

// ═══════════════════════════════════════════════════════════════
// Tab 2：效率曲线
// ═══════════════════════════════════════════════════════════════

const curveVoltage = ref('low')
const curveMode    = ref('pin_eta')
const curveChartEl = ref(null)
let curveChart = null

// 效率曲线原始数据
const curves = computed(() => form.efficiency_curves || {})

// ── 电压档位选项（动态生成，仅保留有实际数据的档位）──────────
// 修复：用真实字段 pdc_list 判断数据是否存在
const voltageOptions = computed(() => {
  const labelMap = { low: '低压', mid: '中压', high: '高压' }
  return ['low', 'mid', 'high']
    .filter(k => {
      const c = curves.value[k]
      return c && Array.isArray(c.pdc_list) && c.pdc_list.length > 0
    })
    .map(k => ({
      value: k,
      label: `${labelMap[k]} ${curves.value[k].voltage ?? ''} V`,
    }))
})

// 档位变化时自动选中第一个有效档位
watch(
  voltageOptions,
  (opts) => {
    if (!opts.length) return
    if (!opts.find(o => o.value === curveVoltage.value)) {
      curveVoltage.value = opts[0].value
    }
  },
  { immediate: true }
)

// 程序化切换档位时也触发图表重绘
watch(curveVoltage, () => {
  if (activeTab.value === 'curve') renderCurveChart()
})

// 当前档位的曲线对象
const activeCurve = computed(() => curves.value[curveVoltage.value] || null)

// 功率数据统一转换为 kW（原始数据为 W）
const pdcListKw = computed(() => activeCurve.value?.pdc_list?.map(v => v / 1000) || [])
const pacListKw = computed(() => activeCurve.value?.pac_list?.map(v => v / 1000) || [])

// X / Y 数据列表（修复字段名：pdc_list=输入功率，pac_list=输出功率）
const xDataList = computed(() => {
  if (!activeCurve.value) return []
  return curveMode.value === 'pout_eta' ? pacListKw.value : pdcListKw.value
})
const yDataList = computed(() => {
  if (!activeCurve.value) return []
  return curveMode.value === 'pin_pout' ? pacListKw.value : activeCurve.value.eta_list || []
})
const xAxisLabel = computed(() =>
  curveMode.value === 'pout_eta' ? '输出功率' : '输入功率'
)
const yAxisLabel = computed(() =>
  curveMode.value === 'pin_pout' ? '输出功率' : '效率'
)

function formatNum(val) {
  if (val === undefined || val === null) return ''
  const n = Number(val)
  return n % 1 === 0 ? String(n) : n.toFixed(6).replace(/\.?0+$/, '')
}

// ── 渲染效率曲线 ───────────────────────────────────────────────
function renderCurveChart() {
  nextTick(() => {
    if (!curveChartEl.value) return
    if (!curveChart) curveChart = echarts.init(curveChartEl.value)

    const data = activeCurve.value
    // 修复：用真实字段 pdc_list 判断数据有效性
    if (!data || !data.pdc_list?.length) {
      curveChart.clear()
      return
    }

    const xList = xDataList.value
    const yList = yDataList.value

    // 空值兜底，避免 Math.max 计算异常
    const validX = xList.filter(v => typeof v === 'number' && isFinite(v) && v > 0)
    const validY = yList.filter(v => typeof v === 'number' && isFinite(v) && v > 0)
    const maxX = validX.length ? Math.max(...validX) * 1.05 : 10
    const maxY = curveMode.value === 'pin_pout'
      ? (validY.length ? Math.ceil(Math.max(...validY) * 1.1) : 10)
      : 100

    const isEta      = curveMode.value !== 'pin_pout'
    const xLabel     = xAxisLabel.value + ' (kW)'
    const yLabel     = isEta ? '效率 (%)' : '输出功率 (kW)'
    const chartTitle = curveMode.value === 'pin_eta'  ? '输入功率 vs 效率'
                     : curveMode.value === 'pout_eta' ? '输出功率 vs 效率'
                     : '输入功率 vs 输出功率'

    // 低/中/高压三条曲线同时绘制，当前档位高亮
    const colorMap    = { low: '#5bc0eb', mid: '#7ec8a0', high: '#f5a623' }
    const labelMap    = { low: '低压',    mid: '中压',    high: '高压'    }
    const allSeries = ['low', 'mid', 'high']
      .filter(k => curves.value[k]?.pdc_list?.length) // 修复字段名
      .map(k => {
        const c    = curves.value[k]
        // 修复字段名 + 单位转换 W→kW
        const xArr = curveMode.value === 'pout_eta' 
          ? c.pac_list.map(v => v / 1000) 
          : c.pdc_list.map(v => v / 1000)
        const yArr = curveMode.value === 'pin_pout' 
          ? c.pac_list.map(v => v / 1000) 
          : c.eta_list
        const pts  = (xArr || []).map((x, i) => [x, yArr?.[i] ?? 0])
        const isCurrent = k === curveVoltage.value
        return {
          type:        'line',
          name:        labelMap[k],
          smooth:      true,
          showSymbol:  isCurrent,
          symbol:      'circle',
          symbolSize:  6,
          lineStyle: {
            color:   isCurrent ? '#e05c2a' : colorMap[k],
            width:   isCurrent ? 2.5 : 1.5,
            opacity: isCurrent ? 1   : 0.5,
          },
          itemStyle: { color: '#e05c2a' },
          data: pts,
          z:   isCurrent ? 10 : 1,
        }
      })

    curveChart.setOption({
      backgroundColor: '#fff',
      title: {
        text: chartTitle,
        left: 'center', top: 4,
        textStyle: { fontSize: 13, color: '#333', fontWeight: 'normal' },
      },
      grid: { left: 60, right: 24, top: 40, bottom: 52 },
      tooltip: {
        trigger: 'axis',
        formatter(params) {
          const curLabel = labelMap[curveVoltage.value]
          const p = params.find(s => s.seriesName === curLabel)
          if (!p) return ''
          const [x, y] = p.data
          const yUnit = isEta ? '%' : ' kW'
          return `${xAxisLabel.value}：${formatNum(x)} kW<br/>${yAxisLabel.value}：${formatNum(y)}${yUnit}`
        },
      },
      xAxis: {
        type: 'value', name: xLabel,
        nameLocation: 'middle', nameGap: 36,
        min: 0, max: maxX,
        splitLine: { lineStyle: { color: '#f0f0f0' } },
      },
      yAxis: {
        type: 'value', name: yLabel,
        nameLocation: 'middle', nameGap: 48,
        min: 0, max: maxY,
        splitLine: { lineStyle: { color: '#f0f0f0' } },
      },
      series: allSeries,
    }, true)

    curveChart.resize()
  })
}

// ═══════════════════════════════════════════════════════════════
// Tab 3：输出参数（温度限制曲线）
// ═══════════════════════════════════════════════════════════════

const tempChartEl = ref(null)
let tempChart = null

function renderTempChart() {
  nextTick(() => {
    if (!tempChartEl.value) return
    if (!tempChart) tempChart = echarts.init(tempChartEl.value)

    const {
      pac_max, pac_nom,
      temp_pac_max, temp_pac_nom,
      temp_derating, pac_derating,
      temp_derating_limit,
    } = form

    // 绿色段：0 → temp_pac_max 维持 pac_max 平台 → 折至 pac_nom
    const greenPoints = [
      [0,             pac_max],
      [temp_pac_max,  pac_max],
      [temp_pac_nom,  pac_nom],
    ]
    // 橙色段：温度继续升高时的降额折线
    const orangePoints = [
      [temp_pac_nom,       pac_nom],
      [temp_derating,      pac_derating],
      [temp_derating_limit, 0],
    ]

    const maxPwr = Math.ceil((pac_max ?? 10) * 1.15)

    tempChart.setOption({
      backgroundColor: '#fff',
      grid: { left: 60, right: 24, top: 24, bottom: 52 },
      tooltip: {
        trigger: 'axis',
        formatter(params) {
          const p = params[0]
          return `温度：${p.data[0]} ℃<br/>功率：${p.data[1]} kW`
        },
      },
      xAxis: {
        type: 'value', name: '温度 (℃)',
        nameLocation: 'middle', nameGap: 36,
        min: 0, max: 70,
        splitLine: { lineStyle: { color: '#f0f0f0' } },
      },
      yAxis: {
        type: 'value', name: '功率 (kW)',
        nameLocation: 'middle', nameGap: 48,
        min: 0, max: maxPwr,
        splitLine: { lineStyle: { color: '#f0f0f0' } },
      },
      series: [
        {
          type: 'line', smooth: false,
          showSymbol: true, symbol: 'circle', symbolSize: 8,
          lineStyle: { color: '#3a9a5c', width: 2.5 },
          itemStyle: { color: '#3a9a5c' },
          data: greenPoints,
          label: {
            show: true, position: 'top',
            color: '#3a9a5c', fontSize: 12,
            formatter(p) {
              if (p.dataIndex === 1) return `Pmax = ${pac_max} kW`
              if (p.dataIndex === 2) return `标称功率 = ${pac_nom} kW`
              return ''
            },
          },
        },
        {
          type: 'line', smooth: false, showSymbol: false,
          lineStyle: { color: '#f5a623', width: 2.5 },
          itemStyle: { color: '#f5a623' },
          data: orangePoints,
        },
      ],
    }, true)

    tempChart.resize()
  })
}

// ── Tab 切换时初始化对应图表 ───────────────────────────────────
watch(activeTab, (val) => {
  if (val === 'curve')  nextTick(() => renderCurveChart())
  if (val === 'output') nextTick(() => renderTempChart())
})

// ── 保存 ──────────────────────────────────────────────────────
const saving = ref(false)

async function handleSave() {
  saving.value = true
  try {
    const payload = {
      manufacturer:        form.manufacturer,
      model_name:          form.model_name,
      vmp_min:             form.vmp_min,
      vmp_nom:             form.vmp_nom,
      vmp_max:             form.vmp_max,
      vdc_max:             form.vdc_max,
      vac_out:             form.vac_out,
      pac_nom:             form.pac_nom,
      pac_max:             form.pac_max,
      efficiency:          form.efficiency,
      temp_pac_nom:        form.temp_pac_nom,
      temp_pac_max:        form.temp_pac_max,
      temp_derating:       form.temp_derating,
      pac_derating:        form.pac_derating,
      temp_derating_limit: form.temp_derating_limit,
      efficiency_curves:   form.efficiency_curves,
    }
    const res = await inverterApi.update(props.inverter.id, payload)
    ElMessage.success('保存成功')
    emit('updated', res.data)
  } catch (e) {
    ElMessage.error(e?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// ── 窗口 resize ───────────────────────────────────────────────
function onResize() {
  curveChart?.resize()
  tempChart?.resize()
}

onMounted(() => window.addEventListener('resize', onResize))
onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  curveChart?.dispose()
  tempChart?.dispose()
})
</script>

<style scoped>
/* ── 整体布局 ─────────────────────────────────────────────────── */
.inverter-detail {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0 2px;
}

/* ── 自定义 Tab 导航（橙色下划线样式）───────────────────────── */
.tab-nav {
  display: flex;
  gap: 32px;
  padding: 0 4px;
}

.tab-item {
  font-size: 14px;
  color: #666;
  cursor: pointer;
  padding-bottom: 8px;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  user-select: none;
}

.tab-item.active {
  color: #f5a623;
  border-bottom-color: #f5a623;
  font-weight: 500;
}

.tab-divider {
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 24px;
}

/* ── Tab 内容区 ──────────────────────────────────────────────── */
.tab-content {
  flex: 1;
  padding-right: 4px;
}

/* ── 区块标题 ────────────────────────────────────────────────── */
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #222;
  margin: 20px 0 16px;
}

/* ── 只读文本 ────────────────────────────────────────────────── */
.readonly-text {
  font-size: 14px;
  color: #333;
  line-height: 32px;
}

/* ── Tab2：效率曲线控制行 ────────────────────────────────────── */
.curve-control-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.control-label {
  font-size: 14px;
  color: #333;
  white-space: nowrap;
  min-width: 72px;
}

/* ── 数据点格子 ──────────────────────────────────────────────── */
.curve-data-block {
  margin: 20px 0 12px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.data-row {
  display: flex;
  border-bottom: 1px solid #e4e7ed;
}

.data-row:last-child {
  border-bottom: none;
}

.data-label {
  width: 80px;
  min-width: 80px;
  background: #f5f7fa;
  font-size: 12px;
  color: #555;
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 1px solid #e4e7ed;
  padding: 6px 4px;
}

.data-cell {
  flex: 1;
  font-size: 12px;
  color: #333;
  text-align: center;
  padding: 6px 2px;
  border-right: 1px solid #e4e7ed;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.data-cell:last-child {
  border-right: none;
}

.cell-disabled {
  background: #fafafa;
  color: #bbb;
}

/* ── ECharts 容器 ────────────────────────────────────────────── */
.echarts-box {
  width: 100%;
  height: 340px;
}

/* ── Tab3：温度参数行 ────────────────────────────────────────── */
.temp-row {
  margin-bottom: 16px;
  align-items: center;
}

.no-margin {
  margin-bottom: 0 !important;
}

.up-to-col {
  display: flex;
  align-items: center;
  gap: 8px;
}

.up-to-label {
  font-size: 13px;
  color: #666;
  white-space: nowrap;
}

/* ── 底部按钮 ────────────────────────────────────────────────── */
.drawer-footer {
  padding: 16px 0 4px;
  display: flex;
  justify-content: right;
  gap: 16px;
  border-top: 1px solid #ebeef5;
  margin-top: 16px;
}
</style>
