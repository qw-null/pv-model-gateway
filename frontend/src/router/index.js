import { createRouter, createWebHistory } from 'vue-router'
import ModelList   from '../views/ModelList.vue'
import ModelEditor from '../views/ModelEditor.vue'
import ModelDebug  from '../views/ModelDebug.vue'
import ModelStats  from '../views/ModelStats.vue'

const routes = [
  {
    path:      '/',
    name:      'ModelList',
    component: ModelList,
    meta:      { title: '模型列表' }
  },
  {
    path:      '/editor',
    name:      'ModelCreate',
    component: ModelEditor,
    meta:      { title: '新增模型' }
  },
  {
    path:      '/editor/:name',
    name:      'ModelEdit',
    component: ModelEditor,
    meta:      { title: '编辑模型' }
  },
  {
    path:      '/debug/:name',
    name:      'ModelDebug',
    component: ModelDebug,
    meta:      { title: '调试模型' }
  },
  {
    path:      '/stats',
    name:      'ModelStats',
    component: ModelStats,
    meta:      { title: '模型统计' }
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
