from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.database import init_db
from app.api import auth, categories, links, engines, settings as settings_api, home, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("正在初始化数据库...")
    await init_db()
    
    # 确保数据目录存在
    import os
    os.makedirs("./data", exist_ok=True)
    
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} 启动成功!")
    yield
    # 关闭时执行（如果需要）


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="开发文档导航系统 API",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(links.router, prefix="/api")
app.include_router(engines.router, prefix="/api")
app.include_router(settings_api.router, prefix="/api")
app.include_router(home.router, prefix="/api")
app.include_router(upload.router, prefix="/api")

# 健康检查路由
@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": settings.APP_VERSION}

# 前端路由回退处理（SPA支持）- 必须在所有具体路由之后
# 注意：这个路由会匹配所有未被上面路由处理的 GET 请求
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """处理前端路由，所有非API请求都返回index.html"""
    # 如果是 API 路径，说明没有匹配到任何 API 路由
    if full_path.startswith("api/"):
        return JSONResponse(
            status_code=404, 
            content={"detail": f"API endpoint /api/{full_path} not found. Check if the route is registered."}
        )
    
    # 检查是否是静态资源
    static_file = f"./static/{full_path}"
    if os.path.exists(static_file) and os.path.isfile(static_file):
        return FileResponse(static_file)
    
    # 返回 index.html（SPA路由）
    index_path = "./static/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
