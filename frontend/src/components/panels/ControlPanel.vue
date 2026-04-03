<template>
<div v-if="activeGroup === 'control'" class="group-content">
          
          <div class="card priority-card">
            <div class="card-head">
              <h4>控制权管理</h4>
            </div>
            <p class="card-hint">遇40012/40020先「抢占控制」；遇40101需在锁定设备上释放</p>
            <div class="ctrl-form-row">
              <div class="form-field compact">
                <label>抢占者</label>
                <input v-model="controlNickname" placeholder="agv-web" />
              </div>
            </div>
            <div class="ctrl-btns">
              <button class="btn btn-orange" @click="handleTakeControl" :disabled="loading">抢占控制</button>
              <button class="btn btn-ghost" @click="handleReleaseControl" :disabled="loading">释放控制</button>
              <button class="btn btn-blue-outline" @click="handleSetMode(0)" :disabled="loading">手动模式</button>
              <button class="btn btn-green-outline" @click="handleSetMode(1)" :disabled="loading">自动模式</button>
            </div>
          </div>

          
          <div class="card">
            <div class="card-head"><h4>移动控制</h4></div>
            <div class="input-row-3">
              <div class="form-field compact">
                <label>Vx (m/s)</label>
                <input v-model.number="moveForm.vx" type="number" step="0.1" />
              </div>
              <div class="form-field compact">
                <label>Vy (m/s)</label>
                <input v-model.number="moveForm.vy" type="number" step="0.1" />
              </div>
              <div class="form-field compact">
                <label>W (rad/s)</label>
                <input v-model.number="moveForm.w" type="number" step="0.1" />
              </div>
            </div>
            <div class="btn-row-2">
              <button class="btn btn-green" @click="handleMove" :disabled="loading">执行移动</button>
              <button class="btn btn-red" @click="handleStop" :disabled="loading">停止</button>
            </div>
          </div>

          
          <div class="card">
            <div class="card-head"><h4>定位控制</h4></div>
            <p class="card-hint">重定位(2002)后自动确认定位(2003)并刷新位置</p>
            <div class="input-row-3">
              <div class="form-field compact">
                <label>X (m)</label>
                <input v-model.number="relocateForm.x" type="number" step="0.1" />
              </div>
              <div class="form-field compact">
                <label>Y (m)</label>
                <input v-model.number="relocateForm.y" type="number" step="0.1" />
              </div>
              <div class="form-field compact">
                <label>角度 (°)</label>
                <input v-model.number="relocateForm.angleDeg" type="number" step="0.1" />
              </div>
            </div>
            <div class="btn-wrap">
              <button class="btn btn-ghost-sm" @click="fillRelocateFromCurrent" :disabled="loading || !locationInfo.x">使用当前位置</button>
              <button class="btn btn-blue" @click="handleRelocate" :disabled="loading">重定位</button>
              <button class="btn btn-ghost-sm" @click="handleConfirmLocation" :disabled="loading">确认定位</button>
              <button class="btn btn-ghost-sm" @click="handleCancelRelocate" :disabled="loading">取消重定位</button>
            </div>
          </div>

          
          <div class="card">
            <div class="card-head"><h4>平动 (API 3055)</h4></div>
            <p class="card-hint">直线运动固定距离，只需填距离；可选速度与模式</p>
            <div class="input-row-4">
              <div class="form-field compact">
                <label>距离 (m)</label>
                <input v-model.number="translateForm.dist" type="number" step="0.1" min="0" placeholder="必填" />
              </div>
              <div class="form-field compact">
                <label>Vx (m/s)</label>
                <input v-model.number="translateForm.vx" type="number" step="0.1" placeholder="可选" />
              </div>
              <div class="form-field compact">
                <label>Vy (m/s)</label>
                <input v-model.number="translateForm.vy" type="number" step="0.1" placeholder="可选" />
              </div>
              <div class="form-field compact">
                <label>模式</label>
                <select v-model.number="translateForm.mode">
                  <option :value="0">里程模式</option>
                  <option :value="1">定位模式</option>
                </select>
              </div>
            </div>
            <button class="btn btn-blue full" @click="handleTranslate" :disabled="loading || !Number.isFinite(translateForm.dist) || translateForm.dist <= 0">执行平动</button>
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
