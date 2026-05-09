"""
将浏览器对 Java 编排服务（AgvJavaServer）的请求转发到本机或内网地址。
浏览器只访问 Python /api，避免 9000→8001 跨域与客户端直连 Java 被防火墙拦截。
"""
from __future__ import annotations

import os
from typing import Any

import httpx
from fastapi import HTTPException
from fastapi.responses import JSONResponse


def java_api_base_url() -> str:
    """与前端原 VITE_JAVA_API_BASE 一致：含 /api 后缀，例如 http://127.0.0.1:8001/api"""
    raw = os.environ.get("AGV_JAVA_API_BASE", "http://127.0.0.1:8001/api")
    return raw.strip().rstrip("/")


async def forward_java_post(rel_path: str, body: dict[str, Any]) -> JSONResponse:
    """
    rel_path: robokit 下的相对路径，如 connect、workflow/fangshang/java/load
    """
    base = java_api_base_url()
    url = f"{base}/robokit/{rel_path.lstrip('/')}"
    timeout = httpx.Timeout(300.0, connect=15.0)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(url, json=body)
    except httpx.ConnectError as e:
        raise HTTPException(
            status_code=503,
            detail=f"无法连接 Java 编排服务 ({base})。请确认进程已启动且 AGV_JAVA_API_BASE 正确: {e}",
        ) from e
    except httpx.TimeoutException as e:
        raise HTTPException(status_code=504, detail="Java 编排服务请求超时") from e

    ct = (r.headers.get("content-type") or "").lower()
    if "application/json" in ct and r.content:
        try:
            data = r.json()
        except Exception:
            data = {"detail": r.text[:800] if r.text else f"Java 返回非 JSON（{r.status_code}）"}
    elif r.content and r.text:
        data = {"detail": r.text[:800]}
    else:
        data = {}
    return JSONResponse(status_code=r.status_code, content=data)
