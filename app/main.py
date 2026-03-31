"""
AGV 调度系统 FastAPI 主入口（前后端分离）
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.deps import get_map_repo, get_sim_adapter, get_robokit_client
from app.routers.map_router import router as map_router
from app.routers.fleet_router import router as fleet_router
from app.routers.tasks_router import router as tasks_router
from app.routers.sim_router import router as sim_router
from app.routers.robokit_router import router as robokit_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时预加载
    get_map_repo().load()
    get_sim_adapter()
    # 获取robokit客户端实例(不自动连接)
    get_robokit_client()
    yield
    # 关闭时停止模拟和断开Robokit连接
    adapter = get_sim_adapter()
    if adapter:
        adapter.stop()
    # 关闭Robokit客户端连接
    robokit = get_robokit_client()
    await robokit.close()


app = FastAPI(
    title="AGV 调度系统 Demo",
    description="可扩展的 AGV 调度系统，支持模拟与真实 AGV（前后端分离）",
    lifespan=lifespan,
)

# CORS：允许前端跨域调用（allow_origins 为 * 时 allow_credentials 必须为 False，否则浏览器会拒绝）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 机器人连接异常处理：超时/连接失败返回 504/503，避免 500
@app.exception_handler(TimeoutError)
async def timeout_handler(request, exc):
    return JSONResponse(status_code=504, content={"detail": "机器人请求超时"})

@app.exception_handler(ConnectionError)
async def connection_handler(request, exc):
    return JSONResponse(status_code=503, content={"detail": "无法连接机器人"})

# API 路由，统一 /api 前缀
app.include_router(map_router, prefix="/api", tags=["map"])
app.include_router(fleet_router, prefix="/api", tags=["fleet"])
app.include_router(tasks_router, prefix="/api", tags=["tasks"])
app.include_router(sim_router, prefix="/api", tags=["sim"])
app.include_router(robokit_router, prefix="/api", tags=["robokit"])


@app.get("/")
def root():
    """API 根路径"""
    return {"message": "AGV 调度系统 API", "docs": "/docs", "api_prefix": "/api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
