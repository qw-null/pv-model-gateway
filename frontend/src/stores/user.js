// src/stores/user.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token    = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')
  const role     = ref(localStorage.getItem('role') || '')
  const nickname = ref(localStorage.getItem('nickname') || '')

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin    = computed(() => role.value === 'admin')

  function setUser(data) {
    token.value    = data.access_token
    username.value = data.username
    role.value     = data.role
    nickname.value = data.nickname || data.username
    localStorage.setItem('token',    token.value)
    localStorage.setItem('username', username.value)
    localStorage.setItem('role',     role.value)
    localStorage.setItem('nickname', nickname.value)
  }

  function logout() {
    token.value = username.value = role.value = nickname.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('role')
    localStorage.removeItem('nickname')
  }

  return { token, username, role, nickname, isLoggedIn, isAdmin, setUser, logout }
})
