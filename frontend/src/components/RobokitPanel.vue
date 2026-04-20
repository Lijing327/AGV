<template>
  <div class="robokit-panel" :class="{ 'robokit-panel--offline': !connectionStatus.connected }">
    <!-- 连接状态头部 -->
    <div class="conn-header">
      <div class="conn-status-row">
        <span class="conn-dot" :class="{ online: connectionStatus.connected }"></span>
        <span class="conn-text">{{ connectionStatus.connected ? '已连接' : '离线' }}</span>
        <span class="conn-host" v-if="connectionStatus.connected">{{ connectionStatus.host }}</span>
        <button
          class="conn-btn"
          type="button"
          :class="{ disconnect: connectionStatus.connected }"
          :disabled="loading"
          @click="handleToggleConnection"
        >
          {{ connectionStatus.connected ? '断开' : loading ? '连接中…' : '连接' }}
        </button>
      </div>
      <!-- 连接表单 -->
      <div class="conn-form" v-if="!connectionStatus.connected">
        <div class="conn-inputs">
          <div class="form-field">
            <label>IP 地址</label>
            <input v-model="connectForm.host" placeholder="172.16.11.211" />
          </div>
          <div class="form-field">
            <label>端口</label>
            <input v-model="connectForm.port" type="number" placeholder="19204" />
          </div>
        </div>
        <button class="btn btn-blue full" type="button" :disabled="loading" @click="handleConnect">
          {{ loading ? '连接中…' : '连接机器人' }}
        </button>
      </div>
    </div>

    <div v-if="!connectionStatus.connected" class="offline-banner" role="status">
      离线模式：可进入各页查看与编辑参数；连接机器人后方可下发指令与轮询状态。
    </div>

    <!-- 主界面（未连接时亦可浏览，为离线配置） -->
    <div class="group-tabs">
      <button
        v-for="g in groups"
        :key="g.id"
        class="group-tab"
        :class="{ active: activeGroup === g.id }"
        @click="activeGroup = g.id"
      >
        <span class="tab-icon" v-html="g.icon"></span>
        <span class="tab-label">{{ g.name }}</span>
      </button>
    </div>

    <div class="panel-main">
      <div class="panel-content">
        <OverviewPanel v-if="activeGroup === 'overview'" />
        <ControlPanel v-if="activeGroup === 'control'" />
        <MonitorPanel v-if="activeGroup === 'monitor'" />
        <NavigationPanel v-if="activeGroup === 'navigation'" />
      </div>
      <div class="log-section">
        <div class="log-head">
          <h4>操作日志</h4>
          <span class="log-count" v-if="logs.length">{{ logs.length }}</span>
        </div>
        <div class="log-list">
          <template v-if="logs.length">
            <div
              v-for="(entry, i) in logs"
              :key="i"
              class="log-entry"
              :class="{ error: entry.error, success: entry.success }"
            >
              <span class="log-time">[{{ entry.time }}]</span>
              <span class="log-msg">{{ entry.message }}</span>
            </div>
          </template>
          <div v-else class="empty-hint">暂无日志</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRobokit } from "../composables/useRobokit.js"
import OverviewPanel from "./panels/OverviewPanel.vue"
import ControlPanel from "./panels/ControlPanel.vue"
import MonitorPanel from "./panels/MonitorPanel.vue"
import NavigationPanel from "./panels/NavigationPanel.vue"

const {
  api,
  groups,
  activeGroup,
  connectionStatus,
  loading,
  pollTimer,
  moveHeartbeatTimer,
  connectForm,
  robotInfo,
  locationInfo,
  speedInfo,
  batteryInfo,
  emergencyInfo,
  ioInfo,
  navStatusInfo,
  binsInfo,
  motorInfo,
  laserInfo,
  encoderInfo,
  slamInfo,
  modbusResult,
  modbusRegisters,
  moveForm,
  controlNickname,
  relocateForm,
  translateForm,
  planPathForm,
  oneKeyForm,
  oneKeyPreviewJson,
  navForm,
  planPathLastRoute,
  specPath3066PreviewJson,
  specPath3066PreviewError,
  specPath3066PreviewContinuityWarnings,
  tasklistResult,
  tasklistStatusHint,
  simpleBattery,
  logs,
  locMethodText,
  slamStatusText,
  log,
  sleep,
  findDiEntry,
  parseForkDiIdList,
  forkDiSignalsAnyReady,
  forkDiSignalsAllReady,
  forkDiSignalsReady,
  resolveDiCombineMode,
  waitForForkDiReady,
  waitForForkDiReadyAtPickup,
  normalizeLocationFromApi,
  isRobotAtStation,
  waitForNavigationTaskCompleted,
  mergeForkNumericFromPickDropLoad,
  monitorPickLegForDiOrArrival,
  FORK_NUMERIC_KEYS,
  mergeForkNumericFromSeg,
  applyPlanPathForkDefaultsToSegments,
  mergeForkNumericFromForm,
  mergeOneKeyForkNumeric,
  runPreDeliverySetForkHeight,
  sendMoveTaskListBy3051,
  sendTwoLegBy3051Self,
  mergeForkNumericFromPathNavForm,
  getSegmentContinuityWarnings,
  buildMoveTaskListFromSegments,
  updateSpecPath3066Preview,
  copySpecPath3066Preview,
  refreshOneKeyPreview,
  handleOneKeyCarryPickOnly,
  handleOneKeyCarryDropOnly,
  handleOneKeyCarry,
  formatRobokitError,
  handleConnect,
  handleDisconnect,
  handleToggleConnection,
  loadAllStatus,
  loadRobotInfo,
  loadLocation,
  loadSpeed,
  loadBattery,
  loadEmergency,
  loadIO,
  loadNavStatus,
  loadBins,
  loadMotor,
  loadLaser,
  loadEncoder,
  loadSlam,
  handleQueryModbus,
  handleTakeControl,
  handleReleaseControl,
  handleSetMode,
  handleMove,
  handleStop,
  fillRelocateFromCurrent,
  handleRelocate,
  handleConfirmLocation,
  handleCancelRelocate,
  handleTranslate,
  handleEmergencyStop,
  handleQuickRelocate,
  handleMoveTo,
  pathNavForkStatusPreferToApi,
  applyNavFormForkStateWait,
  handlePathNav6040SetHeight,
  handlePathNav6040Quick,
  handlePathNav6040DownZero,
  handlePathNavigation,
  handlePlanPath,
  addSpecifiedSegment,
  removeSpecifiedSegment,
  handleSpecifiedPathNavigation,
  handleStopNavigation,
  handlePauseNavigation,
  handleResumeNavigation,
  handleCancelNavigation,
  handleTurn,
  handleSpin,
  handleCircular,
  handlePathEnable,
  handleClearTargetList,
  handleClearByTaskId,
  TASKLIST_STATUS_MAP,
  handleGetTasklistStatus,
  handleGetTasklistList,
  handleExecuteTasklist,
  handleGetTargetPath,
  startPoll,
  stopPoll,
  stopMoveHeartbeat
} = useRobokit()
</script>

<style>
.robokit-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* 连接头部 */
.conn-header {
  padding: 12px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.conn-status-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.conn-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--red);
  flex-shrink: 0;
}
.conn-dot.online {
  background: var(--green);
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}
.conn-text { font-size: 13px; color: var(--text-secondary); }
.conn-host { flex: 1; font-size: 12px; color: var(--text-muted); font-family: var(--font-mono); }
.conn-btn {
  padding: 5px 14px; font-size: 12px; font-weight: 500;
  border: none; border-radius: var(--radius-sm);
  cursor: pointer; background: var(--blue); color: #fff;
  transition: all var(--transition);
}
.conn-btn:hover { filter: brightness(1.1); }
.conn-btn.disconnect { background: var(--red); }
.conn-form { margin-top: 12px; }
.conn-inputs {
  display: grid; grid-template-columns: 2fr 1fr; gap: 8px; margin-bottom: 10px;
}

.offline-banner {
  padding: 8px 12px;
  font-size: 12px;
  line-height: 1.45;
  color: var(--yellow);
  background: rgba(245, 158, 11, 0.08);
  border-bottom: 1px solid rgba(245, 158, 11, 0.25);
  flex-shrink: 0;
}

/* 分组Tab */
.group-tabs {
  display: flex; gap: 2px; padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.group-tab {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 3px;
  padding: 8px 4px; border: none; border-radius: var(--radius-sm);
  background: transparent; color: var(--text-muted);
  cursor: pointer; font-size: 11px; font-weight: 500;
  transition: all var(--transition);
}
.group-tab:hover { background: rgba(255,255,255,0.04); color: var(--text-secondary); }
.group-tab.active { background: rgba(59, 130, 246, 0.12); color: var(--blue); }
.tab-icon { display: flex; }
.tab-label { white-space: nowrap; }

/* 主区域：上可滚动内容，下固定日志 */
.panel-main {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 内容区 */
.panel-content {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 12px;
  min-width: 0;
}
.group-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 0;
  animation: fadeSlide 0.2s ease;
}
@keyframes fadeSlide {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 卡片 */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 14px;
  min-width: 0;
}
.card-head {
  display: flex; align-items: center; gap: 8px; margin-bottom: 12px;
}
.card-head h4 {
  flex: 1; font-size: 13px; font-weight: 600; color: var(--text-secondary);
}
.card-hint {
  font-size: 11px; color: var(--text-muted); margin: -8px 0 10px; line-height: 1.5;
}
.card-hint.card-warn {
  color: var(--yellow); margin-top: 6px; margin-bottom: 8px;
}
.card-hint.card-error {
  color: var(--red); margin-top: 4px; margin-bottom: 8px; font-size: 11px;
}
.card-hint code {
  background: var(--bg-overlay); padding: 1px 6px; border-radius: 4px; font-size: 11px;
}
.priority-card { border-color: rgba(59, 130, 246, 0.3); }

.icon-btn {
  display: flex; align-items: center; justify-content: center;
  width: 28px; height: 28px; border: none; border-radius: var(--radius-sm);
  background: transparent; color: var(--text-muted); cursor: pointer;
  transition: all var(--transition);
}
.icon-btn:hover { background: rgba(255,255,255,0.06); color: var(--text-secondary); }
.icon-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* KV 网格 */
.kv-grid {
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px 16px;
}
.kv-grid.compact { gap: 6px 12px; }
.kv-item {
  display: flex; justify-content: space-between; align-items: center; font-size: 13px;
}
.kv-key { color: var(--text-muted); font-size: 12px; }
.kv-val { color: var(--text-primary); font-family: var(--font-mono); font-size: 12px; }
.kv-val.accent { color: var(--cyan); font-weight: 600; }
.kv-val.charging { color: var(--green); }
.kv-val.err-code { color: var(--red); }

/* 位置网格 */
.pos-grid {
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;
}
.pos-item {
  display: flex; align-items: baseline; gap: 6px;
  padding: 6px 10px; background: var(--bg-overlay); border-radius: var(--radius-sm);
}
.pos-item.main { background: rgba(6, 182, 212, 0.08); }
.pos-label { font-size: 11px; color: var(--text-muted); min-width: 32px; }
.pos-value { font-size: 14px; font-weight: 600; color: var(--text-primary); font-family: var(--font-mono); }
.pos-value.accent { color: var(--cyan); }
.pos-unit { font-size: 11px; color: var(--text-muted); }

/* 速度 */
.speed-row {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;
}
.speed-item {
  display: flex; flex-direction: column; align-items: center;
  padding: 10px; background: var(--bg-overlay); border-radius: var(--radius-sm);
}
.speed-label { font-size: 11px; color: var(--text-muted); margin-bottom: 4px; }
.speed-val { font-size: 16px; font-weight: 600; color: var(--text-primary); font-family: var(--font-mono); }
.speed-unit { font-size: 10px; color: var(--text-muted); margin-top: 2px; }
.speed-badge {
  font-size: 11px; font-weight: 500; padding: 2px 10px; border-radius: 10px;
  background: rgba(16, 185, 129, 0.15); color: var(--green);
}
.speed-badge.stopped { background: rgba(239, 68, 68, 0.15); color: var(--red); }

/* 表单 */
.form-field { display: flex; flex-direction: column; gap: 4px; }
.form-field.compact { gap: 3px; }
.form-field label {
  font-size: 11px; font-weight: 500; color: var(--text-muted);
  text-transform: uppercase; letter-spacing: 0.04em;
}
.form-field input, .form-field select {
  padding: 7px 10px; background: var(--bg-input); border: 1px solid var(--border);
  border-radius: var(--radius-sm); color: var(--text-primary);
  font-size: 13px; font-family: var(--font-mono); transition: border-color var(--transition);
  box-sizing: border-box; min-width: 0; width: 100%;
}
.form-field input:focus, .form-field select:focus { outline: none; border-color: var(--blue); }
.form-field input::placeholder { color: var(--text-muted); }
.form-field select { cursor: pointer; }
.json-textarea {
  width: 100%; padding: 8px 10px; background: var(--bg-input); border: 1px solid var(--border);
  border-radius: var(--radius-sm); color: var(--text-primary); font-size: 12px; font-family: var(--font-mono);
  resize: vertical; min-height: 60px;
}
.tasklist-result {
  margin-top: 10px; padding: 10px; background: var(--bg-overlay); border-radius: var(--radius-sm);
  max-height: 200px; overflow: auto;
}
.tasklist-hint {
  font-size: 12px; color: var(--cyan); margin-bottom: 8px; font-weight: 500;
}
.tasklist-result pre { margin: 0; font-size: 11px; color: var(--text-muted); white-space: pre-wrap; word-break: break-all; }

.specified-segment {
  padding: 10px 0; border-bottom: 1px solid var(--border);
}
.specified-segment:last-of-type { border-bottom: none; }
.multi-segment-label {
  font-size: 12px; font-weight: 600; color: var(--blue);
  margin-bottom: 8px; padding-bottom: 4px;
}
.segment-head { font-size: 11px; color: var(--text-muted); margin-bottom: 6px; font-weight: 600; }
.segment-actions { display: flex; align-items: flex-end; }
.btn.small { padding: 4px 8px; font-size: 11px; }

.input-row-2 { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 8px; margin-bottom: 10px; }
.input-row-3 { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr); gap: 8px; margin-bottom: 10px; }
.input-row-4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; margin-bottom: 10px; }

.fork-nav-options { margin: 10px 0; display: flex; flex-direction: column; gap: 8px; }
.fork-check {
  display: flex; align-items: flex-start; gap: 8px; font-size: 12px; color: var(--text-secondary);
  cursor: pointer; line-height: 1.45;
}
.fork-check input { margin-top: 3px; flex-shrink: 0; }
.fork-nav-hint { margin: 0 !important; }
.fork-mode-select {
  width: 100%; padding: 8px 10px; background: var(--bg-input); border: 1px solid var(--border);
  border-radius: var(--radius-sm); color: var(--text-primary); font-size: 13px;
}
.fork-di-row { margin-top: 4px; }
.fork-height-row { margin-bottom: 8px; }
.fork-3051-heights { margin-top: 6px; }
.path-nav-fork-state {
  padding: 8px 0 2px;
  border-top: 1px solid var(--border-subtle, #2a3344);
  margin-top: 8px;
}
.path-nav-fork-state .compact-hint { margin-top: 6px !important; }
.path-nav-6040-block {
  padding: 10px 0 4px;
  border-top: 1px solid var(--border-subtle, #2a3344);
  margin-top: 6px;
}
.path-nav-6040-block .compact-hint { margin: 0 0 6px 0 !important; font-size: 11px; line-height: 1.45; }
.path-nav-6040-row { margin-bottom: 4px; }
.path-nav-6040-actions .btn { width: 100%; }
.path-nav-6040-quick {
  display: flex; flex-wrap: wrap; align-items: center; gap: 6px;
  margin-bottom: 6px;
}
.path-nav-6040-quick .quick-label {
  font-size: 11px; color: var(--text-muted);
  flex: 0 0 auto;
  min-width: 7em;
}
.readonly-input {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid var(--border-subtle, #2a3344);
  border-radius: 6px;
  background: var(--bg-muted, rgba(0, 0, 0, 0.2));
  color: var(--text-muted, #8b96a8);
  font-size: 12px;
}
.muted-label { color: var(--text-muted, #8b96a8); }

.plan-3066-preview {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--border);
}
.plan-preview-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 6px;
}
.plan-preview-title {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}
.plan-preview-btns { display: flex; gap: 6px; flex-wrap: wrap; }
.plan-preview-btns .btn { flex: 0 0 auto; }
.plan-preview-desc { margin-top: 0 !important; margin-bottom: 8px !important; }
.plan-route-line {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0 0 8px;
  line-height: 1.5;
}
.plan-preview-warns {
  margin: 0 0 8px;
  padding-left: 18px;
  font-size: 12px;
  color: var(--orange);
}
.plan-preview-ta { font-size: 11px; margin-top: 0; min-height: 200px; }
.plan-fork-hint { margin-top: 10px !important; margin-bottom: 6px !important; }
.plan-fork-defaults { margin-bottom: 6px; }

.ctrl-form-row { margin-bottom: 10px; }
.ctrl-btns { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }

.btn-row-2 { display: flex; gap: 8px; }
.one-key-split-btns { margin-bottom: 6px; }
.btn-wrap { display: flex; flex-wrap: wrap; gap: 6px; }

/* 按钮 */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  padding: 8px 14px; font-size: 13px; font-weight: 500;
  border: none; border-radius: var(--radius-sm);
  cursor: pointer; transition: all var(--transition); flex: 1;
}
.btn:hover { filter: brightness(1.1); }
.btn:active { transform: scale(0.98); }
.btn:disabled { opacity: 0.4; cursor: not-allowed; }
.btn.full { width: 100%; }

.btn-blue { background: var(--blue); color: #fff; }
.btn-green { background: var(--green); color: #fff; }
.btn-red { background: var(--red); color: #fff; }
.btn-orange { background: var(--orange); color: #fff; }
.btn-ghost { background: transparent; color: var(--text-secondary); border: 1px solid var(--border); }
.btn-ghost:hover { border-color: var(--text-muted); }
.btn-ghost-sm {
  background: transparent; color: var(--text-muted); border: 1px solid var(--border);
  font-size: 12px; padding: 5px 10px; flex: 0 0 auto;
}
.btn-ghost-sm:hover { border-color: var(--text-secondary); color: var(--text-secondary); }
.btn-blue-outline { background: transparent; color: var(--blue); border: 1px solid rgba(59,130,246,0.3); }
.btn-blue-outline:hover { background: rgba(59,130,246,0.1); }
.btn-green-outline { background: transparent; color: var(--green); border: 1px solid rgba(16,185,129,0.3); }
.btn-green-outline:hover { background: rgba(16,185,129,0.1); }

/* 电池 */
.battery-visual {
  display: flex; align-items: center; gap: 12px; margin-bottom: 12px;
}
.battery-bar {
  flex: 1; height: 24px; background: var(--bg-overlay);
  border-radius: 4px; overflow: hidden; border: 1px solid var(--border);
}
.battery-fill {
  height: 100%; background: linear-gradient(90deg, var(--green), var(--yellow));
  border-radius: 3px; transition: width 0.5s ease;
}
.battery-fill.low { background: var(--red); }
.battery-pct { font-size: 16px; font-weight: 700; color: var(--text-primary); font-family: var(--font-mono); min-width: 48px; }

/* 急停 */
.emc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px; }
.emc-item {
  display: flex; justify-content: space-between; padding: 10px;
  background: rgba(16, 185, 129, 0.06); border-radius: var(--radius-sm);
  font-size: 13px; color: var(--text-secondary);
}
.emc-item span:last-child { font-weight: 500; color: var(--green); }
.emc-item.danger { background: rgba(239, 68, 68, 0.1); }
.emc-item.danger span:last-child { color: var(--red); }
.emc-item.active span:last-child { color: var(--cyan); }

/* I/O */
.io-group { margin-bottom: 12px; }
.io-group h5 { font-size: 11px; color: var(--text-muted); margin-bottom: 6px; font-weight: 600; }
.io-chips { display: flex; flex-wrap: wrap; gap: 4px; }
.io-chip {
  padding: 4px 8px; background: var(--bg-overlay); border-radius: 4px;
  font-size: 11px; color: var(--text-muted); font-family: var(--font-mono);
}
.io-chip em { font-style: normal; margin-left: 4px; }
.io-chip.on { background: rgba(16, 185, 129, 0.12); color: var(--green); }
.io-chip.on em { font-weight: 600; }
.io-chip.invalid { opacity: 0.4; }

/* 电机 */
.motor-card {
  background: var(--bg-overlay); border-radius: var(--radius-sm);
  padding: 10px; margin-bottom: 8px;
}
.motor-head {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;
  font-size: 13px; color: var(--text-primary); font-weight: 500;
}
.motor-badge {
  font-size: 11px; padding: 2px 8px; border-radius: 10px;
  background: rgba(239, 68, 68, 0.15); color: var(--red);
}
.motor-badge.enabled { background: rgba(16, 185, 129, 0.15); color: var(--green); }

/* 编码器 */
.enc-section { margin-bottom: 10px; }
.enc-section h5 { font-size: 11px; color: var(--text-muted); margin-bottom: 6px; font-weight: 600; }
.enc-chips { display: flex; flex-wrap: wrap; gap: 4px; }
.enc-chip {
  padding: 4px 8px; background: var(--bg-overlay); border-radius: 4px;
  font-size: 12px; color: var(--cyan); font-family: var(--font-mono);
}
.enc-chip em { font-style: normal; color: var(--text-muted); margin-right: 4px; }

/* 激光 */
.laser-mini {
  width: 100%; height: 120px; background: var(--bg-overlay);
  border-radius: var(--radius-sm); position: relative; overflow: hidden;
}
.laser-dot {
  position: absolute; width: 2px; height: 2px;
  background: var(--cyan); border-radius: 50%; transform: translate(-50%, -50%);
}

/* 库位 */
.bins-grid { display: flex; flex-wrap: wrap; gap: 6px; }
.bin-chip {
  padding: 6px 10px; background: var(--bg-overlay); border: 1px solid var(--border);
  border-radius: var(--radius-sm); text-align: center; font-size: 12px;
}
.bin-chip .bin-id { color: var(--text-primary); font-weight: 500; }
.bin-chip .bin-st { display: block; font-size: 10px; color: var(--text-muted); margin-top: 2px; }
.bin-chip.filled { background: rgba(239, 68, 68, 0.08); border-color: rgba(239, 68, 68, 0.2); }
.bin-chip.filled .bin-st { color: var(--red); }

/* Modbus */
.modbus-result { margin-top: 10px; }
.modbus-result h5 { font-size: 11px; color: var(--text-muted); margin-bottom: 6px; font-weight: 600; }

/* SLAM */
.slam-display {
  display: flex; align-items: center; gap: 12px; padding: 16px;
  background: var(--bg-overlay); border-radius: var(--radius-sm);
}
.slam-dot {
  width: 12px; height: 12px; border-radius: 50%; background: var(--text-muted);
}
.slam-dot.scanning { background: var(--green); animation: pulse 1.5s infinite; }
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
}
.slam-text { font-size: 14px; color: var(--text-primary); font-weight: 500; }

/* 日志 */
.log-section {
  border-top: 1px solid var(--border); flex-shrink: 0;
}
.log-head {
  display: flex; align-items: center; gap: 8px; padding: 8px 12px;
}
.log-head h4 { flex: 1; font-size: 12px; font-weight: 600; color: var(--text-muted); }
.log-count { font-size: 11px; color: var(--text-muted); font-family: var(--font-mono); }
.log-list {
  max-height: 200px;
  overflow-y: auto;
  padding: 0 12px 10px;
}
.log-entry {
  display: flex; gap: 8px; font-size: 11px; margin-bottom: 3px;
  font-family: var(--font-mono);
}
.log-time { color: var(--text-muted); opacity: 0.5; min-width: 70px; flex-shrink: 0; }
.log-msg { flex: 1; color: var(--text-muted); }
.log-entry.error .log-msg { color: var(--red); }
.log-entry.success .log-msg { color: var(--green); }

.empty-hint {
  padding: 12px 0; text-align: center; font-size: 12px; color: var(--text-muted);
}
</style>
