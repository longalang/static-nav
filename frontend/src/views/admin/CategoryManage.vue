<template>
  <div class="category-manage">
    <div class="page-header">
      <h2>分类管理</h2>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        添加分类
      </el-button>
    </div>

    <!-- 分类列表 -->
    <el-table :data="paginatedCategories" v-loading="loading" border stripe>
      <el-table-column prop="id" label="ID" align="center" width="80"/>
      <el-table-column prop="name" label="分类名称" min-width="150" align="center"/>
      <el-table-column prop="sort_order" label="排序" width="100" align="center"/>
      <el-table-column prop="is_active" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
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
        :total="categories.length"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑分类' : '添加分类'"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" />
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

const categories = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)

// 计算分页后的数据
const paginatedCategories = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return categories.value.slice(start, end)
})

const form = ref({
  id: null,
  name: '',
  sort_order: 0,
  is_active: true
})

const rules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ]
}

// 加载分类列表
async function loadCategories() {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const res = await axios.get('/api/categories', {
      headers: { Authorization: `Bearer ${token}` }
    })
    categories.value = res.data || []
  } catch (error) {
    console.error('加载分类失败:', error)
    ElMessage.error('加载分类失败')
  } finally {
    loading.value = false
  }
}

// 显示添加对话框
function showAddDialog() {
  isEdit.value = false
  form.value = {
    id: null,
    name: '',
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
    name: row.name,
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
        // 更新
        await axios.put(`/api/categories/${form.value.id}`, form.value, config)
        ElMessage.success('更新成功')
      } else {
        // 创建
        await axios.post('/api/categories', form.value, config)
        ElMessage.success('添加成功')
      }
      
      dialogVisible.value = false
      await loadCategories()
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
      `/api/categories/${row.id}/status`,
      { is_active: !row.is_active },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    ElMessage.success('状态更新成功')
    await loadCategories()
  } catch (error) {
    console.error('更新状态失败:', error)
    ElMessage.error('更新状态失败')
  }
}

// 删除分类
async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除分类「${row.name}」吗？该分类下的所有链接也将被删除！`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const token = localStorage.getItem('access_token')
    await axios.delete(`/api/categories/${row.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    ElMessage.success('删除成功')
    await loadCategories()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 格式化日期
function formatDate(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 分页处理
function handleSizeChange(val) {
  pageSize.value = val
  currentPage.value = 1 // 改变每页数量时重置到第一页
}

function handleCurrentChange(val) {
  currentPage.value = val
}

onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.category-manage {
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

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
