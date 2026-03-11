<template>
  <div class="sim-panel">
    <!-- 模拟控制 -->
    <div class="panel-section">
      <div class="section-header">
        <h3>模拟控制</h3>
      </div>
      <div class="section-body">
        <div class="btn-row">
          <button class="btn btn-green" @click="$emit('simStart')">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M3 2l9 5-9 5V2z" fill="currentColor"/></svg>
            启动模拟
          </button>
          <button class="btn btn-red" @click="$emit('simStop')">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><rect x="2" y="2" width="10" height="10" rx="1.5" fill="currentColor"/></svg>
            停止模拟
          </button>
        </div>
        <div class="import-group">
          <div class="import-row">
            <input
              v-model="importFilePath"
              class="path-input"
              type="text"
              placeholder="服务器文件路径，如 d:/xx/map.smap"
              @keyup.enter="handleImportFromPath"
            />
            <button class="btn btn-primary btn-sm" @click="handleImportFromPath" :disabled="!importFilePath.trim() || importing">
              {{ importing ? '导入中...' : '导入' }}
            </button>
          </div>
          <div class="import-divider">
            <span>或</span>
          </div>
          <button class="btn btn-outline full" @click="triggerImport" :disabled="importing">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M7 2v7M4 6l3 3 3-3M2 10v1.5A1.5 1.5 0 003.5 13h7a1.5 1.5 0 001.5-1.5V10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            浏览器选择文件
          </button>
        </div>
        <input type="file" ref="mapFileRef" accept=".json,.smap" style="display:none" @change="handleImportFile">
      </div>
    </div>

    <!-- 地图信息 -->
    <div class="panel-section">
      <div class="section-header" @click="mapInfoOpen = !mapInfoOpen">
        <h3>地图信息</h3>
        <span class="toggle-icon" :class="{ open: mapInfoOpen }">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M3 4.5l3 3 3-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </span>
      </div>
      <div class="section-body" v-show="mapInfoOpen">
        <div class="info-list" v-if="Object.keys(mapInfoRows).length">
          <div class="info-row" v-for="(val, key) in mapInfoRows" :key="key">
            <span class="info-key">{{ key }}</span>
            <span class="info-val" :class="{ accent: val.highlight }">{{ val.text }}</span>
          </div>
        </div>
        <div class="empty-hint" v-else>暂无地图数据</div>
      </div>
    </div>

    <!-- 任务管理 -->
    <div class="panel-section">
      <div class="section-header">
        <h3>任务管理</h3>
      </div>
      <div class="section-body">
        <div class="form-grid">
          <div class="form-field">
            <label>起点</label>
            <input v-model="fromNode" placeholder="如 R1" />
          </div>
          <div class="form-field">
            <label>终点</label>
            <input v-model="toNode" placeholder="如 D1" />
          </div>
        </div>
        <div class="btn-row">
          <button class="btn btn-blue full" @click="handleCreateTask">创建任务</button>
          <button class="btn btn-ghost" @click="fillDemoNodes">示例</button>
        </div>
        <div class="task-list" v-if="tasks.length">
          <div class="task-item" v-for="t in tasks" :key="t.id">
            <span class="task-id">#{{ t.id }}</span>
            <span class="task-route">{{ t.from_node }} → {{ t.to_node }}</span>
            <span class="task-status" :class="'task-' + t.status">{{ t.status }}</span>
          </div>
        </div>
        <div class="empty-hint" v-else>暂无任务</div>
      </div>
    </div>

    <!-- 车队状态 -->
    <div class="panel-section">
      <div class="section-header" @click="fleetOpen = !fleetOpen">
        <h3>车队状态</h3>
        <div class="badge" v-if="fleetData.agvs?.length">{{ fleetData.agvs.length }}</div>
        <span class="toggle-icon" :class="{ open: fleetOpen }">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M3 4.5l3 3 3-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </span>
      </div>
      <div class="section-body" v-show="fleetOpen">
        <div class="fleet-table" v-if="fleetData.agvs?.length">
          <div class="fleet-head">
            <span>AGV</span>
            <span>状态</span>
            <span>位置</span>
          </div>
          <div class="fleet-row" v-for="agv in fleetData.agvs" :key="agv.id">
            <span class="agv-name">
              <span class="status-dot" :class="'dot-' + (agv.status || 'idle')"></span>
              {{ agv.id }}
            </span>
            <span class="agv-status">{{ statusLabel(agv.status) }}</span>
            <span class="agv-node">{{ agv.current_node }}</span>
          </div>
        </div>
        <div class="empty-hint" v-else>暂无车队数据</div>
        <div class="status-legend">
          <span><span class="status-dot dot-idle"></span>空闲</span>
          <span><span class="status-dot dot-moving"></span>移动中</span>
          <span><span class="status-dot dot-waiting"></span>等待</span>
          <span><span class="status-dot dot-error"></span>异常</span>
        </div>
      </div>
    </div>

    <!-- 系统日志 -->
    <div class="panel-section log-section">
      <div class="section-header">
        <h3>系统日志</h3>
        <span class="log-count" v-if="logs.length">{{ logs.length }}</span>
      </div>
      <div class="log-panel">
        <div v-for="(entry, i) in logs" :key="i" class="log-entry" v-html="entry.html"></div>
        <div class="empty-hint" v-if="!logs.length">暂无日志</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  mapData: { type: Object, default: () => ({ nodes: [], edges: [] }) },
  fleetData: { type: Object, default: () => ({ agvs: [] }) },
  tasks: { type: Array, default: () => [] },
  logs: { type: Array, default: () => [] },
})

const emit = defineEmits(['simStart', 'simStop', 'createTask', 'importMap', 'importMapFromPath'])

const mapFileRef = ref(null)
const fromNode = ref('R1')
const toNode = ref('D1')
const mapInfoOpen = ref(true)
const fleetOpen = ref(true)
const importFilePath = ref('')
const importing = ref(false)

const mapInfoRows = computed(() => {
  const data = props.mapData
  const imported = data.imported_data || {}
  const header = imported.header || {}
  const rows = {}
  if (header.mapName) rows['地图名称'] = { text: header.mapName, highlight: true }
  if (header.resolution) rows['分辨率'] = { text: header.resolution + ' m' }
  if (header.version) rows['版本'] = { text: header.version }
  rows['导航节点'] = { text: (data.nodes || []).length }
  rows['路径连接'] = { text: (data.edges || []).length }

  // 按类型统计节点
  const nodes = data.nodes || []
  const typeCounts = {}
  nodes.forEach(n => {
    const t = n.type || 'Unknown'
    typeCounts[t] = (typeCounts[t] || 0) + 1
  })
  const typeLabels = {
    LocationMark: '定位站点',
    ActionPoint: '动作点',
    ParkPoint: '停靠点',
    ChargePoint: '充电点',
  }
  for (const [type, count] of Object.entries(typeCounts)) {
    const label = typeLabels[type] || type
    rows[label] = { text: count, highlight: true }
  }

  if (header.minPos && header.maxPos) {
    const w = (header.maxPos.x - header.minPos.x).toFixed(1)
    const h = (header.maxPos.y - header.minPos.y).toFixed(1)
    rows['地图范围'] = { text: `${w} × ${h} m` }
  }
  return rows
})

function statusLabel(status) {
  const map = { idle: '空闲', moving: '移动中', waiting: '等待', error: '异常' }
  return map[status || 'idle'] || status
}

function triggerImport() {
  mapFileRef.value?.click()
}

async function handleImportFile(ev) {
  const file = ev.target.files?.[0]
  if (!file) return
  importing.value = true
  try {
    const data = JSON.parse(await file.text())
    emit('importMap', { data, fileName: file.name })
  } catch {
    emit('importMap', { data: null, error: '文件格式错误' })
  }
  ev.target.value = ''
  importing.value = false
}

function handleImportFromPath() {
  const p = importFilePath.value.trim()
  if (!p) return
  importing.value = true
  emit('importMapFromPath', { path: p, callback: () => { importing.value = false } })
}

function handleCreateTask() {
  const from = fromNode.value.trim()
  const to = toNode.value.trim()
  emit('createTask', { from, to })
}

function fillDemoNodes() {
  fromNode.value = 'R1'
  toNode.value = 'D1'
}
</script>

<style scoped>
.sim-panel {
  display: flex;
  flex-direction: column;
  gap: 2px;
  height: 100%;
  overflow-y: auto;
  padding: 12px;
}

.panel-section {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  cursor: pointer;
  user-select: none;
  transition: background var(--transition);
}
.section-header:hover {
  background: rgba(255,255,255,0.02);
}
.section-header h3 {
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.toggle-icon {
  color: var(--text-muted);
  transition: transform var(--transition);
  display: flex;
}
.toggle-icon.open {
  transform: rotate(180deg);
}

.badge {
  font-size: 11px;
  font-weight: 600;
  color: var(--blue);
  background: rgba(59, 130, 246, 0.15);
  padding: 1px 7px;
  border-radius: 10px;
}

.section-body {
  padding: 0 14px 14px;
}

/* 按钮 */
.btn-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 500;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition);
  flex: 1;
}
.btn:hover { filter: brightness(1.1); }
.btn:active { transform: scale(0.98); }

.btn-green { background: var(--green); color: #fff; }
.btn-red { background: var(--red); color: #fff; }
.btn-blue { background: var(--blue); color: #fff; }
.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border);
  flex: 0;
  white-space: nowrap;
}
.btn-ghost:hover { border-color: var(--text-muted); color: var(--text-primary); }
.btn-outline {
  background: transparent;
  color: var(--text-secondary);
  border: 1px dashed var(--border-light);
}
.btn-outline:hover { border-color: var(--blue); color: var(--blue); }
.btn-primary {
  background: var(--blue);
  color: #fff;
}
.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
  flex: 0 0 auto;
}
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  filter: none;
}
.btn.full { width: 100%; }

.import-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.import-row {
  display: flex;
  gap: 6px;
  align-items: center;
}
.path-input {
  flex: 1;
  padding: 6px 10px;
  font-size: 12px;
  font-family: var(--font-mono, 'JetBrains Mono', monospace);
  background: var(--surface-low, #0d1117);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  outline: none;
  transition: border-color var(--transition);
}
.path-input::placeholder { color: var(--text-muted); }
.path-input:focus { border-color: var(--blue); }
.import-divider {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 2px 0;
}
.import-divider::before,
.import-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}
.import-divider span {
  font-size: 11px;
  color: var(--text-muted);
}

/* 表单 */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 8px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.form-field label {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.form-field input {
  padding: 7px 10px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 13px;
  font-family: var(--font-mono);
  transition: border-color var(--transition);
}
.form-field input:focus {
  outline: none;
  border-color: var(--blue);
}
.form-field input::placeholder {
  color: var(--text-muted);
}

/* 信息列表 */
.info-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  font-size: 13px;
}
.info-key { color: var(--text-muted); }
.info-val { color: var(--text-primary); font-family: var(--font-mono); font-size: 12px; }
.info-val.accent { color: var(--cyan); font-weight: 600; }

/* 任务列表 */
.task-list {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 160px;
  overflow-y: auto;
}
.task-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: var(--bg-overlay);
  border-radius: var(--radius-sm);
  font-size: 12px;
}
.task-id {
  color: var(--text-muted);
  font-family: var(--font-mono);
  min-width: 30px;
}
.task-route {
  flex: 1;
  color: var(--text-primary);
  font-family: var(--font-mono);
}
.task-status {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 10px;
}
.task-pending { background: rgba(245, 158, 11, 0.15); color: var(--yellow); }
.task-running { background: rgba(59, 130, 246, 0.15); color: var(--blue); }
.task-completed { background: rgba(16, 185, 129, 0.15); color: var(--green); }
.task-failed { background: rgba(239, 68, 68, 0.15); color: var(--red); }

/* 车队表格 */
.fleet-table {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.fleet-head {
  display: grid;
  grid-template-columns: 1fr 80px 60px;
  padding: 4px 0 8px;
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-bottom: 1px solid var(--border);
}
.fleet-row {
  display: grid;
  grid-template-columns: 1fr 80px 60px;
  align-items: center;
  padding: 7px 0;
  font-size: 13px;
  border-bottom: 1px solid rgba(30, 41, 59, 0.5);
}
.fleet-row:last-child { border-bottom: none; }

.agv-name {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-primary);
  font-weight: 500;
}
.agv-status { color: var(--text-secondary); font-size: 12px; }
.agv-node { color: var(--cyan); font-family: var(--font-mono); font-size: 12px; }

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}
.dot-idle { background: var(--yellow); }
.dot-moving { background: var(--green); }
.dot-waiting { background: var(--orange); }
.dot-error { background: var(--red); }

.status-legend {
  display: flex;
  gap: 14px;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid var(--border);
  font-size: 11px;
  color: var(--text-muted);
}
.status-legend span {
  display: flex;
  align-items: center;
  gap: 5px;
}

/* 日志 */
.log-section {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.log-count {
  font-size: 11px;
  color: var(--text-muted);
  font-family: var(--font-mono);
}
.log-panel {
  flex: 1;
  min-height: 80px;
  max-height: 180px;
  overflow-y: auto;
  padding: 8px 14px 14px;
  font-family: var(--font-mono);
  font-size: 11px;
  line-height: 1.6;
}
.log-entry {
  color: var(--text-muted);
  margin-bottom: 2px;
}
:deep(.log-time) { color: var(--text-muted); opacity: 0.6; margin-right: 6px; }
:deep(.highlight) { color: var(--cyan); font-weight: 600; }

.empty-hint {
  padding: 16px 0;
  text-align: center;
  font-size: 12px;
  color: var(--text-muted);
}
</style>
