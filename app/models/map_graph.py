"""
Map Graph 数据结构：用于表示从 .smap 文件导入的地图
"""
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Any


@dataclass
class MapMeta:
    """地图元数据"""
    mapName: str
    resolution: float
    version: str
    minPos: Dict[str, float]  # {"x": float, "y": float}
    maxPos: Dict[str, float]  # {"x": float, "y": float}


@dataclass
class Node:
    """地图节点"""
    id: str
    type: Optional[str]  # className from advancedPointList
    x: float
    y: float


@dataclass
class Bezier:
    """贝塞尔曲线控制点"""
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass
class Edge:
    """地图边（路段）"""
    id: str
    source: str
    target: str
    bezier: Optional[Bezier] = None
    length: Optional[float] = None


@dataclass
class MapGraph:
    """地图图结构"""
    meta: MapMeta
    nodes: List[Node]
    edges: List[Edge]
    adjacency: Dict[str, List[Dict[str, Any]]]  # {nodeId: [{"to": nodeId, "edgeId": edgeId, "cost": float}]}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，便于序列化为 JSON"""
        return {
            "meta": asdict(self.meta),
            "nodes": [asdict(node) for node in self.nodes],
            "edges": [
                {
                    "id": edge.id,
                    "source": edge.source,
                    "target": edge.target,
                    "bezier": asdict(edge.bezier) if edge.bezier else None,
                    "length": edge.length,
                }
                for edge in self.edges
            ],
            "adjacency": self.adjacency,
        }
