from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os

app = FastAPI(title="Hyperliquid交易员分析系统")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def root():
    """返回主页"""
    print("访问主页")
    return FileResponse(os.path.join(static_path, "index.html"))

@app.get("/api/test")
async def test():
    """测试API"""
    return {"message": "API is working"}

if __name__ == "__main__":
    print("启动服务器...")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        log_level="debug",
        reload=True
    ) 