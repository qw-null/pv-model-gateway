<!-- src/views/PanelManager.vue -->
<template>
  <div class="panel-manager">

    <!-- 顶部：搜索栏 + 上传按钮 -->
    <div class="toolbar">
      <div class="search-area">
        <!-- 厂家下拉 -->
        <span class="search-label">厂家：</span>
        <el-select
          v-model="searchForm.manufacturer"
          placeholder="请选择"
          clearable
          style="width: 160px"
        >
          <el-option
            v-for="m in manufacturerOptions"
            :key="m"
            :label="m"
            :value="m"
          />
        </el-select>

        <!-- 型号输入 -->
        <span class="search-label" style="margin-left:12px">型号：</span>
        <el-input
          v-model="searchForm.model_name"
          placeholder="请输入型号"
          clearable
          style="width: 200px"
          @keyup.enter="handleSearch"
        />

        <el-button type="primary" style="margin-left:8px" @click="handleSearch">
          搜索
        </el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>

      <!-- 上传按钮 -->
      <el-upload
        :show-file-list="false"
        accept=".pan"
        :before-upload="handleUpload"
      >
        <el-button type="primary" :loading="uploading">
          上传文件
        </el-button>
      </el-upload>
    </div>

    <!-- 组件列表表格 -->
    <el-table
      :data="panels"
      v-loading="loading"
      border
      stripe
      class="panel-table"
    >
      <el-table-column prop="manufacturer" label="厂家"  />
      <el-table-column prop="model_name"   label="型号" />
      <el-table-column  label="尺寸" width="250">
        <template #default="{ row }">
          {{ row.length/1000 }}m × {{ row.width/1000 }}m x {{ row.thickness/1000 }}m
        </template>
      </el-table-column>
      <el-table-column prop="pmp_calc"     label="功率（W）">
      </el-table-column>
      <el-table-column prop="vmp_calc"     label="最大功率点电压（V）">
      </el-table-column>
      <el-table-column prop="imp_calc"     label="最大功率点电流（A）">
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-tooltip content="编辑详情" placement="top">
            <el-button
              :icon="Edit"
              circle
              size="small"
              @click="openDetail(row)"
            />
          </el-tooltip>
          <!-- <el-tooltip content="下载 .pan 文件" placement="top">
            <el-button
              :icon="Download"
              circle
              size="small"
              style="margin-left:6px"
              @click="handleDownload(row)"
            />
          </el-tooltip> -->
        </template>
      </el-table-column>
    </el-table>

    <!-- 底部分页 -->
    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[20, 50, 100, 200]"
        :total="pagination.total"
        layout="total, prev, pager, next, sizes, jumper"
        background
        @current-change="fetchList"
        @size-change="handleSizeChange"
      />
    </div>

    <!-- 详情/编辑抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      title="组件详情"
      size="720px"
      destroy-on-close
    >
      <PanelDetail
        v-if="currentPanel"
        :panel="currentPanel"
        @updated="handleUpdated"
      />
    </el-drawer>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Download } from '@element-plus/icons-vue'
import { panelApi } from '@/api/panel'
import PanelDetail from '@/components/PanelDetail.vue'

// ── 搜索表单 ──────────────────────────────────────────────────
const searchForm = reactive({
  manufacturer: '',
  model_name:   '',
})
const manufacturerOptions = ref([])

// ── 分页状态 ──────────────────────────────────────────────────
const pagination = reactive({
  page:     1,
  pageSize: 100,
  total:    0,
})

// ── 列表数据 ──────────────────────────────────────────────────
const panels        = ref([])
const loading       = ref(false)
const uploading     = ref(false)
const drawerVisible = ref(false)
const currentPanel  = ref(null)

// ── 获取厂家列表 ───────────────────────────────────────────────
async function fetchManufacturers() {
  try {
    const res = await panelApi.manufacturers()
    manufacturerOptions.value = res.data || []
  } catch {}
}

// ── 获取组件列表 ───────────────────────────────────────────────
async function fetchList() {
  loading.value = true
  try {
    const res = await panelApi.list({
      manufacturer: searchForm.manufacturer || undefined,
      model_name:   searchForm.model_name   || undefined,
      page:         pagination.page,
      page_size:    pagination.pageSize,
    })
    panels.value       = res.data  || []
    pagination.total   = res.total || 0
  } finally {
    loading.value = false
  }
}

// ── 搜索 & 重置 ───────────────────────────────────────────────
function handleSearch() {
  pagination.page = 1
  fetchList()
}

function handleReset() {
  searchForm.manufacturer = ''
  searchForm.model_name   = ''
  pagination.page         = 1
  fetchList()
}

function handleSizeChange() {
  pagination.page = 1
  fetchList()
}

// ── 上传 ──────────────────────────────────────────────────────
async function handleUpload(file) {
  uploading.value = true
  try {
    await panelApi.upload(file)
    ElMessage.success('上传成功')
    await fetchManufacturers()
    pagination.page = 1
    await fetchList()
  } catch (e) {
    ElMessage.error(e?.message || '上传失败')
  } finally {
    uploading.value = false
  }
  return false
}

// ── 下载 .pan 文件 ─────────────────────────────────────────────
async function handleDownload(row) {
  try {
    // 通过详情接口获取 raw_content 并触发浏览器下载
    const res  = await panelApi.get(row.id)
    const text = res.data?.raw_content
    if (!text) return ElMessage.warning('该组件无原始文件内容')
    const blob = new Blob([text], { type: 'text/plain' })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href     = url
    a.download = row.filename || `${row.model_name}.pan`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    ElMessage.error('下载失败')
  }
}

// ── 详情 ──────────────────────────────────────────────────────
function openDetail(row) {
  currentPanel.value  = { ...row }
  drawerVisible.value = true
}

function handleUpdated(updated) {
  const idx = panels.value.findIndex(p => p.id === updated.id)
  if (idx !== -1) panels.value[idx] = updated
  drawerVisible.value = false
}

onMounted(async () => {
  await fetchManufacturers()
  await fetchList()
})
</script>

<style scoped>
.panel-manager {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.search-area {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}
.search-label {
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}
.panel-table {
  flex: 1;
}
.pagination-bar {
  display: flex;
  justify-content: center;
  padding: 8px 0;
}
</style>
