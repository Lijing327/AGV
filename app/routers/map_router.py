"""
地图 API
"""
import json
import tempfile
import time
from dataclasses import asdict
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException

from app.deps import get_map_repo, set_map_data, get_import_meta
from app.domain.models import Node, Edge, MapData
from app.services.path_service import PathService
from app.services.smap_importer import import_smap

router = APIRouter(prefix="/map")


@router.get("")
def get_map():
    """获取地图（nodes + edges + 点云 + 特征线）"""
    map_data = get_map_repo().get_map()
    import_meta = get_import_meta()

    # 构建 advancedPointList 的 instanceName -> 原始数据 映射
    adv_points = import_meta.get("advancedPointList") or []
    adv_point_map = {}
    for ap in adv_points:
        name = ap.get("instanceName") if isinstance(ap, dict) else getattr(ap, "instanceName", None)
        if name:
            adv_point_map[name] = ap

    # 节点响应：带上 type 和 dir 信息
    nodes_resp = []
    for n in map_data.nodes:
        node_dict = {"id": n.id, "x": n.x, "y": n.y}
        ap = adv_point_map.get(n.id)
        if ap:
            if isinstance(ap, dict):
                node_dict["type"] = ap.get("className", "")
                node_dict["dir"] = ap.get("dir", 0)
            else:
                node_dict["type"] = getattr(ap, "className", getattr(ap, "type", ""))
                node_dict["dir"] = getattr(ap, "dir", 0)
        nodes_resp.append(node_dict)

    response = {
        "nodes": nodes_resp,
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
        "imported_data": {
            "header": import_meta.get("header") or {},
            "advancedPointList": adv_points,
            "advancedCurveList": import_meta.get("advancedCurveList"),
        },
    }

    if import_meta.get("adjacency"):
        response["adjacency"] = import_meta.get("adjacency")

    return response


@router.post("/plan-path")
def plan_path(body: Annotated[dict, Body()]):
    """
    根据起点和终点自动规划最优路径，并生成指定路径(3066)所需的 move_task_list 参数。

    请求体: {"source_id": "LM1", "target_id": "AP1"}
    返回: {"path": ["LM1", "LM2", "AP1"], "move_task_list": [...]}

    使用 BFS 算法计算最短路径（最少经过节点数），路径段首尾相连。
    """
    source_id = (body.get("source_id") or "").strip()
    target_id = (body.get("target_id") or "").strip()
    if not source_id or not target_id:
        raise HTTPException(status_code=400, detail="请提供 source_id 和 target_id")

    map_data = get_map_repo().get_map()
    path_service = PathService(map_data)
    node_ids = path_service.find_path(source_id, target_id)

    if not node_ids:
        raise HTTPException(
            status_code=404,
            detail=f"无法找到从 {source_id} 到 {target_id} 的路径，请确认两节点在地图中存在且连通",
        )

    # 构建完整路径：起点 + 中间节点
    full_path = [source_id] + node_ids

    # 将路径转换为 move_task_list 格式，每段 source_id -> id 首尾相连
    move_task_list = []
    base_task_id = int(time.time() * 1000) % 100000000
    for i in range(len(full_path) - 1):
        seg_source = full_path[i]
        seg_target = full_path[i + 1]
        task_id = str(base_task_id + i)
        move_task_list.append({
            "source_id": seg_source,
            "id": seg_target,
            "task_id": task_id,
        })

    return {"path": full_path, "move_task_list": move_task_list}


@router.get("/advanced")
def get_advanced_data():
    """获取最后导入的原始 advanced 数据"""
    return get_import_meta()


@router.post("/import-file")
def import_map_file(body: Annotated[dict, Body()]):
    """从服务器本地文件路径导入 .smap 地图（适用于大文件，避免前端传输 8MB 数据）

    Args:
        body: {"path": "d:/00-Project/AGV/20260310.smap"}
    """
    file_path = body.get("path", "")
    if not file_path:
        return {"error": "缺少 path 参数", "success": False}

    p = Path(file_path)
    if not p.exists():
        return {"error": f"文件不存在: {file_path}", "success": False}
    if not p.suffix.lower() in ('.smap', '.json'):
        return {"error": "仅支持 .smap / .json 文件", "success": False}

    try:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return {"error": f"文件读取失败: {e}", "success": False}

    return import_map(data)


@router.post("/import")
def import_map(data: Annotated[dict, Body()]):
    """导入地图（.smap 格式）

    识别 advancedPointList（节点）和 advancedCurveList（边）数据

    Args:
        data: 地图数据，包含 header、advancedPointList、advancedCurveList 或 normalPosList
    """
    # 检查是否有 advancedPointList 和 advancedCurveList
    has_advanced_points = "advancedPointList" in data and data.get("advancedPointList")
    has_advanced_curves = "advancedCurveList" in data and data.get("advancedCurveList")

    if has_advanced_points and has_advanced_curves:
        # 使用 smap_importer 直接解析 .smap 数据
        # 保存到临时文件以使用 import_smap 函数
        with tempfile.NamedTemporaryFile(mode='w', suffix='.smap', delete=False, encoding='utf-8') as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            map_graph = import_smap(temp_path)

            # 转换为 MapData 格式
            nodes = [
                Node(id=n.id, x=n.x, y=n.y)
                for n in map_graph.nodes
            ]

            edges = []
            for edge in map_graph.edges:
                edges.append(Edge(
                    from_node=edge.source,
                    to_node=edge.target,
                    bidirectional=True,
                    capacity=1,
                    occupied_by=None,
                ))

            # 保存到数据目录
            map_dir = Path(__file__).parent.parent / "data"
            map_dir.mkdir(exist_ok=True)
            output_path = map_dir / f"{map_graph.meta.mapName}.json"

            # 保存为标准格式
            output_data = {
                "meta": asdict(map_graph.meta),
                "nodes": [{"id": n.id, "x": n.x, "y": n.y} for n in nodes],
                "edges": [
                    {
                        "from": e.from_node,
                        "to": e.to_node,
                        "bidirectional": e.bidirectional,
                        "capacity": e.capacity,
                    }
                    for e in edges
                ],
                "adjacency": map_graph.adjacency,
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            # 更新 map_repo 的数据（包含元数据）
            set_map_data(
                nodes, edges,
                meta={
                    "header": asdict(map_graph.meta),
                    "advancedPointList": data.get("advancedPointList"),
                    "advancedCurveList": data.get("advancedCurveList"),
                    "advancedLineList": data.get("advancedLineList"),
                }
            )

            return {
                "success": True,
                "mapName": map_graph.meta.mapName,
                "mapType": "2D-Map",
                "nodeCount": len(nodes),
                "edgeCount": len(edges),
                "resolution": map_graph.meta.resolution,
                "version": map_graph.meta.version,
                "advancedPointListCount": len(data.get("advancedPointList", [])),
                "advancedCurveListCount": len(data.get("advancedCurveList", [])),
            }

        finally:
            # 清理临时文件
            import os
            try:
                os.unlink(temp_path)
            except:
                pass

    # 兼容旧格式（normalPosList）
    header = data.get("header", {})
    points = data.get("normalPosList", [])

    # 支持应用内部格式（nodes + edges）
    if not points and "nodes" in data and "edges" in data:
        # 这是应用保存的格式，直接使用
        nodes = [
            Node(id=n["id"], x=float(n["x"]), y=float(n["y"]))
            for n in data["nodes"]
        ]
        edges = []
        for e in data["edges"]:
            edges.append(Edge(
                from_node=e["from"],
                to_node=e["to"],
                bidirectional=e.get("bidirectional", True),
                capacity=e.get("capacity", 1),
                occupied_by=e.get("occupied_by"),
            ))

        # 准备元数据
        meta = data.get("meta", {})
        combined_meta = meta or header or {}
        # 确保 mapName 存在
        if "mapName" not in combined_meta:
            combined_meta["mapName"] = "imported"

        # 更新地图数据（包含元数据）
        set_map_data(
            nodes, edges,
            meta={
                "header": combined_meta,
            }
        )

        return {
            "success": True,
            "mapName": combined_meta.get("mapName"),
            "mapType": "internal",
            "nodeCount": len(nodes),
            "edgeCount": len(edges),
            "resolution": combined_meta.get("resolution"),
            "version": combined_meta.get("version"),
        }

    if not points:
        return {"error": "normalPosList or advancedPointList or nodes is empty", "success": False}

    # 将点转换为 Node
    nodes = [
        Node(id=f"P{i}", x=float(p["x"]), y=float(p["y"]))
        for i, p in enumerate(points)
    ]

    # 按索引顺序连接相邻点
    edges = []
    for i in range(len(nodes) - 1):
        edges.append(Edge(
            from_node=nodes[i].id,
            to_node=nodes[i + 1].id,
            bidirectional=True,
            capacity=1,
            occupied_by=None,
        ))

    # 更新地图数据（包含元数据）
    # 确保 mapName 存在
    if "mapName" not in header:
        header["mapName"] = "unnamed"

    set_map_data(
        nodes, edges,
        meta={
            "header": header,
        }
    )

    return {
        "success": True,
        "mapName": header.get("mapName"),
        "mapType": header.get("mapType", "unknown"),
        "nodeCount": len(nodes),
        "edgeCount": len(edges),
        "resolution": header.get("resolution"),
    }
