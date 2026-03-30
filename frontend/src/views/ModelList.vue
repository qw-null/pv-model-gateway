<template>
  <div>
    <el-row justify="space-between" align="middle" style="margin-bottom:20px;">
      <el-col>
        <h2 style="font-size:22px; font-weight:700;">模型列表</h2>
        <p style="color:#64748b; margin-top:4px;">共 {{ store.models.length }} 个已注册模型</p>
      </el-col>
      <el-col style="text-align:right;">
        <el-button type="primary" :icon="Plus" @click="$router.push('/editor')">新增模型</el-button>
        <el-button :icon="Refresh" @click="store.fetchModels()">刷新</el-button>
      </el-col>
    </el-row>

    <el-row :gutter="20" v-loading="store.loading">
      <el-col :span="8" v-for="model in store.models" :key="model.name" style="margin-bottom:20px;">
        <el-card shadow="hover" style="cursor:pointer;">
          <template #header>
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span style="font-weight:600;">{{ model.title }}</span>
              <el-tag size="small" type="success">v{{ model.version }}</el-tag>
            </div>
          </template>

          <p style="color:#64748b; font-size:13px; min-height:40px;">{{ model.description }}</p>

          <div style="margin:12px 0;">
            <el-tag
              v-for="tag in model.tags"
              :key="tag"
              size="small"
              style="margin-right:4px;"
            >{{ tag }}</el-tag>
          </div>

          <div style="color:#94a3b8; font-size:12px; margin-bottom:12px;">
            调用次数: {{ model.call_count }} &nbsp;|&nbsp;
            API: <code>/api/run/{{ model.name }}</code>
          </div>

          <el-button-group>
            <el-button size="small" type="primary" @click="$router.push(`/debug/${model.name}`)">
              调试运行
            </el-button>
            <el-button size="small" @click="$router.push(`/editor/${model.name}`)">
              编辑
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(model.name)">
              删除
            </el-button>
          </el-button-group>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="!store.loading && store.models.length === 0" description="暂无模型，点击新增" />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useModelStore } from '../stores/modelStore.js'
import { modelApi } from '../api/index.js'

const store = useModelStore()
onMounted(() => store.fetchModels())

async function handleDelete(name) {
  await ElMessageBox.confirm(`确认删除模型 "${name}"？此操作不可恢复。`, '警告', { type: 'warning' })
  await modelApi.delete(name)
  ElMessage.success('删除成功')
  store.fetchModels()
}
</script>
