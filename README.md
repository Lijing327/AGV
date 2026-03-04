# AGV 调度系统 Demo

基于 FastAPI 的可扩展 AGV 调度系统，支持地图可视化与模拟运行，后续可替换为真实 AGV。

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│  API 层 (FastAPI routers)                                     │
│  GET /map | GET /fleet | POST /tasks | GET /tasks             │
│  POST /sim/start | POST /sim/stop                             │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│  Adapters 层                                                  │
│  - MapRepository: 从 app/data/map_demo.json 加载地图           │
│  - SimAGVAdapter: 3 台模拟 AGV，tick 驱动移动                  │
│  - RealAGVAdapter: 占位，扩展时对接真实 AGV 硬件/中间件          │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│  Services 层                                                  │
│  - DispatchService: 选最近 idle AGV 分配任务                   │
│  - PathService: BFS 最短路径                                  │
│  - TrafficService: 路段锁（进入前占用，离开后释放）             │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│  Domain 层                                                    │
│  Node, Edge, MapData, AGV, Task, AGVStatus, TaskStatus         │
└─────────────────────────────────────────────────────────────┘
```

### 目录结构

```
AGV/
├── app/
│   ├── data/
│   │   └── map_demo.json      # 地图：nodes + edges
│   ├── domain/
│   │   └── models.py          # 纯模型
│   ├── services/
│   │   ├── dispatch_service.py
│   │   ├── path_service.py
│   │   └── traffic_service.py
│   ├── adapters/
│   │   ├── map_repo.py
│   │   ├── sim_agv_adapter.py
│   │   └── real_agv_adapter.py  # 占位
│   ├── routers/
│   │   ├── map_router.py
│   │   ├── fleet_router.py
│   │   ├── tasks_router.py
│   │   └── sim_router.py
│   └── main.py
├── static/
│   └── index.html             # 前端可视化
├── requirements.txt
└── README.md
```

## 如何运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- 前端：<http://localhost:8000/>
- API 文档：<http://localhost:8000/docs>

### 使用流程

1. 打开前端页面，查看地图与 3 台 AGV 初始位置
2. 点击「启动模拟」开始每秒 tick
3. 输入起点、终点（如 N1、N12），点击「创建」下发任务
4. 系统自动选最近 idle AGV，BFS 规划路径，按路段锁移动
5. 点击「停止模拟」暂停 tick

## 地图格式 (map_demo.json)

```json
{
  "nodes": [{"id": "N1", "x": 1, "y": 1}, ...],
  "edges": [
    {
      "from": "N1",
      "to": "N2",
      "bidirectional": true,
      "capacity": 1,
      "occupied_by": null
    }
  ]
}
```

- `bidirectional`: 双向边，同一物理路段共享锁
- `capacity` / `occupied_by`: 路段占用管理

## 现有文件说明

- `agv_simulation.html`：早期纯前端演示（无后端），可作参考
- `static/index.html`：当前使用的前端，对接 FastAPI 接口

## 如何扩展到真实 AGV

1. 实现 `RealAGVAdapter`，替代 `SimAGVAdapter`：
   - 与真实 AGV 通信（MQTT、HTTP、TCP 等）
   - 实现 `get_agvs()`、`create_task()`、`start()`、`stop()`
   - 上报 AGV 位置、状态，接收调度指令

2. 在 `app/main.py` 中切换适配器：

```python
# 使用真实 AGV
from app.adapters.real_agv_adapter import RealAGVAdapter
_sim_adapter = RealAGVAdapter(...)  # 替换 SimAGVAdapter
```

3. Domain 与 Services 层保持不变，仅替换 Adapters 即可对接真实设备。
