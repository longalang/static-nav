<template>
  <div class="main-container">
    <div class="inner-center main">
      <div class="content-inside">
        <!-- Logo -->
        <div class="logo-box">
          <img src="/logo.png" alt="logo" height="130px">
        </div>
        
        <!-- 搜索框 -->
        <div id="search_form" class="search-section">
          <div class="search-left">
            <div 
              id="search_logo" 
              class="search-logo"
              v-html="currentEngine?.icon_svg || defaultSvgIcon"
              @click="showEngineList = !showEngineList"
            ></div>
            <div class="input-wrap">
              <input 
                ref="searchInput"
                id="search_keyword"
                class="search-input"
                v-model="keyword"
                @keyup="handleKeyup"
                @focus="handleFocus"
                @blur="handleBlur"
                placeholder="点击左侧按钮可切换到其他搜索引擎"
                autocomplete="off"
              >
              <div 
                class="clear-keyword" 
                id="clear_keyword" 
                v-show="keyword"
                @click="clearKeyword"
                title="清空搜索"
              >×</div>
            </div>
            
            <!-- 搜索引擎列表 -->
            <ul 
              id="search_methods" 
              class="search-methods"
              v-show="showEngineList"
              @mouseleave="showEngineList = false"
            >
              <li 
                v-for="engine in engines" 
                :key="engine.id"
                class="search-item"
                :data-engine="engine.name"
                @click="selectEngine(engine)"
              >
                <span class="engine-icon" v-html="engine.icon_svg"></span>
                <span class="engine-name">{{ engine.name }}</span>
              </li>
            </ul>
          </div>
          <input 
            class="search-submit" 
            value="给爷搜" 
            id="search_submit" 
            type="submit"
            @click="doSearch"
          >
        </div>
        
        <!-- 导航内容 -->
        <div class="nav-content">
          <div 
            v-for="category in categories" 
            :key="category.id"
            class="jj-list"
          >
            <div class="jj-list-tit">{{ category.name }}</div>
            <div 
              v-for="(linkGroup, groupIndex) in getCategoryLinkGroups(category.links)" 
              :key="groupIndex"
              class="link-group"
            >
              <ul class="jj-list-con">
                <li v-for="link in linkGroup" :key="link.id">
                  <a 
                    :href="link.url" 
                    class="jj-list-link" 
                    target="_blank"
                  >{{ link.title }}</a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 页脚 -->
    <footer class="inner-center footer">
      <div class="footer-content">
        <div class="beian" v-if="settings.icp_beian || settings.police_beian">
          <div class="beian_icp" v-if="settings.icp_beian">
            <img src="/beian_icp_favicon.png" width="20px">
            <a href="http://beian.miit.gov.cn/" target="_blank">
              &nbsp;{{ settings.icp_beian }}&nbsp;&nbsp;&nbsp;
            </a>
          </div>
          <div class="beian_police" v-if="settings.police_beian">
            <img src="/beian_police.png" width="20px">
            <a :href="`http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=${settings.police_beian.replace(/[^\d]/g, '')}`" target="_blank">
              &nbsp;{{ settings.police_beian }}&nbsp;&nbsp;&nbsp;
            </a>
          </div>
        </div>
        <div class="github-info">
          <span style="color:#999fa6;">Powered By &nbsp;</span>
          <a href="https://gitee.com/longalone/static-nav" target="_blank">
            <img src="https://badgen.net/badge/gitee/static-nav?color=red&icon=gitee"/>
          </a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { homeAPI } from '@/api/modules'

const searchInput = ref(null)
const keyword = ref('')
const currentEngine = ref(null)
const engines = ref([])
const categories = ref([])
const settings = ref({})
const showEngineList = ref(false)

// 默认SVG图标（搜索图标）
const defaultSvgIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.35-4.35"></path></svg>'

// 自动聚焦搜索框
onMounted(async () => {
  await loadData()
  nextTick(() => {
    searchInput.value?.focus()
  })
})

// 加载数据
async function loadData() {
  try {
    const data = await homeAPI.getData()
    // 过滤掉没有链接的分类
    categories.value = data.categories.filter(cat => cat.links && cat.links.length > 0)
    engines.value = data.engines
    settings.value = data.settings
    
    // 设置默认搜索引擎
    const savedEngine = localStorage.getItem('SearchEngine')
    if (savedEngine) {
      currentEngine.value = engines.value.find(e => e.name === savedEngine) || engines.value[0]
    } else {
      // 查找默认引擎或第一个
      currentEngine.value = engines.value.find(e => e.is_default) || engines.value[0]
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

// 将链接分组，每组最多12个
function getCategoryLinkGroups(links) {
  if (!links || links.length === 0) return []
  
  const groups = []
  const groupSize = 12
  
  for (let i = 0; i < links.length; i += groupSize) {
    groups.push(links.slice(i, i + groupSize))
  }
  
  return groups
}

// 选择搜索引擎
function selectEngine(engine) {
  currentEngine.value = engine
  localStorage.setItem('SearchEngine', engine.name)
  showEngineList.value = false
  searchInput.value?.focus()
}

// 键盘事件
function handleKeyup(event) {
  if (event.key === 'Enter') {
    doSearch()
    return
  }
  
  // ESC键关闭列表
  if (event.key === 'Escape') {
    showEngineList.value = false
  }
}

// 执行搜索
function doSearch() {
  if (!keyword.value.trim() || !currentEngine.value) return
  
  const searchUrl = currentEngine.value.search_url + encodeURIComponent(keyword.value)
  window.open(searchUrl, '_blank')
}

// 清空关键词
function clearKeyword() {
  keyword.value = ''
  searchInput.value?.focus()
}

// 焦点事件
function handleFocus() {
  if (keyword.value) {
    getSuggestions(keyword.value)
  }
}

function handleBlur() {
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}
</script>

<style scoped>
.main-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 主要内容区域自动扩展 */
.inner-center.main {
  flex: 1;
}

/* 页脚样式 */
.footer {
  margin-top: auto;
}

/* 页脚内容容器 - 水平布局 */
.footer-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

/* 备案信息样式 */
.beian {
  display: flex;
  align-items: center;
  gap: 15px;
}

.beian_icp,
.beian_police {
  display: flex;
  align-items: center;
  color: #999fa6;
}

.beian_icp a,
.beian_police a {
  color: #999fa6;
  text-decoration: none;
}

.beian_icp a:hover,
.beian_police a:hover {
  opacity: 0.8;
}

/* GitHub信息样式 */
.github-info {
  display: flex;
  align-items: center;
}
</style>
