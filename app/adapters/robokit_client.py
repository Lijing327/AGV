"""
Robokit TCP/IP 客户端
连接到Robokit机器人并调用各种API
"""
import asyncio
import json
import struct
import socket
from typing import Any, Callable, Optional
from contextlib import asynccontextmanager

from app.adapters.robokit_protocol import (
    build_request,
    parse_response,
    get_response_type,
    HEADER_SIZE,
    HEADER_VERSION_V34,
)


# API端口定义
PORT_STATUS = 19204   # 机器人状态 API
PORT_CONTROL = 19205  # 机器人控制 API
PORT_NAVIGATION = 19206  # 机器人导航 API
PORT_CONFIG = 19207   # 机器人配置 API
PORT_OTHER = 19210    # 其他 API
PORT_PUSH = 19301     # 机器人推送 API


class RobokitClient:
    """
    Robokit TCP客户端

    使用示例:
        client = RobokitClient(host="192.168.192.5")
        await client.connect()
        result = await client.call(PORT_STATUS, 1000)  # 查询机器人信息
        await client.close()
    """

    def __init__(self, host: str, default_port: int = PORT_STATUS,
                 timeout: float = 10.0, version: int = HEADER_VERSION_V34):
        """
        初始化客户端

        Args:
            host: 机器人IP地址
            default_port: 默认端口
            timeout: 超时时间(秒)
            version: 协议版本
        """
        self.host = host
        self.default_port = default_port
        self.timeout = timeout
        self.version = version
        self._request_number = 0
        self._connections: dict[int, asyncio.StreamReader] = {}
        self._writers: dict[int, asyncio.StreamWriter] = {}
        self._locks: dict[int, asyncio.Lock] = {}
        self._push_task: asyncio.Task | None = None
        self._push_reader: asyncio.StreamReader | None = None
        self._push_writer: asyncio.StreamWriter | None = None
        self._push_position_callback: Optional[Callable[..., Any]] = None

    async def connect(self, port: int | None = None) -> bool:
        """
        连接到机器人

        Args:
            port: 端口号，None使用默认端口

        Returns:
            是否连接成功
        """
        port = port or self.default_port
        if port in self._connections:
            return True  # 已连接

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, port),
                timeout=self.timeout
            )
            self._connections[port] = reader
            self._writers[port] = writer
            self._locks[port] = asyncio.Lock()
            return True
        except Exception as e:
            print(f"连接失败 {self.host}:{port} - {e}")
            return False

    async def close(self, port: int | None = None) -> None:
        """
        关闭连接

        Args:
            port: 端口号，None关闭所有连接
        """
        await self.stop_push_listener()
        if port is None:
            # 关闭所有连接
            ports = list(self._writers.keys())
            for p in ports:
                await self._close_port(p)
        else:
            await self._close_port(port)

    async def _close_port(self, port: int) -> None:
        """关闭指定端口的连接"""
        if port in self._writers:
            writer = self._writers[port]
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
            self._writers.pop(port, None)
            self._connections.pop(port, None)
            self._locks.pop(port, None)

    def _next_number(self) -> int:
        """获取下一个请求序号"""
        self._request_number = (self._request_number + 1) % 65536
        return self._request_number

    async def call(self, port: int, msg_type: int, params: dict | None = None) -> dict:
        """
        调用API

        Args:
            port: 端口号
            msg_type: API编号/消息类型
            params: 请求参数

        Returns:
            响应数据字典

        Raises:
            ConnectionError: 连接失败
            TimeoutError: 请求超时
            ValueError: 响应格式错误
        """
        # 确保已连接
        if port not in self._connections:
            success = await self.connect(port)
            if not success:
                raise ConnectionError(f"无法连接到 {self.host}:{port}")

        lock = self._locks.get(port)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[port] = lock

        async with lock:
            # 可能在等待 lock 的过程中，被其它协程关闭了该端口连接
            if port not in self._connections or port not in self._writers:
                success = await self.connect(port)
                if not success or port not in self._connections or port not in self._writers:
                    raise ConnectionError(f"无法连接到 {self.host}:{port}")
            reader = self._connections[port]
            writer = self._writers[port]

            # 构建请求
            number = self._next_number()
            request = build_request(number, msg_type, params, self.version)

            # 发送请求
            try:
                writer.write(request)
                await asyncio.wait_for(writer.drain(), timeout=self.timeout)
            except Exception as e:
                raise ConnectionError(f"发送请求失败: {e}")

            # 读取响应
            try:
                # 先读取报文头
                header_data = await asyncio.wait_for(
                    reader.readexactly(HEADER_SIZE),
                    timeout=self.timeout
                )

                # 解析长度
                import struct
                sync, version, resp_number, length, resp_type, _ = struct.unpack(
                    '!BBHLH6s', header_data
                )

                # 读取数据区
                if length > 0:
                    data_bytes = await asyncio.wait_for(
                        reader.readexactly(length),
                        timeout=self.timeout
                    )
                else:
                    data_bytes = b''

                # 解析JSON
                if data_bytes:
                    result = __import__('json').loads(data_bytes.decode('utf-8'))
                else:
                    result = {}

                return result

            except asyncio.TimeoutError:
                raise TimeoutError(f"请求超时 (端口={port}, 类型={msg_type})")
            except asyncio.IncompleteReadError as e:
                # 对端断开或网络闪断：读不到完整报文头/数据区
                try:
                    await self._close_port(port)
                except Exception:
                    pass
                raise ConnectionError(f"连接已断开 (端口={port}, 类型={msg_type}): {e}")
            except (ConnectionResetError, BrokenPipeError) as e:
                try:
                    await self._close_port(port)
                except Exception:
                    pass
                raise ConnectionError(f"连接异常 (端口={port}, 类型={msg_type}): {e}")
            except Exception as e:
                # 其它解析/协议错误
                raise ValueError(f"解析响应失败: {e}")

    async def call_status(self, msg_type: int, params: dict | None = None) -> dict:
        """调用状态API (端口19204)"""
        return await self.call(PORT_STATUS, msg_type, params)

    async def call_control(self, msg_type: int, params: dict | None = None) -> dict:
        """调用控制API (端口19205)"""
        return await self.call(PORT_CONTROL, msg_type, params)

    async def call_navigation(self, msg_type: int, params: dict | None = None) -> dict:
        """调用导航API (端口19206)"""
        return await self.call(PORT_NAVIGATION, msg_type, params)

    async def call_config(self, msg_type: int, params: dict | None = None) -> dict:
        """调用配置API (端口19207)"""
        return await self.call(PORT_CONFIG, msg_type, params)

    async def call_other(self, msg_type: int, params: dict | None = None) -> dict:
        """调用其他API (端口19210)"""
        return await self.call(PORT_OTHER, msg_type, params)

    def is_connected(self, port: int | None = None) -> bool:
        """
        检查连接状态

        Args:
            port: 端口号，None检查默认端口

        Returns:
            是否已连接
        """
        port = port or self.default_port
        return port in self._connections

    # ==================== 机器人推送 API (端口 19301) ====================

    async def start_push_listener(self, on_position: Optional[Callable[..., Any]] = None) -> bool:
        """
        连接机器人推送端口 19301，持续监听位置等数据

        机器人会主动推送数据，客户端只需连接并读取。
        每次收到推送后调用 on_position(data) 传递解析后的 JSON。

        Args:
            on_position: 收到推送数据时的回调，参数为 dict

        Returns:
            是否连接成功
        """
        if self._push_task and not self._push_task.done():
            return True  # 已在监听

        self._push_position_callback = on_position
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, PORT_PUSH),
                timeout=self.timeout
            )
            self._push_reader = reader
            self._push_writer = writer
            self._push_task = asyncio.create_task(self._push_listen_loop())
            return True
        except Exception as e:
            print(f"推送端口连接失败 {self.host}:{PORT_PUSH} - {e}")
            return False

    async def _push_listen_loop(self) -> None:
        """推送监听循环：持续读取报文并解析"""
        reader = self._push_reader
        if not reader:
            return
        try:
            while True:
                header_data = await reader.readexactly(HEADER_SIZE)
                sync, version, number, length, msg_type, _ = struct.unpack(
                    '!BBHLH6s', header_data
                )
                if sync != 0x5A:
                    continue
                data_bytes = await reader.readexactly(length) if length > 0 else b''
                if data_bytes:
                    try:
                        data = json.loads(data_bytes.decode('utf-8'))
                        if self._push_position_callback:
                            self._push_position_callback(data)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"推送监听异常: {e}")
        finally:
            # 不在此处在 Cancelled/销毁阶段 await wait_closed()，否则可能触发
            # RuntimeError: coroutine ignored GeneratorExit / Task destroyed pending
            self._push_reader = None
            push_writer = self._push_writer
            self._push_writer = None
            if push_writer is not None:
                try:
                    push_writer.close()
                except Exception:
                    pass

    async def stop_push_listener(self) -> None:
        """停止推送监听"""
        if self._push_task and not self._push_task.done():
            self._push_task.cancel()
            try:
                await self._push_task
            except asyncio.CancelledError:
                pass
            self._push_task = None
        self._push_reader = None
        if self._push_writer:
            try:
                self._push_writer.close()
                await self._push_writer.wait_closed()
            except Exception:
                pass
            self._push_writer = None


# 同步版本的客户端（用于简单的脚本场景）
class RobokitClientSync:
    """
    Robokit同步TCP客户端
    使用socket实现的同步版本，适合简单场景
    """

    def __init__(self, host: str, port: int = PORT_STATUS, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._sock: socket.socket | None = None
        self._request_number = 0

    def connect(self) -> bool:
        """连接到机器人"""
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(self.timeout)
            self._sock.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"连接失败 {self.host}:{self.port} - {e}")
            return False

    def close(self) -> None:
        """关闭连接"""
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None

    def _next_number(self) -> int:
        """获取下一个请求序号"""
        self._request_number = (self._request_number + 1) % 65536
        return self._request_number

    def call(self, msg_type: int, params: dict | None = None) -> dict:
        """
        调用API

        Args:
            msg_type: API编号/消息类型
            params: 请求参数

        Returns:
            响应数据字典
        """
        if not self._sock:
            raise ConnectionError("未连接，请先调用connect()")

        # 构建请求
        number = self._next_number()
        request = build_request(number, msg_type, params)

        # 发送请求
        self._sock.sendall(request)

        # 读取报文头
        header_data = self._sock.recv(HEADER_SIZE)
        if len(header_data) < HEADER_SIZE:
            raise ConnectionError("连接已关闭")

        # 解析长度
        import struct
        sync, version, resp_number, length, resp_type, _ = struct.unpack(
            '!BBHLH6s', header_data
        )

        # 读取数据区
        if length > 0:
            data_bytes = b''
            remaining = length
            while remaining > 0:
                chunk = self._sock.recv(min(remaining, 4096))
                if not chunk:
                    raise ConnectionError("连接已关闭")
                data_bytes += chunk
                remaining -= len(chunk)
        else:
            data_bytes = b''

        # 解析JSON
        if data_bytes:
            result = json.loads(data_bytes.decode('utf-8'))
        else:
            result = {}

        return result

    def __enter__(self):
        """上下文管理器支持"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器支持"""
        self.close()


@asynccontextmanager
async def robokit_client(host: str, port: int = PORT_STATUS):
    """
    异步上下文管理器，自动管理连接

    使用示例:
        async with robokit_client("192.168.192.5") as client:
            result = await client.call_status(1000)
    """
    client = RobokitClient(host, port)
    try:
        await client.connect()
        yield client
    finally:
        await client.close()
