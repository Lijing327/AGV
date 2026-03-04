"""
模拟 AGV 适配器：管理 3 台模拟 AGV，tick 驱动移动
"""
import asyncio
import uuid
from typing import Callable

from app.domain.models import AGV, Task, AGVStatus, TaskStatus, MapData
from app.services.dispatch_service import DispatchService
from app.services.path_service import PathService
from app.services.traffic_service import TrafficService


class SimAGVAdapter:
    """
    模拟 AGV 适配器
    - 3 台 AGV 初始分布在不同节点
    - 每 1 秒 tick：沿 path 前进一个节点
    - 进入 edge 前必须获得占用，释放上一条 edge
    """

    AGV_COLORS = ["#4caf50", "#2196f3", "#ffc107"]

    def __init__(self, map_data: MapData):
        self._map_data = map_data
        self._path_service = PathService(map_data)
        self._traffic_service = TrafficService(map_data)
        self._dispatch_service = DispatchService(map_data)

        # 3 台 AGV，初始分布在不同节点（接收区、主通道、装配区）
        nodes = [n.id for n in map_data.nodes]
        init_nodes = ["R1", "C3", "A2"] if all(n in nodes for n in ["R1", "C3", "A2"]) else nodes[:3]
        self._agvs: list[AGV] = [
            AGV(
                id=f"AGV-{i+1:03d}",
                current_node=init_nodes[i],
                status=AGVStatus.IDLE,
                path=[],
                color=self.AGV_COLORS[i],
            )
            for i in range(min(3, len(init_nodes)))
        ]

        self._tasks: dict[str, Task] = {}
        self._running = False
        self._tick_task: asyncio.Task | None = None

    def get_agvs(self) -> list[AGV]:
        """获取所有 AGV"""
        return self._agvs.copy()

    def get_tasks(self) -> list[Task]:
        """获取所有任务"""
        return list(self._tasks.values())

    def get_map(self) -> MapData:
        """获取地图"""
        return self._map_data

    def create_task(self, from_node: str, to_node: str) -> Task | None:
        """
        创建任务，自动分配最近 idle AGV
        返回创建的任务，若无法分配则返回 None
        """
        task_id = f"T-{uuid.uuid4().hex[:8]}"
        task = Task(
            id=task_id,
            from_node=from_node,
            to_node=to_node,
            status=TaskStatus.PENDING,
        )

        agv = self._dispatch_service.select_nearest_idle_agv(
            self._agvs, from_node, to_node
        )
        if agv is None:
            self._tasks[task_id] = task
            return task  # 仍创建任务，但保持 PENDING

        path = self._dispatch_service.assign_task(task, agv)
        if not path:
            self._tasks[task_id] = task
            return task

        task.status = TaskStatus.ASSIGNED
        task.assigned_agv_id = agv.id
        agv.current_task_id = task_id
        agv.status = AGVStatus.MOVING
        agv.path = path

        self._tasks[task_id] = task
        return task

    def _tick_one_agv(self, agv: AGV) -> None:
        """
        对单台 AGV 执行一次 tick
        - 若有 path：尝试进入下一节点（需先获得 edge 锁，释放上一条）
        - 若下一路段被占用：保持 WAITING
        """
        if not agv.path:
            if agv.current_task_id:
                task = self._tasks.get(agv.current_task_id)
                if task:
                    task.status = TaskStatus.COMPLETED
                agv.current_task_id = None
            agv.status = AGVStatus.IDLE
            return

        next_node = agv.path[0]
        from_node = agv.current_node
        to_node = next_node

        # 释放上一条 edge（若之前有移动过，需要记录上一段）
        # 简化：每次移动前，先尝试获取下一段；进入后释放当前段
        # 当前在 from_node，要进入 to_node，需要占用 from_node->to_node
        if not self._traffic_service.is_available(from_node, to_node, agv.id):
            agv.status = AGVStatus.WAITING
            return

        # 1. 获取路段锁（进入前必须占用）
        if not self._traffic_service.try_acquire(from_node, to_node, agv.id):
            agv.status = AGVStatus.WAITING
            return

        # 2. 移动：进入下一节点
        agv.current_node = to_node
        agv.path.pop(0)
        agv.status = AGVStatus.MOVING

        # 3. 释放路段（已离开该路段）
        self._traffic_service.release(from_node, to_node, agv.id)

    def _tick(self) -> None:
        """执行一次模拟 tick"""
        for agv in self._agvs:
            self._tick_one_agv(agv)

    async def _tick_loop(self) -> None:
        """每秒执行一次 tick"""
        while self._running:
            self._tick()
            await asyncio.sleep(1)

    def start(self) -> None:
        """启动模拟"""
        if self._running:
            return
        self._running = True
        self._tick_task = asyncio.create_task(self._tick_loop())

    def stop(self) -> None:
        """停止模拟"""
        self._running = False
        if self._tick_task:
            self._tick_task.cancel()
            self._tick_task = None
