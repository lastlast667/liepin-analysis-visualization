import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')
  const loading = ref(false)

  const isLoggedIn = computed(() => !!token.value)
  const username = computed(() => user.value?.username || '')

  async function checkAuth() {
    if (!token.value) return
    try {
      const res = await authAPI.getUser()
      user.value = res.data
    } catch {
      token.value = ''
      localStorage.removeItem('token')
    }
  }

  async function login(credentials) {
    loading.value = true
    try {
      const res = await authAPI.login(credentials)
      token.value = res.data.token
      user.value = res.data.user
      localStorage.setItem('token', res.data.token)
      return true
    } catch (err) {
      throw err.response?.data || { detail: '登录失败' }
    } finally {
      loading.value = false
    }
  }

  async function register(data) {
    loading.value = true
    try {
      const res = await authAPI.register(data)
      return res.data
    } catch (err) {
      throw err.response?.data || { detail: '注册失败' }
    } finally {
      loading.value = false
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return { user, token, loading, isLoggedIn, username, checkAuth, login, register, logout }
})
