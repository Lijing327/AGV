<template>
<div v-if="activeGroup === 'monitor'" class="group-content">
          
          <div class="card">
            <div class="card-head">
              <h4>电池状态</h4>
              <button class="icon-btn" @click="loadBattery" :disabled="loading" title="刷新">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M12 7a5 5 0 11-1.5-3.5M12 2v3h-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>
            </div>
            <div class="battery-visual">
              <div class="battery-bar">
                <div class="battery-fill" :style="{ width: (batteryInfo.battery_level * 100) + '%' }" :class="{ low: batteryInfo.battery_level < 0.2 }"></div>
              </div>
              <span class="battery-pct">{{ (batteryInfo.battery_level * 100)?.toFixed(0) || '0' }}%</span>
            </div>
            <div class="kv-grid compact">
              <div class="kv-item"><span class="kv-key">电压</span><span class="kv-val">{{ batteryInfo.voltage?.toFixed(1) || '-' }} V</span></div>
              <div class="kv-item"><span class="kv-key">电流</span><span class="kv-val">{{ batteryInfo.current?.toFixed(1) || '-' }} A</span></div>
              <div class="kv-item"><span class="kv-key">温度</span><span class="kv-val">{{ batteryInfo.battery_temp || '-' }} ℃</span></div>
              <div class="kv-item">
                <span class="kv-key">充电中</span>
                <span class="kv-val" :class="{ charging: batteryInfo.charging }">{{ batteryInfo.charging ? '是' : '否' }}</span>
              </div>
              <div class="kv-item"><span class="kv-key">循环次数</span><span class="kv-val">{{ batteryInfo.battery_cycle || '-' }}</span></div>
            </div>
          </div>

          
          <div class="card">
            <div class="card-head">
              <h4>急停状态</h4>
              <button class="icon-btn" @click="loadEmergency" :disabled="loading" title="刷新">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M12 7a5 5 0 11-1.5-3.5M12 2v3h-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>
            </div>
            <div class="emc-grid">
              <div class="emc-item" :class="{ danger: emergencyInfo.emergency }">
                <span>急停按钮</span><span>{{ emergencyInfo.emergency ? '按下' : '正常' }}</span>
              </div>
              <div class="emc-item" :class="{ danger: emergencyInfo.driver_emc }">
                <span>驱动器急停</span><span>{{ emergencyInfo.driver_emc ? '急停' : '正常' }}</span>
              </div>
              <div class="emc-item" :class="{ danger: emergencyInfo.soft_emc }">
                <span>软急停</span><span>{{ emergencyInfo.soft_emc ? '急停' : '正常' }}</span>
              </div>
              <div class="emc-item" :class="{ active: emergencyInfo.electric }">
                <span>继电器</span><span>{{ emergencyInfo.electric ? '开启' : '关闭' }}</span>
              </div>
            </div>
            <button class="btn btn-red full" @click="handleEmergencyStop" :disabled="loading">紧急停车</button>
          </div>

          
          <div class="card">
            <div class="card-head">
              <h4>I/O 状态</h4>
              <button class="icon-btn" @click="loadIO" :disabled="loading" title="刷新">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M12 7a5 5 0 11-1.5-3.5M12 2v3h-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>
            </div>
            <div class="io-group" v-if="ioInfo.DI?.length">
              <h5>DI</h5>
              <div class="io-chips">
                <span v-for="item in ioInfo.DI" :key="item.id" class="io-chip" :class="{ on: item.status, invalid: !item.valid }">
                  DI{{ item.id }} <em>{{ item.status ? 'ON' : 'OFF' }}</em>
                </span>
              </div>
            </div>
            <div class="io-group" v-if="ioInfo.DO?.length">
              <h5>DO</h5>
              <div class="io-chips">
                <span v-for="item in ioInfo.DO" :key="item.id" class="io-chip" :class="{ on: item.status }">
                  DO{{ item.id }} <em>{{ item.status ? 'ON' : 'OFF' }}</em>
                </span>
              </div>
            </div>
            <div class="empty-hint" v-if="!ioInfo.DI?.length && !ioInfo.DO?.length">点击刷新获取 I/O 数据</div>
          </div>

          
          <div class="card">
            <div class="card-head">
              <h4>电机状态</h4>
              <button class="icon-btn" @click="loadMotor" :disabled="loading" title="刷新">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M12 7a5 5 0 11-1.5-3.5M12 2v3h-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>
            </div>
            <div v-for="(motor, idx) in motorInfo.motor_info" :key="idx" class="motor-card">
              <div class="motor-head">
                <span>电机 {{ idx + 1 }}</span>
                <span class="motor-badge" :class="{ enabled: motor.enabled }">{{ motor.enabled ? '使能' : '禁用' }}</span>
              </div>
              <div class="kv-grid compact">
                <div class="kv-item"><span class="kv-key">电流</span><span class="kv-val">{{ motor.current?.toFixed(2) || '-' }} A</span></div>
                <div class="kv-item"><span class="kv-key">温度</span><span class="kv-val">{{ motor.temperature || '-' }} ℃</span></div>
                <div class="kv-item"><span class="kv-key">速度</span><span class="kv-val">{{ motor.speed?.toFixed(1) || '-' }} rpm</span></div>
                <div class="kv-item"><span class="kv-key">错误</span><span class="kv-val" :class="{ 'err-code': motor.error_code }">{{ motor.error_code || 0 }}</span></div>
              </div>
            </div>
            <div class="empty-hint" v-if="!motorInfo.motor_info?.length">点击刷新获取电机数据</div>
          </div>

          
          <div class="card">
            <div class="card-head">
              <h4>编码器</h4>
              <button class="icon-btn" @click="loadEncoder" :disabled="loading" title="刷新">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M12 7a5 5 0 11-1.5-3.5M12 2v3h-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>
            </div>
            <div class="enc-section" v-if="encoderInfo.encoder?.length">
              <h5>编码器</h5>
              <div class="enc-chips">
                <span v-for="(val, idx) in encoderInfo.encoder" :key="idx" class="enc-chip">
                  <em>ENC{{ idx }}</em> {{ val }}
                </span>
              </div>
            </div>
            <div class="enc-section" v-if="encoderInfo.motor_encoder?.length">
              <h5>电机编码器</h5>
              <div class="enc-chips">
                <span v-for="(val, idx) in encoderInfo.motor_encoder" :key="idx" class="enc-chip">
                  <em>MENC{{ idx }}</em> {{ val }}
                </span>
              </div>
            </div>
            <div class="empty-hint" v-if="!encoderInfo.encoder?.length && !encoderInfo.motor_encoder?.length">点击刷新获取编码器数据</div>
          </div>

          
          <div class="card">
            <div class="card-head">
              <h4>激光点云</h4>
              <span class="kv-val" v-if="laserInfo.lasers?.length">{{ laserInfo.lasers.length }} 点</span>
              <button class="icon-btn" @click="loadLaser" :disabled="loading" title="刷新">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M12 7a5 5 0 11-1.5-3.5M12 2v3h-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>
            </div>
            <div class="laser-mini" v-if="laserInfo.lasers?.length">
              <div
                v-for="(p, i) in laserInfo.lasers.slice(0, 100)"
                :key="i"
                class="laser-dot"
                :style="{ left: `${50 + p.x * 2}px`, top: `${50 + p.y * 2}px` }"
              ></div>
            </div>
            <div class="empty-hint" v-else>点击刷新获取激光数据</div>
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
