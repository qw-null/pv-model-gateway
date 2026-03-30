<template>
  <div>

    <!-- 页头 -->
    <el-row justify="space-between" align="middle" style="margin-bottom:20px;">
      <el-col>
        <h2 style="font-size:22px; font-weight:700;">模型列表</h2>
        <p style="color:#64748b; margin-top:4px;">
          共 <strong v-text="store.models.length"></strong> 个已注册模型
        </p>
      </el-col>
      <el-col style="text-align:right; display:flex; justify-content:flex-end; gap:8px; align-items:center;">
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
        <el-button :icon="Refresh" @click="store.fetchModels()">刷新</el-button>
      </el-col>
    </el-row>

    <!-- ══════════════════════ 卡片视图 ══════════════════════ -->
    <template v-if="viewMode === 'card'">
      <el-row :gutter="20" v-loading="store.loading">
        <el-col
          :span="8"
          v-for="model in store.models"
          :key="model.name"
          style="margin-bottom:20px;"
        >
          <el-card shadow="hover" style="cursor:pointer; height:100%;">
            <template #header>
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:600; font-size:15px;" v-text="model.title"></span>
                <div style="display:flex; gap:6px; align-items:center;">
                  <el-tag size="small" type="info" v-text="model.category"></el-tag>
                  <el-tag size="small" type="success">
                    v<span v-text="model.version"></span>
                  </el-tag>
                </div>
              </div>
            </template>

            <p
              style="color:#64748b; font-size:13px; min-height:40px; margin-bottom:10px;"
              v-text="model.description || '暂无描述'"
            ></p>

            <div style="margin-bottom:10px;">
              <el-tag
                v-for="tag in (model.tags || [])"
                :key="tag"
                size="small"
                style="margin-right:4px; margin-bottom:4px;"
                v-text="tag"
              ></el-tag>
            </div>

            <div style="color:#94a3b8; font-size:12px; margin-bottom:12px;">
              调用次数: <strong v-text="model.call_count"></strong>
              &nbsp;|&nbsp;
              API: <code style="color:#0369a1;">/api/run/<span v-text="model.name"></span></code>
            </div>

            <el-button-group>
              <el-button
                size="small"
                type="primary"
                @click="$router.push('/debug/' + model.name)"
              >
                调试运行
              </el-button>
              <el-button
                size="small"
                @click="$router.push('/editor/' + model.name)"
              >
                编辑
              </el-button>
              <el-button
                size="small"
                type="danger"
                @click="handleDelete(model.name)"
              >
                删除
              </el-button>
            </el-button-group>

          </el-card>
        </el-col>
      </el-row>
    </template>

    <!-- ══════════════════════ 表格视图 ══════════════════════ -->
    <template v-else>
      <el-card v-loading="store.loading">
        <el-table
          :data="store.models"
          style="width:100%;"
          row-key="name"
          stripe
        >
          <el-table-column prop="id" label="ID" width="65" align="center" />

          <el-table-column label="模型名称" min-width="160">
            <template #default="{ row }">
              <div>
                <div
                  style="font-weight:600; font-size:13px;"
                  v-text="row.title"
                ></div>
                <div
                  style="font-size:11px; color:#94a3b8; font-family:monospace;"
                  v-text="row.name"
                ></div>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="分类" width="100">
            <template #default="{ row }">
              <el-tag size="small" type="info" v-text="row.category"></el-tag>
            </template>
          </el-table-column>

          <el-table-column label="版本" width="80" align="center">
            <template #default="{ row }">
              <el-tag size="small" type="success">
                v<span v-text="row.version"></span>
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="标签" min-width="130">
            <template #default="{ row }">
              <el-tag
                v-for="tag in (row.tags || [])"
                :key="tag"
                size="small"
                style="margin-right:4px;"
                v-text="tag"
              ></el-tag>
              <span
                v-if="!row.tags?.length"
                style="color:#94a3b8; font-size:12px;"
              >—</span>
            </template>
          </el-table-column>

          <el-table-column label="前置" width="70" align="center">
            <template #default="{ row }">
              <el-tag
                v-if="row.related_models?.pre?.length"
                type="warning"
                size="small"
              >
                <span v-text="row.related_models.pre.length"></span> 个
              </el-tag>
              <span v-else style="color:#94a3b8; font-size:12px;">—</span>
            </template>
          </el-table-column>

          <el-table-column label="后置" width="70" align="center">
            <template #default="{ row }">
              <el-tag
                v-if="row.related_models?.post?.length"
                type="success"
                size="small"
              >
                <span v-text="row.related_models.post.length"></span> 个
              </el-tag>
              <span v-else style="color:#94a3b8; font-size:12px;">—</span>
            </template>
          </el-table-column>

          <el-table-column prop="call_count" label="调用" width="70" align="center" />

          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button
                size="small"
                type="primary"
                text
                @click="$router.push('/debug/' + row.name)"
              >
                调试
              </el-button>
              <el-button
                size="small"
                type="warning"
                text
                @click="$router.push('/editor/' + row.name)"
              >
                编辑
              </el-button>
              <el-button
                size="small"
                type="danger"
                text
                @click="handleDelete(row.name)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>

        </el-table>
      </el-card>
    </template>

    <!-- 空态 -->
    <el-empty
      v-if="!store.loading && store.models.length === 0"
      description="暂无模型，点击新增"
    />

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Refresh, Grid, List } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useModelStore } from '../stores/modelStore.js'
import { modelApi } from '../api/index.js'

const store = useModelStore()
const viewMode = ref('card')

onMounted(() => store.fetchModels())

async function handleDelete(name) {
  await ElMessageBox.confirm(
    '确认删除模型 "' + name + '"？此操作不可恢复。',
    '警告',
    { type: 'warning' }
  )
  await modelApi.delete(name)
  ElMessage.success('删除成功')
  store.fetchModels()
}
</script>
