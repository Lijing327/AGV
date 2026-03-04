"""
地图 API
"""
from fastapi import APIRouter

from app.deps import get_map_repo

router = APIRouter(prefix="/map")


@router.get("")
def get_map():
    """获取地图（nodes + edges）"""
    map_data = get_map_repo().get_map()
    return {
        "nodes": [
            {"id": n.id, "x": n.x, "y": n.y}
            for n in map_data.nodes
        ],
        "edges": [
            {
                "from": e.from_node,
                "to": e.to_node,
                "bidirectional": e.bidirectional,
                "capacity": e.capacity,
                "occupied_by": e.occupied_by,
            }
            for e in map_data.edges
        ],
    }
