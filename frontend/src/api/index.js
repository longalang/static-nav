import axios from 'axios'

// 全局请求拦截器：自动添加 Token 和尾部斜杠
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 自动为 API 路径添加尾部斜杠（FastAPI 要求）
    // 只处理 /api/ 开头的路径
    // 排除：已有斜杠、查询参数、上传接口、带ID的路径、带动作的路径（如/set-default）
    if (config.url && config.url.startsWith('/api/') && 
        !config.url.endsWith('/') && 
        !config.url.includes('?') && 
        !config.url.includes('/upload/') &&
        !/\/\d+$/.test(config.url) &&  // 不以数字结尾（如 /categories/1）
        !/\/(set-default|toggle|activate|deactivate)$/.test(config.url)) {  // 不以动作结尾
      config.url = config.url + '/'
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// 请求拦截器（用于 api 实例）
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // 只在已登录状态下（有token）且非登录接口才自动跳转
    const isLoginAPI = error.config?.url?.includes('/auth/login')
    const hasToken = localStorage.getItem('access_token')
    
    if (error.response?.status === 401 && !isLoginAPI && hasToken) {
      // token过期或无效，清除并跳转
      localStorage.removeItem('access_token')
      window.location.href = '/admin/login'
    }
    return Promise.reject(error)
  }
)

export default api
