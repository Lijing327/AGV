<template>
  <div
    class="map-canvas"
    ref="containerRef"
    @wheel.prevent="handleWheel"
    @mousedown="handlePanStart"
    @mousemove="handleMouseMove"
    @mouseup="handlePanEnd"
    @mouseleave="handlePanEnd"
  >
    <canvas ref="canvasRef"></canvas>

    <!-- 缩放工具栏 -->
    <div class="map-toolbar">
      <button class="toolbar-btn" @click="zoomIn" title="放大">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
      </button>
      <span class="zoom-display">{{ (zoomLevel * 100).toFixed(0) }}%</span>
      <button class="toolbar-btn" @click="zoomOut" title="缩小">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3 8h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
      </button>
      <div class="toolbar-divider"></div>
      <button class="toolbar-btn" @click="resetView" title="适应全图">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 6V2h4M14 10v4h-4M2 2l5 5M14 14l-5-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </button>
    </div>

    <!-- 图层控制 -->
    <div class="layer-panel">
      <div class="layer-title">图层</div>
      <label class="layer-item">
        <input type="checkbox" v-model="layers.edges" /><span class="layer-dot" style="background:#3b82f6"></span>路径
      </label>
      <label class="layer-item">
        <input type="checkbox" v-model="layers.nodes" /><span class="layer-dot" style="background:#06b6d4"></span>站点
      </label>
      <label class="layer-item">
        <input type="checkbox" v-model="layers.labels" /><span class="layer-dot" style="background:#94a3b8"></span>标签
      </label>
      <label class="layer-item">
        <input type="checkbox" v-model="layers.directions" /><span class="layer-dot" style="background:#f59e0b"></span>方向
      </label>
      <label class="layer-item">
        <input type="checkbox" v-model="layers.agvs" /><span class="layer-dot" style="background:#10b981"></span>AGV
      </label>
    </div>

    <!-- 坐标显示 -->
    <div class="coord-display" v-if="cursorWorld">
      <span>X: {{ cursorWorld.x.toFixed(3) }}m</span>
      <span>Y: {{ cursorWorld.y.toFixed(3) }}m</span>
    </div>

    <!-- 节点悬停提示 -->
    <div class="node-tooltip" v-if="hoveredNode" :style="tooltipStyle">
      <div class="tooltip-title">{{ hoveredNode.id }}</div>
      <div class="tooltip-row"><span>类型</span><span>{{ pointTypeLabel(hoveredNode.type) }}</span></div>
      <div class="tooltip-row"><span>X</span><span>{{ hoveredNode.x.toFixed(3) }} m</span></div>
      <div class="tooltip-row"><span>Y</span><span>{{ hoveredNode.y.toFixed(3) }} m</span></div>
      <div class="tooltip-row" v-if="hoveredNode.dir != null"><span>方向</span><span>{{ (hoveredNode.dir * 180 / Math.PI).toFixed(1) }}°</span></div>
    </div>

    <!-- 空地图提示 -->
    <div v-if="!hasNodes" class="map-empty">
      <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
        <rect x="6" y="6" width="36" height="36" rx="4" stroke="#4a5568" stroke-width="2" stroke-dasharray="4 3"/>
        <path d="M18 24h12M24 18v12" stroke="#4a5568" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <p>暂无地图数据</p>
      <span>请导入 .smap 地图文件</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  mapData: { type: Object, default: () => ({ nodes: [], edges: [] }) },
  fleetData: { type: Object, default: () => ({ agvs: [] }) }
})

const AGV_R = 14
const ZOOM_MIN = 0.1
const ZOOM_MAX = 10
const NODE_HOVER_RADIUS = 12

const containerRef = ref(null)
const canvasRef = ref(null)
const zoomLevel = ref(1)
const panX = ref(0)
const panY = ref(0)
const isPanning = ref(false)
const panStartX = ref(0)
const panStartY = ref(0)
const panStartOffsetX = ref(0)
const panStartOffsetY = ref(0)
const cursorWorld = ref(null)
const hoveredNode = ref(null)
const tooltipPos = ref({ x: 0, y: 0 })
const viewInitialized = ref(false)

const layers = reactive({
  edges: true,
  nodes: true,
  labels: true,
  directions: true,
  agvs: true,
})

let ctx = null
// 视口变换参数（世界坐标 -> 画布像素）
let vpScale = 1
let vpOffsetX = 0
let vpOffsetY = 0

const hasNodes = computed(() => (props.mapData.nodes || []).length > 0)

const tooltipStyle = computed(() => ({
  left: tooltipPos.value.x + 16 + 'px',
  top: tooltipPos.value.y - 10 + 'px',
}))

const pointTypeColors = {
  LocationMark: '#3b82f6',
  ActionPoint: '#f97316',
  ParkPoint: '#10b981',
  ChargePoint: '#f59e0b',
  TransferLocation: '#8b5cf6',
  WorkLocation: '#ec4899',
}

function pointTypeLabel(type) {
  const labels = {
    LocationMark: '定位站点',
    ActionPoint: '动作点',
    ParkPoint: '停靠点',
    ChargePoint: '充电点',
    TransferLocation: '运输点',
    WorkLocation: '工作点',
  }
  return labels[type] || type || '未知'
}

function initCanvas() {
  const canvas = canvasRef.value
  if (canvas) ctx = canvas.getContext('2d')
}

function computeViewport(w, h) {
  const nodes = props.mapData.nodes || []
  const header = props.mapData.imported_data?.header || {}

  let minX, maxX, minY, maxY
  if (header.minPos && header.maxPos) {
    minX = header.minPos.x
    maxX = header.maxPos.x
    minY = header.minPos.y
    maxY = header.maxPos.y
  } else if (nodes.length) {
    minX = Math.min(...nodes.map(n => n.x))
    maxX = Math.max(...nodes.map(n => n.x))
    minY = Math.min(...nodes.map(n => n.y))
    maxY = Math.max(...nodes.map(n => n.y))
    const padX = (maxX - minX) * 0.1 || 10
    const padY = (maxY - minY) * 0.1 || 10
    minX -= padX; maxX += padX; minY -= padY; maxY += padY
  } else {
    minX = -10; maxX = 10; minY = -10; maxY = 10
  }

  const rangeX = maxX - minX || 1
  const rangeY = maxY - minY || 1
  const padding = 40

  const scaleX = (w - padding * 2) / rangeX
  const scaleY = (h - padding * 2) / rangeY
  const baseScale = Math.min(scaleX, scaleY)

  return { baseScale, minX, minY, maxX, maxY, rangeX, rangeY }
}

function worldToCanvas(wx, wy) {
  const x = (wx - vpMinX) * vpScale * zoomLevel.value + vpOffsetX + panX.value
  const y = (vpMaxY - wy) * vpScale * zoomLevel.value + vpOffsetY + panY.value
  return { x, y }
}

function canvasToWorld(cx, cy) {
  const wx = (cx - vpOffsetX - panX.value) / (vpScale * zoomLevel.value) + vpMinX
  const wy = vpMaxY - (cy - vpOffsetY - panY.value) / (vpScale * zoomLevel.value)
  return { x: wx, y: wy }
}

let vpMinX = 0, vpMaxY = 0

function resetView() {
  zoomLevel.value = 1
  panX.value = 0
  panY.value = 0
  viewInitialized.value = false
  render()
}

function zoomIn() {
  zoomLevel.value = Math.min(ZOOM_MAX, zoomLevel.value * 1.3)
}

function zoomOut() {
  zoomLevel.value = Math.max(ZOOM_MIN, zoomLevel.value / 1.3)
}

function handleWheel(ev) {
  const rect = containerRef.value.getBoundingClientRect()
  const cx = ev.clientX - rect.left
  const cy = ev.clientY - rect.top
  const worldBefore = canvasToWorld(cx, cy)

  const factor = ev.deltaY > 0 ? 0.9 : 1.1
  zoomLevel.value = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, zoomLevel.value * factor))

  const afterPos = worldToCanvas(worldBefore.x, worldBefore.y)
  panX.value += cx - afterPos.x
  panY.value += cy - afterPos.y
}

function handlePanStart(ev) {
  if (ev.button !== 0) return
  isPanning.value = true
  panStartX.value = ev.clientX
  panStartY.value = ev.clientY
  panStartOffsetX.value = panX.value
  panStartOffsetY.value = panY.value
}

function handleMouseMove(ev) {
  const rect = containerRef.value?.getBoundingClientRect()
  if (!rect) return
  const cx = ev.clientX - rect.left
  const cy = ev.clientY - rect.top

  if (isPanning.value) {
    panX.value = panStartOffsetX.value + ev.clientX - panStartX.value
    panY.value = panStartOffsetY.value + ev.clientY - panStartY.value
    render()
  }

  cursorWorld.value = canvasToWorld(cx, cy)
  tooltipPos.value = { x: cx, y: cy }

  const nodes = props.mapData.nodes || []
  const hitRadius = NODE_HOVER_RADIUS / (vpScale * zoomLevel.value)
  let found = null
  for (const n of nodes) {
    const dx = cursorWorld.value.x - n.x
    const dy = cursorWorld.value.y - n.y
    if (dx * dx + dy * dy < hitRadius * hitRadius) {
      found = n
      break
    }
  }
  hoveredNode.value = found
}

function handlePanEnd() {
  isPanning.value = false
}

function render() {
  const canvas = canvasRef.value
  const container = containerRef.value
  if (!canvas || !container || !ctx) return

  const dpr = window.devicePixelRatio || 1
  const w = container.clientWidth
  const h = container.clientHeight
  canvas.width = w * dpr
  canvas.height = h * dpr
  canvas.style.width = w + 'px'
  canvas.style.height = h + 'px'
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  ctx.clearRect(0, 0, w, h)

  const nodes = props.mapData.nodes || []
  const nodeMap = Object.fromEntries(nodes.map(n => [n.id, n]))
  const edges = props.mapData.edges || []
  const importedData = props.mapData.imported_data || {}
  const agvs = props.fleetData.agvs || []

  // 初始化视口
  const vp = computeViewport(w, h)
  vpScale = vp.baseScale
  vpMinX = vp.minX
  vpMaxY = vp.maxY

  if (!viewInitialized.value && nodes.length) {
    const padding = 40
    vpOffsetX = padding + (w - padding * 2 - vp.rangeX * vpScale) / 2
    vpOffsetY = padding + (h - padding * 2 - vp.rangeY * vpScale) / 2
    viewInitialized.value = true
  }

  const toX = wx => (wx - vpMinX) * vpScale * zoomLevel.value + vpOffsetX + panX.value
  const toY = wy => (vpMaxY - wy) * vpScale * zoomLevel.value + vpOffsetY + panY.value

  // 1. 路径层（advancedCurveList）
  if (layers.edges) {
    ctx.lineWidth = Math.max(1.5, 2 * zoomLevel.value)

    const curveList = importedData.advancedCurveList || []
    if (curveList.length) {
      const curveMap = {}
      curveList.forEach(curve => {
        const sn = curve.startPos?.instanceName
        const en = curve.endPos?.instanceName
        if (sn && en) {
          curveMap[`${sn}-${en}`] = curve
        }
      })

      const drawnEdges = new Set()
      edges.forEach(e => {
        const key = `${e.from}-${e.to}`
        if (drawnEdges.has(key)) return
        drawnEdges.add(key)

        const fromN = nodeMap[e.from]
        const toN = nodeMap[e.to]
        if (!fromN || !toN) return

        const curve = curveMap[key]
        ctx.strokeStyle = 'rgba(59, 130, 246, 0.5)'

        if (curve) {
          const cn = curve.className || ''
          const cp1 = curve.controlPos1
          const cp2 = curve.controlPos2
          if ((cn === 'BezierPath' || cn === 'DegenerateBezier') && cp1 && cp2) {
            ctx.beginPath()
            ctx.moveTo(toX(fromN.x), toY(fromN.y))
            ctx.bezierCurveTo(
              toX(cp1.x), toY(cp1.y),
              toX(cp2.x), toY(cp2.y),
              toX(toN.x), toY(toN.y)
            )
            ctx.stroke()
          } else {
            ctx.beginPath()
            ctx.moveTo(toX(fromN.x), toY(fromN.y))
            ctx.lineTo(toX(toN.x), toY(toN.y))
            ctx.stroke()
          }
        } else {
          ctx.beginPath()
          ctx.moveTo(toX(fromN.x), toY(fromN.y))
          ctx.lineTo(toX(toN.x), toY(toN.y))
          ctx.stroke()
        }
      })
    } else {
      ctx.strokeStyle = 'rgba(59, 130, 246, 0.4)'
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
  }

  // 4. 节点层
  if (layers.nodes) {
    const nodeRadius = Math.max(3, 5 * Math.min(zoomLevel.value, 2))

    nodes.forEach(n => {
      const nx = toX(n.x)
      const ny = toY(n.y)
      if (nx < -20 || nx > w + 20 || ny < -20 || ny > h + 20) return

      const color = pointTypeColors[n.type] || '#64748b'
      const isHovered = hoveredNode.value?.id === n.id

      // 外圈光晕
      if (isHovered) {
        ctx.fillStyle = color + '40'
        ctx.beginPath()
        ctx.arc(nx, ny, nodeRadius + 8, 0, Math.PI * 2)
        ctx.fill()
      }

      // 根据类型绘制不同形状
      ctx.fillStyle = color
      if (n.type === 'ActionPoint') {
        // 菱形
        const s = nodeRadius * 1.2
        ctx.beginPath()
        ctx.moveTo(nx, ny - s)
        ctx.lineTo(nx + s, ny)
        ctx.lineTo(nx, ny + s)
        ctx.lineTo(nx - s, ny)
        ctx.closePath()
        ctx.fill()
      } else if (n.type === 'ParkPoint') {
        // 圆角方形
        const s = nodeRadius
        ctx.beginPath()
        ctx.roundRect(nx - s, ny - s, s * 2, s * 2, s * 0.3)
        ctx.fill()
      } else if (n.type === 'ChargePoint') {
        // 三角形
        const s = nodeRadius * 1.3
        ctx.beginPath()
        ctx.moveTo(nx, ny - s)
        ctx.lineTo(nx + s * 0.87, ny + s * 0.5)
        ctx.lineTo(nx - s * 0.87, ny + s * 0.5)
        ctx.closePath()
        ctx.fill()
      } else {
        // 圆形（LocationMark 等）
        ctx.beginPath()
        ctx.arc(nx, ny, nodeRadius, 0, Math.PI * 2)
        ctx.fill()
      }

      // 节点描边
      ctx.strokeStyle = isHovered ? '#fff' : (color + '80')
      ctx.lineWidth = isHovered ? 2 : 1
      ctx.stroke()
    })
  }

  // 5. 方向箭头层
  if (layers.directions) {
    const arrowLen = Math.max(10, 16 * Math.min(zoomLevel.value, 2))
    ctx.strokeStyle = '#f59e0b'
    ctx.lineWidth = Math.max(1.5, 2 * Math.min(zoomLevel.value, 1.5))

    nodes.forEach(n => {
      if (n.dir == null || n.dir === 0) return
      const nx = toX(n.x)
      const ny = toY(n.y)
      if (nx < -20 || nx > w + 20 || ny < -20 || ny > h + 20) return

      // smap 中 dir 是世界坐标系角度(rad)，Y 轴取反
      const angle = -n.dir
      const endX = nx + Math.cos(angle) * arrowLen
      const endY = ny + Math.sin(angle) * arrowLen

      ctx.beginPath()
      ctx.moveTo(nx, ny)
      ctx.lineTo(endX, endY)
      ctx.stroke()

      const headLen = 5
      const headAngle = Math.PI / 6
      ctx.beginPath()
      ctx.moveTo(endX, endY)
      ctx.lineTo(endX - headLen * Math.cos(angle - headAngle), endY - headLen * Math.sin(angle - headAngle))
      ctx.moveTo(endX, endY)
      ctx.lineTo(endX - headLen * Math.cos(angle + headAngle), endY - headLen * Math.sin(angle + headAngle))
      ctx.stroke()
    })
  }

  // 6. 标签层
  if (layers.labels) {
    const fontSize = Math.max(9, 11 * Math.min(zoomLevel.value, 1.5))
    ctx.font = `500 ${fontSize}px 'Inter', sans-serif`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'top'

    nodes.forEach(n => {
      const nx = toX(n.x)
      const ny = toY(n.y)
      if (nx < -20 || nx > w + 20 || ny < -20 || ny > h + 20) return

      const color = pointTypeColors[n.type] || '#94a3b8'
      ctx.fillStyle = hoveredNode.value?.id === n.id ? '#fff' : color
      const offset = Math.max(8, 10 * Math.min(zoomLevel.value, 2))
      ctx.fillText(n.id, nx, ny + offset)
    })
  }

  // 7. AGV 层
  if (layers.agvs) {
    agvs.forEach(agv => {
      const n = nodeMap[agv.current_node]
      if (!n) return
      const px = toX(n.x)
      const py = toY(n.y)

      const agvColor = agv.color || '#10b981'

      ctx.fillStyle = agvColor + '25'
      ctx.beginPath()
      ctx.arc(px, py, AGV_R + 4, 0, Math.PI * 2)
      ctx.fill()

      ctx.fillStyle = agvColor
      ctx.beginPath()
      ctx.arc(px, py, AGV_R, 0, Math.PI * 2)
      ctx.fill()

      ctx.strokeStyle = 'rgba(255,255,255,0.8)'
      ctx.lineWidth = 2
      ctx.stroke()

      ctx.fillStyle = '#fff'
      ctx.font = "bold 11px 'Inter', sans-serif"
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(agv.id.replace('AGV-', ''), px, py)

      if (agv.status === 'moving' && agv.path?.length > 0) {
        const nextNode = nodeMap[agv.path[0]]
        if (nextNode) {
          const nextX = toX(nextNode.x)
          const nextY = toY(nextNode.y)
          const dx = nextX - px
          const dy = nextY - py
          const len = Math.sqrt(dx * dx + dy * dy)
          if (len > 0) {
            const dirX = dx / len
            const dirY = dy / len
            ctx.strokeStyle = '#f59e0b'
            ctx.lineWidth = 2.5
            ctx.beginPath()
            ctx.moveTo(px + dirX * AGV_R, py + dirY * AGV_R)
            ctx.lineTo(px + dirX * (AGV_R + 18), py + dirY * (AGV_R + 18))
            ctx.stroke()
          }
        }
      }
    })
  }
}

watch(
  [() => props.mapData, () => props.fleetData, zoomLevel, panX, panY, layers],
  () => render(),
  { deep: true }
)

onMounted(() => {
  initCanvas()
  render()
  window.addEventListener('resize', render)
})

onUnmounted(() => {
  window.removeEventListener('resize', render)
})
</script>

<style scoped>
.map-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  background: var(--bg-root);
  cursor: grab;
  overflow: hidden;
}
.map-canvas:active {
  cursor: grabbing;
}

canvas {
  display: block;
}

.map-toolbar {
  position: absolute;
  right: 16px;
  bottom: 16px;
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 4px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  z-index: 10;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition);
}
.toolbar-btn:hover {
  background: rgba(59, 130, 246, 0.15);
  color: var(--blue);
}

.zoom-display {
  font-size: 11px;
  font-family: var(--font-mono);
  color: var(--text-muted);
  min-width: 40px;
  text-align: center;
  user-select: none;
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  background: var(--border);
  margin: 0 2px;
}

/* 图层控制 */
.layer-panel {
  position: absolute;
  left: 12px;
  top: 12px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 8px 10px;
  z-index: 10;
  box-shadow: var(--shadow-md);
  min-width: 100px;
}
.layer-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 6px;
}
.layer-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 2px 0;
  user-select: none;
}
.layer-item input[type="checkbox"] {
  width: 14px;
  height: 14px;
  accent-color: var(--blue);
  cursor: pointer;
}
.layer-dot {
  width: 8px;
  height: 8px;
  border-radius: 2px;
  flex-shrink: 0;
}

/* 坐标显示 */
.coord-display {
  position: absolute;
  left: 12px;
  bottom: 16px;
  display: flex;
  gap: 12px;
  padding: 4px 10px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 11px;
  font-family: var(--font-mono);
  color: var(--text-muted);
  z-index: 10;
  user-select: none;
}

/* 节点提示 */
.node-tooltip {
  position: absolute;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  z-index: 20;
  box-shadow: var(--shadow-lg);
  pointer-events: none;
  min-width: 140px;
}
.tooltip-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
  font-family: var(--font-mono);
}
.tooltip-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 11px;
  padding: 1px 0;
}
.tooltip-row span:first-child {
  color: var(--text-muted);
}
.tooltip-row span:last-child {
  color: var(--text-primary);
  font-family: var(--font-mono);
}

.map-empty {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--text-muted);
  user-select: none;
}
.map-empty p {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-secondary);
}
.map-empty span {
  font-size: 13px;
}
</style>
