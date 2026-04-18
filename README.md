# 自用导航网站

## 项目简介

个人自用的静态导航网站，原来是 Fork 自 [TopVitamin/static-nav: 静态导航页面](https://github.com/TopVitamin/static-nav)，个人比较喜欢这种简洁样式，用了好几年，但苦于配置链接比较麻烦，最近用 AI 工具 + 手改整个重构了一遍，增加了后台管理的功能，虽然已经不算静态导航网站了，但依然还算轻量。数据库初始化脚本里面包含了常用的搜索引擎。

项目地址： [![img](https://badgen.net/badge/github/static-nav?icon=github)](https://github.com/longalang/static-nav) |  [![img](https://badgen.net/badge/gitee/static-nav?color=red&icon=gitee)](https://gitee.com/longalone/static-nav)

预览：[ByteMan开发文档导航  - Roookie博客](https://byteman.wlplove.com/)

---

以下说明文档由 AI 生成。

（~~AI 真好用，原来这就是吸一口的感觉~~）

## 技术架构

### 前端技术栈

- **框架**: Vue 3.4.15 (Composition API)
- **构建工具**: Vite 5.0.11
- **路由**: Vue Router 4.2.5
- **状态管理**: Pinia 2.1.7
- **UI组件库**: Element Plus 2.5.3
- **HTTP客户端**: Axios 1.6.5
- **CSS预处理器**: Sass 1.70.0

### 后端技术栈

- **框架**: FastAPI 0.109.0
- **服务器**: Uvicorn 0.27.0
- **数据库**: SQLite + SQLAlchemy 2.0.25
- **异步驱动**: aiosqlite 0.19.0
- **认证**: JWT (python-jose) + bcrypt
- **数据验证**: Pydantic 2.5.3
- **文件上传**: python-multipart 0.0.6

## 项目启动

### 环境要求
- **Node.js**: >= 18.0.0
- **Python**: >= 3.9

#### 1. 后端启动
```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

接口文档：http://localhost:8000/docs


#### 2. 前端启动
```bash
cd frontend

# 安装依赖
npm install

# 启动
npm run dev
```

访问前端页面：http://localhost:5173

### 默认管理员账号
- **用户名**: admin
- **密码**: admin123

⚠️ **登录后建议修改密码！**

---

## 打包部署

### 前端打包

```bash
cd frontend

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

打包后的文件位于 `backend/static/` 目录。

### 后端部署

#### 开发环境

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 生产环境
```bash
cd backend

# 使用gunicorn（Linux/Mac）
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 或使用uvicorn多进程
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Nginx配置示例
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/xxxx/backend/static;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 静态资源
    location /assets/ {
        alias /path/xxxx/backend/static/assets/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## 数据库设计

### 数据库类型
- **SQLite** (开发/小型应用)
- 可扩展至 PostgreSQL / MySQL

### 数据表结构

#### 1. 导航分类表 (categories)

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 主键 | PRIMARY KEY |
| name | VARCHAR(50) | 分类名称 | NOT NULL |
| sort_order | INTEGER | 排序 | DEFAULT 0 |
| is_active | BOOLEAN | 是否启用 | DEFAULT 1 |
| created_at | DATETIME | 创建时间 | DEFAULT CURRENT_TIMESTAMP |
| updated_at | DATETIME | 更新时间 | DEFAULT CURRENT_TIMESTAMP |

**关系**: 一对多关联 navigation_links

#### 2. 导航链接表 (navigation_links)

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 主键 | PRIMARY KEY |
| category_id | INTEGER | 分类ID | FOREIGN KEY → categories.id |
| title | VARCHAR(100) | 链接标题 | NOT NULL |
| url | VARCHAR(500) | 链接地址 | NOT NULL |
| description | VARCHAR(200) | 描述信息 | NULLABLE |
| sort_order | INTEGER | 排序 | DEFAULT 0 |
| is_active | BOOLEAN | 是否启用 | DEFAULT 1 |
| created_at | DATETIME | 创建时间 | DEFAULT CURRENT_TIMESTAMP |
| updated_at | DATETIME | 更新时间 | DEFAULT CURRENT_TIMESTAMP |

**外键**: category_id → categories.id (CASCADE删除)

#### 3. 搜索引擎表 (search_engines)

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 主键 | PRIMARY KEY |
| name | VARCHAR(50) | 引擎名称 | NOT NULL |
| search_url | VARCHAR(500) | 搜索URL模板 | NOT NULL |
| icon_svg | TEXT | SVG图标内容 | NULLABLE |
| is_active | BOOLEAN | 是否启用 | DEFAULT 1 |
| is_default | BOOLEAN | 是否默认 | DEFAULT 0 |
| sort_order | INTEGER | 排序 | DEFAULT 0 |
| created_at | DATETIME | 创建时间 | DEFAULT CURRENT_TIMESTAMP |
| updated_at | DATETIME | 更新时间 | DEFAULT CURRENT_TIMESTAMP |

#### 4. 系统设置表 (settings)

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | INTEGER | 主键 | PRIMARY KEY |
| key | VARCHAR(50) | 配置键 | UNIQUE, NOT NULL |
| value | TEXT | 配置值 | NULLABLE |
| description | VARCHAR(200) | 描述 | NULLABLE |
| updated_at | DATETIME | 更新时间 | DEFAULT CURRENT_TIMESTAMP |

**配置项说明**:
- `icp_beian`: ICP备案号
- `police_beian`: 公网安备号
- `site_title`: 网站标题
- `site_keywords`: 网站关键词
- `site_description`: 网站描述
- `admin_username`: 管理员用户名
- `admin_password`: 管理员密码哈希（bcrypt加密）

**注意**: 系统中只有一个管理员账号，用户名和密码存储在settings表中，可通过系统设置页面修改。

### 数据库位置
```
backend/data/nav.db
```

**功能说明**:

- ✅ 创建所有数据库表（categories, navigation_links, search_engines, settings, admins）
- ✅ 检查并创建默认管理员账号
- ✅ 如果已存在管理员，则跳过创建
- ✅ 不导入任何业务数据，保持数据库干净

**使用场景**:
- 首次部署时初始化数据库
- 开发环境重置数据库
- 测试环境重新创建表结构

---

## 功能说明

### 核心功能

#### 1. 导航管理

- ✅ 分类管理：增删改查、排序、启用/禁用
- ✅ 链接管理：增删改查、分页、筛选、排序
- ✅ 级联删除：删除分类时自动删除相关链接

#### 2. 搜索引擎
- ✅ 多引擎切换：支持百度、谷歌、必应等
- ✅ SVG图标：数据库存储，动态渲染
- ✅ 默认引擎：可设置默认搜索引擎
- ✅ 搜索功能：输入关键词，新窗口打开搜索结果

#### 3. 系统设置
- ✅ 备案信息：ICP备案号、公网安备号
- ✅ SEO优化：网站标题、关键词、描述
- ✅ 动态标题：实时应用到浏览器标签页
- ✅ Meta标签：自动更新keywords和description

#### 4. 文件管理
- ✅ Favicon上传：支持.ico格式
- ✅ Logo上传：支持PNG/JPG/GIF/SVG
- ✅ 自动备份：上传前自动备份原文件
- ✅ 备份命名：`原文件名_bak_yyyy-MM-dd.扩展名`
- ✅ 防覆盖：同一天多次上传添加时间戳
- ✅ 备份管理：查看和删除备份文件

#### 5. 用户认证
- ✅ JWT认证：安全的Token机制
- ✅ 密码加密：bcrypt哈希存储
- ✅ 路由守卫：未登录自动跳转
- ✅ 默认管理员：首次启动自动创建

#### 6. 响应式设计
- ✅ 桌面端：完整功能展示
- ✅ 平板端：自适应布局
- ✅ 手机端：优化交互体验
- ✅ 媒体查询：断点768px、480px

---

####  管理员账号

**重要**: 系统中只有一个管理员账号，用户名和密码存储在settings表中。

**修改方式**:
1. 登录后台管理系统
2. 进入“系统设置”页面
3. 在“其他设置”部分找到“管理员用户名”和“管理员密码”
4. 修改后点击“保存设置”
5. 系统会提示使用新凭据重新登录

**注意事项**:
- ✅ 密码字段留空则不修改密码
- ✅ 修改后立即生效，需要重新登录
- ✅ 密码使用bcrypt加密存储，安全可靠
- ❌ 不要直接修改数据库中的密码哈希值

---

## 常见问题

### Q1: 启动时提示"数据库文件不存在"
**A**: 确保`backend/data/`目录存在，运行`migrate_data.py`初始化数据库。

### Q2: 前端无法连接后端API
**A**: 检查：
1. 后端是否正常运行（访问http://localhost:8000/docs）
2. CORS配置是否正确
3. 前端代理配置（vite.config.js）

### Q3: 上传文件后看不到新图标
**A**: 浏览器缓存导致，尝试：
- Ctrl + F5 硬刷新
- 清除浏览器缓存
- 使用无痕模式测试

### Q4: 忘记管理员密码

#### 方法：直接修改数据库

```python
>>> from passlib.hash import bcrypt
>>> print(bcrypt.hash("新密码"))
# 复制输出的哈希值，更新到数据库
```

### Q5: 数据库被锁定
**A**: SQLite不支持并发写入，确保：
- 没有其他进程访问数据库
- 关闭所有数据库管理工具
- 重启后端服务

### Q6: 打包后页面空白
**A**: 检查：
1. `vite.config.js`中的`base`配置
2. Nginx配置是否正确
3. 浏览器控制台是否有错误

### Q7: 搜索引擎切换不生效
**A**: 检查：
1. 数据库中是否有启用的搜索引擎
2. 是否设置了默认搜索引擎
3. 浏览器控制台是否有JavaScript错误
