<template>
  <el-container style="height:100vh;">
    <!-- 侧边栏 -->
    <el-aside width="220px" style="background:#1e1e2e; color:#fff; flex-shrink:0;">
      <!-- Logo -->
      <div style="padding:20px 20px 12px; border-bottom:1px solid #2d2d3f;">
        <div style="font-size:16px; font-weight:700; color:#7dd3fc; line-height:1.3;">
          PV Model Gateway
        </div>
        <div style="font-size:11px; color:#fff; margin-top:4px;">
          光伏模型网关平台
        </div>
      </div>

      <!-- 菜单 -->
      <el-menu :default-active="$route.path" router background-color="#1e1e2e" text-color="#94a3b8"
        active-text-color="#7dd3fc" style="border:none;">
        <el-menu-item index="/stats">
          <el-icon>
            <DataAnalysis />
          </el-icon>
          <span>模型统计</span>
        </el-menu-item>
        <el-menu-item index="/">
          <el-icon>
            <Grid />
          </el-icon>
          <span>模型列表</span>
        </el-menu-item>

        <el-menu-item index="/editor">
          <el-icon>
            <EditPen />
          </el-icon>
          <span>新增模型</span>
        </el-menu-item>
      </el-menu>

      <!-- 底部版本信息 -->
      <div style="position:absolute; bottom:16px; left:0; right:0;
                  padding:0 20px; font-size:11px; color:#334155;">
        <div>v1.0.0 · PV Team</div>
        <div style="margin-top:2px; color:#1e3a5f;">
          API Docs:
          <a href="/docs" target="_blank" style="color:#3b82f6; text-decoration:none;">
            /docs
          </a>
        </div>
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-container style="flex:1; overflow:hidden;">
      <!-- 顶部面包屑 -->
      <el-header style="background:#fff; border-bottom:1px solid #e2e8f0;
                        height:48px; line-height:48px; padding:0 24px;
                        display:flex; align-items:center; justify-content:space-between;">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item v-if="$route.meta.title">
            {{ $route.meta.title }}
          </el-breadcrumb-item>
        </el-breadcrumb>

        <div style="display:flex; align-items:center; gap:12px;">
          <span style="font-size:13px; color:#64748b;"> {{ $route.meta?.title || '' }} </span>
          <el-tag type="success" size="small">服务运行中</el-tag>
          <el-button size="small" :icon="RefreshRight" circle @click="$router.go(0)" title="刷新页面" />
        </div>
      </el-header>

      <!-- 页面内容 -->
      <el-main style="background:#f5f7fa; padding:24px; overflow:auto;">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { Grid, EditPen, DataAnalysis, RefreshRight } from '@element-plus/icons-vue'
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Element Plus 菜单激活样式增强 */
.el-menu-item.is-active {
  background-color: #1e3a5f !important;
  border-radius: 6px;
}
</style>
