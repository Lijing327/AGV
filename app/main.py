"""
AGV 调度系统 FastAPI 主入口
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.deps import get_map_repo, get_sim_adapter
from app.routers.map_router import router as map_router
from app.routers.fleet_router import router as fleet_router
from app.routers.tasks_router import router as tasks_router
from app.routers.sim_router import router as sim_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时预加载
    get_map_repo().load()
    get_sim_adapter()
    yield
    # 关闭时停止模拟
    adapter = get_sim_adapter()
    if adapter:
        adapter.stop()


app = FastAPI(
    title="AGV 调度系统 Demo",
    description="可扩展的 AGV 调度系统，支持模拟与真实 AGV",
    lifespan=lifespan,
)

app.include_router(map_router, tags=["map"])
app.include_router(fleet_router, tags=["fleet"])
app.include_router(tasks_router, tags=["tasks"])
app.include_router(sim_router, tags=["sim"])

# 静态文件与首页
static_dir = Path(__file__).parent.parent / "static"


@app.get("/")
def index():
    """首页：AGV 调度可视化"""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "AGV 调度系统 API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
