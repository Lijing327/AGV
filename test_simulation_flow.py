#!/usr/bin/env python3
"""
测试导入地图后小车模拟执行任务的完整流程
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path

# 添加项目根目录到系统路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.adapters.map_repo import MapRepository
from app.adapters.sim_agv_adapter import SimAGVAdapter
from app.services.smap_importer import import_smap
from app.deps import set_map_data, get_sim_adapter, get_map_repo


async def test_simulation_flow():
    """测试模拟流程的完整步骤"""
    print("=" * 60)
    print("开始测试导入地图后小车模拟执行任务的完整流程")
    print("=" * 60)
    
    # 1. 导入地图文件
    print("\n1. 导入地图文件...")
    smap_path = project_root / "assets" / "demo_advanced.smap"
    if not smap_path.exists():
        print(f"找不到地图文件: {smap_path}")
        # 使用测试地图
        smap_path = project_root / "assets" / "test_map.smap"
        if not smap_path.exists():
            print("找不到测试地图文件，创建简单测试地图...")
            create_simple_test_map(project_root / "assets" / "test_map.smap")
            smap_path = project_root / "assets" / "test_map.smap"
    
    try:
        # 导入地图
        map_graph = import_smap(str(smap_path))
        print(f"成功导入地图: {map_graph.meta.mapName}")
        print(f"  - 节点数: {len(map_graph.nodes)}")
        print(f"  - 边数: {len(map_graph.edges)}")
        
        # 转换为 MapData 格式
        from app.domain.models import Node, Edge
        nodes = [Node(id=n.id, x=n.x, y=n.y) for n in map_graph.nodes]
        edges = []
        for edge in map_graph.edges:
            edges.append(Edge(
                from_node=edge.source,
                to_node=edge.target,
                bidirectional=True,
                capacity=1,
                occupied_by=None,
            ))
        
        # 设置地图数据
        set_map_data(
            nodes, edges,
            meta={
                "header": {
                    "mapName": map_graph.meta.mapName,
                    "resolution": map_graph.meta.resolution,
                    "version": map_graph.meta.version,
                },
                "advancedPointList": map_graph.nodes,
                "advancedCurveList": map_graph.edges,
                "adjacency": map_graph.adjacency,
            }
        )
        print("地图数据已设置")
        
        # 2. 初始化模拟适配器
        print("\n2. 初始化模拟适配器...")
        adapter = get_sim_adapter()
        agvs = adapter.get_agvs()
        print(f"创建了 {len(agvs)} 台 AGV:")
        for agv in agvs:
            print(f"  - {agv.id}: 初始位置 {agv.current_node}, 状态 {agv.status.value}, 颜色 {agv.color}")
        
        # 3. 创建测试任务
        print("\n3. 创建测试任务...")
        map_data = get_map_repo().get_map()
        node_ids = [n.id for n in map_data.nodes]
        
        if len(node_ids) < 2:
            print("节点数不足，无法创建任务")
            return
        
        # 选择第一个和最后一个节点作为起点和终点
        from_node = node_ids[0]
        to_node = node_ids[-1]
        
        print(f"创建任务: {from_node} -> {to_node}")
        task = adapter.create_task(from_node, to_node)
        if task:
            print(f"任务创建成功: {task.id}")
            print(f"  - 起点: {task.from_node}")
            print(f"  - 终点: {task.to_node}")
            print(f"  - 状态: {task.status.value}")
            print(f"  - 分配的AGV: {task.assigned_agv_id}")
        else:
            print("任务创建失败")
            return
        
        # 4. 启动模拟
        print("\n4. 启动模拟...")
        adapter.start()
        print("模拟已启动，开始执行任务...")
        
        # 5. 监控模拟执行
        print("\n5. 监控模拟执行...")
        max_steps = 30
        task_completed = False
        
        for step in range(max_steps):
            print(f"\n--- 步骤 {step + 1} ---")
            
            # 检查任务状态
            tasks = adapter.get_tasks()
            current_task = next((t for t in tasks if t.id == task.id), None)
            if current_task:
                print(f"任务状态: {current_task.status.value}")
                
                if current_task.status.value == "completed":
                    print("任务已完成!")
                    task_completed = True
                    break
            
            # 检查AGV状态
            agvs = adapter.get_agvs()
            for agv in agvs:
                print(f"  {agv.id}: 位置 {agv.current_node}, 状态 {agv.status.value}")
                if agv.path:
                    print(f"    路径: {' -> '.join(agv.path)}")
            
            # 等待1秒
            await asyncio.sleep(1)
        
        # 6. 停止模拟
        print("\n6. 停止模拟...")
        adapter.stop()
        print("模拟已停止")
        
        # 7. 测试结果
        print("\n7. 测试结果...")
        if task_completed:
            print("[成功] 测试成功: 任务已完成")
        else:
            print("[失败] 测试失败: 任务未在预期时间内完成")
        
        print("\n测试流程完成!")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


def create_simple_test_map(file_path):
    """创建简单的测试地图文件"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    test_data = {
        "header": {
            "mapType": "2D-Map",
            "mapName": "test_map",
            "minPos": {"x": 0.0, "y": 0.0},
            "maxPos": {"x": 10.0, "y": 10.0},
            "resolution": 0.02,
            "version": "1.0.6"
        },
        "normalPosList": [],
        "advancedPointList": [
            {"instanceName": "R1", "className": "Station", "pos": {"x": 1.0, "y": 1.0}},
            {"instanceName": "C1", "className": "Conveyor", "pos": {"x": 5.0, "y": 1.0}},
            {"instanceName": "C2", "className": "Conveyor", "pos": {"x": 5.0, "y": 5.0}},
            {"instanceName": "D1", "className": "Delivery", "pos": {"x": 1.0, "y": 5.0}},
        ],
        "advancedCurveList": [
            {
                "instanceName": "edge_R1_C1",
                "className": "NormalPath",
                "startPos": {"instanceName": "R1"},
                "endPos": {"instanceName": "C1"}
            },
            {
                "instanceName": "edge_C1_C2",
                "className": "BezierPath",
                "startPos": {"instanceName": "C1"},
                "endPos": {"instanceName": "C2"},
                "controlPos1": {"x": 7.0, "y": 1.0},
                "controlPos2": {"x": 7.0, "y": 5.0}
            },
            {
                "instanceName": "edge_C2_D1",
                "className": "NormalPath",
                "startPos": {"instanceName": "C2"},
                "endPos": {"instanceName": "D1"}
            }
        ]
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    print(f"已创建测试地图文件: {file_path}")


if __name__ == "__main__":
    asyncio.run(test_simulation_flow())