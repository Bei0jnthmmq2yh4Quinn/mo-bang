"""Content Tools - 自媒体运营工具主入口。"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routes import analysis, health, media, mobang, subscriptions, topics, trends

app = FastAPI(title="墨榜", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(trends.router, prefix="/api/trends", tags=["trends"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(topics.router, prefix="/api/topics", tags=["topics"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["subscriptions"])
app.include_router(media.router, prefix="/api/media", tags=["media"])
app.include_router(mobang.router, prefix="/api/mobang", tags=["mobang"])


@app.get("/")
async def root():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
