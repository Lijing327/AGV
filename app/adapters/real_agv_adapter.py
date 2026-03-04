"""
真实 AGV 适配器（占位）
后续替换 SimAGVAdapter 时，实现与真实 AGV 的通信接口
"""
from app.domain.models import AGV, Task, MapData


class RealAGVAdapter:
    """
    真实 AGV 适配器占位类
    扩展时需实现：
    - get_agvs() -> list[AGV]
    - get_tasks() -> list[Task]
    - create_task(from_node, to_node) -> Task | None
    - start() / stop()
    以及与真实 AGV 硬件/中间件的通信（MQTT、HTTP、TCP 等）
    """
    pass
