<template>
  <div class="link-manage">
    <div class="page-header">
      <h2>链接管理</h2>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        添加链接
      </el-button>
    </div>

    <!-- 筛选器 -->
    <el-card shadow="never" style="margin-bottom: 20px">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="分类">
          <el-select 
            v-model="filterCategory" 
            placeholder="请选择分类" 
            clearable 
            @change="loadLinks"
            style="width: 200px"
          >
            <el-option 
              v-for="cat in categories" 
              :key="cat.id" 
              :label="cat.name" 
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select 
            v-model="filterStatus" 
            placeholder="请选择状态" 
            clearable 
            @change="loadLinks"
            style="width: 150px"
          >
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 链接列表 -->
    <el-table :data="paginatedLinks" v-loading="loading" border stripe>
      <el-table-column prop="id" label="ID" align="center" width="50" />
      <el-table-column prop="title" label="标题" min-width="60" />
      <el-table-column prop="url" label="链接" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <a 
            :href="row.url" 
            target="_blank" 
            rel="noopener noreferrer"
            class="link-url"
            @click.stop
          >
            {{ row.url }}
          </a>
        </template>
      </el-table-column>
      <el-table-column label="分类" width="120">
        <template #default="{ row }">
          {{ getCategoryName(row.category_id) }}
        </template>
      </el-table-column>
      <el-table-column prop="sort_order" label="排序" width="80" align="center" />
      <el-table-column prop="is_active" label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="showEditDialog(row)">编辑</el-button>
          <el-button 
            size="small" 
            :type="row.is_active ? 'warning' : 'success'"
            @click="toggleStatus(row)"
          >
            {{ row.is_active ? '禁用' : '启用' }}
          </el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[5, 10, 20]"
        :total="links.length"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑链接' : '添加链接'"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入链接标题" />
        </el-form-item>
        <el-form-item label="链接地址" prop="url">
          <el-input v-model="form.url" placeholder="https://example.com" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="form.description" 
            type="textarea" 
            :rows="3"
            placeholder="可选，链接描述"
          />
        </el-form-item>
        <el-form-item label="所属分类" prop="category_id">
          <el-select v-model="form.category_id" placeholder="请选择分类" style="width: 100%">
            <el-option 
              v-for="cat in categories" 
              :key="cat.id" 
              :label="cat.name" 
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="0" :max="999" />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import axios from 'axios'

const links = ref([])
const categories = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const filterCategory = ref(null)
const filterStatus = ref(null)

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)

// 计算分页后的数据
const paginatedLinks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return links.value.slice(start, end)
})

const form = ref({
  id: null,
  title: '',
  url: '',
  description: '',
  category_id: null,
  sort_order: 0,
  is_active: true
})

const rules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  url: [
    { required: true, message: '请输入链接地址', trigger: 'blur' },
    { pattern: /^https?:\/\//, message: '请输入有效的URL地址', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ]
}

// 加载数据
async function loadData() {
  await Promise.all([loadCategories(), loadLinks()])
}

async function loadCategories() {
  try {
    const token = localStorage.getItem('access_token')
    const res = await axios.get('/api/categories', {
      headers: { Authorization: `Bearer ${token}` }
    })
    categories.value = res.data || []
  } catch (error) {
    console.error('加载分类失败:', error)
  }
}

async function loadLinks() {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const params = {}
    if (filterCategory.value) params.category_id = filterCategory.value
    // 只有当filterStatus有明确值时才传递参数（true或false）
    if (filterStatus.value === true || filterStatus.value === false) {
      params.is_active = filterStatus.value
    }
    
    const res = await axios.get('/api/links', {
      params,
      headers: { Authorization: `Bearer ${token}` }
    })
    links.value = res.data || []
  } catch (error) {
    console.error('加载链接失败:', error)
    ElMessage.error('加载链接失败')
  } finally {
    loading.value = false
  }
}

// 获取分类名称
function getCategoryName(categoryId) {
  const cat = categories.value.find(c => c.id === categoryId)
  return cat ? cat.name : '-'
}

// 重置筛选条件
function resetFilters() {
  filterCategory.value = null
  filterStatus.value = null
  loadLinks()
}

// 显示添加对话框
function showAddDialog() {
  isEdit.value = false
  form.value = {
    id: null,
    title: '',
    url: '',
    description: '',
    category_id: categories.value.length > 0 ? categories.value[0].id : null,
    sort_order: 0,
    is_active: true
  }
  dialogVisible.value = true
}

// 显示编辑对话框
function showEditDialog(row) {
  isEdit.value = true
  form.value = {
    id: row.id,
    title: row.title,
    url: row.url,
    description: row.description || '',
    category_id: row.category_id,
    sort_order: row.sort_order,
    is_active: row.is_active
  }
  dialogVisible.value = true
}

// 提交表单
async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      const token = localStorage.getItem('access_token')
      const config = {
        headers: { Authorization: `Bearer ${token}` }
      }
      
      if (isEdit.value) {
        await axios.put(`/api/links/${form.value.id}`, form.value, config)
        ElMessage.success('更新成功')
      } else {
        await axios.post('/api/links', form.value, config)
        ElMessage.success('添加成功')
      }
      
      dialogVisible.value = false
      await loadLinks()
    } catch (error) {
      console.error('提交失败:', error)
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

// 切换状态
async function toggleStatus(row) {
  try {
    const token = localStorage.getItem('access_token')
    await axios.put(
      `/api/links/${row.id}/status`,
      { is_active: !row.is_active },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    ElMessage.success('状态更新成功')
    // 重新加载时清除筛选条件，确保能看到所有链接
    filterCategory.value = null
    filterStatus.value = null
    await loadLinks()
  } catch (error) {
    ElMessage.error('更新状态失败')
  }
}

// 删除链接
async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除链接「${row.title}」吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const token = localStorage.getItem('access_token')
    await axios.delete(`/api/links/${row.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    ElMessage.success('删除成功')
    await loadLinks()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 分页处理
function handleSizeChange(val) {
  pageSize.value = val
  currentPage.value = 1
}

function handleCurrentChange(val) {
  currentPage.value = val
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.link-manage {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

/* 筛选表单样式 */
.filter-form {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-form :deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: 10px;
}

.filter-form :deep(.el-select) {
  min-width: 150px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 链接URL样式 */
.link-url {
  color: #409eff;
  text-decoration: none;
  transition: all 0.3s ease;
}

.link-url:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.link-url:active {
  color: #3a8ee6;
}
</style>
