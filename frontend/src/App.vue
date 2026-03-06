<template>
  <div class="app">
    <div class="map-container" ref="mapContainerRef" @wheel.prevent="handleWheel" @mousedown="handlePanStart" @mousemove="handlePanMove" @mouseup="handlePanEnd" @mouseleave="handlePanEnd">
      <canvas ref="canvasRef"></canvas>
      <div class="map-controls">
        <button class="zoom-btn" @click="zoomIn" title="放大">+</button>
        <button class="zoom-btn" @click="zoomOut" title="缩小">−</button>
        <button class="zoom-btn reset-btn" @click="resetZoom" title="重置视图">⟲</button>
      </div>
    </div>
    <aside class="sidebar">
      <!-- 模式切换 -->
      <div class="mode-tabs">
        <button class="mode-tab" :class="{ active: activeMode === 'sim' }" @click="activeMode = 'sim'">
          模拟器
        </button>
        <button class="mode-tab" :class="{ active: activeMode === 'robot' }" @click="activeMode = 'robot'">
          机器人
        </button>
      </div>

      <!-- 模拟器面板 -->
      <template v-if="activeMode === 'sim'">
        <h2>AGV 调度系统 Demo</h2>
        <h3>控制</h3>
        <div class="control-row">
          <button class="success" @click="handleSimStart">启动模拟</button>
          <button class="danger" @click="handleSimStop">停止模拟</button>
        </div>
        <div class="control-row">
          <input type="file" ref="mapFileRef" accept=".json,.smap" style="display:none" @change="handleImportMap">
          <button class="import-btn" @click="mapFileRef?.click()">导入地图</button>
        </div>
      <h3>地图数据</h3>
      <div class="stat-card map-info">
        <div v-for="(val, key) in mapInfoRows" :key="key" class="data-row">
          <span class="data-label">{{ key }}:</span>
          <span class="data-value" :class="{ highlight: val.highlight }">{{ val.text }}</span>
        </div>
        <span v-if="!Object.keys(mapInfoRows).length">加载中...</span>
      </div>
      <h3>创建任务</h3>
      <p class="hint">AGV 只有接到任务才会移动</p>
      <div class="task-form">
        <input v-model="fromNode" placeholder="起点 (如 R1)">
        <input v-model="toNode" placeholder="终点 (如 D1)">
      </div>
      <button class="primary full" @click="handleCreateTask">创建任务</button>
      <button type="button" class="demo-btn" @click="fillDemoNodes">填充示例 R1→D1</button>
      <h3>车队状态</h3>
      <div class="stat-card fleet-status">
        <div class="fleet-header">
          <span>AGV</span>
          <span>位置</span>
        </div>
        <div v-for="agv in fleetData.agvs" :key="agv.id" class="agv-item">
          <span><span class="status-dot" :class="'status-' + (agv.status || 'idle')" :title="statusLabel(agv.status)"></span><strong>{{ agv.id }}</strong></span>
          <span class="node-id">{{ agv.current_node }}</span>
        </div>
        <span v-if="!fleetData.agvs?.length">加载中...</span>
        <div class="status-legend">
          <span class="legend-item"><span class="status-dot status-idle"></span>空闲</span>
          <span class="legend-item"><span class="status-dot status-moving"></span>移动中</span>
          <span class="legend-item"><span class="status-dot status-waiting"></span>等待</span>
          <span class="legend-item"><span class="status-dot status-error"></span>异常</span>
        </div>
      </div>
      <h3>任务列表</h3>
      <div class="stat-card task-list">
        <template v-if="tasks.length">
          <div v-for="t in tasks" :key="t.id">{{ t.id }}: {{ t.from_node }}→{{ t.to_node }} [{{ t.status }}]</div>
        </template>
        <span v-else>无任务</span>
      </div>
      <h3>日志</h3>
      <div class="log-panel">
        <div v-for="(entry, i) in logs" :key="i" class="log-entry" v-html="entry.html"></div>
      </div>
      </template>

      <!-- 机器人控制面板 -->
      <RobokitPanel v-if="activeMode === 'robot'" />
    </aside>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import * as api from './api'
import RobokitPanel from './components/RobokitPanel.vue'

const GRID = 50
const AGV_R = 14

const activeMode = ref('sim') // 'sim' 或 'robot'
const mapContainerRef = ref(null)
const canvasRef = ref(null)
const mapFileRef = ref(null)

const mapData = ref({ nodes: [], edges: [] })
const fleetData = ref({ agvs: [] })
const tasks = ref([])
const fromNode = ref('R1')
const toNode = ref('D1')
const logs = ref([])
const pollTimer = ref(null)

// 地图缩放与平移
const zoomLevel = ref(1)
const panX = ref(0)
const panY = ref(0)
const ZOOM_MIN = 0.3
const ZOOM_MAX = 3

const mapInfoRows = computed(() => {
  const data = mapData.value
  const imported = data.imported_data || {}
  const header = imported.header || {}
  const rows = {}
  if (header.mapName) rows['地图名称'] = { text: header.mapName, highlight: true }
  if (header.resolution) rows['分辨率'] = { text: header.resolution }
  if (header.version) rows['版本'] = { text: header.version }
  rows['节点数量'] = { text: (data.nodes || []).length }
  rows['边数量'] = { text: (data.edges || []).length }
  if (imported.advancedPointList) rows['advancedPointList'] = { text: `${imported.advancedPointList.length} 个节点`, highlight: true }
  if (imported.advancedCurveList) rows['advancedCurveList'] = { text: `${imported.advancedCurveList.length} 条边`, highlight: true }
  return rows
})

function statusLabel(status) {
  const map = { idle: '空闲', moving: '移动中', waiting: '等待', error: '异常' }
  return map[status || 'idle'] || status
}

function zoomIn() {
  zoomLevel.value = Math.min(ZOOM_MAX, zoomLevel.value + 0.25)
  render()
}

function zoomOut() {
  zoomLevel.value = Math.max(ZOOM_MIN, zoomLevel.value - 0.25)
  render()
}

function resetZoom() {
  zoomLevel.value = 1
  panX.value = 0
  panY.value = 0
  render()
}

function handleWheel(ev) {
  const delta = ev.deltaY > 0 ? -0.1 : 0.1
  zoomLevel.value = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, zoomLevel.value + delta))
  render()
}

// 拖拽平移
const isPanning = ref(false)
const panStartX = ref(0)
const panStartY = ref(0)
const panStartOffsetX = ref(0)
const panStartOffsetY = ref(0)

function handlePanStart(ev) {
  if (ev.button !== 0) return
  isPanning.value = true
  panStartX.value = ev.clientX
  panStartY.value = ev.clientY
  panStartOffsetX.value = panX.value
  panStartOffsetY.value = panY.value
}

function handlePanMove(ev) {
  if (!isPanning.value) return
  panX.value = panStartOffsetX.value + ev.clientX - panStartX.value
  panY.value = panStartOffsetY.value + ev.clientY - panStartY.value
  render()
}

function handlePanEnd() {
  isPanning.value = false
}

function log(msg) {
  const time = new Date().toLocaleTimeString()
  logs.value.unshift({ html: `<span class="log-time">[${time}]</span> ${msg}` })
}

async function loadMap() {
  const data = await api.fetchMap()
  if (data) mapData.value = data
}

async function loadFleet() {
  const data = await api.fetchFleet()
  if (data) fleetData.value = data
}

async function loadTasks() {
  const data = await api.fetchTasks()
  if (data) tasks.value = data.tasks || []
}

async function handleSimStart() {
  if (await api.simStart()) {
    log('模拟已启动')
    startPoll()
  }
}

async function handleSimStop() {
  if (await api.simStop()) {
    log('模拟已停止')
    stopPoll()
  }
}

function fillDemoNodes() {
  fromNode.value = 'R1'
  toNode.value = 'D1'
  log('已填充示例节点，请点击「创建」')
}

async function handleCreateTask() {
  const from = fromNode.value.trim()
  const to = toNode.value.trim()
  if (!from || !to) {
    log('请输入起点和终点')
    return
  }
  const data = await api.createTask(from, to)
  if (data.error) {
    log('创建失败: ' + (data.error || data.detail))
  } else {
    log(`任务已创建: ${from} -> ${to} (${data.assigned_agv_id || '待分配'})`)
    await loadTasks()
  }
}

async function handleImportMap(ev) {
  const file = ev.target.files?.[0]
  if (!file) return
  log('正在导入地图: ' + file.name)
  let data
  try {
    data = JSON.parse(await file.text())
  } catch {
    log('地图文件格式错误')
    ev.target.value = ''
    return
  }
  const hasAdvanced = data.advancedPointList && data.advancedCurveList
  if (hasAdvanced) {
    log(`检测到 advancedPointList (${data.advancedPointList.length}) 和 advancedCurveList (${data.advancedCurveList.length})`)
  } else {
    log('使用 normalPosList (兼容模式)')
  }
  const result = await api.importMap(data)
  if (result.success) {
    log(`<span class="highlight">地图导入成功: ${result.mapName}</span>`)
    log(`  - 节点: ${result.nodeCount}，边: ${result.edgeCount}`)
    await loadMap()
  } else {
    log('导入失败: ' + (result.error || result.detail))
  }
  ev.target.value = ''
}

function startPoll() {
  if (pollTimer.value) return
  pollTimer.value = setInterval(poll, 1000)
}

function stopPoll() {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

async function poll() {
  await loadMap()
  await loadFleet()
  await loadTasks()
}

function render() {
  const canvas = canvasRef.value
  const container = mapContainerRef.value
  if (!canvas || !container || !ctx) return
  const w = container.clientWidth
  const h = container.clientHeight
  canvas.width = w
  canvas.height = h
  ctx.clearRect(0, 0, w, h)

  const nodes = mapData.value.nodes || []
  const nodeMap = Object.fromEntries(nodes.map(n => [n.id, n]))
  const edges = mapData.value.edges || []
  const importedData = mapData.value.imported_data || {}
  const adjacency = mapData.value.adjacency || {}
  const agvs = fleetData.value.agvs || []

  // 检查是否有贝塞尔曲线数据
  const hasBezierCurves = importedData.advancedCurveList && 
    importedData.advancedCurveList.some(curve => curve.className === 'BezierPath')
  
  // 计算基础缩放比例（适应画布）
  const maxX = Math.max(...nodes.map(n => n.x), 1)
  const maxY = Math.max(...nodes.map(n => n.y), 1)
  const baseScale = nodes.length ? Math.min((w - 80) / (maxX * GRID), (h - 80) / (maxY * GRID)) || 1 : 1
  const scale = baseScale * zoomLevel.value
  const ox = 40 + panX.value
  const oy = 40 + panY.value
  const toX = x => ox + x * GRID * scale
  const toY = y => oy + y * GRID * scale

  // 绘制边（支持贝塞尔曲线）
  ctx.strokeStyle = '#2c3e50'
  ctx.lineWidth = 2
  
  // 如果有贝塞尔曲线数据，优先使用
  if (hasBezierCurves && importedData.advancedCurveList) {
    const curveMap = {}
    // 构建曲线映射
    importedData.advancedCurveList.forEach(curve => {
      const startPos = curve.startPos || {}
      const endPos = curve.endPos || {}
      const sourceId = startPos.instanceName
      const targetId = endPos.instanceName
      if (sourceId && targetId) {
        curveMap[`${sourceId}-${targetId}`] = curve
        curveMap[`${targetId}-${sourceId}`] = curve // 双向
      }
    })
    
    edges.forEach(e => {
      const fromN = nodeMap[e.from]
      const toN = nodeMap[e.to]
      if (!fromN || !toN) return
      
      const curve = curveMap[`${e.from}-${e.to}`]
      if (curve && curve.className === 'BezierPath') {
        // 绘制贝塞尔曲线
        const p0 = { x: toX(fromN.x), y: toY(fromN.y) }
        const p3 = { x: toX(toN.x), y: toY(toN.y) }
        
        const control1 = curve.controlPos1 || {}
        const control2 = curve.controlPos2 || {}
        
        // 控制点需要从地图坐标转换为画布坐标
        const p1 = { x: toX(parseFloat(control1.x || fromN.x)), y: toY(parseFloat(control1.y || fromN.y)) }
        const p2 = { x: toX(parseFloat(control2.x || toN.x)), y: toY(parseFloat(control2.y || toN.y)) }
        
        ctx.beginPath()
        ctx.moveTo(p0.x, p0.y)
        ctx.bezierCurveTo(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y)
        ctx.stroke()
      } else {
        // 绘制直线
        ctx.beginPath()
        ctx.moveTo(toX(fromN.x), toY(fromN.y))
        ctx.lineTo(toX(toN.x), toY(toN.y))
        ctx.stroke()
      }
    })
  } else {
    // 标准直线边
    edges.forEach(e => {
      const fromN = nodeMap[e.from]
      const toN = nodeMap[e.to]
      if (!fromN || !toN) return
      ctx.beginPath()
      ctx.moveTo(toX(fromN.x), toY(fromN.y))
      ctx.lineTo(toX(toN.x), toY(toN.y))
      ctx.stroke()
    })
  }

  // 绘制节点
  ctx.fillStyle = '#34495e'
  nodes.forEach(n => {
    // 根据节点类型设置不同颜色
    if (n.type) {
      // 根据节点类型设置颜色
      if (n.type.includes('Station') || n.type.includes('R')) {
        ctx.fillStyle = '#8e44ad' // 紫色 - 接收区
      } else if (n.type.includes('Conveyor') || n.type.includes('C')) {
        ctx.fillStyle = '#3498db' // 蓝色 - 传送带
      } else if (n.type.includes('Delivery') || n.type.includes('D')) {
        ctx.fillStyle = '#e67e22' // 橙色 - 配送区
      } else if (n.type.includes('Assembly') || n.type.includes('A')) {
        ctx.fillStyle = '#2ecc71' // 绿色 - 装配区
      } else {
        ctx.fillStyle = '#34495e' // 默认灰色
      }
    } else {
      ctx.fillStyle = '#34495e'
    }
    
    ctx.beginPath()
    ctx.arc(toX(n.x), toY(n.y), 6, 0, Math.PI * 2)
    ctx.fill()
    
    // 绘制节点标签
    ctx.fillStyle = '#95a5a6'
    ctx.font = '10px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText(n.id, toX(n.x), toY(n.y) + 18)
  })
  ctx.fillStyle = '#34495e' // 恢复默认填充颜色

  // 绘制AGV
  agvs.forEach(agv => {
    const n = nodeMap[agv.current_node]
    if (!n) return
    const px = toX(n.x), py = toY(n.y)
    
    // 绘制AGV圆圈
    ctx.fillStyle = agv.color || '#2ecc71'
    ctx.beginPath()
    ctx.arc(px, py, AGV_R, 0, Math.PI * 2)
    ctx.fill()
    
    // 绘制边框
    ctx.strokeStyle = '#fff'
    ctx.lineWidth = 2
    ctx.stroke()
    
    // 绘制AGV ID
    ctx.fillStyle = '#fff'
    ctx.font = 'bold 11px sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(agv.id.replace('AGV-', ''), px, py)
    
    // 如果AGV正在移动，绘制路径指示器
    if (agv.status === 'moving' && agv.path && agv.path.length > 0) {
      const nextNodeId = agv.path[0]
      const nextNode = nodeMap[nextNodeId]
      if (nextNode) {
        const nextX = toX(nextNode.x), nextY = toY(nextNode.y)
        
        // 绘制方向指示器
        ctx.strokeStyle = '#f39c12'
        ctx.lineWidth = 3
        ctx.beginPath()
        ctx.moveTo(px, py)
        
        // 计算方向向量
        const dx = nextX - px
        const dy = nextY - py
        const len = Math.sqrt(dx * dx + dy * dy)
        const dirX = dx / len
        const dirY = dy / len
        
        // 绘制箭头
        const arrowLen = 20
        const arrowEndX = px + dirX * arrowLen
        const arrowEndY = py + dirY * arrowLen
        ctx.lineTo(arrowEndX, arrowEndY)
        ctx.stroke()
        
        // 箭头头部
        const headLen = 8
        const headAngle = Math.PI / 6
        ctx.beginPath()
        ctx.moveTo(arrowEndX, arrowEndY)
        ctx.lineTo(
          arrowEndX - headLen * Math.cos(Math.atan2(dirY, dirX) - headAngle),
          arrowEndY - headLen * Math.sin(Math.atan2(dirY, dirX) - headAngle)
        )
        ctx.moveTo(arrowEndX, arrowEndY)
        ctx.lineTo(
          arrowEndX - headLen * Math.cos(Math.atan2(dirY, dirX) + headAngle),
          arrowEndY - headLen * Math.sin(Math.atan2(dirY, dirX) + headAngle)
        )
        ctx.stroke()
      }
    }
  })
}

let ctx = null

function initCanvas() {
  const canvas = canvasRef.value
  if (canvas) ctx = canvas.getContext('2d')
}

watch([mapData, fleetData, zoomLevel, panX, panY], () => render(), { deep: true })

onMounted(async () => {
  initCanvas()
  await loadMap()
  await loadFleet()
  await loadTasks()
  render()
  log('地图与车队已加载')
  window.addEventListener('resize', render)
})

onUnmounted(() => {
  stopPoll()
  window.removeEventListener('resize', render)
})
</script>

<style scoped>
.app {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #1a1a2e;
  color: #e0e0e0;
  font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
}
.map-container {
  flex: 1;
  position: relative;
  background: #16213e;
  overflow: hidden;
  border-right: 1px solid #0f3460;
  cursor: grab;
}
.map-container:active {
  cursor: grabbing;
}
canvas {
  display: block;
}
.map-controls {
  position: absolute;
  right: 16px;
  bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  z-index: 10;
}
.zoom-btn {
  width: 36px;
  height: 36px;
  padding: 0;
  background: rgba(15, 52, 96, 0.95);
  color: #00d9ff;
  border: 1px solid #2c3e50;
  border-radius: 6px;
  font-size: 20px;
  font-weight: 300;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}
.zoom-btn:hover {
  background: rgba(0, 217, 255, 0.2);
}
.zoom-btn.reset-btn {
  font-size: 18px;
  margin-top: 4px;
}
.sidebar {
  width: 380px;
  background: #0f3460;
  display: flex;
  flex-direction: column;
  padding: 16px;
  box-shadow: -4px 0 12px rgba(0,0,0,0.4);
  overflow-y: auto;
}

/* 模式切换标签 */
.mode-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #2c3e50;
}

.mode-tab {
  flex: 1;
  padding: 10px;
  background: rgba(0,0,0,0.2);
  color: #95a5a6;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

.mode-tab:hover {
  background: rgba(52, 152, 219, 0.2);
}

.mode-tab.active {
  background: #3498db;
  color: #fff;
  box-shadow: 0 0 12px rgba(52, 152, 219, 0.3);
}

h2 { margin: 0 0 16px; font-size: 18px; color: #00d9ff; }
h3 { font-size: 13px; color: #7f8c8d; margin: 12px 0 8px; padding-bottom: 6px; border-bottom: 1px solid #2c3e50; }
.hint { font-size: 11px; color: #95a5a6; margin: 0 0 8px; }
.stat-card {
  background: rgba(0,0,0,0.2);
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 12px;
  font-size: 13px;
}
.data-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 12px;
}
.data-label { color: #95a5a6; }
.data-value { color: #e0e0e0; font-weight: 500; }
.data-value.highlight { color: #00d9ff; font-weight: bold; }
.fleet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0 8px;
  margin-bottom: 4px;
  font-size: 11px;
  color: #95a5a6;
  border-bottom: 1px solid #2c3e50;
}
.agv-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding: 4px 0;
}
.agv-item .node-id {
  font-family: monospace;
  color: #00d9ff;
}
.status-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 16px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #2c3e50;
  font-size: 11px;
  color: #95a5a6;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.status-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 8px;
}
.status-idle { background: #f1c40f; }
.status-moving { background: #2ecc71; }
.status-waiting { background: #e67e22; }
.status-error { background: #e74c3c; }
.control-row { display: flex; gap: 8px; margin-bottom: 12px; }
button {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
}
button.primary { background: #3498db; color: #fff; }
button.primary:hover { background: #2980b9; }
button.success { background: #2ecc71; color: #fff; }
button.success:hover { background: #27ae60; }
button.danger { background: #e74c3c; color: #fff; }
button.danger:hover { background: #c0392b; }
button.import-btn { background: #9b59b6; color: #fff; }
button.import-btn:hover { background: #8e44ad; }
button.full { width: 100%; margin-bottom: 6px; }
button.demo-btn { background: #555; font-size: 11px; padding: 6px; }
.task-form { display: flex; gap: 8px; margin-bottom: 8px; }
.task-form input {
  flex: 1;
  padding: 8px;
  border: 1px solid #2c3e50;
  border-radius: 4px;
  background: #1a1a2e;
  color: #fff;
  font-size: 12px;
}
.log-panel {
  flex: 1;
  min-height: 100px;
  background: #0d1117;
  border: 1px solid #2c3e50;
  border-radius: 6px;
  padding: 10px;
  overflow-y: auto;
  font-family: 'Consolas', monospace;
  font-size: 11px;
  color: #8b949e;
}
.log-entry { margin-bottom: 4px; }
:deep(.log-time) { color: #484f58; margin-right: 6px; }
:deep(.highlight) { color: #00d9ff; font-weight: bold; }
</style>
