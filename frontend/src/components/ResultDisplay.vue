<template>
  <div>
    <!-- 执行成功 -->
    <template v-if="result && result.success">
      <el-alert
        :title="`执行成功 — 耗时 ${result.execution_time_ms} ms`"
        type="success"
        show-icon
        :closable="false"
        style="margin-bottom:16px;"
      />

      <el-descriptions :column="2" border>
        <el-descriptions-item
          v-for="(val, key) in result.outputs"
          :key="key"
          :label="getOutputLabel(key)"
        >
          <!-- ✅ 使用安全的 getTagType，永远不会返回 null/undefined -->
          <el-tag :type="getTagType(val)">
            {{ formatValue(val) }}
          </el-tag>
          <span
            v-if="getOutputUnit(key)"
            style="color:#94a3b8; font-size:12px; margin-left:6px;"
          >
            {{ getOutputUnit(key) }}
          </span>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 原始 JSON -->
      <el-collapse style="margin-top:16px;">
        <el-collapse-item title="查看原始 JSON 响应">
          <pre style="background:#1e1e2e; color:#7dd3fc; padding:16px;
                      border-radius:6px; overflow:auto; font-size:13px;
                      white-space:pre-wrap; word-break:break-all;">{{ formatJSON(result) }}</pre>
        </el-collapse-item>
      </el-collapse>
    </template>

    <!-- 执行失败 -->
    <el-alert
      v-else-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="false"
    />

    <!-- 空状态 -->
    <el-empty
      v-else
      description="填写参数后点击「执行模型」"
      :image-size="80"
    />
  </div>
</template>

<script setup>
const props = defineProps({
  result:  { type: Object, default: null },
  error:   { type: String, default: '' },
  outputs: { type: Array,  default: () => [] },
})

/**
 * ✅ 安全获取 ElTag type，只返回 Element Plus 允许的合法值
 * 允许值：'success' | 'warning' | 'danger' | 'info' | 'primary'
 * 不传 type 属性时使用 'primary'（默认蓝色）
 */
function getTagType(val) {
  if (typeof val === 'boolean') {
    return val ? 'success' : 'info'
  }
  if (typeof val === 'number') {
    if (val === null || val === undefined) return 'info'
    if (val < 0) return 'danger'
    return 'primary'
  }
  return 'primary'
}

/**
 * 获取输出字段的展示标签（含单位）
 */
function getOutputLabel(key) {
  const def = props.outputs.find(o => o.name === key)
  if (!def) return key
  return def.unit ? `${def.description || key}` : (def.description || key)
}

/**
 * 获取输出字段的单位
 */
function getOutputUnit(key) {
  const def = props.outputs.find(o => o.name === key)
  return def?.unit || ''
}

/**
 * 格式化展示值
 */
function formatValue(val) {
  if (val === null || val === undefined) return 'null'
  if (typeof val === 'boolean')          return val ? 'true' : 'false'
  if (typeof val === 'number')           return val.toLocaleString('zh-CN', { maximumFractionDigits: 6 })
  if (typeof val === 'object')           return JSON.stringify(val)
  return String(val)
}

/**
 * 格式化完整 JSON 响应，处理 null 值
 */
function formatJSON(obj) {
  return JSON.stringify(obj, null, 2)
}
</script>
