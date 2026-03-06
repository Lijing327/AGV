"""
Robokit API 服务封装
提供友好的API接口，支持调用各种Robokit机器人API
"""
from typing import Optional, Any
from dataclasses import dataclass

from app.adapters.robokit_client import (
    RobokitClient,
    PORT_STATUS,
    PORT_CONTROL,
    PORT_NAVIGATION,
    PORT_CONFIG,
    PORT_OTHER,
)

# 控制权 API 编号 (端口19207 配置API)
API_TAKE_CONTROL = 4005     # 抢占控制权 robot_config_lock_req
API_RELEASE_CONTROL = 4006  # 释放控制权 robot_config_unlock_req


# ==================== 机器人状态 API (1000-1999) ====================

class RobotStatusAPI:
    """机器人状态API - 端口19204"""

    def __init__(self, client: RobokitClient):
        self.client = client

    async def get_info(self) -> dict:
        """
        查询机器人信息

        API编号: 1000 (0x03E8)
        响应编号: 11000 (0x2AF8)

        Returns:
            机器人信息，包含id, version, model, dsp_version, map_version等
        """
        return await self.client.call_status(1000)

    async def get_run_info(self) -> dict:
        """
        查询机器人运行信息

        API编号: 1002 (0x03EA)
        响应编号: 11002 (0x2AFA)

        Returns:
            运行信息，包含odo(里程), time(运行时间), controller_temp等
        """
        return await self.client.call_status(1002)

    async def get_location(self) -> dict:
        """
        查询机器人位置

        API编号: 1004 (0x03EC)
        响应编号: 11004 (0x2AFC)

        Returns:
            位置信息，包含x, y, angle, confidence, current_station等
        """
        return await self.client.call_status(1004)

    async def get_speed(self) -> dict:
        """
        查询机器人速度

        API编号: 1005 (0x03ED)
        响应编号: 11005 (0x2AFD)

        Returns:
            速度信息，包含vx, vy, w(角速度), steer, is_stop等
        """
        return await self.client.call_status(1005)

    async def get_blocked_status(self) -> dict:
        """
        查询机器人被阻挡状态

        API编号: 1006 (0x03EE)
        响应编号: 11006 (0x2AFE)

        Returns:
            阻挡状态，包含blocked, block_reason, block_x, block_y等
        """
        return await self.client.call_status(1006)

    async def get_battery(self, simple: bool = False) -> dict:
        """
        查询机器人电池状态

        API编号: 1007 (0x03EF)
        响应编号: 11007 (0x2AFF)

        Args:
            simple: 是否只返回简单数据(仅电量)

        Returns:
            电池信息，包含battery_level, voltage, current, charging等
        """
        params = {"simple": True} if simple else None
        return await self.client.call_status(1007, params)

    async def get_laser(self, return_beams3d: bool = False) -> dict:
        """
        查询机器人激光点云数据

        API编号: 1009 (0x03F1)
        响应编号: 11009 (0x2B01)

        Args:
            return_beams3d: 是否返回多线激光数据

        Returns:
            激光点云数据
        """
        params = {"return_beams3D": True} if return_beams3d else None
        return await self.client.call_status(1009, params)

    async def get_area(self) -> dict:
        """
        查询机器人当前所在区域

        API编号: 1011 (0x03F3)
        响应编号: 11011 (0x2B03)

        Returns:
            区域信息，包含area_ids数组
        """
        return await self.client.call_status(1011)

    async def get_emergency_status(self) -> dict:
        """
        查询机器人急停状态

        API编号: 1012 (0x03F4)
        响应编号: 11012 (0x2B04)

        Returns:
            急停状态，包含emergency, driver_emc, electric, soft_emc
        """
        return await self.client.call_status(1012)

    async def get_io(self) -> dict:
        """
        查询机器人I/O数据

        API编号: 1013 (0x03F5)
        响应编号: 11013 (0x2B05)

        Returns:
            I/O数据，包含DI数组和DO数组
        """
        return await self.client.call_status(1013)

    async def get_encoder(self) -> dict:
        """
        查询编码器脉冲值

        API编号: 1018 (0x03FA)
        响应编号: 11018 (0x2B0A)

        Returns:
            编码器数据
        """
        return await self.client.call_status(1018)

    async def get_motor(self, motor_names: Optional[list[str]] = None) -> dict:
        """
        查询电机状态信息

        API编号: 1040 (0x0410)
        响应编号: 11040 (0x2B20)

        Args:
            motor_names: 电机名称列表，None表示查询所有电机

        Returns:
            电机状态信息
        """
        params = {"motor_names": motor_names} if motor_names else None
        return await self.client.call_status(1040, params)

    async def get_slam_status(self) -> dict:
        """
        查询机器人扫图状态

        API编号: 1025 (0x0401)
        响应编号: 11025 (0x2B11)

        Returns:
            扫图状态，包含slam_status
        """
        return await self.client.call_status(1025)

    async def get_modbus(self, registers: list[int]) -> dict:
        """
        查询modbus数据

        API编号: 1071 (0x042F)
        响应编号: 11071 (0x2B3F)

        Args:
            registers: 需要查询的寄存器地址列表

        Returns:
            modbus数据
        """
        return await self.client.call_status(1071, {"4x": registers})


# ==================== 机器人控制 API (2000-2999) ====================

class RobotControlAPI:
    """机器人控制API - 端口19205"""

    def __init__(self, client: RobokitClient):
        self.client = client

    async def relocate(self, x: float, y: float, angle: float = 0) -> dict:
        """
        重定位

        API编号: 2002 (0x07D2)
        响应编号: 12002 (0x2ED2)

        Args:
            x: 世界坐标系x坐标(米)
            y: 世界坐标系y坐标(米)
            angle: 世界坐标系角度(弧度)

        Returns:
            响应结果
        """
        return await self.client.call_control(2002, {
            "x": x,
            "y": y,
            "angle": angle
        })

    async def confirm_location(self) -> dict:
        """
        确认定位正确

        API编号: 2003
        响应编号: 12003

        Returns:
            响应结果
        """
        return await self.client.call_control(2003)

    async def move_by_velocity(self, vx: float, vy: float = 0, w: float = 0) -> dict:
        """
        速度控制移动 (平动、转动)

        API编号: 2004，端口19205 (2xxx属控制API，19206期望3xxx会报60000)
        """
        return await self.client.call_control(2004, {
            "vx": vx,
            "vy": vy,
            "w": w
        })

    async def stop(self) -> dict:
        """
        停止移动

        API编号: 2005
        响应编号: 12005

        Returns:
            响应结果
        """
        return await self.client.call_control(2005)

    async def emergency_stop(self) -> dict:
        """
        急停

        API编号: 2006
        响应编号: 12006

        Returns:
            响应结果
        """
        return await self.client.call_control(2006)

    async def release_control(self) -> dict:
        """
        释放控制权 - 将控制权交还给调度系统，端口19207
        """
        return await self.client.call_config(API_RELEASE_CONTROL)

    async def take_control(self) -> dict:
        """
        抢占控制权 - 从调度系统夺取控制权，端口19207
        遇 40012/40020 时需先调用此接口
        """
        return await self.client.call_config(API_TAKE_CONTROL)


# ==================== 机器人导航 API (3000-3999) ====================

class RobotNavigationAPI:
    """机器人导航API - 端口19206"""

    def __init__(self, client: RobokitClient):
        self.client = client

    async def path_navigation(self, path_id: int) -> dict:
        """
        路径导航

        API编号: 3051
        响应编号: 13051

        Args:
            path_id: 路径ID

        Returns:
            响应结果
        """
        return await self.client.call_navigation(3051, {
            "path_id": path_id
        })

    async def stop_navigation(self) -> dict:
        """
        停止导航

        API编号: 3052
        响应编号: 13052

        Returns:
            响应结果
        """
        return await self.client.call_navigation(3052)

    async def move_to(self, target: str, target_type: str = "point") -> dict:
        """
        移动到目标点

        API编号: 3061
        响应编号: 13061

        Args:
            target: 目标名称(点ID或区域ID)
            target_type: 目标类型 ("point" 或 "area")

        Returns:
            响应结果
        """
        return await self.client.call_navigation(3061, {
            "target": target,
            "type": target_type
        })

    async def get_navigation_status(self) -> dict:
        """
        查询导航状态

        API编号: 1020 (状态API)
        响应编号: 11020

        Returns:
            导航状态
        """
        return await self.client.call_status(1020)

    async def get_location_status(self) -> dict:
        """
        查询定位状态

        API编号: 1021 (状态API)
        响应编号: 11021

        Returns:
            定位状态
        """
        return await self.client.call_status(1021)


# ==================== 机器人配置 API (4000-4999) ====================

class RobotConfigAPI:
    """机器人配置API - 端口19207"""

    def __init__(self, client: RobokitClient):
        self.client = client

    async def set_mode(self, mode: int) -> dict:
        """
        切换运行模式

        API编号: 4000 (0x0FA0)
        响应编号: 14000

        Args:
            mode: 0=手动模式(可执行移动/重定位等控制指令), 1=自动模式(可执行任务API)

        Returns:
            响应结果

        文档: RoboKit NetProtocol - 切换运行模式
        注: 控制API(2002-2006)仅在手动模式下有效; 任务API仅在自动模式下有效
        """
        return await self.client.call_config(4000, {"mode": mode})

    async def download_map(self, map_name: str) -> dict:
        """
        下载地图

        API编号: 4001
        响应编号: 14001

        Args:
            map_name: 地图名称

        Returns:
            地图数据
        """
        return await self.client.call_config(4001, {
            "map_name": map_name
        })

    async def upload_map(self, map_data: str, map_name: str) -> dict:
        """
        上传地图

        API编号: 4002
        响应编号: 14002

        Args:
            map_data: 地图数据(JSON字符串或base64编码)
            map_name: 地图名称

        Returns:
            响应结果
        """
        return await self.client.call_config(4002, {
            "map_data": map_data,
            "map_name": map_name
        })

    async def delete_map(self, map_name: str) -> dict:
        """
        删除地图

        API编号: 4003
        响应编号: 14003

        Args:
            map_name: 地图名称

        Returns:
            响应结果
        """
        return await self.client.call_config(4003, {
            "map_name": map_name
        })

    async def get_map_list(self) -> dict:
        """
        获取地图列表

        API编号: 4004
        响应编号: 14004

        Returns:
            地图列表
        """
        return await self.client.call_config(4004)

    async def set_current_map(self, map_name: str) -> dict:
        """
        设置当前地图

        API编号: 4005
        响应编号: 14005

        Args:
            map_name: 地图名称

        Returns:
            响应结果
        """
        return await self.client.call_config(4005, {
            "map_name": map_name
        })


# ==================== 统一API入口 ====================

class RobokitAPI:
    """
    Robokit统一API入口

    使用示例:
        client = RobokitClient("192.168.192.5")
        await client.connect()

        api = RobokitAPI(client)
        info = await api.status.get_info()
        location = await api.status.get_location()

        await client.close()
    """

    def __init__(self, client: RobokitClient):
        self.status = RobotStatusAPI(client)
        self.control = RobotControlAPI(client)
        self.navigation = RobotNavigationAPI(client)
        self.config = RobotConfigAPI(client)
        self._client = client

    async def connect(self) -> bool:
        """连接到机器人所有API端口"""
        success = await self._client.connect()
        if success:
            # 连接其他端口
            for port in [PORT_CONTROL, PORT_NAVIGATION, PORT_CONFIG, PORT_OTHER]:
                try:
                    await self._client.connect(port)
                except Exception:
                    pass  # 某些端口可能不可用
        return success

    async def close(self) -> None:
        """关闭所有连接"""
        await self._client.close()

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._client.is_connected()


# ==================== 错误处理 ====================

class RobokitError(Exception):
    """Robokit API错误基类"""
    pass


class RobokitConnectionError(RobokitError):
    """连接错误"""
    pass


class RobokitTimeoutError(RobokitError):
    """超时错误"""
    pass


class RobokitAPIError(RobokitError):
    """API错误

    Attributes:
        ret_code: 错误码
        err_msg: 错误信息
    """

    def __init__(self, ret_code: int, err_msg: str = ""):
        self.ret_code = ret_code
        self.err_msg = err_msg
        super().__init__(f"API错误[{ret_code}]: {err_msg}")


def check_response(response: dict) -> None:
    """
    检查响应是否包含错误

    Args:
        response: API响应字典

    Raises:
        RobokitAPIError: 如果响应包含错误码
    """
    ret_code = response.get('ret_code', 0)
    if ret_code != 0:
        err_msg = response.get('err_msg', '')
        raise RobokitAPIError(ret_code, err_msg)
