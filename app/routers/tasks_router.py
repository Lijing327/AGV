"""
任务 API
"""
from fastapi import APIRouter
from pydantic import BaseModel

from app.deps import get_sim_adapter

router = APIRouter(prefix="/tasks")


class CreateTaskRequest(BaseModel):
    """创建任务请求"""
    from_node: str
    to_node: str


@router.get("")
def get_tasks():
    """获取所有任务"""
    adapter = get_sim_adapter()
    tasks = adapter.get_tasks()
    return {
        "tasks": [
            {
                "id": t.id,
                "from_node": t.from_node,
                "to_node": t.to_node,
                "status": t.status.value,
                "assigned_agv_id": t.assigned_agv_id,
            }
            for t in tasks
        ],
    }


@router.post("")
def create_task(req: CreateTaskRequest):
    """创建任务"""
    adapter = get_sim_adapter()
    task = adapter.create_task(req.from_node, req.to_node)
    if task is None:
        return {"error": "创建失败"}
    return {
        "id": task.id,
        "from_node": task.from_node,
        "to_node": task.to_node,
        "status": task.status.value,
        "assigned_agv_id": task.assigned_agv_id,
    }
