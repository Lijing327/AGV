"""
依赖注入：地图仓储与模拟适配器
"""
from pathlib import Path

from app.adapters.map_repo import MapRepository
from app.adapters.sim_agv_adapter import SimAGVAdapter

_map_repo: MapRepository | None = None
_sim_adapter: SimAGVAdapter | None = None


def get_map_repo() -> MapRepository:
    global _map_repo
    if _map_repo is None:
        map_path = Path(__file__).parent / "data" / "map_demo.json"
        _map_repo = MapRepository(map_path)
    return _map_repo


def get_sim_adapter() -> SimAGVAdapter:
    global _sim_adapter
    if _sim_adapter is None:
        map_data = get_map_repo().load()
        _sim_adapter = SimAGVAdapter(map_data)
    return _sim_adapter
