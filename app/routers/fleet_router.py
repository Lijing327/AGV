"""
车队 API
"""
from fastapi import APIRouter

from app.deps import get_sim_adapter

router = APIRouter(prefix="/fleet")


@router.get("")
def get_fleet():
    """获取车队状态"""
    adapter = get_sim_adapter()
    agvs = adapter.get_agvs()
    return {
        "agvs": [
            {
                "id": a.id,
                "current_node": a.current_node,
                "status": a.status.value,
                "path": a.path,
                "current_task_id": a.current_task_id,
                "color": a.color,
            }
            for a in agvs
        ],
    }
