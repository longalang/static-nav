import { ref, watch } from 'vue'
import axios from 'axios'

// 全局网站设置
const siteSettings = ref({
  title: '开发文档导航',
  keywords: '',
  description: ''
})

/**
 * 加载系统设置并更新网站标题和SEO信息
 */
export async function loadSiteSettings() {
  try {
    const res = await axios.get('/api/settings')
    if (res.data) {
      if (res.data.site_title) {
        siteSettings.value.title = res.data.site_title
      }
      if (res.data.site_keywords) {
        siteSettings.value.keywords = res.data.site_keywords
      }
      if (res.data.site_description) {
        siteSettings.value.description = res.data.site_description
      }
      // 立即更新当前页面标题和SEO信息
      updatePageTitle()
      updateMetaTags()
    }
  } catch (error) {
    console.error('加载网站设置失败:', error)
  }
}

/**
 * 更新页面标题
 * @param {string} suffix - 可选的后缀，如 " - 后台管理"
 */
export function updatePageTitle(suffix = '') {
  if (suffix) {
    document.title = `${siteSettings.value.title}${suffix}`
  } else {
    document.title = siteSettings.value.title
  }
}

/**
 * 更新SEO meta标签
 */
export function updateMetaTags() {
  // 更新keywords
  let keywordsMeta = document.querySelector('meta[name="keywords"]')
  if (!keywordsMeta) {
    keywordsMeta = document.createElement('meta')
    keywordsMeta.name = 'keywords'
    document.head.appendChild(keywordsMeta)
  }
  if (siteSettings.value.keywords) {
    keywordsMeta.content = siteSettings.value.keywords
  }
  
  // 更新description
  let descriptionMeta = document.querySelector('meta[name="description"]')
  if (!descriptionMeta) {
    descriptionMeta = document.createElement('meta')
    descriptionMeta.name = 'description'
    document.head.appendChild(descriptionMeta)
  }
  if (siteSettings.value.description) {
    descriptionMeta.content = siteSettings.value.description
  }
}

/**
 * 获取当前网站设置
 */
export function getSiteSettings() {
  return siteSettings.value
}

/**
 * 监听路由变化，自动更新页面标题
 * @param {Router} router - Vue Router实例
 */
export function setupRouteTitleWatcher(router) {
  router.afterEach((to) => {
    // 根据路由元信息或路径设置不同的后缀
    let suffix = ''
    
    if (to.meta.title) {
      suffix = ` - ${to.meta.title}`
    } else if (to.path.startsWith('/admin')) {
      suffix = ' - 后台管理'
    }
    
    updatePageTitle(suffix)
  })
}
