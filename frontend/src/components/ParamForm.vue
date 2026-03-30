<template>
  <el-form :model="localData" label-position="top" size="small" class="compact-form">
    <!-- 无参数 -->
    <el-empty v-if="!inputs || !Array.isArray(inputs) || inputs.length === 0" description="该模型无需输入参数"
      :image-size="60" />

    <!-- 有参数 -->
    <template v-else>
      <el-form-item v-for="inp in inputs" :key="inp.name" style="margin-bottom:10px;">
        <!-- label -->
        <template #label>
          <div class="compact-label">
            <span class="param-name">
              {{ inp.name }}
            </span>

            <el-tag size="small" type="info">
              {{ inp.type }}
            </el-tag>

            <el-tag v-if="inp.required" size="small" type="danger">
              必填
            </el-tag>

            <span v-if="inp.description" class="param-desc">
              {{ inp.description }}
            </span>
          </div>
        </template>

        <!-- 枚举 -->
        <el-select v-if="inp.type === 'enum'" v-model="localData[inp.name]" placeholder="请选择" style="width:100%;"
          @change="emitChange">
          <el-option v-for="opt in (inp.options || [])" :key="opt" :label="opt" :value="opt" />
        </el-select>

        <!-- 布尔 -->
        <el-switch v-else-if="inp.type === 'bool'" v-model="localData[inp.name]" @change="emitChange" />

        <!-- float -->
        <el-input-number v-else-if="inp.type === 'float'" v-model="localData[inp.name]"
          :min="inp.min !== undefined ? Number(inp.min) : undefined"
          :max="inp.max !== undefined ? Number(inp.max) : undefined" :precision="4" :step="0.1" style="width:100%;"
          controls-position="right" @change="emitChange" />

        <!-- int -->
        <el-input-number v-else-if="inp.type === 'int'" v-model="localData[inp.name]"
          :min="inp.min !== undefined ? Number(inp.min) : undefined"
          :max="inp.max !== undefined ? Number(inp.max) : undefined" :precision="0" :step="1" style="width:100%;"
          controls-position="right" @change="emitChange" />

        <!-- datetime -->
        <div v-else-if="isDatetime(inp)" style="width:100%;">
          <el-date-picker v-model="localData[inp.name]" type="datetime" placeholder="请选择日期和时间"
            format="YYYY-MM-DD HH:mm:ss" value-format="YYYY-MM-DDTHH:mm:ssZ" style="width:100%;" @change="emitChange" />

          <div v-if="localData[inp.name]" class="submit-preview">
            提交值：{{ localData[inp.name] }}
          </div>
        </div>

        <!-- timezone 下拉选择 -->
        <el-select v-else-if="inp.name === 'timezone'" v-model="localData[inp.name]" style="width:100%;"
          placeholder="选择时区" @change="emitChange">
          <el-option v-for="tz in timezoneOptions" :key="tz" :label="tz" :value="tz" />
        </el-select>

        <!-- 普通字符串 -->
        <el-input v-else v-model="localData[inp.name]" :placeholder="`请输入 ${inp.name}`" clearable @input="emitChange" />



        <!-- 范围提示 -->
        <div v-if="(inp.type === 'float' || inp.type === 'int') &&
          (inp.min !== undefined || inp.max !== undefined)" class="compact-tip">
          范围：
          <span v-if="inp.min !== undefined">{{ inp.min }}</span>
          <span v-if="inp.min !== undefined && inp.max !== undefined"> ～ </span>
          <span v-if="inp.max !== undefined">{{ inp.max }}</span>
        </div>
      </el-form-item>
    </template>
  </el-form>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  inputs: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:formData'])

const localData = reactive({})

const timezoneOptions = [
  'Asia/Shanghai',
  'Asia/Chongqing',
  'Asia/Tokyo',
  'Asia/Seoul',
  'UTC',
  'Europe/London',
  'Europe/Berlin',
  'America/New_York',
  'America/Los_Angeles',
]

/* 判断 datetime 类型 */
function isDatetime(inp) {
  return (
    inp.type === 'str' &&
    (
      inp.format === 'datetime' ||
      inp.name === 'datetime' ||
      inp.name === 'start_time' ||
      inp.name === 'end_time'
    )
  )
}

/* 默认值生成 */
function getDefault(inp) {
  if (isDatetime(inp)) {
    const now = new Date()
    const p = (n) => String(n).padStart(2, '0')
    return `${now.getFullYear()}-${p(now.getMonth() + 1)}-${p(now.getDate())}T${p(now.getHours())}:${p(now.getMinutes())}:${p(now.getSeconds())}`
  }

  if (inp.default !== undefined && inp.default !== null) {
    return inp.type === 'float'
      ? Number(inp.default)
      : inp.type === 'int'
        ? Number(inp.default)
        : inp.default
  }

  if (inp.type === 'float')
    return inp.min !== undefined ? Number(inp.min) : 0.0

  if (inp.type === 'int')
    return inp.min !== undefined ? Number(inp.min) : 0

  if (inp.type === 'bool')
    return false

  if (inp.type === 'enum')
    return inp.options?.[0] ?? ''

  return ''
}

/* 向父组件回传 */
function emitChange() {
  emit('update:formData', { ...localData })
}

/* 监听 inputs 变化 */
watch(
  () => props.inputs,
  (newInputs) => {
    if (!newInputs || newInputs.length === 0) return

    Object.keys(localData).forEach(k => delete localData[k])

    newInputs.forEach(inp => {
      localData[inp.name] = getDefault(inp)
    })

    emit('update:formData', { ...localData })
  },
  { immediate: true, deep: true }
)
</script>

<style scoped>
/* 表单整体缩小 */
.compact-form {
  font-size: 13px;
}

/* label 区域 */
.compact-label {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 2px;
}

.param-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 13px;
}

.param-desc {
  font-size: 11px;
  color: #94a3b8;
}

/* 提交值预览 */
.submit-preview {
  margin-top: 4px;
  padding: 3px 8px;
  background: #f0f9ff;
  border-radius: 4px;
  font-size: 11px;
  color: #0369a1;
  font-family: monospace;
}

/* 范围提示 */
.compact-tip {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}

/* input 高度压缩 */
.compact-form :deep(.el-input__wrapper),
.compact-form :deep(.el-input-number),
.compact-form :deep(.el-select__wrapper),
.compact-form :deep(.el-date-editor) {
  min-height: 30px !important;
  height: 30px !important;
}

/* tag 缩小 */
.compact-form :deep(.el-tag) {
  font-size: 10px;
  padding: 0 6px;
  height: 18px;
  line-height: 16px;
}
</style>
