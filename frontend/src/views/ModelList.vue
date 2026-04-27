<!-- frontend/src/views/ModelList.vue -->
<template>
  <div class="model-list">

    <!-- ── 顶部工具栏 ─────────────────────────────────────────── -->
    <div class="toolbar">
      <div class="search-area">
        <!-- 分类下拉 -->
        <span class="search-label">分类：</span>
        <el-select
          v-model="searchForm.category"
          placeholder="全部分类"
          clearable
          style="width: 140px"
        >
          <el-option
            v-for="c in categoryOptions"
            :key="c.category"
            :label="`${c.category}（${c.count}）`"
            :value="c.category"
          />
        </el-select>

        <!-- 关键词输入 -->
        <span class="search-label" style="margin-left: 12px">关键词：</span>
        <el-input
          v-model="searchForm.keyword"
          placeholder="模型名称 / 标题"
          clearable
          style="width: 200px"
          @keyup.enter="handleSearch"
        />

        <el-button type="primary" style="margin-left: 8px" @click="handleSearch">
          搜索
        </el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>

      <!-- 右侧操作区 -->
      <div class="action-area">
        <el-radio-group v-model="viewMode" size="small">
          <el-radio-button value="card">
            <el-icon><Grid /></el-icon> 卡片
          </el-radio-button>
          <el-radio-button value="table">
            <el-icon><List /></el-icon> 表格
          </el-radio-button>
        </el-radio-group>
        <el-button type="primary" :icon="Plus" @click="$router.push('/editor')">
          新增模型
        </el-button>
        <el-button :icon="Refresh" @click="handleRefresh">刷新</el-button>
      </div>
    </div>

    <!-- ── 数量提示 ────────────────────────────────────────────── -->
    <p class="count-tip">
      共 <strong>{{ pagination.total }}</strong> 个模型
      <template v-if="searchForm.keyword || searchForm.category">
        （已过滤）
      </template>
    </p>

    <!-- ── 卡片视图 ────────────────────────────────────────────── -->
    <template v-if="viewMode === 'card'">
      <el-row :gutter="20" v-loading="loading">
        <el-col
          :span="8"
          v-for="model in models"
          :key="model.name"
          style="margin-bottom: 20px"
        >
          <el-card shadow="hover" style="cursor: pointer; height: 100%">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center">
                <span style="font-weight: 600; font-size: 15px" v-text="model.title" />
                <div style="display: flex; gap: 6px; align-items: center">
                  <el-tag size="small" type="info" v-text="model.category" />
                  <el-tag size="small" type="success">v{{ model.version }}</el-tag>
                </div>
              </div>
            </template>

            <p
              style="color: #64748b; font-size: 13px; min-height: 40px; margin-bottom: 10px"
              v-text="model.description || '暂无描述'"
            />

            <div style="margin-bottom: 10px">
              <el-tag
                v-for="tag in (model.tags || [])"
                :key="tag"
                size="small"
                style="margin-right: 4px; margin-bottom: 4px"
                v-text="tag"
              />
            </div>

            <div style="color: #94a3b8; font-size: 12px; margin-bottom: 12px">
              调用次数: <strong v-text="model.call_count" />
              &nbsp;|&nbsp;
              API: <code style="color: #0369a1">/api/run/{{ model.name }}</code>
            </div>

            <el-button-group>
              <el-button size="small" type="primary" @click="$router.push('/debug/' + model.name)">
                调试运行
              </el-button>
              <el-button size="small" @click="$router.push('/editor/' + model.name)">
                编辑
              </el-button>
              <el-button size="small" type="danger" @click="handleDelete(model.name)">
                删除
              </el-button>
            </el-button-group>
          </el-card>
        </el-col>
      </el-row>
    </template>

    <!-- ── 表格视图 ────────────────────────────────────────────── -->
    <template v-else>
      <el-card v-loading="loading">
        <el-table :data="models" style="width: 100%" row-key="name" stripe>
          <el-table-column prop="id" label="ID" width="65" align="center" />

          <el-table-column label="模型名称" min-width="160">
            <template #default="{ row }">
              <div style="font-weight: 600; font-size: 13px" v-text="row.title" />
              <div style="font-size: 11px; color: #94a3b8; font-family: monospace" v-text="row.name" />
            </template>
          </el-table-column>

          <el-table-column label="分类" width="100">
            <template #default="{ row }">
              <el-tag size="small" type="info" v-text="row.category" />
            </template>
          </el-table-column>

          <el-table-column label="版本" width="80" align="center">
            <template #default="{ row }">
              <el-tag size="small" type="success">v{{ row.version }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column label="标签" min-width="130">
            <template #default="{ row }">
              <el-tag
                v-for="tag in (row.tags || [])"
                :key="tag"
                size="small"
                style="margin-right: 4px"
                v-text="tag"
              />
              <span v-if="!row.tags?.length" style="color: #94a3b8; font-size: 12px">—</span>
            </template>
          </el-table-column>

          <el-table-column label="前置" width="70" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.related_models?.pre?.length" type="warning" size="small">
                {{ row.related_models.pre.length }} 个
              </el-tag>
              <span v-else style="color: #94a3b8; font-size: 12px">—</span>
            </template>
          </el-table-column>

          <el-table-column label="后置" width="70" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.related_models?.post?.length" type="success" size="small">
                {{ row.related_models.post.length }} 个
              </el-tag>
              <span v-else style="color: #94a3b8; font-size: 12px">—</span>
            </template>
          </el-table-column>

          <el-table-column prop="call_count" label="调用" width="70" align="center" />

          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button size="small" type="primary" text @click="$router.push('/debug/' + row.name)">
                调试
              </el-button>
              <el-button size="small" type="warning" text @click="$router.push('/editor/' + row.name)">
                编辑
              </el-button>
              <el-button size="small" type="danger" text @click="handleDelete(row.name)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </template>

    <!-- ── 空状态 ──────────────────────────────────────────────── -->
    <el-empty
      v-if="!loading && models.length === 0"
      description="暂无模型，点击新增"
    />

    <!-- ── 底部分页 ─────────────────────────────────────────────── -->
    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, prev, pager, next, sizes, jumper"
        background
        @current-change="fetchList"
        @size-change="handleSizeChange"
      />
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Refresh, Grid, List } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { modelApi } from '../api/index.js'

// ── 视图模式 ────────────────────────────────────────────────────
const viewMode = ref('card')

// ── 搜索表单 ────────────────────────────────────────────────────
const searchForm = reactive({
  category: '',
  keyword: '',
})

// 分类选项（从接口拉取）
const categoryOptions = ref([])

async function fetchCategories() {
  try {
    const res = await modelApi.categories()
    categoryOptions.value = res.data
  } catch {}
}

// ── 分页状态 ────────────────────────────────────────────────────
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

// ── 列表数据 ────────────────────────────────────────────────────
const models  = ref([])
const loading = ref(false)

// ── 核心：带搜索+分页参数拉取列表 ───────────────────────────────
async function fetchList() {
  loading.value = true
  try {
    const res = await modelApi.list({
      category:  searchForm.category  || undefined,
      keyword:   searchForm.keyword   || undefined,
      page:      pagination.page,
      page_size: pagination.pageSize,
    })
    // 兼容后端新旧两种结构
    const payload = res.data
    models.value        = payload?.data  ?? payload ?? []
    pagination.total    = payload?.total ?? models.value.length
  } finally {
    loading.value = false
  }
}

// ── 搜索：重置到第 1 页再拉取 ───────────────────────────────────
function handleSearch() {
  pagination.page = 1
  fetchList()
}

// ── 重置：清空搜索条件，回到第 1 页 ────────────────────────────
function handleReset() {
  searchForm.category = ''
  searchForm.keyword  = ''
  pagination.page     = 1
  fetchList()
}

// ── 刷新：保留当前搜索条件 ──────────────────────────────────────
function handleRefresh() {
  fetchList()
}

// ── 每页条数变化：回到第 1 页 ───────────────────────────────────
function handleSizeChange() {
  pagination.page = 1
  fetchList()
}

// ── 删除 ────────────────────────────────────────────────────────
async function handleDelete(name) {
  await ElMessageBox.confirm(
    `确认删除模型 "${name}"？此操作不可恢复。`,
    '警告',
    { type: 'warning' }
  )
  await modelApi.delete(name)
  ElMessage.success('删除成功')
  // 若当前页删空，退回上一页
  if (models.value.length === 1 && pagination.page > 1) {
    pagination.page--
  }
  fetchList()
}

// ── 初始化 ──────────────────────────────────────────────────────
onMounted(async () => {
  await fetchCategories()
  await fetchList()
})
</script>

<style scoped>
.model-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.search-area {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}

.action-area {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-label {
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}

.count-tip {
  color: #64748b;
  font-size: 13px;
  margin: 0;
}

.pagination-bar {
  display: flex;
  justify-content: center;
  padding: 8px 0;
}
</style>
