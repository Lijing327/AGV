"""
交通服务：路段锁，管理 edge 的占用与释放
双向边共享同一物理路段，占用时同时锁定两个方向
"""
from app.domain.models import MapData, Edge


class TrafficService:
    """路段占用管理（锁机制）"""

    def __init__(self, map_data: MapData):
        self._edges = map_data.edges

    def _find_edge(self, from_node: str, to_node: str) -> Edge | None:
        """查找 from -> to 的边"""
        for edge in self._edges:
            if edge.from_node == from_node and edge.to_node == to_node:
                return edge
        return None

    def _find_bidirectional_pair(self, from_node: str, to_node: str) -> list[Edge]:
        """查找双向边对（同一物理路段的两个方向）"""
        result = []
        e1 = self._find_edge(from_node, to_node)
        e2 = self._find_edge(to_node, from_node)
        if e1:
            result.append(e1)
        if e2 and e2 != e1:
            result.append(e2)
        return result

    def try_acquire(self, from_node: str, to_node: str, agv_id: str) -> bool:
        """
        尝试占用路段 from_node -> to_node
        双向边会同时锁定反向，避免对向冲突
        成功返回 True，已被占用返回 False
        """
        pair = self._find_bidirectional_pair(from_node, to_node)
        if not pair:
            return False
        for edge in pair:
            if edge.occupied_by is not None and edge.occupied_by != agv_id:
                return False
        for edge in pair:
            edge.occupied_by = agv_id
        return True

    def release(self, from_node: str, to_node: str, agv_id: str) -> bool:
        """
        释放路段占用
        双向边同时释放
        """
        pair = self._find_bidirectional_pair(from_node, to_node)
        if not pair:
            return False
        released = False
        for edge in pair:
            if edge.occupied_by == agv_id:
                edge.occupied_by = None
                released = True
        return released

    def is_available(self, from_node: str, to_node: str, agv_id: str) -> bool:
        """检查路段是否可用（未被占用或已被本车占用）"""
        pair = self._find_bidirectional_pair(from_node, to_node)
        if not pair:
            return False
        for edge in pair:
            if edge.occupied_by is not None and edge.occupied_by != agv_id:
                return False
        return True
