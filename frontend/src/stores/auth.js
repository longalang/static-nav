import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api/modules'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const userInfo = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(username, password) {
    try {
      const data = await authAPI.login({ username, password })
      token.value = data.access_token
      localStorage.setItem('access_token', data.access_token)
      await fetchUserInfo()
      return true
    } catch (error) {
      throw error
    }
  }

  async function fetchUserInfo() {
    try {
      userInfo.value = await authAPI.getInfo()
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('access_token')
  }

  return {
    token,
    userInfo,
    isAuthenticated,
    login,
    logout,
    fetchUserInfo,
  }
})
