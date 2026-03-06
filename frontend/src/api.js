/**
 * API 配置与请求
 * 开发环境通过 Vite proxy 使用 /api，生产环境需配置 VITE_API_BASE 或 nginx 反向代理
 */
const API_BASE = import.meta.env.VITE_API_BASE || '/api'

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

// ==================== Robokit 机器人API ====================

// 连接管理
export async function robokitConnect(host, port) {
  const r = await fetch(`${API_BASE}/robokit/connect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ host, port }),
  })
  return r.ok ? r.json() : null
}

export async function robokitDisconnect() {
  const r = await fetch(`${API_BASE}/robokit/disconnect`, { method: 'POST' })
  return r.ok
}

export async function robokitStatus() {
  const r = await fetch(`${API_BASE}/robokit/status`)
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
export async function robokitPathNavigation(pathId) {
  const r = await fetch(`${API_BASE}/robokit/navigation/path`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path_id: pathId }),
  })
  return r.ok ? r.json() : null
}

export async function robokitStopNavigation() {
  const r = await fetch(`${API_BASE}/robokit/navigation/stop`, { method: 'POST' })
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
  return r.ok ? r.json() : null
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
