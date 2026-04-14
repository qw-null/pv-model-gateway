<!-- src/views/UserProfile.vue -->
<template>
  <div class="profile-wrapper">

    <el-page-header content="个人信息" @back="router.back()" />

    <el-row :gutter="24" class="profile-body">

      <!-- 左侧：基本信息卡片 -->
      <el-col :span="8">
        <el-card class="info-card" shadow="never">
          <div class="avatar-area">
            <el-avatar :size="80" :icon="UserFilled" class="avatar" />
            <div class="name">{{ userStore.nickname }}</div>
            <el-tag :type="userStore.isAdmin ? 'danger' : 'primary'" size="small">
              {{ userStore.isAdmin ? '管理员' : '普通用户' }}
            </el-tag>
          </div>

          <el-divider />

          <ul class="meta-list">
            <li>
              <el-icon><User /></el-icon>
              <span class="label">用户名</span>
              <span class="value">{{ userStore.username }}</span>
            </li>
            <li>
              <el-icon><Clock /></el-icon>
              <span class="label">账号状态</span>
              <el-tag type="success" size="small">正常</el-tag>
            </li>
          </ul>
        </el-card>
      </el-col>

      <!-- 右侧：编辑昵称 + 修改密码 -->
      <el-col :span="16">

        <!-- 编辑昵称 -->
        <el-card shadow="never" class="edit-card">
          <template #header>
            <span class="card-title">基本信息</span>
          </template>

          <el-form
            ref="infoFormRef"
            :model="infoForm"
            :rules="infoRules"
            label-width="80px"
          >
            <el-form-item label="昵称" prop="nickname">
              <el-input v-model="infoForm.nickname" placeholder="请输入昵称" clearable />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="infoLoading" @click="handleUpdateInfo">
                保存修改
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 修改密码 -->
        <el-card shadow="never" class="edit-card">
          <template #header>
            <span class="card-title">修改密码</span>
          </template>

          <el-form
            ref="pwdFormRef"
            :model="pwdForm"
            :rules="pwdRules"
            label-width="80px"
          >
            <el-form-item label="原密码" prop="oldPassword">
              <el-input
                v-model="pwdForm.oldPassword"
                type="password"
                show-password
                placeholder="请输入原密码"
                clearable
              />
            </el-form-item>
            <el-form-item label="新密码" prop="newPassword">
              <el-input
                v-model="pwdForm.newPassword"
                type="password"
                show-password
                placeholder="至少 6 个字符"
                clearable
              />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="pwdForm.confirmPassword"
                type="password"
                show-password
                placeholder="再次输入新密码"
                clearable
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="pwdLoading" @click="handleChangePwd">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Clock, UserFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { updateProfile, changePassword } from '@/api/auth'

const router    = useRouter()
const userStore = useUserStore()

// ── 编辑昵称 ──────────────────────────────────────────────────
const infoFormRef = ref(null)
const infoLoading = ref(false)
const infoForm    = reactive({ nickname: userStore.nickname })
const infoRules   = {
  nickname: [{ required: true, message: '昵称不能为空', trigger: 'blur' }],
}

async function handleUpdateInfo() {
  await infoFormRef.value.validate()
  infoLoading.value = true
  try {
    await updateProfile({ nickname: infoForm.nickname })
    userStore.nickname = infoForm.nickname
    localStorage.setItem('nickname', infoForm.nickname)
    ElMessage.success('昵称修改成功')
  } catch (e) {
    ElMessage.error(e?.message || '修改失败')
  } finally {
    infoLoading.value = false
  }
}

// ── 修改密码 ──────────────────────────────────────────────────
const pwdFormRef = ref(null)
const pwdLoading = ref(false)
const pwdForm    = reactive({
  oldPassword:     '',
  newPassword:     '',
  confirmPassword: '',
})

const validateConfirmPwd = (_rule, value, callback) => {
  if (!value) {
    callback(new Error('请再次输入新密码'))
  } else if (value !== pwdForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const pwdRules = {
  oldPassword:     [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword:     [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 个字符', trigger: 'blur' },
  ],
  confirmPassword: [{ required: true, validator: validateConfirmPwd, trigger: 'blur' }],
}

async function handleChangePwd() {
  await pwdFormRef.value.validate()
  pwdLoading.value = true
  try {
    await changePassword({
      old_password: pwdForm.oldPassword,
      new_password: pwdForm.newPassword,
    })
    ElMessage.success('密码修改成功，请重新登录')
    userStore.logout()
    router.push('/login')
  } catch (e) {
    ElMessage.error(e?.message || '密码修改失败，请检查原密码是否正确')
  } finally {
    pwdLoading.value = false
  }
}
</script>

<style scoped>
.profile-wrapper {
  padding: 8px 0;
}
.profile-body {
  margin-top: 24px;
}
.info-card {
  border-radius: 8px;
}
.avatar-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 16px 0 8px;
}
.avatar {
  background: #1a3a5c;
}
.name {
  font-size: 18px;
  font-weight: 600;
  color: #1a3a5c;
}
.meta-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.meta-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #555;
}
.meta-list .label {
  color: #999;
  min-width: 56px;
}
.meta-list .value {
  color: #333;
  font-weight: 500;
}
.edit-card {
  border-radius: 8px;
  margin-bottom: 20px;
}
.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a3a5c;
}
</style>
