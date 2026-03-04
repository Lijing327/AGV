"""
地图仓储：从 JSON 文件加载地图数据
"""
import json
from pathlib import Path

from app.domain.models import Node, Edge, MapData


class MapRepository:
    """地图数据仓储"""

    def __init__(self, map_path: str | Path):
        self._map_path = Path(map_path)
        self._map_data: MapData | None = None

    def load(self) -> MapData:
        """加载地图数据"""
        with open(self._map_path, encoding="utf-8") as f:
            raw = json.load(f)

        nodes = [
            Node(id=n["id"], x=float(n["x"]), y=float(n["y"]))
            for n in raw["nodes"]
        ]

        edges_raw = raw["edges"]
        edges = []
        for e in edges_raw:
            edges.append(Edge(
                from_node=e["from"],
                to_node=e["to"],
                bidirectional=e.get("bidirectional", True),
                capacity=e.get("capacity", 1),
                occupied_by=e.get("occupied_by"),
            ))
            # 双向边需要反向边
            if e.get("bidirectional", True):
                edges.append(Edge(
                    from_node=e["to"],
                    to_node=e["from"],
                    bidirectional=True,
                    capacity=e.get("capacity", 1),
                    occupied_by=e.get("occupied_by"),
                ))

        self._map_data = MapData(nodes=nodes, edges=edges)
        return self._map_data

    def get_map(self) -> MapData:
        """获取地图（若未加载则先加载）"""
        if self._map_data is None:
            return self.load()
        return self._map_data

    def get_edges_mutable(self) -> list[Edge]:
        """获取可修改的边列表（用于 traffic 占用）"""
        if self._map_data is None:
            self.load()
        return self._map_data.edges
