"""
Robokit TCP/IP 协议处理模块
处理报文头的编解码和消息序列化/反序列化
"""
import struct
import json
from dataclasses import dataclass
from typing import Any


# 协议常量
SYNC_BYTE = 0x5A
HEADER_VERSION_V34 = 0x01
HEADER_VERSION_V35 = 0x02
HEADER_SIZE = 16  # 报文头固定16字节
RESPONSE_OFFSET = 10000  # 响应编号 = 请求编号 + 10000 (0x2710)

# 压缩类型
COMPRESS_NONE = 0
COMPRESS_GZIP = 1
COMPRESS_ZLIB = 2
COMPRESS_BROTLI = 3


@dataclass
class ProtocolHeader:
    """Robokit协议报文头结构"""
    m_sync: int      # uint8  - 报文同步头 (0x5A)
    m_version: int   # uint8  - 协议版本号
    m_number: int    # uint16 - 请求及响应的序号
    m_length: int    # uint32 - 数据总长度
    m_type: int      # uint16 - 报文类型(API编号)
    m_reserved: bytes  # uint8[6] - 保留区域

    @classmethod
    def pack(cls, number: int, msg_type: int, data: bytes = b'',
             version: int = HEADER_VERSION_V34, compress_type: int = COMPRESS_NONE) -> bytes:
        """
        打包报文头

        Args:
            number: 请求序号 (0-65535)
            msg_type: API编号/报文类型
            data: 数据区字节
            version: 协议版本 (0x01 for RBK3.4, 0x02 for RBK3.5)
            compress_type: 压缩类型

        Returns:
            打包后的报文头(16字节) + 数据区
        """
        # 计算数据长度
        data_length = len(data)

        # 构造保留区域，第5位作为压缩类型
        reserved = bytes([0, 0, 0, 0, compress_type, 0])

        # 打包报文头: sync(1) + version(1) + number(2) + length(4) + type(2) + reserved(6)
        # 使用大端序 ! 与官方协议一致 (PACK_FMT_STR = '!BBHLH6s')
        header = struct.pack(
            '!BBHLH6s',
            SYNC_BYTE,
            version,
            number,
            data_length,
            msg_type,
            reserved
        )
        return header + data

    @classmethod
    def unpack(cls, data: bytes) -> tuple['ProtocolHeader', bytes]:
        """
        解包报文头

        Args:
            data: 接收到的完整报文数据

        Returns:
            (ProtocolHeader, data_bytes) - 协议头对象和数据区字节

        Raises:
            ValueError: 数据长度不足或格式错误
        """
        if len(data) < HEADER_SIZE:
            raise ValueError(f"数据长度不足，至少需要{HEADER_SIZE}字节")

        # 解包报文头 (大端序，与官方协议一致)
        sync, version, number, length, msg_type, reserved = struct.unpack(
            '!BBHLH6s', data[:HEADER_SIZE]
        )

        if sync != SYNC_BYTE:
            raise ValueError(f"同步头错误，期望0x{SYNC_BYTE:02X}，实际0x{sync:02X}")

        header = cls(
            m_sync=sync,
            m_version=version,
            m_number=number,
            m_length=length,
            m_type=msg_type,
            m_reserved=reserved
        )

        # 提取数据区
        data_bytes = data[HEADER_SIZE:HEADER_SIZE + length] if length > 0 else b''
        return header, data_bytes


def build_request(number: int, msg_type: int, params: dict | None = None,
                 version: int = HEADER_VERSION_V34) -> bytes:
    """
    构建请求报文

    Args:
        number: 请求序号
        msg_type: API编号
        params: 请求参数字典，None表示无数据区
        version: 协议版本

    Returns:
        完整的请求报文字节
    """
    if params is None:
        data = b''
    else:
        # 序列化为JSON字节（紧凑格式，无空格）
        data = json.dumps(params, ensure_ascii=False, separators=(',', ':')).encode('utf-8')

    return ProtocolHeader.pack(number, msg_type, data, version)


def parse_response(data: bytes) -> tuple[int, int, dict]:
    """
    解析响应报文

    Args:
        data: 接收到的完整响应报文

    Returns:
        (number, msg_type, result) - 响应序号、消息类型、解析后的JSON数据
    """
    header, data_bytes = ProtocolHeader.unpack(data)

    # 解析数据区
    if data_bytes:
        result = json.loads(data_bytes.decode('utf-8'))
    else:
        result = {}

    return header.m_number, header.m_type, result


def get_response_type(request_type: int) -> int:
    """
    获取响应类型编号

    Args:
        request_type: 请求类型编号

    Returns:
        响应类型编号 (请求编号 + 10000)
    """
    return request_type + RESPONSE_OFFSET


def is_response_expected(request_type: int, response_type: int) -> bool:
    """
    检查响应类型是否与请求类型匹配

    Args:
        request_type: 请求类型编号
        response_type: 响应类型编号

    Returns:
        是否匹配
    """
    return response_type == get_response_type(request_type)
