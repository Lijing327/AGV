"""
Robokit REST API 路由器
提供HTTP接口供前端调用Robokit机器人API
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Body

from app.deps import (
    get_robokit_client,
    dispose_robokit_client,
    _on_robot_push,
    get_robot_push_position,
    clear_robot_push_position,
)
from app.services.robokit_api import (
    RobokitAPI, RobokitError, RobokitConnectionError, RobokitTimeoutError, check_response,
    API_RELEASE_CONTROL, API_TAKE_CONTROL,
)

router = APIRouter(prefix="/robokit", tags=["robokit"])

# ==================== 连接管理 ====================

@router.post("/connect")
async def connect(
    host: str = Body(..., embed=True),
    port: Optional[int] = Body(None, embed=True)
):
    """
    连接到Robokit机器人

    Request Body:
        {
            "host": "192.168.192.5",  // 机器人IP地址
            "port": 19204              // 端口号(可选，默认19204)
        }

    Returns:
        {"success": true, "message": "连接成功"}
    """
    # 必须先关闭旧客户端，否则会泄漏 _push_listen_loop 任务导致异常与连接无响应
    await dispose_robokit_client()
    clear_robot_push_position()
    client = get_robokit_client(host)
    try:
        success = await client.connect(port)
        if success:
            # 启动机器人推送监听（端口 19301），用于地图实时位置
            push_ok = await client.start_push_listener(on_position=_on_robot_push)
            if push_ok:
                return {"success": True, "message": "连接成功"}
            return {
                "success": True,
                "message": "控制端口已连接，推送端口 19301 未连通（地图实时位姿可能不更新）",
                "push_listener": False,
            }
        else:
            return {"success": False, "message": "连接失败"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/disconnect")
async def disconnect():
    """
    断开与Robokit机器人的连接

    Returns:
        {"success": true}
    """
    client = get_robokit_client()
    try:
        await client.close()
        clear_robot_push_position()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_status():
    """
    获取连接状态

    Returns:
        {"connected": true, "host": "192.168.192.5"}
    """
    client = get_robokit_client()
    return {
        "connected": client.is_connected(),
        "host": client.host
    }


@router.get("/position")
async def get_position():
    """
    获取机器人实时位置（来自推送 API 19301）

    连接机器人后，后端会持续接收推送数据，此接口返回最新位置。
    用于在地图上实时显示机器人位置。

    Returns:
        {"x": 1.2, "y": 3.4, "angle": 0.5, "vehicle_id": "AGV-001", ...}
    """
    return get_robot_push_position()

# ==================== 机器人状态 API ====================

@router.get("/robot/info")
async def get_robot_info():
    """
    查询机器人信息

    Returns:
        机器人信息，包含id, version, model, dsp_version等
    """
    client = get_robokit_client()
    try:
        result = await client.call_status(1000)
        check_response(result)
        return result
    except RobokitConnectionError:
        raise HTTPException(status_code=503, detail="无法连接到机器人")
    except RobokitTimeoutError:
        raise HTTPException(status_code=504, detail="请求超时")
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/robot/run-info")
async def get_run_info():
    """
    查询机器人运行信息

    Returns:
        {
            "odo": 146.34,              // 累计行驶里程(m)
            "today_odo": 50.0,         // 今日累计里程(m)
            "time": 794297,            // 本次运行时间(ms)
            "total_time": 116606929,    // 累计运行时间(ms)
            "controller_temp": 30,       // 控制器温度(℃)
            "controller_humi": 50,       // 控制器湿度(%)
            "controller_voltage": 24     // 控制器电压(V)
        }
    """
    client = get_robokit_client()
    try:
        result = await client.call_status(1002)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/robot/location")
async def get_location():
    """
    查询机器人位置

    Returns:
        {
            "x": 3.5069,               // x坐标(m)
            "y": 0.0687,               // y坐标(m)
            "angle": -0.0064,          // 角度(rad)
            "confidence": 0.637,        // 定位置信度[0,1]
            "current_station": "LM1",   // 当前站点ID
            "last_station": "LM2",      // 上一个站点ID
            "loc_method": 0             // 定位方式
        }
    """
    client = get_robokit_client()
    try:
        result = await client.call_status(1004)
        check_response(result)
        return result
    except (TimeoutError, ConnectionError) as e:
        raise HTTPException(status_code=504 if isinstance(e, TimeoutError) else 503, detail=str(e))
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/robot/speed")
async def get_speed():
    """
    查询机器人速度

    Returns:
        {
            "vx": 0.5,                 // x方向速度(m/s)
            "vy": 0,                   // y方向速度(m/s)
            "w": 0.1,                  // 角速度(rad/s)
            "steer": 0,                // 舵轮角度(rad)
            "spin": 0,                 // 托盘角度(rad)
            "r_vx": 0.5,              // 接收的x速度
            "r_vy": 0,                 // 接收的y速度
            "r_w": 0.1,                // 接收的角速度
            "is_stop": false            // 是否静止
        }
    """
    client = get_robokit_client()
    try:
        result = await client.call_status(1005)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.get("/robot/blocked")
async def get_blocked_status():
    """
    查询机器人被阻挡状态

    Returns:
        {
            "blocked": false,           // 是否被阻挡
            "block_reason": 0,          // 阻挡原因
            "block_x": 15.2845,         // 障碍物x坐标
            "block_y": -8.1834,        // 障碍物y坐标
            "slowed": false             // 是否减速
        }
    """
    client = get_robokit_client()
    try:
        result = await client.call_status(1006)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/robot/battery")
async def get_battery(simple: bool = Query(False, description="是否只返回简单数据(仅电量)")):
    """
    查询机器人电池状态

    Query参数:
        simple: 是否只返回简单数据

    Returns:
        {
            "battery_level": 0.87,      // 电量[0,1]
            "battery_temp": 35,         // 电池温度(℃)
            "charging": false,          // 是否充电
            "voltage": 24.5,           // 电压(V)
            "current": 2,              // 电流(A)
            "max_charge_voltage": 48,    // 最大充电电压
            "max_charge_current": 5,     // 最大充电电流
            "battery_cycle": 9          // 电池循环次数
        }
    """
    client = get_robokit_client()
    try:
        params = {"simple": True} if simple else None
        result = await client.call_status(1007, params)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/robot/emergency")
async def get_emergency_status():
    """
    查询机器人急停状态

    Returns:
        {
            "emergency": false,         // 急停按钮状态
            "driver_emc": false,        // 驱动器急停
            "electric": false,          // 继电器状态
            "soft_emc": false          // 软急停
        }
    """
    client = get_robokit_client()
    try:
        result = await client.call_status(1012)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.get("/robot/io")
async def get_io_status():
    """
    查询机器人I/O状态

    Returns:
        {
            "DI": [...],               // 数字输入数组
            "DO": [...]                // 数字输出数组
        }
    """
    client = get_robokit_client()
    try:
        result = await client.call_status(1013)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.get("/robot/motor")
async def get_motor_status(motor_names: Optional[str] = Query(None, description="电机名称，多个用逗号分隔")):
    """
    查询电机状态信息

    Query参数:
        motor_names: 电机名称列表，如 "motor1,motor2"

    Returns:
        {
            "motor_info": [...]
        }
    """
    client = get_robokit_client()
    try:
        params = {"motor_names": motor_names.split(',') if motor_names else None}
        result = await client.call_status(1040, params)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/robot/laser")
async def get_laser_data():
    """
    查询机器人激光点云数据

    Returns:
        {
            "lasers": [...]
        }
    """
    client = get_robokit_client()
    try:
        result = await client.call_status(1009)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/robot/area")
async def get_area_info():
    """
    查询机器人当前所在区域

    Returns:
        {
            "area_ids": ["1", "2"]
        }
    """
    client = get_robokit_client()
    try:
        result = await client.call_status(1011)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/robot/slams")
async def get_slam_status():
    """
    查询机器人当前的扫图状态

    Returns:
        {
            "slam_status": 0
        }
    """
    client = get_robokit_client()
    try:
        result = await client.call_status(1025)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/robot/encoder")
async def get_encoder_status():
    """
    查询编码器脉冲值

    Returns:
        {
            "encoder": [],
            "motor_encoder": []
        }
    """
    client = get_robokit_client()
    try:
        result = await client.call_status(1018)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/robot/modbus")
async def query_modbus(registers: list = Body(..., embed=True)):
    """
    查询modbus数据

    Request Body:
        {
            "registers": [121, 122]  // 寄存器地址列表
        }

    Returns:
        {
            "4x": {"121": 1, "122": 2}
        }
    """
    client = get_robokit_client()
    try:
        result = await client.call_status(1071, {"4x": registers})
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/robot/bins")
async def get_bins_status():
    """
    查询机器人能看到的库位状态信息

    Returns:
        {
            "header": {...},
            "bins": [{"binId": "BIN-1", "filled": false, "status": 1}]
        }
    """
    client = get_robokit_client()
    try:
        result = await client.call_status(1803)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== 机器人控制 API ====================

@router.post("/control/relocate")
async def relocate(
    x: float = Body(..., embed=True),
    y: float = Body(..., embed=True),
    angle: float = Body(0, embed=True)
):
    """
    重定位机器人

    Request Body:
        {
            "x": 10.0,           // x坐标(m)
            "y": 3.0,            // y坐标(m)
            "angle": 0            // 角度(rad)
        }

    Returns:
        {"ret_code": 0}
    """
    client = get_robokit_client()
    try:
        result = await client.call_control(2002, {"x": x, "y": y, "angle": angle})
        check_response(result)
        return result
    except (TimeoutError, ConnectionError) as e:
        raise HTTPException(status_code=504 if isinstance(e, TimeoutError) else 503, detail=str(e))
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/control/confirm-location")
async def confirm_location():
    """
    确认定位正确 (API 2003)

    Returns:
        {"ret_code": 0}
    """
    client = get_robokit_client()
    try:
        result = await client.call_control(2003)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/control/cancel-relocate")
async def cancel_relocate():
    """
    取消重定位 (API 2004，端口19205)
    """
    client = get_robokit_client()
    try:
        result = await client.call_control(2004)
        check_response(result)
        return result
    except (TimeoutError, ConnectionError) as e:
        raise HTTPException(status_code=504 if isinstance(e, TimeoutError) else 503, detail=str(e))
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/control/move")
async def move_by_velocity(
    vx: float = Body(..., embed=True),
    vy: float = Body(0, embed=True),
    w: float = Body(0, embed=True)
):
    """
    开环运动 / 速度控制 (API 2010，端口19205)
    原 2004 在部分文档中为「取消重定位」，开环运动为 2010。

    Request Body:
        {
            "vx": 0.5,            // x方向速度(m/s)
            "vy": 0,              // y方向速度(m/s)
            "w": 0.1              // 角速度(rad/s)
        }

    Returns:
        {"ret_code": 0}
    """
    client = get_robokit_client()
    try:
        result = await client.call_control(2010, {"vx": vx, "vy": vy, "w": w})
        check_response(result)
        return result
    except (TimeoutError, ConnectionError) as e:
        raise HTTPException(status_code=504 if isinstance(e, TimeoutError) else 503, detail=str(e))
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/control/stop")
async def stop_movement():
    """
    停止开环运动 (API 2000，端口19205)
    """
    client = get_robokit_client()
    try:
        result = await client.call_control(2000)
        check_response(result)
        return result
    except (TimeoutError, ConnectionError) as e:
        raise HTTPException(status_code=504 if isinstance(e, TimeoutError) else 503, detail=str(e))
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/control/release")
async def release_control():
    """
    释放控制权 - 将控制权交还给调度系统，端口19207
    """
    client = get_robokit_client()
    try:
        result = await client.call_config(API_RELEASE_CONTROL)
        check_response(result)
        return result
    except (TimeoutError, ConnectionError) as e:
        raise HTTPException(status_code=504 if isinstance(e, TimeoutError) else 503, detail=str(e))
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/control/take")
async def take_control(nick_name: str = Body(default="agv-web", embed=True)):
    """
    抢占控制权 - 从调度系统夺取控制权，端口19207
    遇 40012/40020 时需先调用此接口
    需传入 nick_name（控制权抢占者名称），默认 agv-web
    """
    client = get_robokit_client()
    try:
        result = await client.call_config(API_TAKE_CONTROL, {"nick_name": nick_name})
        check_response(result)
        return result
    except (TimeoutError, ConnectionError) as e:
        raise HTTPException(status_code=504 if isinstance(e, TimeoutError) else 503, detail=str(e))
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/control/emergency-stop")
async def emergency_stop():
    """
    急停

    Returns:
        {"ret_code": 0}
    """
    client = get_robokit_client()
    try:
        result = await client.call_control(2006)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/navigation/path")
async def path_navigation(payload: dict = Body(...)):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="请求体须为 JSON 对象")
    source_id = str(payload.get("source_id") or "").strip()
    target_raw = payload.get("target_id")
    if target_raw is None:
        target_raw = payload.get("id")
    id_val = str(target_raw or "").strip()
    if not source_id or not id_val:
        raise HTTPException(status_code=400, detail="缺少 source_id 与 target_id（或 id）")
    client = get_robokit_client()
    body = {"source_id": source_id, "id": id_val}
    skip = frozenset({"source_id", "target_id", "id"})
    for k, v in payload.items():
        if k in skip or v is None:
            continue
        body[k] = v
    try:
        result = await client.call_navigation(3051, body)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/navigation/specified-path")
async def specified_path_navigation(body: dict = Body(..., embed=False)):
    move_task_list = body.get("move_task_list")
    if not move_task_list or not isinstance(move_task_list, list):
        raise HTTPException(status_code=400, detail="缺少 move_task_list 或格式错误，须为数组")
    for i, item in enumerate(move_task_list):
        if not isinstance(item, dict):
            raise HTTPException(status_code=400, detail=f"move_task_list[{i}] 须为对象")
        if not item.get("id") or not item.get("source_id") or not item.get("task_id"):
            raise HTTPException(
                status_code=400,
                detail=f"move_task_list[{i}] 须包含 id、source_id、task_id",
            )
    client = get_robokit_client()
    try:
        result = await client.call_navigation(3066, {"move_task_list": move_task_list})
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/navigation/translate")
async def translate(
    dist: float = Body(..., embed=True),
    vx: float = Body(None, embed=True),
    vy: float = Body(None, embed=True),
    mode: int = Body(0, embed=True),
):
    client = get_robokit_client()
    try:
        params = {"dist": dist, "mode": mode}
        if vx is not None:
            params["vx"] = vx
        if vy is not None:
            params["vy"] = vy
        result = await client.call_navigation(3055, params)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/navigation/stop")
async def stop_navigation():
    client = get_robokit_client()
    try:
        result = await client.call_navigation(3052)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/navigation/pause")
async def pause_navigation():
    client = get_robokit_client()
    try:
        result = await client.call_navigation(3001, None)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/navigation/resume")
async def resume_navigation():
    client = get_robokit_client()
    try:
        result = await client.call_navigation(3002, None)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/navigation/cancel")
async def cancel_navigation():
    client = get_robokit_client()
    try:
        result = await client.call_navigation(3003, None)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/navigation/target-path")
async def get_target_path(body: dict = Body(None, embed=False)):
    client = get_robokit_client()
    try:
        result = await client.call_navigation(3053, body or {})
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/navigation/turn")
async def turn(
    move_angle: float = Body(..., embed=True),
    speed_w: float = Body(None, embed=True),
    loc_mode: int = Body(0, embed=True),
):
    client = get_robokit_client()
    try:
        params = {"move_angle": move_angle, "loc_mode": loc_mode}
        if speed_w is not None:
            params["speed_w"] = speed_w
        result = await client.call_navigation(3056, params)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/navigation/spin")
async def spin(body: dict = Body(..., embed=False)):
    client = get_robokit_client()
    try:
        result = await client.call_navigation(3057, body)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/navigation/circular")
async def circular(body: dict = Body(..., embed=False)):
    client = get_robokit_client()
    try:
        result = await client.call_navigation(3058, body)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/navigation/path-enable")
async def path_enable(body: dict = Body(..., embed=False)):
    client = get_robokit_client()
    try:
        result = await client.call_navigation(3059, body)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/navigation/clear-target-list")
async def clear_target_list():
    client = get_robokit_client()
    try:
        result = await client.call_navigation(3067, None)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/navigation/clear-by-task-id")
async def clear_by_task_id(task_id: str = Body(..., embed=True)):
    client = get_robokit_client()
    try:
        result = await client.call_navigation(3068, {"task_id": task_id})
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/navigation/tasklist-status")
async def get_tasklist_status():
    client = get_robokit_client()
    try:
        result = await client.call_navigation(3101, None)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/navigation/tasklist-list")
async def get_tasklist_list():
    client = get_robokit_client()
    try:
        result = await client.call_navigation(3115, None)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/navigation/tasklist-execute")
async def execute_tasklist(name: str = Body(..., embed=True)):
    client = get_robokit_client()
    try:
        result = await client.call_navigation(3106, {"name": name})
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/navigation/move-to")
async def move_to(
    target: str = Body(..., embed=True),
    target_type: str = Body("point", embed=True)
):
    client = get_robokit_client()
    try:
        result = await client.call_navigation(3061, {"target": target, "type": target_type})
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/navigation/status")
async def get_navigation_status():
    """
    查询导航任务状态（机器人状态口 API **1020**，响应 11020）。

    task_status（与项目根目录 API接口.docx 一致）：
    0=NONE，1=WAITING，2=RUNNING，3=SUSPENDED，4=COMPLETED，5=FAILED，6=CANCELED。
    simple=true 时响应可仅含关键字段，例如 {"task_status": 4}。
    分段流程可在 **task_status=4（COMPLETED）** 后再下发后续导航（如一键搬运第二段 3051）。
    """
    client = get_robokit_client()
    try:
        result = await client.call_status(1020)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/navigation/location-status")
async def get_location_status():
    client = get_robokit_client()
    try:
        result = await client.call_status(1021)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== 机器人配置 API ====================

@router.post("/config/set-mode")
async def set_robot_mode(mode: int = Body(..., embed=True)):
    """
    切换运行模式 (API 4000)

    Request Body:
        {"mode": 0}  # 0=手动模式, 1=自动模式

    手动模式: 可执行开环运动(2010)、重定位(2002)等控制指令
    自动模式: 可执行任务API(导航、去目标点等)
    错误40020(control is preempted)表示当前为自动模式，需先切换为手动模式
    """
    client = get_robokit_client()
    try:
        result = await client.call_config(4000, {"mode": mode})
        check_response(result)
        return result
    except (TimeoutError, ConnectionError) as e:
        raise HTTPException(status_code=504 if isinstance(e, TimeoutError) else 503, detail=str(e))
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/config/maps")
async def get_map_list():
    """
    获取地图列表

    Returns:
        {
            "maps": ["map1", "map2"]
        }
    """
    client = get_robokit_client()
    try:
        result = await client.call_config(4004)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/config/set-map")
async def set_current_map(map_name: str = Body(..., embed=True)):
    """
    设置当前地图

    Request Body:
        {
            "map_name": "map1"
        }

    Returns:
        {"ret_code": 0}
    """
    client = get_robokit_client()
    try:
        # 文档中 4005 为抢占控制权；若设备要求不同编号请改为对应 API
        result = await client.call_config(4005, {"map_name": map_name})
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/config/download-map")
async def download_map(map_name: str = Body(..., embed=True)):
    """
    下载地图

    Request Body:
        {
            "map_name": "map1"
        }

    Returns:
        地图数据
    """
    client = get_robokit_client()
    try:
        result = await client.call_config(4001, {"map_name": map_name})
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== 通用API调用 ====================

@router.post("/call")
async def call_api(
    port: int = Body(..., embed=True, description="端口号: 19204状态, 19205控制, 19206导航, 19207配置, 19210其他API"),
    msg_type: int = Body(..., embed=True, description="API编号/消息类型"),
    params: dict = Body(None, embed=True, description="请求参数")
):
    """
    通用API调用接口

    Request Body:
        {
            "port": 19204,          // 端口号
            "msg_type": 1000,        // API编号
            "params": {}             // 参数(可选)
        }

    Returns:
        API响应数据
    """
    client = get_robokit_client()
    try:
        result = await client.call(port, msg_type, params)
        check_response(result)
        return result
    except RobokitError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== 错误码参考 ====================

@router.get("/error-codes")
async def get_error_codes():
    """
    获取API错误码参考

    Returns:
        错误码说明字典
    """
    return {
        "error_codes": {
            0: "成功",
            40000: "请求不可用",
            40001: "必要参数缺失",
            40002: "参数类型错误",
            40004: "运行模式错误",
            40009: "API 已弃用(如 3.3.4+ 弃用模式切换 4000，抢占控制后可直接执行移动)",
            40012: "调度系统控制中(需先抢占控制)",
            40016: "急停状态中",
            40020: "控制权被抢占(需先抢占控制)",
            40101: "机器人被其他设备锁定(需在该设备上释放)",
            40400: "获取控制权错误",
            40401: "释放控制权错误",
            60000: "错误的报文类型(端口与API编号不匹配)",
            60001: "未知的报文类型",
            2: "设备忙",
            3: "设备未就绪",
            4: "操作失败",
            5: "超时",
            6: "连接失败",
            7: "认证失败",
            8: "权限不足",
            9: "地图不存在",
            10: "路径不存在",
            11: "定位失败",
            12: "导航失败",
            100: "内部错误"
        }
    }
