<!-- src/views/Login.vue -->
<template>
  <div class="login-wrapper">
    <div class="login-card">

      <div class="login-header">
        <img src="@/assets/logo.png" alt="logo" class="logo" />
        <h2>光伏系统模型链管理平台</h2>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        size="large"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <!-- ✅ 新增：注册入口 -->
      <div class="register-link">
        还没有账号？
        <el-link type="primary" :underline="false" @click="router.push('/register')">
          立即注册
        </el-link>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '@/api/auth'       // ✅ 统一从 api/index.js 引入
import { useUserStore } from '@/stores/user'

const router  = useRouter()
const store   = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码',   trigger: 'blur' }],
}

async function handleLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    const data = await login(form.username, form.password)
    store.setUser(data)
    ElMessage.success('登录成功')
    // 支持登录后回跳原页面
    const redirect = router.currentRoute.value.query.redirect
    router.push(redirect ? decodeURIComponent(redirect) : '/')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '登录失败，请检查用户名或密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3c8ef7 0%, #0d6efd22 100%);
}
.login-card {
  width: 420px;
  padding: 48px 40px 36px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
}
.login-header {
  text-align: center;
  margin-bottom: 32px;
}
.login-header .logo {
  width: 64px;
  margin-bottom: 12px;
}
.login-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1a3a5c;
  margin: 0 0 6px;
}
.login-header p {
  font-size: 13px;
  color: #999;
  margin: 0;
}
.login-btn {
  width: 100%;
  letter-spacing: 4px;
}

/* ✅ 新增：注册入口样式 */
.register-link {
  text-align: center;
  margin-top: 16px;
  font-size: 13px;
  color: #999;
}
</style>
