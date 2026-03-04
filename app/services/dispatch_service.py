"""
调度服务：任务分配，选择最近的 idle AGV
"""
from app.domain.models import AGV, Task, AGVStatus, TaskStatus, MapData
from app.services.path_service import PathService


class DispatchService:
    """任务调度服务"""

    def __init__(self, map_data: MapData):
        self._path_service = PathService(map_data)

    def select_nearest_idle_agv(
        self, agvs: list[AGV], from_node: str, to_node: str
    ) -> AGV | None:
        """
        选择距离 from_node 最近的 idle AGV
        使用路径长度作为距离度量
        """
        idle_agvs = [a for a in agvs if a.status == AGVStatus.IDLE]
        if not idle_agvs:
            return None

        best_agv: AGV | None = None
        best_len = float("inf")

        for agv in idle_agvs:
            path = self._path_service.find_path(agv.current_node, from_node)
            # path 为空表示已在起点（距离 0），应优先选择
            path_len = len(path)
            if path_len < best_len:
                best_len = path_len
                best_agv = agv

        return best_agv

    def assign_task(self, task: Task, agv: AGV) -> list[str]:
        """
        为 AGV 分配任务，返回完整路径（从 AGV 当前位置到任务起点，再到终点）
        """
        path_to_pickup = self._path_service.find_path(agv.current_node, task.from_node)
        path_to_deliver = self._path_service.find_path(task.from_node, task.to_node)

        if not path_to_deliver:
            return []

        # path_to_pickup 可能为空（AGV 已在起点）；path_to_deliver 不含起点、含终点
        full_path = path_to_pickup + path_to_deliver
        return full_path
