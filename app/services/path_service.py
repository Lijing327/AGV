"""
路径服务：使用 BFS 计算节点间最短路径
"""
from collections import deque

from app.domain.models import MapData, Edge


class PathService:
    """路径规划服务（BFS）"""

    def __init__(self, map_data: MapData):
        self._map_data = map_data
        self._adj: dict[str, list[str]] = {}
        self._build_adjacency()

    def _build_adjacency(self) -> None:
        """构建邻接表"""
        self._adj = {}
        for edge in self._map_data.edges:
            if edge.from_node not in self._adj:
                self._adj[edge.from_node] = []
            if edge.to_node not in self._adj[edge.from_node]:
                self._adj[edge.from_node].append(edge.to_node)

    def find_path(self, from_node: str, to_node: str) -> list[str]:
        """
        使用 BFS 查找最短路径
        返回节点 id 列表，不含起点，含终点
        若无法到达返回空列表
        """
        if from_node == to_node:
            return []  # 已在终点，无需移动

        if from_node not in self._adj or to_node not in self._adj:
            return []

        visited: set[str] = {from_node}
        queue: deque[tuple[str, list[str]]] = deque([(from_node, [from_node])])

        while queue:
            node, path = queue.popleft()
            for neighbor in self._adj.get(node, []):
                if neighbor == to_node:
                    return path[1:] + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return []
