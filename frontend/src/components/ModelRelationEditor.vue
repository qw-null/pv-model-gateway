<template>
  <el-drawer
    :model-value="visible"
    @update:modelValue="val => emit('update:visible', val)"
    title="模型关系编辑"
    size="900px"
    destroy-on-close
  >
    <!-- 危险提示 -->
    <el-alert
      title="修改模型关系属于危险操作，可能影响模型执行链。"
      type="warning"
      show-icon
      style="margin-bottom:16px;"
    />

    <!-- 只读状态 -->
    <div v-if="!editing">
      <RelationView
        :relations="localRelations"
        :models="allModels"
      />

      <div style="margin-top:20px; text-align:right;">
        <el-button type="danger" @click="enableEdit">
          修改关系
        </el-button>
      </div>
    </div>

    <!-- 编辑状态 -->
    <div v-else>
      <el-row :gutter="20">

        <el-col :span="12">
          <Section title="⬆ 上游模型" color="#92400e">
            <RelationSelect
              v-model="localRelations.pre"
              :options="availableModels"
              :current-model-name="modelName"
              type="warning"
            />
          </Section>
        </el-col>

        <el-col :span="12">
          <Section title="⬇ 下游模型" color="#065f46">
            <RelationSelect
              v-model="localRelations.post"
              :options="availableModels"
              :current-model-name="modelName"
              type="success"
            />
          </Section>
        </el-col>

        <el-col :span="12" style="margin-top:20px;">
          <Section title="🔗 依赖模型" color="#1d4ed8">
            <RelationSelect
              v-model="localRelations.depends_on"
              :options="availableModels"
              :current-model-name="modelName"
              type="info"
            />
          </Section>
        </el-col>

        <el-col :span="12" style="margin-top:20px;">
          <Section title="⚠️ 冲突模型" color="#b91c1c">
            <RelationSelect
              v-model="localRelations.conflicts_with"
              :options="availableModels"
              :current-model-name="modelName"
              type="danger"
            />
          </Section>
        </el-col>

      </el-row>

      <div style="margin-top:20px; text-align:right;">
        <el-button @click="cancelEdit">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          保存关系
        </el-button>
      </div>
    </div>

  </el-drawer>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { modelApi } from '../api/index.js'
import RelationSelect from './RelationSelect.vue'
import Section from './Section.vue'
import RelationView from './RelationView.vue'

const props = defineProps({
  visible: Boolean,
  modelName: String,
  currentModelId: String,
  relatedModels: Object,
})

const emit = defineEmits(['update:visible', 'saved'])

const editing = ref(false)
const saving = ref(false)
const allModels = ref([])

const localRelations = ref({
  pre: [],
  post: [],
  depends_on: [],
  conflicts_with: [],
})

/* 初始化关系数据 */
watch(
  () => props.relatedModels,
  (v) => {
    if (!v) return
    localRelations.value = {
      pre: [...(v.pre || [])],
      post: [...(v.post || [])],
      depends_on: [...(v.depends_on || [])],
      conflicts_with: [...(v.conflicts_with || [])],
    }
  },
  { immediate: true }
)

/* ✅ 只声明一次 onMounted */
onMounted(async () => {
  const res = await modelApi.list()
  allModels.value = res.data || []
})

/* ✅ 用 name 排除自身（不再使用 model_id） */
const availableModels = computed(() =>
  allModels.value.filter(m => m.name !== props.modelName)
)

function enableEdit() {
  ElMessageBox.confirm(
    '修改模型关系可能影响执行链，是否继续？',
    '危险操作确认',
    {
      confirmButtonText: '确认修改',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    editing.value = true
  })
}

function cancelEdit() {
  editing.value = false
}

async function handleSave() {
  saving.value = true
  try {
    await modelApi.updateRelations(props.modelName, {
      related_models: localRelations.value,
    })

    ElMessage.success('模型关系已更新')
    editing.value = false
    emit('saved')
  } finally {
    saving.value = false
  }
}
</script>
