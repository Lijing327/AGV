/**
 * API 配置与请求
 *
 * - 开发 (npm run dev)：默认走相对路径 /api，由 Vite 代理到 VITE_DEV_PROXY_TARGET（见 vite.config.js）
 * - 生产 (build)：优先使用 VITE_API_BASE（完整 URL，如 https://www.yonghongjituan.com:6715/api）
 *   未配置时：与当前页面同主机、端口 6715（与线上部署约定一致，可按需改 env）
 *
 * 环境变量说明见 frontend/.env.example
 */
function getApiBase() {
  const fromEnv = import.meta.env.VITE_API_BASE
  if (fromEnv !== undefined && String(fromEnv).trim() !== '') {
    return String(fromEnv).trim().replace(/\/+$/, '')
  }
  if (import.meta.env.DEV) {
    return '/api'
  }
  if (typeof window !== 'undefined' && window.location?.hostname) {
    const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:'
    const host = window.location.hostname
    return `${protocol}//${host}:6715/api`
  }
  return '/api'
}
const API_BASE = getApiBase()

export async function fetchMap() {
  const r = await fetch(`${API_BASE}/map`)
  return r.ok ? r.json() : null
}

export async function fetchFleet() {
  const r = await fetch(`${API_BASE}/fleet`)
  return r.ok ? r.json() : null
}

export async function fetchTasks() {
  const r = await fetch(`${API_BASE}/tasks`)
  return r.ok ? r.json() : null
}

export async function simStart() {
  const r = await fetch(`${API_BASE}/sim/start`, { method: 'POST' })
  return r.ok
}

export async function simStop() {
  const r = await fetch(`${API_BASE}/sim/stop`, { method: 'POST' })
  return r.ok
}

export async function createTask(fromNode, toNode) {
  const r = await fetch(`${API_BASE}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ from_node: fromNode, to_node: toNode }),
  })
  return r.json()
}

export async function importMap(data) {
  const r = await fetch(`${API_BASE}/map/import`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  return r.json()
}

export async function importMapFromFile(filePath) {
  const r = await fetch(`${API_BASE}/map/import-file`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: filePath }),
  })
  return r.json()
}

/**
 * 路径规划：根据起点和终点自动计算最优路径，返回 move_task_list 格式
 * @param {string} sourceId - 起点节点 ID
 * @param {string} targetId - 终点节点 ID
 * @returns {{ path: string[], move_task_list: Array<{source_id, id, task_id}> }}
 */
export async function planPath(sourceId, targetId) {
  const r = await fetch(`${API_BASE}/map/plan-path`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source_id: sourceId, target_id: targetId }),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `路径规划失败 ${r.status}`)
  return data
}

// ==================== Robokit 机器人API ====================

// 连接管理（超时避免 fetch 一直挂起导致界面「点了没反应」）
export async function robokitConnect(host, port, timeoutMs = 45000) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)
  const payload = {
    host: String(host || '').trim(),
    port:
      port === '' || port == null || Number.isNaN(Number(port))
        ? null
        : Number(port),
  }
  try {
    const r = await fetch(`${API_BASE}/robokit/connect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal,
    })
    let data = {}
    try {
      data = await r.json()
    } catch {
      data = {}
    }
    if (!r.ok) {
      const detail =
        typeof data.detail === 'string'
          ? data.detail
          : Array.isArray(data.detail)
            ? data.detail.map((d) => d.msg || d).join('; ')
            : `HTTP ${r.status}`
      throw new Error(detail)
    }
    return data
  } catch (e) {
    if (e.name === 'AbortError') {
      throw new Error(`连接请求超时（${timeoutMs / 1000}s），请检查后端是否运行、代理与机器人 IP`)
    }
    throw e
  } finally {
    clearTimeout(timer)
  }
}

export async function robokitDisconnect() {
  const r = await fetch(`${API_BASE}/robokit/disconnect`, { method: 'POST' })
  return r.ok
}

export async function robokitStatus() {
  const r = await fetch(`${API_BASE}/robokit/status`)
  return r.ok ? r.json() : null
}

/** 获取机器人实时位置（来自推送 API 19301） */
export async function robokitPosition() {
  const r = await fetch(`${API_BASE}/robokit/position`)
  return r.ok ? r.json() : null
}

// 机器人状态API
export async function robokitGetInfo() {
  const r = await fetch(`${API_BASE}/robokit/robot/info`)
  return r.ok ? r.json() : null
}

export async function robokitGetRunInfo() {
  const r = await fetch(`${API_BASE}/robokit/robot/run-info`)
  return r.ok ? r.json() : null
}

export async function robokitGetLocation() {
  const r = await fetch(`${API_BASE}/robokit/robot/location`)
  return r.ok ? r.json() : null
}

export async function robokitGetSpeed() {
  const r = await fetch(`${API_BASE}/robokit/robot/speed`)
  return r.ok ? r.json() : null
}

export async function robokitGetBlocked() {
  const r = await fetch(`${API_BASE}/robokit/robot/blocked`)
  return r.ok ? r.json() : null
}

export async function robokitGetBattery(simple = false) {
  const r = await fetch(`${API_BASE}/robokit/robot/battery${simple ? '?simple=true' : ''}`)
  return r.ok ? r.json() : null
}

export async function robokitGetEmergency() {
  const r = await fetch(`${API_BASE}/robokit/robot/emergency`)
  return r.ok ? r.json() : null
}

export async function robokitGetIO() {
  const r = await fetch(`${API_BASE}/robokit/robot/io`)
  return r.ok ? r.json() : null
}

export async function robokitGetMotor(motorNames) {
  const r = await fetch(`${API_BASE}/robokit/robot/motor${motorNames ? '?motor_names=' + motorNames : ''}`)
  return r.ok ? r.json() : null
}

export async function robokitGetLaser() {
  const r = await fetch(`${API_BASE}/robokit/robot/laser`)
  return r.ok ? r.json() : null
}

export async function robokitGetArea() {
  const r = await fetch(`${API_BASE}/robokit/robot/area`)
  return r.ok ? r.json() : null
}

export async function robokitGetEncoder() {
  const r = await fetch(`${API_BASE}/robokit/robot/encoder`)
  return r.ok ? r.json() : null
}

export async function robokitGetSlam() {
  const r = await fetch(`${API_BASE}/robokit/robot/slams`)
  return r.ok ? r.json() : null
}

export async function robokitQueryModbus(registers) {
  const r = await fetch(`${API_BASE}/robokit/robot/modbus`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ registers }),
  })
  return r.ok ? r.json() : null
}

export async function robokitGetBins() {
  const r = await fetch(`${API_BASE}/robokit/robot/bins`)
  return r.ok ? r.json() : null
}

// 机器人控制API
export async function robokitRelocate(x, y, angle = 0) {
  const r = await fetch(`${API_BASE}/robokit/control/relocate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ x, y, angle }),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

export async function robokitConfirmLocation() {
  const r = await fetch(`${API_BASE}/robokit/control/confirm-location`, { method: 'POST' })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

export async function robokitCancelRelocate() {
  const r = await fetch(`${API_BASE}/robokit/control/cancel-relocate`, { method: 'POST' })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

export async function robokitMove(vx, vy = 0, w = 0) {
  const r = await fetch(`${API_BASE}/robokit/control/move`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ vx, vy, w }),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

export async function robokitStop() {
  const r = await fetch(`${API_BASE}/robokit/control/stop`, { method: 'POST' })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

export async function robokitTakeControl(nickName = 'agv-web') {
  const r = await fetch(`${API_BASE}/robokit/control/take`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nick_name: nickName }),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

export async function robokitReleaseControl() {
  const r = await fetch(`${API_BASE}/robokit/control/release`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

export async function robokitEmergencyStop() {
  const r = await fetch(`${API_BASE}/robokit/control/emergency-stop`, { method: 'POST' })
  return r.ok ? r.json() : null
}

// 机器人导航API
/**
 * 路径导航 (API 3051)：给定起点、终点站点名，机器人沿固定路径运行。
 * @param {string} sourceId
 * @param {string} targetId
 * @param {string|null} taskId
 * @param {Record<string, unknown>|null} extra 可选，如货叉 { operation: 'ForkUnload', end_height: 0 } 等会并入请求体
 */
export async function robokitPathNavigation(sourceId, targetId, taskId = null, extra = null) {
  const body = { source_id: sourceId, target_id: targetId }
  if (taskId != null && taskId !== '') body.task_id = taskId
  if (extra && typeof extra === 'object') {
    for (const [k, v] of Object.entries(extra)) {
      if (v === undefined || v === null || v === '') continue
      body[k] = v
    }
  }
  const r = await fetch(`${API_BASE}/robokit/navigation/path`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  return r.ok ? r.json() : null
}

/**
 * 指定路径导航 (API 3066)：发送站点序列 move_task_list，每段必填 id、source_id、task_id。
 * @param {Array<{source_id: string, id: string, task_id: string, ...}>} moveTaskList
 */
export async function robokitSpecifiedPathNavigation(moveTaskList) {
  const r = await fetch(`${API_BASE}/robokit/navigation/specified-path`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ move_task_list: moveTaskList }),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

/** 平动 (API 3055，端口19206)：直线运动固定距离，只需给 dist，可选 vx/vy/mode */
export async function robokitTranslate(dist, vx = null, vy = null, mode = 0) {
  const body = { dist: Number(dist), mode }
  if (vx != null) body.vx = Number(vx)
  if (vy != null) body.vy = Number(vy)
  const r = await fetch(`${API_BASE}/robokit/navigation/translate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

export async function robokitStopNavigation() {
  const r = await fetch(`${API_BASE}/robokit/navigation/stop`, { method: 'POST' })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

/** 暂停当前导航 (API 3001) */
export async function robokitPauseNavigation() {
  const r = await fetch(`${API_BASE}/robokit/navigation/pause`, { method: 'POST' })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

/** 继续当前导航 (API 3002) */
export async function robokitResumeNavigation() {
  const r = await fetch(`${API_BASE}/robokit/navigation/resume`, { method: 'POST' })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

/** 取消当前导航 (API 3003) */
export async function robokitCancelNavigation() {
  const r = await fetch(`${API_BASE}/robokit/navigation/cancel`, { method: 'POST' })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

/** 获取路径导航的路径 (API 3053)，body 可选 */
export async function robokitGetTargetPath(body = null) {
  const r = await fetch(`${API_BASE}/robokit/navigation/target-path`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {}),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

/** 转动 (API 3056)：角度 rad，角速度 rad/s 可选 */
export async function robokitTurn(moveAngle, speedW = null, locMode = 0) {
  const body = { move_angle: Number(moveAngle), loc_mode: locMode }
  if (speedW != null) body.speed_w = Number(speedW)
  const r = await fetch(`${API_BASE}/robokit/navigation/turn`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

/** 托盘旋转 (API 3057)，body 如 { angle: 1.57 } */
export async function robokitSpin(body) {
  const r = await fetch(`${API_BASE}/robokit/navigation/spin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

/** 圆弧运动 (API 3058)，body 见接口文档 */
export async function robokitCircular(body) {
  const r = await fetch(`${API_BASE}/robokit/navigation/circular`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

/** 启用和禁用线路 (API 3059)，body 见接口文档 */
export async function robokitPathEnable(body) {
  const r = await fetch(`${API_BASE}/robokit/navigation/path-enable`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

/** 清除指定导航路径 (API 3067) */
export async function robokitClearTargetList() {
  const r = await fetch(`${API_BASE}/robokit/navigation/clear-target-list`, { method: 'POST' })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

/** 根据任务id清除指定导航路径 (API 3068) */
export async function robokitClearByTaskId(taskId) {
  const r = await fetch(`${API_BASE}/robokit/navigation/clear-by-task-id`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task_id: taskId }),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

/** 查询机器人任务链 (API 3101) */
export async function robokitGetTasklistStatus() {
  const r = await fetch(`${API_BASE}/robokit/navigation/tasklist-status`)
  return r.ok ? r.json() : null
}

/** 查询机器人所有任务链 (API 3115) */
export async function robokitGetTasklistList() {
  const r = await fetch(`${API_BASE}/robokit/navigation/tasklist-list`)
  return r.ok ? r.json() : null
}

/** 执行预存任务链 (API 3106) */
export async function robokitExecuteTasklist(name) {
  const r = await fetch(`${API_BASE}/robokit/navigation/tasklist-execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

export async function robokitMoveTo(target, targetType = 'point') {
  const r = await fetch(`${API_BASE}/robokit/navigation/move-to`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ target, type: targetType }),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || data.err_msg || `请求失败 ${r.status}`)
  return data
}

export async function robokitGetNavStatus() {
  const r = await fetch(`${API_BASE}/robokit/navigation/status`)
  return r.ok ? r.json() : null
}

export async function robokitGetLocStatus() {
  const r = await fetch(`${API_BASE}/robokit/navigation/location-status`)
  return r.ok ? r.json() : null
}

// 机器人配置API
export async function robokitSetMode(mode) {
  const r = await fetch(`${API_BASE}/robokit/config/set-mode`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode }),
  })
  const data = await r.json().catch(() => ({}))
  if (!r.ok) throw new Error(data.detail || `请求失败 ${r.status}`)
  return data
}

export async function robokitGetMaps() {
  const r = await fetch(`${API_BASE}/robokit/config/maps`)
  return r.ok ? r.json() : null
}

export async function robokitSetMap(mapName) {
  const r = await fetch(`${API_BASE}/robokit/config/set-map`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ map_name: mapName }),
  })
  return r.ok ? r.json() : null
}

export async function robokitDownloadMap(mapName) {
  const r = await fetch(`${API_BASE}/robokit/config/download-map`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ map_name: mapName }),
  })
  return r.ok ? r.json() : null
}

// 通用API调用
export async function robokitCall(port, msgType, params = null) {
  const r = await fetch(`${API_BASE}/robokit/call`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ port, msg_type: msgType, params }),
  })
  return r.ok ? r.json() : null
}
