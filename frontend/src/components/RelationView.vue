<template>
  <div class="relation-view">

    <div
      v-for="(list, key) in relations"
      :key="key"
      class="relation-section"
    >
      <div class="relation-header">
        <span class="relation-icon">{{ relationMeta[key]?.icon }}</span>
        <span class="relation-title">{{ relationMeta[key]?.label }}</span>
      </div>

      <div v-if="list && list.length" class="relation-list">
        <div
          v-for="name in list"
          :key="name"
          class="model-chip"
        >
          <div class="model-title">{{ getModel(name)?.title || name }}</div>
          <div class="model-sub">{{ name }}</div>
        </div>
      </div>

      <div v-else class="relation-empty">无</div>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  relations: { type: Object, required: true },
  models: { type: Array, required: true },
})

const relationMeta = {
  pre:            { label: '上游模型（前置）',   icon: '⬆' },
  post:           { label: '下游模型（后置）',   icon: '⬇' },
  depends_on:     { label: '运行依赖模型',       icon: '🔗' },
  conflicts_with: { label: '冲突模型（互斥）',   icon: '⚠️' },
}

const modelMap = computed(() => {
  const map = {}
  props.models.forEach(m => { map[m.name] = m })
  return map
})

function getModel(name) {
  return modelMap.value[name]
}
</script>

<style scoped>
.relation-view { display: flex; flex-direction: column; gap: 18px; }
.relation-section { padding: 14px 16px; background: #f8fafc; border-radius: 8px; }
.relation-header { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.relation-icon { font-size: 15px; }
.relation-title { font-size: 14px; font-weight: 600; color: #334155; }
.relation-list { display: flex; flex-wrap: wrap; gap: 10px; }
.model-chip {
  padding: 8px 12px;
  background: #ffffff;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  min-width: 160px;
  transition: all 0.15s ease;
}
.model-chip:hover { border-color: #3b82f6; background: #f0f9ff; }
.model-title { font-size: 13px; font-weight: 600; color: #1e293b; }
.model-sub { margin-top: 2px; font-size: 11px; color: #64748b; font-family: monospace; }
.relation-empty { font-size: 12px; color: #94a3b8; }
</style>
