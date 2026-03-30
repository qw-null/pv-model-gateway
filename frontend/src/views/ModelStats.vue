<template>
  <div>

    <!-- 页面标题 -->
    <div style="margin-bottom:20px;">
      <h2 style="font-size:22px; font-weight:700;">模型统计</h2>
      <p style="color:#64748b; margin-top:4px;">
        查看模型分类、调用统计与详细信息
      </p>
    </div>

    <!-- 概览 -->
    <el-row :gutter="16" style="margin-bottom:20px;" v-loading="overviewLoading">

      <el-col :span="6">
        <el-card shadow="hover" :body-style="{ padding: '12px 16px' }">
          <div class="overview-item">
            <div class="icon blue"><el-icon><Grid /></el-icon></div>
            <div>
              <div class="value blue">{{ overview.total_models ?? 0 }}</div>
              <div class="label">模型总数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" :body-style="{ padding: '12px 16px' }">
          <div class="overview-item">
            <div class="icon purple"><el-icon><Menu /></el-icon></div>
            <div>
              <div class="value purple">{{ overview.total_categories ?? 0 }}</div>
              <div class="label">分类总数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" :body-style="{ padding: '12px 16px' }">
          <div class="overview-item">
            <div class="icon green"><el-icon><DataLine /></el-icon></div>
            <div>
              <div class="value green">{{ overview.total_calls ?? 0 }}</div>
              <div class="label">累计调用次数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" :body-style="{ padding: '12px 16px' }">
          <div class="overview-item">
            <div class="icon orange"><el-icon><Trophy /></el-icon></div>
            <div>
              <div class="value orange">
                {{ overview.top_models?.[0]?.title ?? '—' }}
              </div>
              <div class="label">
                Top: {{ overview.top_models?.[0]?.call_count ?? 0 }} 次
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

    </el-row>

    <!-- 主体 -->
    <el-row :gutter="20">

      <!-- 分类 -->
      <el-col :span="6">
        <el-card style="min-height:560px;">
          <template #header>
            <div class="card-header">
              <span>模型分类</span>
              <el-button size="small" :icon="Refresh" circle @click="loadAll" />
            </div>
          </template>

          <el-input
            v-model="categorySearch"
            placeholder="搜索分类..."
            :prefix-icon="Search"
            clearable
            size="small"
            style="margin-bottom:12px;"
          />

          <div v-loading="categoryLoading">
            <div
              @click="selectCategory(null)"
              :style="getCategoryItemStyle(null)"
            >
              <span>全部模型</span>
              <el-badge :value="overview.total_models || 0" type="info" />
            </div>

            <div
              v-for="cat in filteredCategories"
              :key="cat.category"
              @click="selectCategory(cat.category)"
              :style="getCategoryItemStyle(cat.category)"
            >
              <span>{{ cat.category }}</span>
              <el-badge :value="cat.count" type="primary" />
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 模型列表 -->
      <el-col :span="18">
        <el-card style="min-height:560px;">
          <template #header>
            <div class="card-header">
              <span>
                模型列表
                <el-tag v-if="selectedCategory" type="primary" style="margin-left:8px;">
                  {{ selectedCategory }}
                </el-tag>
                <el-tag v-else type="info" style="margin-left:8px;">全部</el-tag>
              </span>

              <div style="display:flex; gap:10px;">
                <el-input
                  v-model="nameSearch"
                  placeholder="按 name / 标题 搜索"
                  :prefix-icon="Search"
                  clearable
                  size="small"
                  style="width:240px;"
                  @input="onNameSearch"
                />
                <el-button size="small" :icon="Refresh" @click="loadModels">
                  刷新
                </el-button>
              </div>
            </div>
          </template>

          <div v-loading="detailLoading">
            <el-table
              :data="displayModels"
              style="width:100%;"
              row-key="id"
            >
              <el-table-column prop="id" label="ID" width="70" align="center" />
              <el-table-column prop="name" label="模型标识(name)" width="180" />
              <el-table-column prop="title" label="模型名称" min-width="130" />

              <el-table-column label="分类" width="90">
                <template #default="{ row }">
                  <el-tag
                    size="small"
                    :style="{ background: getCategoryColor(row.category), color:'#fff', border:'none' }"
                  >
                    {{ row.category }}
                  </el-tag>
                </template>
              </el-table-column>

              <!-- 前置 -->
              <el-table-column label="前置模型" width="90" align="center">
                <template #default="{ row }">
                  <template v-if="row.related_models?.pre?.length">
                    <el-tooltip
                      placement="top"
                      :content="joinNames(row.related_models.pre)"
                    >
                      <el-tag type="warning" size="small">
                        {{ row.related_models.pre.length }} 个
                      </el-tag>
                    </el-tooltip>
                  </template>
                  <span v-else class="muted">—</span>
                </template>
              </el-table-column>

              <!-- 后置 -->
              <el-table-column label="后置模型" width="90" align="center">
                <template #default="{ row }">
                  <template v-if="row.related_models?.post?.length">
                    <el-tooltip
                      placement="top"
                      :content="joinNames(row.related_models.post)"
                    >
                      <el-tag type="success" size="small">
                        {{ row.related_models.post.length }} 个
                      </el-tag>
                    </el-tooltip>
                  </template>
                  <span v-else class="muted">—</span>
                </template>
              </el-table-column>

              <el-table-column prop="call_count" label="调用" width="70" align="center" />

              <el-table-column label="操作" width="80" fixed="right">
                <template #default="{ row }">
                  <el-button
                    size="small"
                    type="warning"
                    text
                    @click.stop="openRelationEditor(row)"
                  >
                    关系
                  </el-button>
                </template>
              </el-table-column>

            </el-table>

            <el-empty
              v-if="!detailLoading && displayModels.length === 0"
              description="暂无模型数据"
              :image-size="80"
            />
          </div>
        </el-card>
      </el-col>

    </el-row>

    <!-- 执行日志 -->
    <el-row :gutter="20" style="margin-top:20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近执行记录</span>
              <el-button size="small" :icon="Refresh" @click="loadOverview">
                刷新
              </el-button>
            </div>
          </template>

          <el-table
            :data="overview.recent_logs || []"
            size="small"
            style="width:100%;"
          >
            <el-table-column label="模型名称" prop="model_name" width="200" />

            <el-table-column label="状态" width="80" align="center">
              <template #default="{ row }">
                <el-tag
                  :type="row.success ? 'success' : 'danger'"
                  size="small"
                >
                  {{ row.success ? '成功' : '失败' }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="耗时(ms)" width="110" align="right">
              <template #default="{ row }">
                <span
                  :style="{
                    color: row.execution_time_ms > 1000 ? '#ef4444' : '#10b981',
                    fontWeight: 600,
                    fontSize: '13px'
                  }"
                >
                  {{ row.execution_time_ms != null ? row.execution_time_ms.toFixed(1) : '—' }}
                </span>
              </template>
            </el-table-column>

            <el-table-column label="执行时间" min-width="200">
              <template #default="{ row }">
                <span style="font-size:12px; color:#64748b;">
                  {{ row.created_at }}
                </span>
              </template>
            </el-table-column>

          </el-table>

          <el-empty
            v-if="!(overview.recent_logs?.length)"
            :image-size="60"
            description="暂无执行记录"
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- ModelRelationEditor -->
    <ModelRelationEditor
      v-if="relationModel"
      v-model:visible="relationDialogVisible"
      :model-name="relationModel.name"
      :current-model-id="String(relationModel.id)"
      :related-models="relationModel.related_models"
      @saved="onRelationUpdated"
    />

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Refresh, Grid, Menu, DataLine, Trophy } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ModelRelationEditor from '../components/ModelRelationEditor.vue'
import { modelApi } from '../api/index.js'

const overview = ref({})
const overviewLoading = ref(false)
const categories = ref([])
const categoryLoading = ref(false)
const categorySearch = ref('')
const selectedCategory = ref(null)
const allModels = ref([])
const detailLoading = ref(false)
const nameSearch = ref('')
const relationDialogVisible = ref(false)
const relationModel = ref(null)

const CATEGORY_COLORS = {
  '太阳位置': '#f59e0b',
  '辐照分离': '#3b82f6',
  '光伏转换': '#10b981',
  '光学修正': '#8b5cf6',
  '未分类':   '#94a3b8',
}

function getCategoryColor(cat) {
  return CATEGORY_COLORS[cat] || '#64748b'
}

function getCategoryItemStyle(cat) {
  const active = selectedCategory.value === cat
  return {
    padding: '10px 14px',
    borderRadius: '6px',
    cursor: 'pointer',
    marginBottom: '6px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    background: active ? '#eff6ff' : '#f8fafc',
    borderLeft: active ? '3px solid #3b82f6' : '3px solid transparent',
    transition: 'all 0.2s',
    fontWeight: active ? '600' : '400',
  }
}

// ✅ 修复换行符编译错误
function joinNames(list) {
  return (list || []).join('\n')
}

const filteredCategories = computed(() => {
  if (!categorySearch.value) return categories.value
  return categories.value.filter(c => c.category.includes(categorySearch.value))
})

const displayModels = computed(() => {
  let list = allModels.value
  if (selectedCategory.value) {
    list = list.filter(m => m.category === selectedCategory.value)
  }
  if (nameSearch.value) {
    const kw = nameSearch.value.toLowerCase()
    list = list.filter(m =>
      m.name.toLowerCase().includes(kw) ||
      m.title.toLowerCase().includes(kw)
    )
  }
  return list
})

async function loadAll() {
  await Promise.all([loadOverview(), loadCategories(), loadModels()])
}

async function loadOverview() {
  overviewLoading.value = true
  try {
    const res = await modelApi.statsOverview()
    overview.value = res.data
  } finally {
    overviewLoading.value = false
  }
}

async function loadCategories() {
  categoryLoading.value = true
  try {
    const res = await modelApi.categories()
    categories.value = res.data
  } finally {
    categoryLoading.value = false
  }
}

async function loadModels() {
  detailLoading.value = true
  try {
    const res = await modelApi.list()
    allModels.value = res.data
  } finally {
    detailLoading.value = false
  }
}

function selectCategory(cat) {
  selectedCategory.value = cat
  nameSearch.value = ''
}

function onNameSearch() {
  selectedCategory.value = null
}

function openRelationEditor(row) {
  relationModel.value = row
  relationDialogVisible.value = true
}

async function onRelationUpdated() {
  await loadModels()
  relationDialogVisible.value = false
  ElMessage.success('模型关系已更新')
}

onMounted(loadAll)
</script>

<style scoped>
.overview-item { display: flex; align-items: center; gap: 12px; }
.icon {
  width: 40px; height: 40px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
}
.icon.blue   { background: #eff6ff; color: #3b82f6 }
.icon.purple { background: #f5f3ff; color: #8b5cf6 }
.icon.green  { background: #ecfdf5; color: #10b981 }
.icon.orange { background: #fffbeb; color: #f59e0b }
.value { font-size: 24px; font-weight: 700; }
.label { font-size: 12px; color: #64748b; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.muted { color: #94a3b8; font-size: 12px; }
</style>
