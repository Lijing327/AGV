"""
.smap 地图导入器
将 .smap JSON 文件转换为 MapGraph 结构
"""
import json
import math
from typing import Tuple, List, Dict, Set
from app.models.map_graph import MapMeta, Node, Bezier, Edge, MapGraph


def bezier_length(p0: Tuple[float, float], p1: Tuple[float, float],
                  p2: Tuple[float, float], p3: Tuple[float, float],
                  segments: int = 50) -> float:
    """
    估算三次贝塞尔曲线的长度

    使用采样法：将曲线分割为 segments 段，计算相邻采样点的欧式距离之和

    Args:
        p0: 起点 (x, y)
        p1: 控制点1 (x, y)
        p2: 控制点2 (x, y)
        p3: 终点 (x, y)
        segments: 采样段数，默认 50

    Returns:
        曲线的估算长度
    """
    if segments <= 0:
        segments = 1

    # 三次贝塞尔公式：B(t) = (1-t)³P0 + 3(1-t)²tP1 + 3(1-t)t²P2 + t³P3
    def bezier_point(t: float) -> Tuple[float, float]:
        mt = 1 - t
        mt2 = mt * mt
        mt3 = mt2 * mt
        t2 = t * t
        t3 = t2 * t

        x = mt3 * p0[0] + 3 * mt2 * t * p1[0] + 3 * mt * t2 * p2[0] + t3 * p3[0]
        y = mt3 * p0[1] + 3 * mt2 * t * p1[1] + 3 * mt * t2 * p2[1] + t3 * p3[1]
        return (x, y)

    total_length = 0.0
    prev_point = bezier_point(0.0)

    for i in range(1, segments + 1):
        t = i / segments
        point = bezier_point(t)
        dx = point[0] - prev_point[0]
        dy = point[1] - prev_point[1]
        total_length += math.sqrt(dx * dx + dy * dy)
        prev_point = point

    return total_length


def euclidean_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """计算两点之间的欧式距离"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def import_smap(path: str) -> MapGraph:
    """
    从 .smap 文件导入地图数据

    Args:
        path: .smap 文件路径

    Returns:
        MapGraph: 包含解析后的地图数据

    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 数据格式错误、重复节点、边引用不存在的节点
    """
    # 1. 读取文件并解析 JSON
    try:
        with open(path, "r", encoding="utf-8") as f:
            smap_data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f".smap 文件不存在: {path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败: {e}")

    # 2. 解析元数据
    header = smap_data.get("header", {})
    meta = MapMeta(
        mapName=header.get("mapName", "unknown"),
        resolution=header.get("resolution", 0.02),
        version=header.get("version", "1.0.0"),
        minPos=header.get("minPos", {"x": 0.0, "y": 0.0}),
        maxPos=header.get("maxPos", {"x": 0.0, "y": 0.0}),
    )

    # 3. 解析节点（来自 advancedPointList）
    advanced_point_list = smap_data.get("advancedPointList", [])
    nodes: List[Node] = []
    node_ids: Set[str] = set()

    for point_data in advanced_point_list:
        instance_name = point_data.get("instanceName")
        if not instance_name:
            continue  # 跳过没有 instanceName 的点

        # 校验节点 ID 不重复
        if instance_name in node_ids:
            raise ValueError(f"重复的节点 ID: {instance_name}")

        pos = point_data.get("pos", {})
        node = Node(
            id=instance_name,
            type=point_data.get("className"),
            x=float(pos.get("x", 0.0)),
            y=float(pos.get("y", 0.0)),
        )
        nodes.append(node)
        node_ids.add(instance_name)

    # 4. 解析边（来自 advancedCurveList）
    advanced_curve_list = smap_data.get("advancedCurveList", [])
    edges: List[Edge] = []

    for curve_data in advanced_curve_list:
        instance_name = curve_data.get("instanceName")
        if not instance_name:
            continue  # 跳过没有 instanceName 的边

        start_pos = curve_data.get("startPos", {})
        end_pos = curve_data.get("endPos", {})
        source_id = start_pos.get("instanceName")
        target_id = end_pos.get("instanceName")

        if not source_id or not target_id:
            continue  # 跳过缺少 source/target 的边

        # 校验 source 和 target 必须存在于 nodes 中
        missing_nodes = []
        if source_id not in node_ids:
            missing_nodes.append(source_id)
        if target_id not in node_ids:
            missing_nodes.append(target_id)

        if missing_nodes:
            raise ValueError(f"边 '{instance_name}' 引用不存在的节点: {missing_nodes}")

        # 解析贝塞尔曲线（BezierPath / DegenerateBezier 均含控制点）
        bezier = None
        class_name = curve_data.get("className", "")
        if class_name in ("BezierPath", "DegenerateBezier"):
            control_pos1 = curve_data.get("controlPos1", {})
            control_pos2 = curve_data.get("controlPos2", {})
            if control_pos1 and control_pos2:
                bezier = Bezier(
                    x1=float(control_pos1.get("x", 0.0)),
                    y1=float(control_pos1.get("y", 0.0)),
                    x2=float(control_pos2.get("x", 0.0)),
                    y2=float(control_pos2.get("y", 0.0)),
                )

        edges.append(Edge(
            id=instance_name,
            source=source_id,
            target=target_id,
            bezier=bezier,
            length=None,  # 稍后计算
        ))

    # 5. 计算边的长度
    node_dict: Dict[str, Node] = {node.id: node for node in nodes}

    for edge in edges:
        source_node = node_dict[edge.source]
        target_node = node_dict[edge.target]

        if edge.bezier:
            # 使用贝塞尔曲线估算长度
            p0 = (source_node.x, source_node.y)
            p1 = (edge.bezier.x1, edge.bezier.y1)
            p2 = (edge.bezier.x2, edge.bezier.y2)
            p3 = (target_node.x, target_node.y)
            edge.length = bezier_length(p0, p1, p2, p3, segments=50)
        else:
            # 直线，使用欧式距离
            edge.length = euclidean_distance(
                source_node.x, source_node.y,
                target_node.x, target_node.y
            )

    # 6. 构建邻接表（双向）
    adjacency: Dict[str, List[Dict[str, float]]] = {node_id: [] for node_id in node_ids}

    for edge in edges:
        if edge.length is None:
            edge.length = 0.0

        # source -> target
        adjacency[edge.source].append({
            "to": edge.target,
            "edgeId": edge.id,
            "cost": edge.length,
        })

        # target -> source (双向)
        adjacency[edge.target].append({
            "to": edge.source,
            "edgeId": edge.id,
            "cost": edge.length,
        })

    return MapGraph(
        meta=meta,
        nodes=nodes,
        edges=edges,
        adjacency=adjacency,
    )
