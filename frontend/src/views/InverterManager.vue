<!-- src/views/InverterManager.vue -->
<template>
  <div class="inverter-manager">

    <!-- 搜索栏 + 上传 -->
    <div class="toolbar">
      <div class="search-area">
        <span class="search-label">厂家：</span>
        <el-select
          v-model="searchForm.manufacturer"
          clearable
          placeholder="请选择"
          style="width:160px"
        >
          <el-option
            v-for="m in manufacturerOptions"
            :key="m"
            :label="m"
            :value="m"
          />
        </el-select>

        <span class="search-label" style="margin-left:12px">型号：</span>
        <el-input
          v-model="searchForm.model_name"
          placeholder="请输入型号"
          clearable
          style="width:200px"
          @keyup.enter="handleSearch"
        />

        <el-button type="primary" style="margin-left:8px" @click="handleSearch">
          搜索
        </el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>

      <el-upload
        :show-file-list="false"
        accept=".ond,.OND"
        :before-upload="handleUpload"
      >
        <el-button type="primary" :loading="uploading">上传文件</el-button>
      </el-upload>
    </div>

    <!-- 列表表格 -->
    <el-table
      :data="inverters"
      v-loading="loading"
      border
      stripe
      class="inverter-table"
    >
      <el-table-column prop="manufacturer" label="厂家"          width="140" />
      <el-table-column prop="model_name"   label="型号"          min-width="180" />
      <el-table-column                     label="效率"          width="90">
        <template #default="{ row }">
            {{ row.efficiency ? `${row.efficiency} %` : 'N/A' }}
        </template>
      </el-table-column>
      <el-table-column                     label="最大直流输入电压" width="150">
        <template #default="{ row }">
          {{ row.vdc_max ? `${row.vdc_max} V` : 'N/A' }}
        </template>
      </el-table-column>
      <el-table-column                     label="MPPT电压上限"   width="130">
        <template #default="{ row }">
          {{ row.vmp_max ? `${row.vmp_max} V` : 'N/A' }}
        </template>
      </el-table-column>
      <el-table-column                     label="MPPT电压下限"   width="130">
        <template #default="{ row }">
          {{ row.vmp_min ? `${row.vmp_min} V` : 'N/A' }}
        </template>
      </el-table-column>
      <el-table-column                     label="额定输出电压"   width="120">
        <template #default="{ row }">
          {{ row.vac_out ? `${row.vac_out} V` : 'N/A' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-tooltip content="查看详情" placement="top">
            <el-button
              :icon="View"
              circle
              size="small"
              @click="openDetail(row)"
            />
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
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

    <!-- 详情抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      title="逆变器详情"
      size="760px"
      destroy-on-close
    >
      <InverterDetail
        v-if="currentInverter"
        :inverter="currentInverter"
        @updated="handleUpdated"
        @cancel="drawerVisible = false"
      />
    </el-drawer>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Download, View } from '@element-plus/icons-vue'
import { inverterApi } from '@/api/inverter'
import InverterDetail from '@/components/InverterDetail.vue'

// ── 状态 ──────────────────────────────────────────────────────
const inverters           = ref([])
const loading             = ref(false)
const uploading           = ref(false)
const drawerVisible       = ref(false)
const currentInverter     = ref(null)
const manufacturerOptions = ref([])

const searchForm = reactive({
  manufacturer: '',
  model_name:   '',
})

const pagination = reactive({
  page:     1,
  pageSize: 10,
  total:    0,
})

// ── 获取厂家列表 ───────────────────────────────────────────────
async function fetchManufacturers() {
  try {
    const res = await inverterApi.manufacturers()
    manufacturerOptions.value = res.data || []
  } catch {}
}

// ── 获取逆变器列表 ─────────────────────────────────────────────
async function fetchList() {
  loading.value = true
  try {
    const res = await inverterApi.list({
      manufacturer: searchForm.manufacturer || undefined,
      model_name:   searchForm.model_name   || undefined,
      page:         pagination.page,
      page_size:    pagination.pageSize,
    })
    inverters.value  = res.data  || []
    pagination.total = res.total || 0
  } finally {
    loading.value = false
  }
}

// ── 搜索 / 重置 ───────────────────────────────────────────────
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

// ── 上传 .OND 文件 ─────────────────────────────────────────────
async function handleUpload(file) {
  uploading.value = true
  try {
    await inverterApi.upload(file)
    ElMessage.success('上传成功')
    await fetchManufacturers()
    pagination.page = 1
    await fetchList()
  } catch (e) {
    ElMessage.error(e?.message || '上传失败')
  } finally {
    uploading.value = false
  }
  return false  // 阻止 el-upload 默认行为
}

// ── 下载原始文件 ───────────────────────────────────────────────
async function handleDownload(row) {
  try {
    const res  = await inverterApi.get(row.id)
    const text = res.data?.raw_content
    if (!text) return ElMessage.warning('该逆变器无原始文件内容')
    const blob = new Blob([text], { type: 'text/plain' })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href     = url
    a.download = row.filename || `.ond`
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    ElMessage.error('下载失败')
  }
}

// ── 打开详情 ──────────────────────────────────────────────────
async function openDetail(row) {
  try {
    const res = await inverterApi.get(row.id)
    currentInverter.value = res.data?.data ?? res.data
  } catch {
    ElMessage.error('获取详情失败')
    return
  }
  drawerVisible.value = true
}

// ── 更新回调 ──────────────────────────────────────────────────
function handleUpdated(updated) {
  const idx = inverters.value.findIndex(i => i.id === updated.id)
  if (idx !== -1) inverters.value[idx] = updated
  drawerVisible.value = false
}

// ── 初始化 ────────────────────────────────────────────────────
onMounted(async () => {
  await fetchManufacturers()
  await fetchList()
})
</script>

<style scoped>
.inverter-manager {
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
.inverter-table {
  flex: 1;
}
.pagination-bar {
  display: flex;
  justify-content: center;
  padding: 8px 0;
}
</style>
