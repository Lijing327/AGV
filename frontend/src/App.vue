<template>
  <div class="app-shell">
    <!-- ===== 顶部导航栏 ===== -->
    <header class="app-header">
      <div class="header-left">
        <div class="logo">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect x="2" y="8" width="24" height="14" rx="4" stroke="#3b82f6" stroke-width="2"/>
            <circle cx="8" cy="22" r="2.5" stroke="#3b82f6" stroke-width="1.5" fill="#0b0f19"/>
            <circle cx="20" cy="22" r="2.5" stroke="#3b82f6" stroke-width="1.5" fill="#0b0f19"/>
            <path d="M10 13h8M10 17h5" stroke="#3b82f6" stroke-width="1.5" stroke-linecap="round"/>
            <circle cx="21" cy="6" r="3" fill="#10b981"/>
          </svg>
        </div>
        <div class="header-title">
          <h1>AGV 调度管理系统</h1>
        </div>
      </div>

      <div class="header-center">
        <div class="mode-switcher">
          <button
            class="mode-btn"
            :class="{ active: activeMode === 'sim' }"
            @click="activeMode = 'sim'"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="1" y="3" width="14" height="10" rx="2" stroke="currentColor" stroke-width="1.4"/><path d="M5 8l2 2 4-4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
            模拟器
          </button>
          <button
            class="mode-btn"
            :class="{ active: activeMode === 'robot' }"
            @click="activeMode = 'robot'"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="4" y="2" width="8" height="6" rx="2" stroke="currentColor" stroke-width="1.4"/><path d="M3 10h10v3a2 2 0 01-2 2H5a2 2 0 01-2-2v-3z" stroke="currentColor" stroke-width="1.4"/><circle cx="6" cy="5" r="1" fill="currentColor"/><circle cx="10" cy="5" r="1" fill="currentColor"/></svg>
            机器人
          </button>
        </div>
      </div>

      <div class="header-right">
        <div class="header-metrics" v-if="activeMode === 'sim'">
          <div class="metric">
            <span class="metric-val">{{ (mapData.nodes || []).length }}</span>
            <span class="metric-label">节点</span>
          </div>
          <div class="metric">
            <span class="metric-val">{{ (fleetData.agvs || []).length }}</span>
            <span class="metric-label">AGV</span>
          </div>
          <div class="metric">
            <span class="metric-val">{{ tasks.length }}</span>
            <span class="metric-label">任务</span>
          </div>
        </div>
        <span class="header-clock">{{ currentTime }}</span>
      </div>
    </header>

    <!-- ===== 主内容区 ===== -->
    <main class="app-main">
      <!-- 地图区域 -->
      <div class="map-area">
        <MapCanvas :mapData="mapData" :fleetData="fleetData" :robotPosition="robotPosition" />
      </div>

      <!-- 右侧控制面板 -->
      <aside class="right-panel" :class="{ collapsed: panelCollapsed }">
        <button class="panel-toggle" @click="panelCollapsed = !panelCollapsed" :title="panelCollapsed ? '展开面板' : '收起面板'">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path :d="panelCollapsed ? 'M5 2l5 5-5 5' : 'M9 2l-5 5 5 5'" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <div class="panel-inner" v-show="!panelCollapsed">
          <SimPanel
            v-if="activeMode === 'sim'"
            :mapData="mapData"
            :fleetData="fleetData"
            :tasks="tasks"
            :logs="logs"
            @simStart="handleSimStart"
            @simStop="handleSimStop"
            @createTask="handleCreateTask"
            @importMap="handleImportMap"
            @importMapFromPath="handleImportMapFromPath"
          />
          <RobokitPanel v-if="activeMode === 'robot'" />
        </div>
      </aside>
    </main>

    <!-- ===== 底部状态栏 ===== -->
    <footer class="app-status">
      <div class="status-left">
        <span class="status-indicator" :class="{ online: systemOnline }"></span>
        <span class="status-text">{{ systemOnline ? '系统在线' : '系统就绪' }}</span>
      </div>
      <div class="status-center">
        <span class="status-msg" v-if="latestLog">{{ latestLog }}</span>
      </div>
      <div class="status-right">
        <span class="status-version">v0.0.1</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import * as api from './api'
import MapCanvas from './components/MapCanvas.vue'
import SimPanel from './components/SimPanel.vue'
import RobokitPanel from './components/RobokitPanel.vue'

const activeMode = ref('sim')
const panelCollapsed = ref(false)
const currentTime = ref('')

const mapData = ref({ nodes: [], edges: [] })
const fleetData = ref({ agvs: [] })
const tasks = ref([])
const logs = ref([])
const pollTimer = ref(null)
const robotPollTimer = ref(null)
const robotPosition = ref(null)
const systemOnline = ref(false)

const latestLog = computed(() => {
  if (!logs.value.length) return ''
  const e = logs.value[0]
  return typeof e === 'string' ? e : (e.text || e.html?.replace(/<[^>]*>/g, '') || '')
})

let clockTimer = null

function updateClock() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour12: false })
}

function log(msg) {
  const time = new Date().toLocaleTimeString()
  logs.value.unshift({ html: `<span class="log-time">[${time}]</span> ${msg}` })
  if (logs.value.length > 100) logs.value.length = 100
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
    systemOnline.value = true
    startPoll()
  }
}

async function handleSimStop() {
  if (await api.simStop()) {
    log('模拟已停止')
    systemOnline.value = false
    stopPoll()
  }
}

async function handleCreateTask({ from, to }) {
  if (!from || !to) { log('请输入起点和终点'); return }
  const data = await api.createTask(from, to)
  if (data.error) {
    log('创建失败: ' + (data.error || data.detail))
  } else {
    log(`任务已创建: ${from} → ${to} (${data.assigned_agv_id || '待分配'})`)
    await loadTasks()
  }
}

async function handleImportMap({ data, fileName, error }) {
  if (error || !data) { log('地图文件格式错误'); return }
  log('正在导入地图: ' + (fileName || ''))
  const hasAdvanced = data.advancedPointList && data.advancedCurveList
  if (hasAdvanced) {
    log(`检测到 advancedPointList (${data.advancedPointList.length}) 和 advancedCurveList (${data.advancedCurveList.length})`)
  }
  const result = await api.importMap(data)
  if (result.success) {
    log(`<span class="highlight">地图导入成功: ${result.mapName}</span>`)
    log(`  节点: ${result.nodeCount}，边: ${result.edgeCount}`)
    await loadMap()
  } else {
    log('导入失败: ' + (result.error || result.detail))
  }
}

async function handleImportMapFromPath({ path, callback }) {
  log('正在从服务器路径导入: ' + path)
  try {
    const result = await api.importMapFromFile(path)
    if (result.success) {
      log(`<span class="highlight">地图导入成功: ${result.mapName}</span>`)
      log(`  节点: ${result.nodeCount}，边: ${result.edgeCount}`)
      await loadMap()
    } else {
      log('导入失败: ' + (result.error || result.detail))
    }
  } catch (e) {
    log('导入异常: ' + e.message)
  }
  callback?.()
}

function startPoll() {
  if (pollTimer.value) return
  pollTimer.value = setInterval(async () => {
    await loadMap()
    await loadFleet()
    await loadTasks()
  }, 1000)
}

function stopPoll() {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

async function loadRobotPosition() {
  const pos = await api.robokitPosition()
  robotPosition.value = pos && (pos.x != null || pos.y != null) ? pos : null
}

function startRobotPoll() {
  if (robotPollTimer.value) return
  loadRobotPosition()
  robotPollTimer.value = setInterval(loadRobotPosition, 400)
}

function stopRobotPoll() {
  if (robotPollTimer.value) {
    clearInterval(robotPollTimer.value)
    robotPollTimer.value = null
  }
  robotPosition.value = null
}

watch(activeMode, (mode) => {
  if (mode === 'robot') startRobotPoll()
  else stopRobotPoll()
})

onMounted(async () => {
  updateClock()
  clockTimer = setInterval(updateClock, 1000)
  await loadMap()
  await loadFleet()
  await loadTasks()
  if (activeMode.value === 'robot') startRobotPoll()
  log('系统已初始化，地图与车队数据已加载')
})

onUnmounted(() => {
  stopPoll()
  stopRobotPoll()
  if (clockTimer) clearInterval(clockTimer)
})
</script>

<!-- 全局 CSS 变量（非 scoped） -->
<style>
:root {
  --bg-root: #0b0f19;
  --bg-surface: #111827;
  --bg-card: #151d2e;
  --bg-card-hover: #1c2640;
  --bg-input: #0d1321;
  --bg-overlay: rgba(0, 0, 0, 0.25);
  --border: #1e293b;
  --border-light: #2d3748;
  --border-active: #3b82f6;
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --blue: #3b82f6;
  --cyan: #06b6d4;
  --green: #10b981;
  --yellow: #f59e0b;
  --orange: #f97316;
  --red: #ef4444;
  --purple: #8b5cf6;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 8px rgba(0,0,0,0.3);
  --shadow-lg: 0 8px 24px rgba(0,0,0,0.4);
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --font-sans: 'Inter', 'Microsoft YaHei', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Consolas', 'Courier New', monospace;
  --transition: 0.2s ease;
  --header-h: 52px;
  --status-h: 32px;
  --panel-w: 460px;
}
</style>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg-root);
  color: var(--text-primary);
  font-family: var(--font-sans);
  overflow: hidden;
}

/* ===== Header ===== */
.app-header {
  height: var(--header-h);
  display: flex;
  align-items: center;
  padding: 0 20px;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 240px;
}
.logo { display: flex; align-items: center; }
.header-title h1 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}
.mode-switcher {
  display: flex;
  gap: 4px;
  padding: 3px;
  background: var(--bg-root);
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
}
.mode-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 18px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition);
}
.mode-btn:hover {
  color: var(--text-secondary);
  background: rgba(255,255,255,0.04);
}
.mode-btn.active {
  color: #fff;
  background: var(--blue);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
  min-width: 240px;
  justify-content: flex-end;
}
.header-metrics {
  display: flex;
  gap: 16px;
}
.metric {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
}
.metric-val {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-mono);
  line-height: 1;
}
.metric-label {
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.header-clock {
  font-size: 13px;
  font-family: var(--font-mono);
  color: var(--text-muted);
  min-width: 70px;
  text-align: right;
}

/* ===== Main ===== */
.app-main {
  flex: 1;
  display: flex;
  min-height: 0;
  overflow: hidden;
}

.map-area {
  flex: 1;
  min-width: 0;
  position: relative;
}

/* ===== Right Panel ===== */
.right-panel {
  width: var(--panel-w);
  background: var(--bg-surface);
  border-left: 1px solid var(--border);
  display: flex;
  flex-shrink: 0;
  position: relative;
  transition: width 0.3s ease, margin 0.3s ease;
}
.right-panel.collapsed {
  width: 0;
  border-left: none;
}

.panel-toggle {
  position: absolute;
  left: -14px;
  top: 50%;
  transform: translateY(-50%);
  width: 28px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 8px 0 0 8px;
  color: var(--text-muted);
  cursor: pointer;
  z-index: 10;
  transition: all var(--transition);
}
.panel-toggle:hover {
  color: var(--text-secondary);
  background: var(--bg-card);
}

.panel-inner {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

/* ===== Status Bar ===== */
.app-status {
  height: var(--status-h);
  display: flex;
  align-items: center;
  padding: 0 16px;
  background: var(--bg-surface);
  border-top: 1px solid var(--border);
  font-size: 12px;
  flex-shrink: 0;
  gap: 16px;
}

.status-left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 120px;
}
.status-indicator {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--text-muted);
}
.status-indicator.online {
  background: var(--green);
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.5);
}
.status-text {
  color: var(--text-muted);
}

.status-center {
  flex: 1;
  overflow: hidden;
}
.status-msg {
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-size: 11px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}

.status-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
.status-version {
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-size: 11px;
  opacity: 0.6;
}
</style>
