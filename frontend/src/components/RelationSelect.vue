<template>
  <div>
    <el-select
      :model-value="modelValue"
      multiple
      filterable
      style="width:100%;"
      placeholder="选择模型"
      @update:modelValue="onChange"
    >
      <el-option
        v-for="m in options"
        :key="m.name"
        :value="m.name"
        :label="`${m.title} (${m.name})`"
        :disabled="m.name === currentModelName"
      />
    </el-select>

    <!-- 已选标签 -->
    <div v-if="modelValue.length" style="margin-top:8px;">
      <el-tag
        v-for="name in modelValue"
        :key="name"
        :type="type"
        closable
        style="margin-right:6px; margin-bottom:6px;"
        @close="remove(name)"
      >
        {{ getTitle(name) }}
      </el-tag>
    </div>

    <div v-else style="color:#94a3b8; font-size:12px; margin-top:8px;">
      未设置
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Array, required: true },
  options: { type: Array, required: true },
  currentModelName: { type: String, default: '' },
  type: { type: String, default: 'info' },
})

const emit = defineEmits(['update:modelValue'])

function onChange(val) {
  emit('update:modelValue', val)
}

function remove(name) {
  emit(
    'update:modelValue',
    props.modelValue.filter(n => n !== name)
  )
}

function getTitle(name) {
  const m = props.options.find(o => o.name === name)
  return m ? `${m.title} (${m.name})` : name
}
</script>
