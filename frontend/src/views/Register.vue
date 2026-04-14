<!-- src/views/Register.vue -->
<template>
  <div class="register-wrapper">
    <div class="register-card">

      <div class="register-header">
        <h2>创建账号</h2>
        <p>光伏系统模型链管理平台</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        size="large"
        label-position="top"
        @keyup.enter="handleRegister"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="3~64 个字符"
            prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item label="昵称" prop="nickname">
          <el-input
            v-model="form.nickname"
            placeholder="选填，默认与用户名相同"
            prefix-icon="EditPen"
            clearable
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="至少 6 个字符"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="再次输入密码"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="submit-btn"
            :loading="loading"
            @click="handleRegister"
          >
            注 册
          </el-button>
        </el-form-item>
      </el-form>

      <div class="footer-link">
        已有账号？
        <el-link type="primary" @click="router.push('/login')">立即登录</el-link>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { register } from '@/api/auth'

const router  = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username:        '',
  nickname:        '',
  password:        '',
  confirmPassword: '',
})

const validateConfirmPwd = (_rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 64, message: '用户名长度为 3~64 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 个字符', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPwd, trigger: 'blur' },
  ],
}

async function handleRegister() {
  await formRef.value.validate()
  loading.value = true
  try {
    await register({
      username: form.username,
      password: form.password,
      nickname: form.nickname || form.username,
    })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (e) {
    ElMessage.error(e?.message || '注册失败，用户名可能已存在')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3c8ef7 0%, #0d6efd22 100%);
}
.register-card {
  width: 440px;
  padding: 48px 40px 36px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
}
.register-header {
  text-align: center;
  margin-bottom: 28px;
}
.register-header h2 {
  font-size: 22px;
  font-weight: 600;
  color: #1a3a5c;
  margin: 0 0 6px;
}
.register-header p {
  font-size: 13px;
  color: #999;
  margin: 0;
}
.submit-btn {
  width: 100%;
  letter-spacing: 4px;
}
.footer-link {
  text-align: center;
  margin-top: 16px;
  font-size: 13px;
  color: #999;
}
</style>
