"""Content Tools - 自媒体运营工具主入口。"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routes import analysis, health, media, topics, trends

# 创建 FastAPI 应用实例。
app = FastAPI(title="墨榜", version="1.0.0")

# 允许前端页面或外部客户端直接调用 API。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态资源目录，用于提供前端页面和静态文件。
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册各业务路由。
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(trends.router, prefix="/api/trends", tags=["trends"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(topics.router, prefix="/api/topics", tags=["topics"])
app.include_router(media.router, prefix="/api/media", tags=["media"])


@app.get("/")
async def root():
    """返回前端首页。"""
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn

    # 本地/服务器直接运行时监听 8081 端口。
    uvicorn.run(app, host="0.0.0.0", port=8081)
