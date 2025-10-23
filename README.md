# 个人博客系统

一个现代化的全栈个人博客系统，采用前后端分离架构，提供丰富的博客功能和优雅的用户界面。

## 🚀 技术栈

### 后端技术
- **FastAPI** - 现代化 Python Web 框架
- **Tortoise ORM** - 异步 ORM 框架
- **SQLite** - 轻量级数据库
- **Uvicorn** - ASGI 服务器
- **Pydantic** - 数据验证和设置管理
- **JWT** - 身份认证
- **Pillow** - 图像处理

### 前端技术
- **Vue 3** - 渐进式 JavaScript 框架
- **Vue Router** - 路由管理
- **Axios** - HTTP 客户端
- **Marked** - Markdown 解析器
- **Highlight.js** - 代码高亮
- **md-editor-v3** - Markdown 编辑器
- **Fancybox** - 图片灯箱效果

## 📋 功能特性

### 博客功能
- 📝 文章发布和管理
- 🏷️ 分类和标签管理
- 📂 文章归档
- 🔍 搜索功能
- 💬 评论系统
- 📊 热度图展示
- 📱 响应式设计

### 管理功能
- 👤 用户认证和授权
- 🖼️ 文件上传管理（图片、视频、文档）
- 📄 Markdown 编辑器
- 🔧 后台管理界面
- 📈 文章统计

### 用户体验
- 🎨 现代化 UI 设计
- ⚡ 快速加载
- 📖 目录导航（TOC）
- 🖱️ 自定义光标
- 🔄 平滑滚动

## 🛠️ 安装和运行

### 环境要求
- Python 3.8+
- Node.js 14+
- npm 或 yarn

### 后端运行

1. 进入后端目录：
```bash
cd back
```

2. 安装 Python 依赖：
```bash
pip install -r requirements.txt
```

3. 启动后端服务：
```bash
python main.py
```

后端服务将在 `http://localhost:8000` 启动，并自动创建数据库。

### 前端运行

1. 进入前端目录：
```bash
cd front
```

2. 安装依赖：
```bash
yarn install
```

3. 启动开发服务器：
```bash
yarn serve
```

前端服务将在 `http://localhost:12138` 启动。

## 📁 项目结构

```
├── back/                    # 后端代码
│   ├── blog/               # 博客核心模块
│   │   ├── api/           # API 路由
│   │   │   ├── admin.py   # 管理功能
│   │   │   ├── post.py    # 文章管理
│   │   │   ├── comments.py # 评论管理
│   │   │   ├── upload.py  # 文件上传
│   │   │   └── other.py   # 其他功能
│   │   ├── models.py      # 数据模型
│   │   └── schemas.py     # 数据模式
│   ├── core/              # 核心模块
│   │   ├── config.py      # 配置管理
│   │   ├── db.py          # 数据库配置
│   │   └── security.py    # 安全认证
│   └── static/            # 静态文件
│       ├── images/        # 图片文件
│       ├── videos/        # 视频文件
│       └── documents/     # 文档文件
└── front/                  # 前端代码
    ├── src/
    │   ├── components/    # Vue 组件
    │   │   ├── Admin/     # 管理组件
    │   │   ├── Header.vue # 头部组件
    │   │   ├── Footer.vue # 底部组件
    │   │   ├── Aside.vue  # 侧边栏
    │   │   └── Toc.vue    # 目录导航
    │   ├── views/         # 页面视图
    │   │   ├── Index.vue  # 首页
    │   │   ├── Post.vue   # 文章页
    │   │   ├── About.vue  # 关于页
    │   │   ├── Archives.vue # 归档页
    │   │   └── Create.vue # 创作页
    │   ├── router/        # 路由配置
    │   └── assets/        # 静态资源
```

## 🔧 API 文档

启动后端服务后，可以访问以下地址查看 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📸 功能截图

（此处可以添加博客的实际运行截图）

## 🚀 部署

### 生产环境构建

前端构建：
```bash
cd front
yarn build
```

构建后的文件位于 `dist/` 目录，可以部署到任何静态文件服务器。

### 数据库

项目使用 SQLite 数据库，数据库文件会自动创建在项目根目录。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 📄 许可证

MIT License

## 📞 联系方式

如有问题，请通过以下方式联系：
- 创建 GitHub Issue
- 发送邮件

---

**注意**: 这是一个开发中的项目，功能可能会持续更新和改进。
