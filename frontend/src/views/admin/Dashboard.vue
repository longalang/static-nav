<template>
  <div class="dashboard-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>控制台概览</h2>
    </div>

    <!-- 统计卡片区域 -->
    <el-row :gutter="20" class="stats-section">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="stat-card category-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="40"><Folder /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.categories }}</div>
              <div class="stat-label">分类数量</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="stat-card link-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="40"><Link /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.links }}</div>
              <div class="stat-label">链接数量</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="stat-card engine-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="40"><Search /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.engines }}</div>
              <div class="stat-label">搜索引擎</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作区域 -->
    <el-row :gutter="20" class="quick-actions-section">
      <el-col :span="24">
        <el-card class="actions-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <div class="action-buttons">
            <el-button type="primary" size="large" @click="$router.push('/admin/categories')">
              <el-icon><Plus /></el-icon>
              <span>管理分类</span>
            </el-button>
            <el-button type="success" size="large" @click="$router.push('/admin/links')">
              <el-icon><Plus /></el-icon>
              <span>管理链接</span>
            </el-button>
            <el-button type="warning" size="large" @click="$router.push('/admin/search-engines')">
              <el-icon><Plus /></el-icon>
              <span>管理搜索引擎</span>
            </el-button>
            <el-button type="info" size="large" @click="$router.push('/admin/settings')">
              <el-icon><Setting /></el-icon>
              <span>系统设置</span>
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { categoryAPI, linkAPI, engineAPI } from '@/api/modules'
import { Folder, Link, Search, Plus, Setting } from '@element-plus/icons-vue'

const router = useRouter()

const stats = ref({
  categories: 0,
  links: 0,
  engines: 0
})

onMounted(async () => {
  try {
    const [categories, links, engines] = await Promise.all([
      categoryAPI.listSimple(),
      linkAPI.list(),
      engineAPI.listAll()
    ])
    stats.value = {
      categories: categories.length,
      links: links.length,
      engines: engines.length
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 页面标题 */
.page-header {
  margin-bottom: 30px;
}

.page-header h2 {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

/* 统计卡片区域 */
.stats-section {
  margin-bottom: 20px;
}

.stat-card {
  transition: all 0.3s ease;
  cursor: pointer;
  height: 100%;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.category-card .stat-icon {
  color: #409EFF;
}

.link-card .stat-icon {
  color: #67C23A;
}

.engine-card .stat-icon {
  color: #E6A23C;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 10px 0;
}

.stat-icon {
  flex-shrink: 0;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.1), rgba(64, 158, 255, 0.05));
  border-radius: 12px;
}

.category-card .stat-icon {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.15), rgba(64, 158, 255, 0.05));
}

.link-card .stat-icon {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.15), rgba(103, 194, 58, 0.05));
}

.engine-card .stat-icon {
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.15), rgba(230, 162, 60, 0.05));
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

/* 快捷操作区域 */
.quick-actions-section {
  margin-bottom: 20px;
}

.actions-card {
  border-radius: 8px;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.action-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  padding: 10px 0;
}

.action-buttons .el-button {
  min-width: 140px;
  height: 48px;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.action-buttons .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 详细信息区域 */
.details-section {
  margin-bottom: 20px;
}

.details-card {
  border-radius: 8px;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  color: #606266;
  width: 180px;
}

:deep(.el-descriptions__content) {
  color: #303133;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 15px;
  }

  .page-header h2 {
    font-size: 24px;
  }

  .stat-content {
    flex-direction: column;
    text-align: center;
    gap: 10px;
  }

  .stat-icon {
    width: 50px;
    height: 50px;
  }

  .stat-number {
    font-size: 28px;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons .el-button {
    width: 100%;
  }

  :deep(.el-descriptions__label) {
    width: 120px;
  }
}
</style>
