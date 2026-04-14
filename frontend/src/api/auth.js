// src/api/auth.js
import request from '@/utils/request'

/**
 * 登录（OAuth2 表单格式）
 */
export function login(username, password) {
  const params = new URLSearchParams()
  params.append('username', username)
  params.append('grant_type', 'password')
  params.append('password', password)
  return request.post('/api/auth/login', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

/**
 * 获取当前用户信息
 */
export function getMe() {
  return request.get('/api/auth/me')
}

/**
 * 注册
 */
export function register(data) {
  return request.post('/api/auth/register', data)
}

/**
 * 更新用户信息
 */
export function updateProfile(data) {
  return request.put('/api/auth/profile', data)
}

/**
 * 修改密码
 */
export function changePassword(data) {
  return request.put('/api/auth/password', data)
}
