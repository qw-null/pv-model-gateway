<!-- src/components/PanelDetail.vue -->
<template>
  <div class="panel-detail">
    <el-tabs v-model="activeTab">
        <!-- Tab 1：基本数据 -->
        <el-tab-pane label="1.基本数据" name="basic">
            <el-form :model="form" label-width="140px" size="default">

            <div class="section-title">基本信息</div>
            <el-row :gutter="24">
                <el-col :span="12">
                <el-form-item label="厂家">
                    <el-input v-model="form.manufacturer" />
                </el-form-item>
                </el-col>
                <el-col :span="12">
                <el-form-item label="型号">
                    <el-input v-model="form.model_name" />
                </el-form-item>
                </el-col>
                <el-col :span="12">
                <el-form-item label="双面">
                    <el-switch v-model="form.is_bifacial" />
                </el-form-item>
                </el-col>
                <el-col :span="12">
                <el-form-item label="双面率">
                    <el-input v-model.number="form.bifacial_factor" :disabled="!form.is_bifacial">
                    <template #append>%</template>
                    </el-input>
                </el-form-item>
                </el-col>
            </el-row>

            <div class="section-title">制造商规格</div>
            <el-row :gutter="24">
                <el-col :span="12">
                <el-form-item label="短路电流 Isc">
                    <el-input v-model.number="form.isc"><template #append>A</template></el-input>
                </el-form-item>
                </el-col>
                <el-col :span="12">
                <el-form-item label="开路电压 Voc">
                    <el-input v-model.number="form.voc"><template #append>V</template></el-input>
                </el-form-item>
                </el-col>
                <el-col :span="12">
                <el-form-item label="最大功率点 Imp">
                    <el-input v-model.number="form.imp"><template #append>A</template></el-input>
                </el-form-item>
                </el-col>
                <el-col :span="12">
                <el-form-item label="最大功率点 Vmp">
                    <el-input v-model.number="form.vmp"><template #append>V</template></el-input>
                </el-form-item>
                </el-col>
                <el-col :span="12">
                <el-form-item label="温度系数">
                    <el-input v-model.number="form.temp_coeff"><template #append>mA/℃</template></el-input>
                </el-form-item>
                </el-col>
            </el-row>

            <div class="section-title">基于组件单二极管模型计算结果</div>
            <el-row :gutter="24">
                <el-col :span="12">
                <el-form-item label="运行条件 GRef">
                    <el-input v-model.number="form.g_ref"><template #append>W/m²</template></el-input>
                </el-form-item>
                </el-col>
                <el-col :span="12">
                <el-form-item label="运行条件 TRef">
                    <el-input v-model.number="form.t_ref"><template #append>℃</template></el-input>
                </el-form-item>
                </el-col>
            </el-row>
            <el-row :gutter="24" class="readonly-row">
                <el-col :span="12">
                <div class="calc-item">短路电流 Isc：<span>{{ form.isc_calc }} A</span></div>
                </el-col>
                <el-col :span="12">
                <div class="calc-item">开路电压 Voc：<span>{{ form.voc_calc }} V</span></div>
                </el-col>
                <el-col :span="12">
                <div class="calc-item">最大功率点 Imp：<span>{{ form.imp_calc }} A</span></div>
                </el-col>
                <el-col :span="12">
                <div class="calc-item">最大功率点 Vmp：<span>{{ form.vmp_calc }} V</span></div>
                </el-col>
                <el-col :span="12">
                <div class="calc-item">最大功率点 Pmp：<span>{{ form.pmp_calc }} W</span></div>
                </el-col>
                <el-col :span="12">
                <div class="calc-item">组件效率：<span>{{ form.efficiency }} %</span></div>
                </el-col>
            </el-row>

            <div class="section-title">尺寸</div>
            <el-row :gutter="24">
                <el-col :span="12">
                <el-form-item label="长度">
                    <el-input v-model.number="form.length"><template #append>mm</template></el-input>
                </el-form-item>
                </el-col>
                <el-col :span="12">
                <el-form-item label="宽度">
                    <el-input v-model.number="form.width"><template #append>mm</template></el-input>
                </el-form-item>
                </el-col>
                <el-col :span="12">
                <el-form-item label="厚度">
                    <el-input v-model.number="form.thickness"><template #append>mm</template></el-input>
                </el-form-item>
                </el-col>
                <el-col :span="12">
                <el-form-item label="重量">
                    <el-input v-model.number="form.weight"><template #append>kg</template></el-input>
                </el-form-item>
                </el-col>
            </el-row>
            <div class="calc-item" style="padding-left:140px">
                            组件面积：{{ form.area }}<span> m²</span>
            </div>

            </el-form>
        </el-tab-pane>
        <!-- Tab 2：IAM 数据 -->
        <el-tab-pane label="2.IAM数据" name="iam">
            <div class="iam-table">
            <div class="iam-row header">
                <div class="iam-cell label">入射角</div>
                <div
                v-for="(angle, idx) in form.iam_angles"
                :key="idx"
                class="iam-cell"
                >
                <el-input v-model.number="form.iam_angles[idx]" size="small" />
                </div>
            </div>
            <div class="iam-row">
                <div class="iam-cell label">IAM</div>
                <div
                v-for="(val, idx) in form.iam_values"
                :key="idx"
                class="iam-cell"
                >
                <el-input v-model.number="form.iam_values[idx]" size="small" />
                </div>
            </div>
            </div>

            <!-- IAM 折线图 -->
            <div ref="iamChartRef" class="iam-chart" />
        </el-tab-pane>
        <!-- Tab 3：电学曲线 -->
        <el-tab-pane label="3.电学曲线" name="curve">
        <el-form label-width="100px" size="default" class="curve-form">

            <!-- 第一行：曲线类型 + 曲线参数 -->
            <el-row :gutter="40">
            <el-col :span="12">
                <el-form-item label="曲线类型">
                <el-radio-group v-model="curveType">
                    <el-radio value="iv">IV曲线</el-radio>
                    <el-radio value="pv">PV曲线</el-radio>
                </el-radio-group>
                </el-form-item>
            </el-col>
            <el-col :span="12">
                <el-form-item label="曲线参数">
                <el-radio-group v-model="curveParam">
                    <el-radio value="irradiance">辐照度</el-radio>
                    <el-radio value="temperature">温度</el-radio>
                </el-radio-group>
                </el-form-item>
            </el-col>
            </el-row>

            <!-- 辐照度模式：基准温度 + 辐照度列表 -->
            <template v-if="curveParam === 'irradiance'">
            <el-form-item label="基准温度">
                <el-input v-model.number="baseTemp" style="width:200px">
                <template #append>℃</template>
                </el-input>
            </el-form-item>
            <el-form-item label="辐照度 W/m²">
                <div class="param-inputs">
                <el-input
                    v-for="(_, idx) in irradiances" :key="idx"
                    v-model.number="irradiances[idx]"
                    style="width:90px"
                />
                </div>
            </el-form-item>
            </template>

            <!-- 温度模式：基准辐照度 + 温度列表 -->
            <template v-else>
            <el-form-item label="基准辐照">
                <el-input v-model.number="baseIrradiance" style="width:180px">
                <template #append>W/m²</template>
                </el-input>
            </el-form-item>
            <el-form-item label="温度 ℃">
                <div class="param-inputs">
                <el-input
                    v-for="(_, idx) in temperatures" :key="idx"
                    v-model.number="temperatures[idx]"
                    style="width:90px"
                />
                </div>
            </el-form-item>
            </template>

            <el-form-item>
            <el-button type="primary" :loading="curveLoading" @click="fetchCurves">
                计算曲线
            </el-button>
            </el-form-item>
        </el-form>

        <!-- 图表 -->
        <div ref="curveChartRef" class="curve-chart" v-loading="curveLoading" />
        </el-tab-pane>
    </el-tabs>

    <!-- 底部保存按钮 -->
    <div class="drawer-footer">
      <el-button @click="$emit('updated', panel)">取消</el-button>
      <!-- <el-button type="primary" :loading="saving" @click="handleSave">保存修改</el-button> -->
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { panelApi } from '@/api/panel'

const props = defineProps({ panel: { type: Object, required: true } })
const emit  = defineEmits(['updated'])

const activeTab   = ref('basic')
const saving      = ref(false)
const iamChartRef = ref(null)
let   chartInstance = null

// 深拷贝 panel 数据到表单
const form = reactive(JSON.parse(JSON.stringify(props.panel)))

// ── 自动计算面积和效率 ─────────────────────────────────────────
watch([() => form.length, () => form.width], () => {
  if (form.length && form.width) {
    form.area = parseFloat((form.length * form.width / 1e6).toFixed(6))
  }
})
watch([() => form.pmp_calc, () => form.g_ref, () => form.area], () => {
  if (form.pmp_calc && form.g_ref && form.area) {
    form.efficiency = parseFloat((form.pmp_calc / (form.g_ref * form.area) * 100).toFixed(4))
  }
})

// ── IAM 图表 ──────────────────────────────────────────────────
function renderIamChart() {
  if (!iamChartRef.value) return
  if (!chartInstance) {
    chartInstance = echarts.init(iamChartRef.value)
  }
  chartInstance.setOption({
    title:   { text: '入射角效应', left: 'center', textStyle: { fontSize: 14 } },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      name: '入射角（度）',
      data: form.iam_angles,
    },
    yAxis: {
      type: 'value',
      name: 'IAM',
      min:  0,
      max:  1,
    },
    series: [{
      type:       'line',
      data:       form.iam_values,
      symbol:     'circle',
      symbolSize: 6,
      lineStyle:  { color: '#f5a623', width: 2 },
      itemStyle:  { color: '#f5a623' },
      smooth:     true,
    }],
  })
}

watch(activeTab, (val) => {
  if (val === 'iam')   nextTick(() => renderIamChart())
  if (val === 'curve') nextTick(() => {
    initCurveChart()
    if (!cachedCurves.length) fetchCurves()
    else renderCurveChart(cachedCurves, cachedMode)
  })
})

watch([() => form.iam_angles, () => form.iam_values], () => {
  if (activeTab.value === 'iam') renderIamChart()
}, { deep: true })

// ── 电学曲线状态 ──────────────────────────────────────────────
const curveType      = ref('iv')
const curveParam     = ref('irradiance')
const baseTemp       = ref(45)
const baseIrradiance = ref(1000)
const irradiances    = ref([1000, 800, 600, 400, 200])
const temperatures   = ref([0, 10, 25, 35, 45])
const curveLoading   = ref(false)
const curveChartRef  = ref(null)
let   curveChart     = null
let   cachedCurves   = []
let   cachedMode     = ''

const CURVE_COLORS = ['#1f4e9c', '#8b1a1a', '#2d6a2d', '#b0a0d0', '#a0a0a0']

function initCurveChart() {
  if (!curveChartRef.value) return
  if (!curveChart) curveChart = echarts.init(curveChartRef.value)
}

function renderCurveChart(curves, mode) {
  initCurveChart()
  if (!curveChart || !curves.length) return

  const isIV     = curveType.value === 'iv'
  const isByTemp = mode === 'temperature'

  const series = curves.map((curve, idx) => {
    const yData  = isIV ? curve.currents : curve.powers
    const label  = isByTemp
      ? ``
      : ``

    const pmpIdx = curve.powers.indexOf(Math.max(...curve.powers))
    const pmpX   = curve.voltages[pmpIdx]
    const pmpY   = isIV ? curve.currents[pmpIdx] : curve.powers[pmpIdx]

    return {
      name:       label,
      type:       'line',
      smooth:     true,
      showSymbol: false,
      lineStyle:  { color: CURVE_COLORS[idx], width: 2 },
      itemStyle:  { color: CURVE_COLORS[idx] },
      data: curve.voltages.map((v, i) => [v, yData[i]]),
      markPoint: {
        symbol:     'circle',
        symbolSize: 10,
        data: [{
          coord:     [pmpX, pmpY],
          itemStyle: { color: CURVE_COLORS[idx] },
          label:     { show: false },
        }],
      },
    }
  })

  const allY = curves.flatMap(c => curveType.value === 'iv' ? c.currents : c.powers)
  const yMax = Math.ceil(Math.max(...allY) * 1.1 / 50) * 50
  const allX = curves.flatMap(c => c.voltages)
  const xMax = Math.ceil(Math.max(...allX) * 1.1 / 10) * 10

  curveChart.setOption({
    grid: { left: 65, right: 20, top: 20, bottom: 60 },
    tooltip: {
      trigger: 'axis',
      formatter(params) {
        const v    = params[0]?.data[0]?.toFixed(2)
        const unit = isIV ? 'A' : 'W'
        let html   = `电压: V<br/>`
        params.forEach(p => {
          html += ` : <br/>`
        })
        return html
      },
    },
    legend: {
      bottom:    0,
      data:      series.map(s => s.name),
      textStyle: { fontSize: 12 },
    },
    xAxis: {
      type:         'value',
      name:         '电压（V）',
      nameLocation: 'middle',
      nameGap:      30,
      min:          0,
      max:          xMax,
    },
    yAxis: {
      type:         'value',
      name:         isIV ? '电流（A）' : '功率（W）',
      nameLocation: 'middle',
      nameGap:      50,
      min:          0,
      max:          yMax,
    },
    series,
  }, true)
}

async function fetchCurves() {
  curveLoading.value = true
  try {
    await nextTick()
    initCurveChart()
    const res = await panelApi.getCurves(props.panel.id, {
      mode:            curveParam.value,
      irradiances:     irradiances.value,
      temperatures:    temperatures.value,
      base_temp:       baseTemp.value,
      base_irradiance: baseIrradiance.value,
    })
    cachedCurves = res.data
    cachedMode   = curveParam.value
    renderCurveChart(cachedCurves, cachedMode)
  } catch (e) {
    ElMessage.error(e?.message || '曲线计算失败')
  } finally {
    curveLoading.value = false
  }
}

// 切换 IV/PV 只重绘，不重新请求
watch(curveType, () => {
  if (cachedCurves.length) renderCurveChart(cachedCurves, cachedMode)
})

// ✅ 切换辐照度/温度模式时，清空缓存并重新请求
watch(curveParam, () => {
  cachedCurves = []
  cachedMode   = ''
  if (activeTab.value === 'curve') {
    fetchCurves()
  }
})


// ── 生命周期 ──────────────────────────────────────────────────
onMounted(() => {
  window.addEventListener('resize', () => {
    chartInstance?.resize()
    curveChart?.resize()
  })
})

onBeforeUnmount(() => {
  chartInstance?.dispose()
  curveChart?.dispose()
})

// ── 保存 ──────────────────────────────────────────────────────
async function handleSave() {
  saving.value = true
  try {
    const res = await panelApi.update(form.id, {
      manufacturer:    form.manufacturer,
      model_name:      form.model_name,
      is_bifacial:     form.is_bifacial,
      bifacial_factor: form.bifacial_factor,
      isc:             form.isc,
      voc:             form.voc,
      imp:             form.imp,
      vmp:             form.vmp,
      temp_coeff:      form.temp_coeff,
      g_ref:           form.g_ref,
      t_ref:           form.t_ref,
      isc_calc:        form.isc_calc,
      voc_calc:        form.voc_calc,
      imp_calc:        form.imp_calc,
      vmp_calc:        form.vmp_calc,
      pmp_calc:        form.pmp_calc,
      efficiency:      form.efficiency,
      length:          form.length,
      width:           form.width,
      thickness:       form.thickness,
      weight:          form.weight,
      area:            form.area,
      iam_angles:      form.iam_angles,
      iam_values:      form.iam_values,
    })
    ElMessage.success('保存成功')
    emit('updated', res.data)
  } catch (e) {
    ElMessage.error(e?.message || '保存失败')
  } finally {
    saving.value = false
  }
}
</script>


<style scoped>
.panel-detail {
  padding: 0 4px;
  display: flex;
  flex-direction: column;
  height: 100%;
}
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a3a5c;
  margin: 20px 0 12px;
  padding-left: 8px;
  border-left: 3px solid #f5a623;
}
.readonly-row {
  background: #fafafa;
  border-radius: 6px;
  padding: 12px 0;
  margin-bottom: 8px;
}
.calc-item {
  font-size: 14px;
  color: #555;
  padding: 6px 0;
}
.calc-item span {
  font-weight: 600;
  color: #1a3a5c;
}
.iam-table {
  overflow-x: auto;
  margin-bottom: 24px;
}
.iam-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  gap: 6px;
}
.iam-cell {
  min-width: 80px;
  flex: 1;
}
.iam-cell.label {
  min-width: 60px;
  flex: 0 0 60px;
  font-size: 13px;
  color: #666;
  font-weight: 500;
}
.iam-chart {
  width: 100%;
  height: 300px;
}
.drawer-footer {
  margin-top: auto;
  padding: 16px 0 0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  border-top: 1px solid #ebeef5;
}

/* 原有样式保持不变，追加以下 */
.curve-form {
  margin-bottom: 16px;
}
.irradiance-inputs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.curve-chart {
  width: 100%;
  height: 420px;
}

.param-inputs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.curve-chart {
  width: 100%;
  height: 420px;
}
.curve-form {
  margin-bottom: 8px;
}
</style>


