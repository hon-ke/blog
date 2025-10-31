"""
用户管理系统API主入口 - 生产环境版本

该模块负责：
1. 初始化FastAPI应用
2. 配置CORS跨域支持
3. 管理应用生命周期
4. 注册所有路由

环境要求：
- Python 3.8+
- FastAPI
- Gunicorn + Uvicorn
"""
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles

from config import settings
from core.security import is_admin
from core.db import close_db, init_db

# 常规路由
from blog.api import post, other, comments, page, rss
from blog.admin import files as files_admin
from blog.admin import page as page_admin
from blog.admin import post as post_admin
from blog.admin import root
from core.api import router as meta_router
from core.api import root_router as meta_root_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理

    负责：
    - 数据库初始化
    - 资源清理
    """
    # 初始化数据库
    await init_db()

    try:
        yield
    finally:
        # 清理资源
        await close_db()

# 初始化FastAPI应用
app = FastAPI(
    title="用户管理系统",
    description="提供用户注册、登录、信息管理等功能的API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    # 生产环境优化配置
    openapi_url="/openapi.json" if settings.DEBUG else None
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS if not settings.DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 配置静态文件服务
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# 注册路由 - 普通路由
prefix = "/api"
app.include_router(page.router, prefix=prefix)
app.include_router(other.router, prefix=prefix)
app.include_router(post.router, prefix=prefix)
app.include_router(comments.router, prefix=prefix)
app.include_router(meta_router, prefix=prefix)
app.include_router(rss.router, prefix=prefix)

# 注册路由 - 管理员路由
app.include_router(post_admin.router, prefix=prefix, dependencies=[Depends(is_admin)])
app.include_router(files_admin.router, prefix=prefix, dependencies=[Depends(is_admin)])
app.include_router(page_admin.router, prefix=prefix, dependencies=[Depends(is_admin)])
app.include_router(root.router, prefix=prefix, dependencies=[Depends(is_admin)])
app.include_router(meta_root_router, prefix=prefix, dependencies=[Depends(is_admin)])

@app.get("/", tags=["根路由"])
async def root_endpoint():
    """根端点
    返回：
    - 欢迎信息
    """
    return {"message": "欢迎使用用户管理系统API", "status": "running"}

@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查端点
    用于负载均衡器和监控系统检查服务状态

    """
    return settings.__dict__

# # 移除开发服务器的启动代码
# # 生产环境使用 Gunicorn 启动

if __name__ == "__main__":
    import uvicorn
    # 使用Uvicorn启动开发服务器
        # 测试不同日志级别

    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # 监听所有网络接口
        port=8000,  # 使用8000端口
        workers=4,  # 单worker模式
        reload=True  # 开发模式下启用热重载
    )
