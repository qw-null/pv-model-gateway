<template>
    <el-container style="height: 100vh;">

        <!-- 侧边栏 -->
        <el-aside width="220px" style="background:#1e1e2e; color:#fff; flex-shrink:0; position:relative;">

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
                <el-menu-item index="/model-chain">
                    <el-icon>
                        <Flag />
                    </el-icon>
                    <span>模型链</span>
                </el-menu-item>
                <el-menu-item index="/editor">
                    <el-icon>
                        <EditPen />
                    </el-icon>
                    <span>新增模型</span>
                </el-menu-item>
                <el-menu-item index="/docs">
                    <el-icon>
                        <Document />
                    </el-icon>
                    <span>API 文档</span>
                </el-menu-item>
            </el-menu>

            <!-- 底部版本信息 -->
            <div style="position:absolute; bottom:16px; left:0; right:0;
                  padding:0 20px; font-size:11px; color:#334155;">
                <div>v1.0.0 · PV Team</div>
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
                    <span style="font-size:13px; color:#64748b;">{{ userStore.nickname }}</span>
                    <el-tag type="success" size="small">服务运行中</el-tag>
                    <el-button size="small" :icon="RefreshRight" circle @click="$router.go(0)" title="刷新页面" />

                    <!-- ✅ 新增：退出登录下拉菜单 -->
                    <el-dropdown @command="handleCommand">
                        <el-button size="small" :icon="User" circle title="账户" />
                        <template #dropdown>
                            <el-dropdown-menu>
                                <el-dropdown-item disabled>
                                    <span style="font-size:12px; color:#94a3b8;">
                                        {{ userStore.username }}（{{ userStore.role === 'admin' ? '管理员' : '普通用户' }}）
                                    </span>
                                </el-dropdown-item>
                                <el-dropdown-item command="profile">
                                    <el-icon>
                                        <User />
                                    </el-icon>
                                    个人信息
                                </el-dropdown-item>
                                <el-dropdown-item divided command="logout">
                                    <el-icon>
                                        <SwitchButton />
                                    </el-icon>
                                    退出登录
                                </el-dropdown-item>
                            </el-dropdown-menu>
                        </template>
                    </el-dropdown>

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
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { Grid, EditPen, DataAnalysis, RefreshRight, User, SwitchButton, Flag } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

function handleCommand(command) {
    if (command === 'profile') {
        router.push('/profile')
    } else if (command === 'logout') {
        ElMessageBox.confirm('确定要退出登录吗？', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }).then(() => {
            userStore.logout()
            ElMessage.success('已退出登录')
            router.push('/login')
        }).catch(() => { })
    }
}
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
