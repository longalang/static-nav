<template>
  <div class="settings-page">
    <h2>系统设置</h2>

    <el-card v-loading="loading">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="150px">
        <el-divider content-position="left">网站设置</el-divider>

        <el-form-item label="管理员用户名" prop="admin_username">
          <el-input 
            v-model="form.admin_username" 
            placeholder="请输入管理员用户名"
            clearable
          />
          <div style="color: #999; font-size: 12px; margin-top: 5px">
            修改后请使用新用户名登录
          </div>
        </el-form-item>

        <el-form-item label="管理员密码" prop="admin_password">
          <el-input 
            v-model="form.admin_password" 
            type="password"
            placeholder="请输入新密码（留空则不修改）"
            show-password
            clearable
          />
          <div style="color: #999; font-size: 12px; margin-top: 5px">
            仅在需要修改时填写，留空保持原密码不变
          </div>
        </el-form-item>

        <el-row :gutter="30">
          <el-col :span="12">
            <el-form-item label="网站图标">
              <div style="display: flex; flex-direction: column; align-items: center; gap: 12px">
                <div>
                  <img 
                    v-if="faviconPreview" 
                    :src="faviconPreview" 
                    alt="favicon预览"
                    style="width: 64px; height: 64px; border: 1px solid #dcdfe6; border-radius: 4px; object-fit: contain; background: #fff"
                  />
                  <div v-else style="width: 64px; height: 64px; background: #f5f7fa; border: 1px dashed #dcdfe6; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #909399; font-size: 12px">
                    无图标
                  </div>
                </div>
                <div style="text-align: center">
                  <el-upload
                    ref="faviconUploadRef"
                    :auto-upload="false"
                    :on-change="handleFaviconChange"
                    accept=".ico"
                    :limit="1"
                    :show-file-list="false"
                  >
                    <el-button type="primary" size="small">选择文件</el-button>
                  </el-upload>
                  <div style="color: #999; font-size: 12px; margin-top: 8px">
                    支持.ico格式<br/>建议尺寸 32x32 或 64x64
                  </div>
                </div>
              </div>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="网站Logo">
              <div style="display: flex; flex-direction: column; align-items: center; gap: 12px">
                <div>
                  <img 
                    v-if="logoPreview" 
                    :src="logoPreview" 
                    alt="logo预览"
                    style="max-width: 360px; max-height: 120px; border: 1px solid #dcdfe6; border-radius: 4px; object-fit: contain; background: #fff"
                  />
                  <div v-else style="width: 360px; height: 120px; background: #f5f7fa; border: 1px dashed #dcdfe6; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #909399; font-size: 12px">
                    无Logo
                  </div>
                </div>
                <div style="text-align: center">
                  <el-upload
                    ref="logoUploadRef"
                    :auto-upload="false"
                    :on-change="handleLogoChange"
                    accept=".png,.jpg,.jpeg,.gif,.svg"
                    :limit="1"
                    :show-file-list="false"
                  >
                    <el-button type="primary" size="small">选择文件</el-button>
                  </el-upload>
                  <div style="color: #999; font-size: 12px; margin-top: 8px">
                    支持PNG、JPG、GIF、SVG<br/>建议宽度不超过300px
                  </div>
                </div>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item v-if="backupFiles.length > 0" label="备份文件">
          <div style="max-height: 200px; overflow-y: auto">
            <el-table :data="backupFiles" size="small" border>
              <el-table-column prop="name" label="文件名" />
              <el-table-column prop="size" label="大小" width="100">
                <template #default="{ row }">
                  {{ formatFileSize(row.size) }}
                </template>
              </el-table-column>
              <el-table-column prop="modified" label="修改时间" width="160" />
              <el-table-column label="操作" width="100" align="center">
                <template #default="{ row }">
                  <el-button 
                    type="danger" 
                    size="small" 
                    link
                    @click="deleteBackup(row.name)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div style="color: #999; font-size: 12px; margin-top: 5px">
            上传新文件时会自动备份原文件
          </div>
        </el-form-item>

        <el-divider content-position="left">备案信息</el-divider>
        
        <el-form-item label="ICP备案号" prop="icp_beian">
          <el-input 
            v-model="form.icp_beian" 
            placeholder="例如：京ICP备12345678号"
            clearable
          />
          <div style="color: #999; font-size: 12px; margin-top: 5px">
            将在网站底部显示
          </div>
        </el-form-item>

        <el-form-item label="公网安备号" prop="police_beian">
          <el-input 
            v-model="form.police_beian" 
            placeholder="例如：京公网安备11000002000001号"
            clearable
          />
          <div style="color: #999; font-size: 12px; margin-top: 5px">
            可选，将在网站底部显示
          </div>
        </el-form-item>

        <el-divider content-position="left">SEO设置</el-divider>

        <el-form-item label="网站标题" prop="site_title">
          <el-input 
            v-model="form.site_title" 
            placeholder="网站导航 - 优质网址导航"
            clearable
          />
        </el-form-item>

        <el-form-item label="网站关键词" prop="site_keywords">
          <el-input 
            v-model="form.site_keywords" 
            type="textarea"
            :rows="2"
            placeholder="导航,网址,搜索引擎"
            clearable
          />
          <div style="color: #999; font-size: 12px; margin-top: 5px">
            多个关键词用逗号分隔
          </div>
        </el-form-item>

        <el-form-item label="网站描述" prop="site_description">
          <el-input 
            v-model="form.site_description" 
            type="textarea"
            :rows="3"
            placeholder="提供优质网址导航服务..."
            clearable
          />
        </el-form-item>

      </el-form>
    </el-card>

    <!-- 固定在底部的操作按钮 -->
    <div class="fixed-footer">
      <div class="footer-content">
        <el-button type="primary" @click="handleSubmit" :loading="submitting" size="large">
          <el-icon style="margin-right: 5px"><Check /></el-icon>
          保存设置
        </el-button>
        <el-button @click="loadSettings" size="large">
          <el-icon style="margin-right: 5px"><Refresh /></el-icon>
          重置
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Refresh } from '@element-plus/icons-vue'
import axios from 'axios'
import { updatePageTitle, updateMetaTags } from '@/composables/useSiteTitle'

const loading = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const faviconUploadRef = ref(null)
const logoUploadRef = ref(null)
const faviconPreview = ref('/favicon.ico')
const logoPreview = ref('/logo.gif')
const backupFiles = ref([])

const form = ref({
  icp_beian: '',
  police_beian: '',
  site_title: '',
  site_keywords: '',
  site_description: '',
  admin_username: 'admin',
  admin_password: '' // 密码默认为空，仅在修改时填写
})

// 保存原始用户名，用于判断是否修改
const originalUsername = ref('admin')

const rules = {
  site_title: [
    { max: 200, message: '最多200个字符', trigger: 'blur' }
  ],
  site_keywords: [
    { max: 500, message: '最多500个字符', trigger: 'blur' }
  ],
  site_description: [
    { max: 1000, message: '最多1000个字符', trigger: 'blur' }
  ]
}

// 加载设置
async function loadSettings() {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const res = await axios.get('/api/settings', {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    if (res.data) {
      form.value = {
        icp_beian: res.data.icp_beian || '',
        police_beian: res.data.police_beian || '',
        site_title: res.data.site_title || '',
        site_keywords: res.data.site_keywords || '',
        site_description: res.data.site_description || '',
        admin_username: res.data.admin_username || 'admin',
        admin_password: '' // 密码不回填，保持为空
      }
      
      // 保存原始用户名
      originalUsername.value = res.data.admin_username || 'admin'
    }
  } catch (error) {
    console.error('加载设置失败:', error)
    ElMessage.error('加载设置失败')
  } finally {
    loading.value = false
  }
}

// 保存设置
async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      // 准备要保存的设置数据
      const settingsToSave = { ...form.value }
      
      // 如果密码为空，不发送给后端（避免覆盖）
      if (!settingsToSave.admin_password) {
        delete settingsToSave.admin_password
      }
      
      const token = localStorage.getItem('access_token')
      await axios.put('/api/settings', settingsToSave, {
        headers: { Authorization: `Bearer ${token}` }
      })
      ElMessage.success('设置保存成功')
      
      // 判断是否修改了管理员凭据（用户名或密码）
      const usernameChanged = form.value.admin_username && form.value.admin_username !== originalUsername.value
      const passwordChanged = form.value.admin_password && form.value.admin_password.trim()
      
      if (usernameChanged || passwordChanged) {
        ElMessageBox.alert(
          '管理员凭据已更新，请使用新的用户名和密码重新登录',
          '提示',
          {
            confirmButtonText: '确定',
            type: 'warning',
            callback: () => {
              // 退出登录
              localStorage.removeItem('access_token')
              window.location.href = '/admin/login'
            }
          }
        )
        return
      }
      
      // 如果修改了网站标题或SEO信息，立即更新
      if (form.value.site_title) {
        updatePageTitle(' - 后台管理')
      }
      if (form.value.site_keywords || form.value.site_description) {
        updateMetaTags()
      }
    } catch (error) {
      console.error('保存失败:', error)
      ElMessage.error(error.response?.data?.detail || '保存失败')
    } finally {
      submitting.value = false
    }
  })
}

// 上传favicon
async function handleFaviconChange(file) {
  try {
    const formData = new FormData()
    formData.append('file', file.raw)
    
    const token = localStorage.getItem('access_token')
    const res = await axios.post('/api/upload/favicon', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${token}`
      }
    })
    
    ElMessage.success(res.data.message)
    // 更新预览（添加时间戳避免缓存）
    faviconPreview.value = `/favicon.ico?t=${Date.now()}`
    // 刷新备份文件列表
    loadBackupFiles()
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error(error.response?.data?.detail || '上传失败')
  }
}

// 上传logo
async function handleLogoChange(file) {
  try {
    const formData = new FormData()
    formData.append('file', file.raw)
    
    const token = localStorage.getItem('access_token')
    const res = await axios.post('/api/upload/logo', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${token}`
      }
    })
    
    ElMessage.success(res.data.message)
    // 更新预览（添加时间戳避免缓存）
    logoPreview.value = `/${res.data.filename}?t=${Date.now()}`
    // 刷新备份文件列表
    loadBackupFiles()
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error(error.response?.data?.detail || '上传失败')
  }
}

// 加载备份文件列表
async function loadBackupFiles() {
  try {
    const token = localStorage.getItem('access_token')
    const res = await axios.get('/api/upload/files', {
      headers: { Authorization: `Bearer ${token}` }
    })
    backupFiles.value = res.data.files.filter(f => f.is_backup)
  } catch (error) {
    console.error('加载文件列表失败:', error)
  }
}

// 删除备份文件
async function deleteBackup(filename) {
  try {
    await ElMessageBox.confirm(`确定要删除备份文件 ${filename} 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const token = localStorage.getItem('access_token')
    await axios.delete(`/api/upload/backup/${filename}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    ElMessage.success('删除成功')
    loadBackupFiles()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 格式化文件大小
function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

onMounted(() => {
  loadSettings()
  loadBackupFiles()
})
</script>

<style scoped>
.settings-page {
  padding: 20px;
  padding-bottom: 100px; /* 为底部固定按钮留出空间 */
}

.settings-page h2 {
  margin-bottom: 20px;
}

.el-divider {
  margin: 30px 0 20px;
}

/* 固定在底部的操作按钮 */
.fixed-footer {
  position: fixed;
  bottom: 0;
  left: 200px; /* 避开左侧导航栏（导航栏宽度200px） */
  right: 0;
  background: #ffffff;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.08);
  z-index: 100;
  padding: 16px 0;
  animation: slideUp 0.3s ease-out;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  justify-content: flex-end; /* 靠右对齐 */
  align-items: center;
  gap: 16px;
}

.footer-content .el-button {
  min-width: 120px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.footer-content .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .settings-page {
    padding-bottom: 90px;
  }
  
  .fixed-footer {
    left: 0; /* 小屏幕时导航栏可能隐藏或变窄 */
  }
  
  .footer-content {
    padding: 0 16px;
    gap: 12px;
    justify-content: center; /* 小屏幕居中显示 */
  }
  
  .footer-content .el-button {
    min-width: 100px;
    font-size: 14px;
  }
}
</style>
