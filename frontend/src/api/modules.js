import api from './index'

// 认证相关
export const authAPI = {
  login(data) {
    return api.post('/auth/login', data)
  },
  getInfo() {
    return api.get('/auth/me')
  },
}

// 分类相关
export const categoryAPI = {
  list() {
    return api.get('/categories/')
  },
  listSimple() {
    return api.get('/categories/simple')
  },
  get(id) {
    return api.get(`/categories/${id}`)
  },
  create(data) {
    return api.post('/categories/', data)
  },
  update(id, data) {
    return api.put(`/categories/${id}`, data)
  },
  delete(id) {
    return api.delete(`/categories/${id}`)
  },
}

// 链接相关
export const linkAPI = {
  list(categoryId = null) {
    const params = categoryId ? { category_id: categoryId } : {}
    return api.get('/links/', { params })
  },
  get(id) {
    return api.get(`/links/${id}`)
  },
  create(data) {
    return api.post('/links/', data)
  },
  update(id, data) {
    return api.put(`/links/${id}`, data)
  },
  delete(id) {
    return api.delete(`/links/${id}`)
  },
}

// 搜索引擎相关
export const engineAPI = {
  list() {
    return api.get('/search-engines/')
  },
  listAll() {
    return api.get('/search-engines/')
  },
  get(id) {
    return api.get(`/search-engines/${id}`)
  },
  create(data) {
    return api.post('/search-engines/', data)
  },
  update(id, data) {
    return api.put(`/search-engines/${id}`, data)
  },
  delete(id) {
    return api.delete(`/search-engines/${id}`)
  },
}

// 系统设置相关
export const settingAPI = {
  list() {
    return api.get('/settings/')
  },
  get(key) {
    return api.get(`/settings/${key}`)
  },
  update(key, data) {
    return api.put(`/settings/${key}`, data)
  },
  create(data) {
    return api.post('/settings/', data)
  },
  updateAll(data) {
    return api.put('/settings/', data)
  },
}

// 首页数据
export const homeAPI = {
  getData() {
    return api.get('/home/data')
  },
}
