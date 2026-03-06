# AGV 调度系统 Demo

基于 FastAPI 的可扩展 AGV 调度系统，支持地图可视化与模拟运行，**前后端分离**，后续可替换为真实 AGV。

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│  前端 (frontend/) - Vue 3 + Vite                              │
│  开发时 Vite proxy 转发 /api，生产环境配置 VITE_API_BASE        │
└─────────────────────────────────────────────────────────────┘
                              │ HTTP
┌─────────────────────────────────────────────────────────────┐
│  API 层 (FastAPI routers) - 统一 /api 前缀                      │
│  GET /api/map | GET /api/fleet | POST /api/tasks | GET /api/tasks │
│  POST /api/sim/start | POST /api/sim/stop                     │
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
├── app/                       # 后端
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
├── frontend/                  # 前端（Vue 3 + Vite）
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── api.js
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── static/                    # 旧版（已弃用，可删除）
├── requirements.txt
└── README.md
```

## 如何运行（前后端分离）

**终端 1 - 启动后端：**
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**终端 2 - 启动前端：**
```bash
cd frontend
npm install
npm run dev
```

- 前端：<http://localhost:3000/>（Vite 自动代理 /api 到后端）
- 后端 API：<http://localhost:8000/api/...>
- API 文档：<http://localhost:8000/docs>

> 生产环境：配置 `frontend/.env` 中的 `VITE_API_BASE` 为实际后端地址，或通过 nginx 反向代理使用相对路径 `/api`。

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

- `frontend/`：Vue 3 + Vite 前端，开发时自动代理 /api 到后端
- `agv_simulation.html`：早期纯前端演示（无后端），可作参考
- `static/`：旧版 HTML 前端（已弃用，可删除）

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
