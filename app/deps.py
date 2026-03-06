"""
依赖注入：地图仓储与模拟适配器、Robokit客户端
"""
from pathlib import Path

from app.adapters.map_repo import MapRepository
from app.adapters.sim_agv_adapter import SimAGVAdapter
from app.adapters.robokit_client import RobokitClient
from app.domain.models import MapData

_map_repo: MapRepository | None = None
_sim_adapter: SimAGVAdapter | None = None
# 存储最后导入的元数据（用于 API 返回）
_last_import_meta: dict | None = None

# Robokit客户端 (单例)
_robokit_client: RobokitClient | None = None
_robokit_host: str = "172.16.11.211"  # 默认机器人IP（测试用，后续会扩展多车）


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


def set_map_data(nodes, edges, meta=None):
    """直接设置地图数据（用于导入）

    Args:
        nodes: 节点列表
        edges: 边列表
        meta: 可选的元数据（用于显示）
    """
    global _map_repo, _sim_adapter, _last_import_meta
    # 确保有 map_repo 实例
    get_map_repo()
    _map_repo._map_data = MapData(nodes=nodes, edges=edges)
    # 保存元数据
    _last_import_meta = meta or {}
    # 重置 sim_adapter 因为地图变了
    _sim_adapter = None
    # 保存新地图数据到文件，便于下次加载
    _save_map_to_file(nodes, edges, meta)

def _save_map_to_file(nodes, edges, meta=None):
    """保存地图数据到默认文件"""
    import json
    from pathlib import Path
    
    map_dir = Path(__file__).parent / "data"
    map_dir.mkdir(exist_ok=True)
    
    map_name = "default_map"
    if meta and "header" in meta and meta["header"].get("mapName"):
        map_name = meta["header"]["mapName"]
    
    output_path = map_dir / f"{map_name}.json"
    
    # 转换节点和边为可序列化的字典格式
    nodes_dict = [{"id": n.id, "x": n.x, "y": n.y} for n in nodes]
    edges_dict = [
        {
            "from": e.from_node,
            "to": e.to_node,
            "bidirectional": e.bidirectional,
            "capacity": e.capacity,
        }
        for e in edges
    ]
    
    # 如果meta中包含复杂对象，也需要转换
    meta_dict = {}
    if meta:
        if "header" in meta:
            meta_dict["header"] = meta["header"]
        
        # 处理advancedPointList（如果有）
        if "advancedPointList" in meta:
            advanced_points = []
            for point in meta["advancedPointList"]:
                # 转换为字典格式
                if hasattr(point, '__dict__'):
                    point_dict = {
                        "id": point.id,
                        "type": point.type,
                        "x": point.x,
                        "y": point.y,
                    }
                else:
                    point_dict = point  # 已经是字典
                advanced_points.append(point_dict)
            meta_dict["advancedPointList"] = advanced_points
        
        # 处理advancedCurveList（如果有）
        if "advancedCurveList" in meta:
            advanced_curves = []
            for curve in meta["advancedCurveList"]:
                # 转换为字典格式
                if hasattr(curve, '__dict__'):
                    curve_dict = {
                        "id": curve.id,
                        "source": curve.source,
                        "target": curve.target,
                        "length": curve.length,
                    }
                    if curve.bezier:
                        curve_dict["bezier"] = {
                            "x1": curve.bezier.x1,
                            "y1": curve.bezier.y1,
                            "x2": curve.bezier.x2,
                            "y2": curve.bezier.y2,
                        }
                else:
                    curve_dict = curve  # 已经是字典
                advanced_curves.append(curve_dict)
            meta_dict["advancedCurveList"] = advanced_curves
        
        # 处理邻接表（如果有）
        if "adjacency" in meta:
            meta_dict["adjacency"] = meta["adjacency"]
    
    data = {
        "meta": meta_dict,
        "nodes": nodes_dict,
        "edges": edges_dict,
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 更新 map_repo 的默认路径为最新导入的地图
    global _map_repo
    _map_repo._map_path = output_path


def get_import_meta() -> dict:
    """获取最后导入的元数据"""
    return _last_import_meta or {}


def update_robokit_host(host: str) -> None:
    """
    更新Robokit机器人IP地址

    Args:
        host: 机器人IP地址
    """
    global _robokit_client, _robokit_host
    _robokit_host = host
    # 清除旧客户端，下次调用get_robokit_client时会创建新客户端
    _robokit_client = None


def get_robokit_client(host: str | None = None) -> RobokitClient:
    """
    获取Robokit客户端单例

    Args:
        host: 可选的机器人IP地址，如果提供则更新连接目标

    Returns:
        RobokitClient实例
    """
    global _robokit_client, _robokit_host

    if host:
        _robokit_host = host
        _robokit_client = None  # 强制重新创建

    if _robokit_client is None:
        _robokit_client = RobokitClient(host=_robokit_host)

    return _robokit_client
