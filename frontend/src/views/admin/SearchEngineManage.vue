<template>
  <div class="engine-manage">
    <div class="page-header">
      <h2>搜索引擎管理</h2>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        添加引擎
      </el-button>
    </div>

    <!-- 搜索引擎列表 -->
    <el-table :data="paginatedEngines" v-loading="loading" border stripe>
      <el-table-column prop="id" label="ID" align="center" width="50" />
      <el-table-column label="图标" width="80" align="center">
        <template #default="{ row }">
          <div 
            v-if="row.icon_svg" 
            class="icon-preview"
            v-html="row.icon_svg"
          ></div>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="名称" align="center" min-width="60" />
      <el-table-column prop="search_url" label="搜索URL" min-width="200" show-overflow-tooltip />
      <el-table-column prop="is_default" label="默认" width="80" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.is_default" type="success" size="small">是</el-tag>
          <span v-else>-</span>
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
            v-if="!row.is_default"
            size="small" 
            type="warning"
            @click="setDefault(row)"
          >
            设为默认
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
        :total="engines.length"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑搜索引擎' : '添加搜索引擎'"
      width="700px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="引擎名称" prop="name">
          <el-input v-model="form.name" placeholder="例如：百度、谷歌" />
        </el-form-item>
        <el-form-item label="搜索URL" prop="search_url">
          <el-input 
            v-model="form.search_url" 
            placeholder="https://www.baidu.com/s?wd={query}"
          />
          <div style="color: #999; font-size: 12px; margin-top: 5px">
            使用 {query} 作为搜索关键词占位符
          </div>
        </el-form-item>
        <el-form-item label="SVG图标" prop="icon_svg">
          <el-input 
            v-model="form.icon_svg" 
            type="textarea" 
            :rows="4"
            placeholder="<svg>...</svg>"
          />
          <div style="color: #999; font-size: 12px; margin-top: 5px">
            可选，SVG格式的图标代码，建议从<a href="https://www.iconfont.cn/" style="color: #409EFF">iconfont</a>获取
          </div>
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="0" :max="999" />
        </el-form-item>
        <el-form-item label="设为默认" prop="is_default">
          <el-switch v-model="form.is_default" active-text="是" inactive-text="否" />
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

const engines = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)

// 计算分页后的数据
const paginatedEngines = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return engines.value.slice(start, end)
})

const form = ref({
  id: null,
  name: '',
  search_url: '',
  icon_svg: '',
  sort_order: 0,
  is_default: false,
  is_active: true
})

const rules = {
  name: [
    { required: true, message: '请输入引擎名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  search_url: [
    { required: true, message: '请输入搜索URL', trigger: 'blur' },
    { pattern: /^https?:\/\//, message: '请输入有效的URL地址', trigger: 'blur' }
  ]
}

// 加载搜索引擎列表
async function loadEngines() {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const res = await axios.get('/api/search-engines/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    engines.value = res.data || []
  } catch (error) {
    console.error('加载搜索引擎失败:', error)
    ElMessage.error('加载搜索引擎失败')
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
    search_url: '',
    suggest_api_url: '',
    icon_svg: '',
    sort_order: 0,
    is_default: false,
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
    search_url: row.search_url,
    icon_svg: row.icon_svg || '',
    sort_order: row.sort_order,
    is_default: row.is_default,
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
        await axios.put(`/api/search-engines/${form.value.id}`, form.value, config)
        ElMessage.success('更新成功')
      } else {
        await axios.post('/api/search-engines', form.value, config)
        ElMessage.success('添加成功')
      }
      
      dialogVisible.value = false
      await loadEngines()
    } catch (error) {
      console.error('提交失败:', error)
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

// 设为默认
async function setDefault(row) {
  try {
    await ElMessageBox.confirm(
      `确定要将「${row.name}」设为默认搜索引擎吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const token = localStorage.getItem('access_token')
    await axios.put(
      `/api/search-engines/${row.id}/set-default`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    )
    ElMessage.success('设置成功')
    await loadEngines()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('设置失败:', error)
      ElMessage.error(error.response?.data?.detail || '设置失败')
    }
  }
}

// 删除搜索引擎
async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除搜索引擎「${row.name}」吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const token = localStorage.getItem('access_token')
    await axios.delete(`/api/search-engines/${row.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    ElMessage.success('删除成功')
    await loadEngines()
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
  loadEngines()
})
</script>

<style scoped>
.engine-manage {
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

/* 图标预览样式 */
.icon-preview {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

/* 确保SVG图标完整显示 */
.icon-preview :deep(svg) {
  width: 100%;
  height: 100%;
  max-width: 40px;
  max-height: 40px;
  object-fit: contain;
  display: block;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
