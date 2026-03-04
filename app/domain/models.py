"""
Domain 模型：纯数据结构，无业务逻辑
"""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class AGVStatus(str, Enum):
    """AGV 状态枚举"""
    IDLE = "idle"
    MOVING = "moving"
    WAITING = "waiting"
    ERROR = "error"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 待分配
    ASSIGNED = "assigned"    # 已分配 AGV
    IN_PROGRESS = "in_progress"  # 执行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


@dataclass
class Node:
    """地图节点"""
    id: str
    x: float
    y: float


@dataclass
class Edge:
    """地图边（路段）"""
    from_node: str
    to_node: str
    bidirectional: bool
    capacity: int
    occupied_by: Optional[str] = None  # 占用的 AGV id


@dataclass
class MapData:
    """地图数据"""
    nodes: list[Node]
    edges: list[Edge]


@dataclass
class AGV:
    """AGV 车辆"""
    id: str
    current_node: str
    status: AGVStatus
    path: list[str] = field(default_factory=list)  # 剩余路径
    current_task_id: Optional[str] = None
    color: str = "#4caf50"


@dataclass
class Task:
    """运输任务"""
    id: str
    from_node: str
    to_node: str
    status: TaskStatus
    assigned_agv_id: Optional[str] = None
