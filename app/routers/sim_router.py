"""
模拟控制 API
"""
from fastapi import APIRouter

from app.deps import get_sim_adapter

router = APIRouter(prefix="/sim")


@router.post("/start")
async def sim_start():
    """启动模拟 tick（需在 async 上下文中以获取事件循环）"""
    adapter = get_sim_adapter()
    adapter.start()
    return {"status": "started"}


@router.post("/stop")
def sim_stop():
    """停止模拟 tick"""
    adapter = get_sim_adapter()
    adapter.stop()
    return {"status": "stopped"}
