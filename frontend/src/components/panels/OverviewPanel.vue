<template>
<div v-if="activeGroup === 'overview'" class="group-content">
          
          <div class="card">
            <div class="card-head">
              <h4>机器人信息</h4>
              <button class="icon-btn" @click="loadRobotInfo" :disabled="loading" title="刷新">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M12 7a5 5 0 11-1.5-3.5M12 2v3h-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>
            </div>
            <div class="kv-grid">
              <div class="kv-item" v-for="(value, key) in robotInfo" :key="key">
                <span class="kv-key">{{ key }}</span>
                <span class="kv-val">{{ value }}</span>
              </div>
              <div class="empty-hint" v-if="!Object.keys(robotInfo).length">加载中...</div>
            </div>
          </div>

          
          <div class="card">
            <div class="card-head">
              <h4>位置状态</h4>
              <button class="icon-btn" @click="loadLocation" :disabled="loading" title="刷新">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M12 7a5 5 0 11-1.5-3.5M12 2v3h-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>
            </div>
            <div class="pos-grid">
              <div class="pos-item main">
                <span class="pos-label">X</span>
                <span class="pos-value">{{ locationInfo.x?.toFixed(3) || '-' }}</span>
                <span class="pos-unit">m</span>
              </div>
              <div class="pos-item main">
                <span class="pos-label">Y</span>
                <span class="pos-value">{{ locationInfo.y?.toFixed(3) || '-' }}</span>
                <span class="pos-unit">m</span>
              </div>
              <div class="pos-item">
                <span class="pos-label">角度</span>
                <span class="pos-value">{{ locationInfo.angle != null ? (locationInfo.angle * 180 / Math.PI).toFixed(1) : '-' }}</span>
                <span class="pos-unit">°</span>
              </div>
              <div class="pos-item">
                <span class="pos-label">置信度</span>
                <span class="pos-value">{{ locationInfo.confidence != null ? (locationInfo.confidence * 100).toFixed(0) : '-' }}</span>
                <span class="pos-unit">%</span>
              </div>
              <div class="pos-item">
                <span class="pos-label">站点</span>
                <span class="pos-value accent">{{ locationInfo.current_station || '-' }}</span>
              </div>
              <div class="pos-item">
                <span class="pos-label">定位方式</span>
                <span class="pos-value">{{ locMethodText }}</span>
              </div>
            </div>
          </div>

          
          <div class="card">
            <div class="card-head">
              <h4>速度状态</h4>
              <span class="speed-badge" :class="{ stopped: speedInfo.is_stop }">
                {{ speedInfo.is_stop ? '静止' : '运动中' }}
              </span>
            </div>
            <div class="speed-row">
              <div class="speed-item">
                <span class="speed-label">Vx</span>
                <span class="speed-val">{{ speedInfo.vx?.toFixed(3) || '0.000' }}</span>
                <span class="speed-unit">m/s</span>
              </div>
              <div class="speed-item">
                <span class="speed-label">Vy</span>
                <span class="speed-val">{{ speedInfo.vy?.toFixed(3) || '0.000' }}</span>
                <span class="speed-unit">m/s</span>
              </div>
              <div class="speed-item">
                <span class="speed-label">W</span>
                <span class="speed-val">{{ speedInfo.w?.toFixed(3) || '0.000' }}</span>
                <span class="speed-unit">rad/s</span>
              </div>
            </div>
          </div>
        </div>

        
</template>

<script setup>
import { useRobokit } from "../../composables/useRobokit.js"

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
  runPickDrop3051Flow,
  FORK_NUMERIC_KEYS,
  mergeForkNumericFromSeg,
  applyPlanPathForkDefaultsToSegments,
  mergeForkNumericFromForm,
  mergeOneKeyForkNumeric,
  resolveOneKey6073Height,
  resolvePickDrop6073Height,
  resolveSpecPath6073Height,
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
