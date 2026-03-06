<template>
  <div class="robokit-panel">
    <!-- 连接状态栏 -->
    <div class="connection-bar">
      <div class="connection-status">
        <span class="status-indicator" :class="{ connected: connectionStatus.connected }"></span>
        <span class="status-text">{{ connectionStatusText }}</span>
      </div>
      <div class="connection-info" v-if="connectionStatus.connected">
        <span class="info-item">IP: {{ connectionStatus.host }}</span>
      </div>
      <button class="connect-btn" @click="handleToggleConnection">
        {{ connectionStatus.connected ? '断开' : '连接' }}
      </button>
    </div>

    <!-- 连接表单 (未连接时显示) -->
    <div class="connection-form" v-if="!connectionStatus.connected">
      <h3>机器人连接</h3>
      <div class="form-row">
        <label>IP地址</label>
        <input v-model="connectForm.host" placeholder="172.16.11.211" />
      </div>
      <div class="form-row">
        <label>端口</label>
        <input v-model="connectForm.port" type="number" placeholder="19204" />
      </div>
      <button class="primary full" @click="handleConnect">连接机器人</button>
    </div>

    <!-- 机器人状态面板 (已连接时显示) -->
    <div class="status-panel" v-if="connectionStatus.connected">
      <!-- 选项卡 -->
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-btn"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.name }}
        </button>
      </div>

      <!-- 基本信息 -->
      <div class="tab-content" v-show="activeTab === 'basic'">
        <div class="info-card">
          <h4>机器人信息</h4>
          <div class="info-grid">
            <div class="info-item" v-for="(value, key) in robotInfo" :key="key">
              <span class="info-label">{{ key }}</span>
              <span class="info-value">{{ value }}</span>
            </div>
          </div>
          <button class="refresh-btn" @click="loadRobotInfo" :disabled="loading">
            {{ loading ? '加载中...' : '刷新' }}
          </button>
        </div>
      </div>

      <!-- 位置信息 -->
      <div class="tab-content" v-show="activeTab === 'location'">
        <div class="info-card">
          <h4>位置状态</h4>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">X坐标</span>
              <span class="info-value highlight">{{ locationInfo.x?.toFixed(3) || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Y坐标</span>
              <span class="info-value highlight">{{ locationInfo.y?.toFixed(3) || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">角度</span>
              <span class="info-value">{{ (locationInfo.angle * 180 / Math.PI)?.toFixed(1) || '-' }}°</span>
            </div>
            <div class="info-item">
              <span class="info-label">置信度</span>
              <span class="info-value">{{ (locationInfo.confidence * 100)?.toFixed(0) || '-' }}%</span>
            </div>
            <div class="info-item">
              <span class="info-label">当前站点</span>
              <span class="info-value highlight">{{ locationInfo.current_station || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">定位方式</span>
              <span class="info-value">{{ locMethodText }}</span>
            </div>
          </div>
          <button class="refresh-btn" @click="loadLocation" :disabled="loading">
            {{ loading ? '加载中...' : '刷新' }}
          </button>
        </div>
      </div>

      <!-- 控制 -->
      <div class="tab-content" v-show="activeTab === 'control'">
        <!-- 模式切换：置顶醒目 -->
        <div class="mode-switch-bar mode-switch-top">
          <span class="mode-hint">遇40012/40020请先点「抢占控制」；遇40101需在锁定设备(如172.16.15.75)上释放</span>
          <label class="nickname-label">抢占者名称</label>
          <input v-model="controlNickname" class="nickname-input" placeholder="agv-web" title="API 4005 必填参数" />
          <button class="mode-btn stop-dispatch" @click="handleTakeControl" :disabled="loading" title="抢占控制权，从调度系统夺取控制">
            抢占控制
          </button>
          <button class="mode-btn release-ctrl" @click="handleReleaseControl" :disabled="loading" title="释放控制权，交还给调度系统">
            释放控制
          </button>
          <button class="mode-btn manual" @click="handleSetMode(0)" :disabled="loading" title="可执行移动、重定位">
            手动模式
          </button>
          <button class="mode-btn auto" @click="handleSetMode(1)" :disabled="loading" title="可执行任务、导航">
            自动模式
          </button>
        </div>
        <div class="info-card">
          <h4>速度控制</h4>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Vx</span>
              <span class="info-value">{{ speedInfo.vx?.toFixed(2) || '0.00' }} m/s</span>
            </div>
            <div class="info-item">
              <span class="info-label">Vy</span>
              <span class="info-value">{{ speedInfo.vy?.toFixed(2) || '0.00' }} m/s</span>
            </div>
            <div class="info-item">
              <span class="info-label">W</span>
              <span class="info-value">{{ speedInfo.w?.toFixed(2) || '0.00' }} rad/s</span>
            </div>
            <div class="info-item">
              <span class="info-label">状态</span>
              <span class="info-value" :class="{ stop: speedInfo.is_stop }">
                {{ speedInfo.is_stop ? '静止' : '运动中' }}
              </span>
            </div>
          </div>

          <div class="control-buttons">
            <div class="button-group">
              <label>移动控制</label>
              <div class="speed-inputs">
                <div>
                  <span>Vx:</span>
                  <input v-model.number="moveForm.vx" type="number" step="0.1" />
                </div>
                <div>
                  <span>Vy:</span>
                  <input v-model.number="moveForm.vy" type="number" step="0.1" />
                </div>
                <div>
                  <span>W:</span>
                  <input v-model.number="moveForm.w" type="number" step="0.1" />
                </div>
              </div>
              <div class="action-buttons">
                <button class="success" @click="handleMove" :disabled="loading">
                  执行移动
                </button>
                <button class="warning" @click="handleStop" :disabled="loading">
                  停止
                </button>
              </div>
            </div>

            <div class="button-group">
              <label>定位控制</label>
              <div class="relocate-inputs">
                <div>
                  <span>X(m):</span>
                  <input v-model.number="relocateForm.x" type="number" step="0.1" />
                </div>
                <div>
                  <span>Y(m):</span>
                  <input v-model.number="relocateForm.y" type="number" step="0.1" />
                </div>
                <div>
                  <span>角度(°):</span>
                  <input v-model.number="relocateForm.angleDeg" type="number" step="0.1" placeholder="度" />
                </div>
              </div>
              <div class="action-buttons">
                <button class="secondary" @click="fillRelocateFromCurrent" :disabled="loading || !locationInfo.x">
                  使用当前位置
                </button>
                <button class="primary" @click="handleRelocate" :disabled="loading">
                  重定位
                </button>
                <button @click="handleConfirmLocation" :disabled="loading">
                  确认定位
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 电池状态 -->
      <div class="tab-content" v-show="activeTab === 'battery'">
        <div class="info-card">
          <h4>电池状态</h4>
          <div class="battery-display">
            <div class="battery-icon">
              <div class="battery-level" :style="{ width: (batteryInfo.battery_level * 100) + '%' }"></div>
              <span class="battery-text">{{ (batteryInfo.battery_level * 100)?.toFixed(0) }}%</span>
            </div>
            <div class="battery-details">
              <div class="detail-item">
                <span>电压</span>
                <span>{{ batteryInfo.voltage?.toFixed(1) || '-' }} V</span>
              </div>
              <div class="detail-item">
                <span>电流</span>
                <span>{{ batteryInfo.current?.toFixed(1) || '-' }} A</span>
              </div>
              <div class="detail-item">
                <span>温度</span>
                <span>{{ batteryInfo.battery_temp || '-' }} ℃</span>
              </div>
              <div class="detail-item">
                <span>充电中</span>
                <span :class="{ charging: batteryInfo.charging }">
                  {{ batteryInfo.charging ? '是' : '否' }}
                </span>
              </div>
              <div class="detail-item">
                <span>循环次数</span>
                <span>{{ batteryInfo.battery_cycle || '-' }}</span>
              </div>
            </div>
          </div>
          <div class="form-row">
            <label>
              <input v-model="simpleBattery" type="checkbox" />
              仅显示电量
            </label>
          </div>
          <button class="refresh-btn" @click="loadBattery" :disabled="loading">
            {{ loading ? '加载中...' : '刷新' }}
          </button>
        </div>
      </div>

      <!-- 急停状态 -->
      <div class="tab-content" v-show="activeTab === 'emergency'">
        <div class="info-card">
          <h4>急停状态</h4>
          <div class="emergency-status">
            <div class="status-row" :class="{ active: emergencyInfo.emergency }">
              <span class="status-label">急停按钮</span>
              <span class="status-value">{{ emergencyInfo.emergency ? '按下' : '正常' }}</span>
            </div>
            <div class="status-row" :class="{ active: emergencyInfo.driver_emc }">
              <span class="status-label">驱动器急停</span>
              <span class="status-value">{{ emergencyInfo.driver_emc ? '急停' : '正常' }}</span>
            </div>
            <div class="status-row" :class="{ active: emergencyInfo.electric }">
              <span class="status-label">继电器</span>
              <span class="status-value">{{ emergencyInfo.electric ? '开启' : '关闭' }}</span>
            </div>
            <div class="status-row" :class="{ active: emergencyInfo.soft_emc }">
              <span class="status-label">软急停</span>
              <span class="status-value">{{ emergencyInfo.soft_emc ? '急停' : '正常' }}</span>
            </div>
          </div>
          <button class="danger full" @click="handleEmergencyStop" :disabled="loading">
            紧急停车
          </button>
          <button class="refresh-btn" @click="loadEmergency" :disabled="loading">
            {{ loading ? '加载中...' : '刷新' }}
          </button>
        </div>
      </div>

      <!-- I/O状态 -->
      <div class="tab-content" v-show="activeTab === 'io'">
        <div class="info-card">
          <h4>I/O 状态</h4>
          <div class="io-section">
            <h5>数字输入 (DI)</h5>
            <div class="io-grid">
              <div
                v-for="item in ioInfo.DI"
                :key="item.id"
                class="io-item"
                :class="{ active: item.status, invalid: !item.valid }"
              >
                <span class="io-id">DI{{ item.id }}</span>
                <span class="io-status">{{ item.status ? 'ON' : 'OFF' }}</span>
                <span class="io-source">{{ item.source }}</span>
              </div>
            </div>
          </div>
          <div class="io-section">
            <h5>数字输出 (DO)</h5>
            <div class="io-grid">
              <div
                v-for="item in ioInfo.DO"
                :key="item.id"
                class="io-item"
                :class="{ active: item.status }"
              >
                <span class="io-id">DO{{ item.id }}</span>
                <span class="io-status">{{ item.status ? 'ON' : 'OFF' }}</span>
                <span class="io-source">{{ item.source }}</span>
              </div>
            </div>
          </div>
          <button class="refresh-btn" @click="loadIO" :disabled="loading">
            {{ loading ? '加载中...' : '刷新' }}
          </button>
        </div>
      </div>

      <!-- 导航状态 -->
      <div class="tab-content" v-show="activeTab === 'nav'">
        <div class="info-card">
          <h4>导航控制</h4>
          <div class="nav-form">
            <div class="form-row">
              <label>目标</label>
              <input v-model="navForm.target" placeholder="如: P1" />
            </div>
            <div class="form-row">
              <label>类型</label>
              <select v-model="navForm.type">
                <option value="point">点</option>
                <option value="area">区域</option>
              </select>
            </div>
            <button class="primary" @click="handleMoveTo" :disabled="loading">
              执行导航
            </button>
            <button @click="handleStopNavigation" :disabled="loading">
              停止导航
            </button>
          </div>
          <div class="nav-status">
            <h5>导航状态</h5>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">状态</span>
                <span class="info-value">{{ navStatusInfo.status || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">定位状态</span>
                <span class="info-value">{{ navStatusInfo.loc_status || '-' }}</span>
              </div>
            </div>
          </div>
          <div class="action-buttons">
            <button class="refresh-btn" @click="loadNavStatus" :disabled="loading">
              {{ loading ? '加载中...' : '刷新' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 库位状态 -->
      <div class="tab-content" v-show="activeTab === 'bins'">
        <div class="info-card">
          <h4>库位状态</h4>
          <div class="bins-info">
            <div class="bins-header" v-if="binsInfo.header">
              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">库位数量</span>
                  <span class="info-value">{{ binsInfo.bins?.length || 0 }}</span>
                </div>
              </div>
            </div>
            <div class="bins-grid">
              <div
                v-for="bin in binsInfo.bins"
                :key="bin.binId"
                class="bin-item"
                :class="{ filled: bin.filled, invalid: bin.status !== 1 }"
              >
                <div class="bin-id">{{ bin.binId }}</div>
                <div class="bin-status">
                  <span v-if="bin.filled">占用</span>
                  <span v-else>空闲</span>
                </div>
              </div>
            </div>
            <div v-if="binsInfo.bins?.length === 0" class="empty-state">
              暂无库位数据
            </div>
          </div>
          <button class="refresh-btn" @click="loadBins" :disabled="loading">
            {{ loading ? '加载中...' : '刷新' }}
          </button>
        </div>
      </div>

      <!-- 电机状态 -->
      <div class="tab-content" v-show="activeTab === 'motor'">
        <div class="info-card">
          <h4>电机状态</h4>
          <div class="motor-list">
            <div
              v-for="(motor, index) in motorInfo.motor_info"
              :key="index"
              class="motor-item"
            >
              <div class="motor-header">
                <span class="motor-name">电机 {{ index + 1 }}</span>
                <span class="motor-status" :class="{ active: motor.enabled }">
                  {{ motor.enabled ? '使能' : '禁用' }}
                </span>
              </div>
              <div class="motor-details">
                <div class="motor-detail">
                  <span>电流:</span>
                  <span>{{ motor.current?.toFixed(2) || '-' }} A</span>
                </div>
                <div class="motor-detail">
                  <span>温度:</span>
                  <span>{{ motor.temperature || '-' }} ℃</span>
                </div>
                <div class="motor-detail">
                  <span>速度:</span>
                  <span>{{ motor.speed?.toFixed(1) || '-' }} rpm</span>
                </div>
                <div class="motor-detail">
                  <span>错误:</span>
                  <span class="error-code">{{ motor.error_code || 0 }}</span>
                </div>
              </div>
            </div>
            <div v-if="motorInfo.motor_info?.length === 0" class="empty-state">
              暂无电机数据
            </div>
          </div>
          <button class="refresh-btn" @click="loadMotor" :disabled="loading">
            {{ loading ? '加载中...' : '刷新' }}
          </button>
        </div>
      </div>

      <!-- 激光数据 -->
      <div class="tab-content" v-show="activeTab === 'laser'">
        <div class="info-card">
          <h4>激光点云数据</h4>
          <div class="laser-info">
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">点数</span>
                <span class="info-value">{{ laserInfo.lasers?.length || 0 }}</span>
              </div>
            </div>
            <div class="laser-preview">
              <div v-if="laserInfo.lasers?.length > 0" class="laser-points">
                <div
                  v-for="(point, index) in laserInfo.lasers.slice(0, 100)"
                  :key="index"
                  class="laser-point"
                  :style="{ left: `${50 + point.x * 2}px`, top: `${50 + point.y * 2}px` }"
                ></div>
              </div>
              <div v-else class="empty-state">暂无激光数据</div>
            </div>
          </div>
          <button class="refresh-btn" @click="loadLaser" :disabled="loading">
            {{ loading ? '加载中...' : '刷新' }}
          </button>
        </div>
      </div>

      <!-- Modbus数据 -->
      <div class="tab-content" v-show="activeTab === 'modbus'">
        <div class="info-card">
          <h4>Modbus数据查询</h4>
          <div class="modbus-form">
            <div class="form-row">
              <label>寄存器</label>
              <input v-model="modbusRegisters" placeholder="如: 121,122,123" />
            </div>
            <button class="primary" @click="handleQueryModbus" :disabled="loading">
              查询
            </button>
          </div>
          <div class="modbus-result" v-if="Object.keys(modbusResult).length > 0">
            <h5>查询结果 (4x)</h5>
            <div class="modbus-grid">
              <div
                v-for="(value, key) in modbusResult['4x'] || {}"
                :key="key"
                class="modbus-item"
              >
                <span class="modbus-addr">{{ key }}</span>
                <span class="modbus-value">{{ value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 编码器 -->
      <div class="tab-content" v-show="activeTab === 'encoder'">
        <div class="info-card">
          <h4>编码器脉冲值</h4>
          <div class="encoder-section">
            <h5>编码器</h5>
            <div class="encoder-grid">
              <div
                v-for="(value, index) in encoderInfo.encoder || []"
                :key="index"
                class="encoder-item"
              >
                <span class="encoder-id">ENC{{ index }}</span>
                <span class="encoder-value">{{ value }}</span>
              </div>
              <div v-if="encoderInfo.encoder?.length === 0" class="empty-state">
                暂无数据
              </div>
            </div>
          </div>
          <div class="encoder-section">
            <h5>电机编码器</h5>
            <div class="encoder-grid">
              <div
                v-for="(value, index) in encoderInfo.motor_encoder || []"
                :key="index"
                class="encoder-item"
              >
                <span class="encoder-id">MENC{{ index }}</span>
                <span class="encoder-value">{{ value }}</span>
              </div>
              <div v-if="encoderInfo.motor_encoder?.length === 0" class="empty-state">
                暂无数据
              </div>
            </div>
          </div>
          <button class="refresh-btn" @click="loadEncoder" :disabled="loading">
            {{ loading ? '加载中...' : '刷新' }}
          </button>
        </div>
      </div>

      <!-- 扫图状态 -->
      <div class="tab-content" v-show="activeTab === 'slam'">
        <div class="info-card">
          <h4>SLAM 扫图状态</h4>
          <div class="slam-status-display">
            <div class="slam-indicator" :class="{ active: slamInfo.slam_status === 1 }">
              <div class="slam-icon"></div>
              <span class="slam-text">
                {{ slamStatusText }}
              </span>
            </div>
          </div>
          <button class="refresh-btn" @click="loadSlam" :disabled="loading">
            {{ loading ? '加载中...' : '刷新' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 日志 -->
    <div class="log-section">
      <h4>操作日志</h4>
      <div class="log-list">
        <div v-for="(entry, i) in logs" :key="i" class="log-entry" :class="{ error: entry.error, success: entry.success }">
          <span class="log-time">{{ entry.time }}</span>
          <span class="log-message">{{ entry.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as api from '../api'

const tabs = [
  { id: 'basic', name: '基本信息' },
  { id: 'location', name: '位置' },
  { id: 'control', name: '控制' },
  { id: 'battery', name: '电池' },
  { id: 'emergency', name: '急停' },
  { id: 'io', name: 'I/O' },
  { id: 'nav', name: '导航' },
  { id: 'bins', name: '库位' },
  { id: 'motor', name: '电机' },
  { id: 'laser', name: '激光' },
  { id: 'modbus', name: 'Modbus' },
  { id: 'encoder', name: '编码器' },
  { id: 'slam', name: '扫图' },
]

const activeTab = ref('basic')
const connectionStatus = ref({ connected: false, host: '' })
const loading = ref(false)
const pollTimer = ref(null)

// 连接表单
const connectForm = ref({
  host: '172.16.11.211',
  port: 19204
})

// 状态数据
const robotInfo = ref({})
const locationInfo = ref({})
const speedInfo = ref({})
const batteryInfo = ref({})
const emergencyInfo = ref({})
const ioInfo = ref({ DI: [], DO: [] })
const navStatusInfo = ref({})
const binsInfo = ref({ header: {}, bins: [] })
const motorInfo = ref({ motor_info: [] })
const laserInfo = ref({ lasers: [] })
const encoderInfo = ref({ encoder: [], motor_encoder: [] })
const slamInfo = ref({ slam_status: 0 })
const modbusResult = ref({})
const modbusRegisters = ref('121,122')

// 控制表单
const moveForm = ref({ vx: 0.5, vy: 0, w: 0 })
const controlNickname = ref('agv-web')  // 抢占控制时的 nick_name，API 4005 必填
const relocateForm = ref({ x: 0, y: 0, angleDeg: 0 })  // angleDeg 为角度(°)，API 需弧度
const navForm = ref({ target: '', type: 'point' })
const simpleBattery = ref(false)

// 日志
const logs = ref([])

const connectionStatusText = computed(() => {
  return connectionStatus.value.connected ? '已连接' : '未连接'
})

const locMethodText = computed(() => {
  const methods = {
    0: '自然轮廓',
    1: '反光柱',
    2: '二维码',
    3: '里程计',
    4: '3D定位',
    5: '天码',
    6: '特征定位',
    7: '3D特征',
    8: '3D KF'
  }
  return methods[locationInfo.value.loc_method] || '-'
})

const slamStatusText = computed(() => {
  const statusMap = {
    0: '未扫图',
    1: '扫图中',
    2: '扫图完成'
  }
  return statusMap[slamInfo.value.slam_status] || '未知'
})

function log(message, isError = false, isSuccess = false) {
  const time = new Date().toLocaleTimeString()
  logs.value.unshift({ time, message, error: isError, success: isSuccess })
  // 限制日志数量
  if (logs.value.length > 50) logs.value.pop()
}

/** 针对 40012/40020/40101 等控制权相关错误，追加友好提示 */
function formatRobokitError(msg) {
  if (!msg || typeof msg !== 'string') return msg
  if (msg.includes('40012')) return msg + ' → 调度中，请先点「抢占控制」'
  if (msg.includes('40020')) return msg + ' → 控制权已被抢占，若抢占也失败，需在锁定设备(如 172.16.15.75)上释放'
  if (msg.includes('40101')) return msg + ' → 机器人被其他设备锁定，需在该设备上释放后再操作'
  return msg
}

// 连接管理
async function handleConnect() {
  loading.value = true
  try {
    const result = await api.robokitConnect(connectForm.value.host, connectForm.value.port)
    if (result && result.success) {
      connectionStatus.value.connected = true
      connectionStatus.value.host = connectForm.value.host
      log('连接成功', false, true)
      // 刷新状态
      await loadAllStatus()
    } else {
      log('连接失败', true)
    }
  } catch (e) {
    log('连接错误: ' + e.message, true)
  } finally {
    loading.value = false
  }
}

async function handleDisconnect() {
  loading.value = true
  try {
    await api.robokitDisconnect()
    connectionStatus.value.connected = false
    connectionStatus.value.host = ''
    log('已断开连接', false, true)
    stopPoll()
  } catch (e) {
    log('断开错误: ' + e.message, true)
  } finally {
    loading.value = false
  }
}

async function handleToggleConnection() {
  if (connectionStatus.value.connected) {
    await handleDisconnect()
  } else {
    await handleConnect()
  }
}

// 状态查询
async function loadAllStatus() {
  await Promise.all([
    loadRobotInfo(),
    loadLocation(),
    loadSpeed(),
    loadBattery(),
    loadEmergency()
  ])
}

async function loadRobotInfo() {
  loading.value = true
  try {
    const data = await api.robokitGetInfo()
    if (data) {
      robotInfo.value = {
        '机器人ID': data.id || '-',
        '型号': data.model || '-',
        '版本': data.version || '-',
        '固件版本': data.dsp_version || '-',
        '地图版本': data.map_version || '-',
        '当前地图': data.current_map || '-',
      }
    }
  } catch (e) {
    log('获取机器人信息失败: ' + e.message, true)
  } finally {
    loading.value = false
  }
}

async function loadLocation() {
  try {
    const data = await api.robokitGetLocation()
    if (data) {
      locationInfo.value = data
    }
  } catch (e) {
    log('获取位置失败: ' + e.message, true)
  }
}

async function loadSpeed() {
  try {
    const data = await api.robokitGetSpeed()
    if (data) {
      speedInfo.value = data
    }
  } catch (e) {
    log('获取速度失败: ' + e.message, true)
  }
}

async function loadBattery() {
  try {
    const data = await api.robokitGetBattery(simpleBattery.value)
    if (data) {
      batteryInfo.value = data
    }
  } catch (e) {
    log('获取电池状态失败: ' + e.message, true)
  }
}

async function loadEmergency() {
  try {
    const data = await api.robokitGetEmergency()
    if (data) {
      emergencyInfo.value = data
    }
  } catch (e) {
    log('获取急停状态失败: ' + e.message, true)
  }
}

async function loadIO() {
  loading.value = true
  try {
    const data = await api.robokitGetIO()
    if (data) {
      ioInfo.value = data
    }
  } catch (e) {
    log('获取I/O状态失败: ' + e.message, true)
  } finally {
    loading.value = false
  }
}

async function loadNavStatus() {
  loading.value = true
  try {
    const [navData, locData] = await Promise.all([
      api.robokitGetNavStatus(),
      api.robokitGetLocStatus()
    ])
    if (navData) navStatusInfo.value.status = '运行中' // 简化处理
    if (locData) navStatusInfo.value.loc_status = '已定位' // 简化处理
  } catch (e) {
    log('获取导航状态失败: ' + e.message, true)
  } finally {
    loading.value = false
  }
}

// 新增API处理函数
async function loadBins() {
  loading.value = true
  try {
    const data = await api.robokitGetBins()
    if (data) {
      binsInfo.value = data
    }
  } catch (e) {
    log('获取库位状态失败: ' + e.message, true)
  } finally {
    loading.value = false
  }
}

async function loadMotor() {
  loading.value = true
  try {
    const data = await api.robokitGetMotor()
    if (data) {
      motorInfo.value = data
    }
  } catch (e) {
    log('获取电机状态失败: ' + e.message, true)
  } finally {
    loading.value = false
  }
}

async function loadLaser() {
  loading.value = true
  try {
    const data = await api.robokitGetLaser()
    if (data) {
      laserInfo.value = data
    }
  } catch (e) {
    log('获取激光数据失败: ' + e.message, true)
  } finally {
    loading.value = false
  }
}

async function loadEncoder() {
  loading.value = true
  try {
    const data = await api.robokitGetEncoder()
    if (data) {
      encoderInfo.value = data
    }
  } catch (e) {
    log('获取编码器数据失败: ' + e.message, true)
  } finally {
    loading.value = false
  }
}

async function loadSlam() {
  loading.value = true
  try {
    const data = await api.robokitGetSlam()
    if (data) {
      slamInfo.value = data
    }
  } catch (e) {
    log('获取扫图状态失败: ' + e.message, true)
  } finally {
    loading.value = false
  }
}

async function handleQueryModbus() {
  loading.value = true
  try {
    const registers = modbusRegisters.value.split(',').map(r => parseInt(r.trim())).filter(r => !isNaN(r))
    if (registers.length === 0) {
      log('请输入有效的寄存器地址', true)
      return
    }
    const data = await api.robokitQueryModbus(registers)
    if (data) {
      modbusResult.value = data
      log(`Modbus查询成功: ${registers.join(',')}`, false, true)
    }
  } catch (e) {
    log('Modbus查询失败: ' + e.message, true)
  } finally {
    loading.value = false
  }
}

// 控制命令
async function handleTakeControl() {
  loading.value = true
  try {
    try {
      await api.robokitTakeControl(controlNickname.value || 'agv-web')
      log('抢占控制权成功', false, true)
      return
    } catch (_) {}
    try {
      await api.robokitStopNavigation()
      log('已停止导航', false, true)
      return
    } catch (_) {}
    await api.robokitStop()
    log('已发送停止指令', false, true)
  } catch (e) {
    log('抢占控制失败: ' + formatRobokitError(e.message), true)
  } finally {
    loading.value = false
  }
}

async function handleReleaseControl() {
  loading.value = true
  try {
    await api.robokitReleaseControl()
    log('已释放控制权', false, true)
  } catch (e) {
    log('释放控制失败: ' + formatRobokitError(e.message), true)
  } finally {
    loading.value = false
  }
}

async function handleSetMode(mode) {
  loading.value = true
  try {
    await api.robokitSetMode(mode)
    log(mode === 0 ? '已切换到手动模式，可执行移动/重定位' : '已切换到自动模式，可执行任务/导航', false, true)
  } catch (e) {
    log('切换模式失败: ' + formatRobokitError(e.message), true)
  } finally {
    loading.value = false
  }
}

async function handleMove() {
  loading.value = true
  try {
    const result = await api.robokitMove(moveForm.value.vx, moveForm.value.vy, moveForm.value.w)
    if (result && result.ret_code === 0) {
      log(`移动指令: Vx=${moveForm.value.vx}, Vy=${moveForm.value.vy}, W=${moveForm.value.w}`, false, true)
    } else {
      log('移动指令失败', true)
    }
  } catch (e) {
    log('移动错误: ' + formatRobokitError(e.message), true)
  } finally {
    loading.value = false
  }
}

async function handleStop() {
  loading.value = true
  try {
    const result = await api.robokitStop()
    if (result && result.ret_code === 0) {
      log('停止指令已发送', false, true)
    } else {
      log('停止指令失败', true)
    }
  } catch (e) {
    log('停止错误: ' + formatRobokitError(e.message), true)
  } finally {
    loading.value = false
  }
}

function fillRelocateFromCurrent() {
  if (locationInfo.value.x != null && locationInfo.value.y != null) {
    relocateForm.value.x = Number(locationInfo.value.x.toFixed(3))
    relocateForm.value.y = Number(locationInfo.value.y.toFixed(3))
    relocateForm.value.angleDeg = Number(((locationInfo.value.angle ?? 0) * 180 / Math.PI).toFixed(1))
    log('已填入当前位置', false, true)
  }
}

async function handleRelocate() {
  loading.value = true
  try {
    const angleRad = (relocateForm.value.angleDeg ?? 0) * Math.PI / 180
    const result = await api.robokitRelocate(relocateForm.value.x, relocateForm.value.y, angleRad)
    if (result && result.ret_code === 0) {
      log(`重定位: X=${relocateForm.value.x}, Y=${relocateForm.value.y}, 角度=${relocateForm.value.angleDeg}°`, false, true)
    } else {
      log('重定位失败', true)
    }
  } catch (e) {
    log('重定位错误: ' + formatRobokitError(e.message), true)
  } finally {
    loading.value = false
  }
}

async function handleConfirmLocation() {
  loading.value = true
  try {
    const result = await api.robokitConfirmLocation()
    if (result && result.ret_code === 0) {
      log('定位已确认', false, true)
    } else {
      log('确认定位失败', true)
    }
  } catch (e) {
    log('确认定位错误: ' + formatRobokitError(e.message), true)
  } finally {
    loading.value = false
  }
}

async function handleEmergencyStop() {
  loading.value = true
  try {
    const result = await api.robokitEmergencyStop()
    if (result && result.ret_code === 0) {
      log('紧急停车已执行', false, true)
    } else {
      log('紧急停车失败', true)
    }
  } catch (e) {
    log('紧急停车错误: ' + formatRobokitError(e.message), true)
  } finally {
    loading.value = false
  }
}

async function handleMoveTo() {
  loading.value = true
  try {
    const result = await api.robokitMoveTo(navForm.value.target, navForm.value.type)
    if (result && result.ret_code === 0) {
      log(`导航到 ${navForm.value.type}: ${navForm.value.target}`, false, true)
    } else {
      log('导航指令失败', true)
    }
  } catch (e) {
    log('导航错误: ' + e.message, true)
  } finally {
    loading.value = false
  }
}

async function handleStopNavigation() {
  loading.value = true
  try {
    const result = await api.robokitStopNavigation()
    if (result && result.ret_code === 0) {
      log('导航已停止', false, true)
    } else {
      log('停止导航失败', true)
    }
  } catch (e) {
    log('停止导航错误: ' + e.message, true)
  } finally {
    loading.value = false
  }
}

// 轮询
function startPoll() {
  if (pollTimer.value) return
  pollTimer.value = setInterval(() => {
    if (connectionStatus.value.connected) {
      loadLocation()
      loadSpeed()
      loadEmergency()
    }
  }, 1000)
}

function stopPoll() {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

onMounted(() => {
  log('Robokit面板已初始化')
  startPoll()
})

onUnmounted(() => {
  stopPoll()
})
</script>

<style scoped>
.robokit-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #0f3460;
  padding: 16px;
  overflow: hidden;
}

/* 连接栏 */
.connection-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(0,0,0,0.2);
  border-radius: 8px;
  margin-bottom: 12px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #e74c3c;
}

.status-indicator.connected {
  background: #2ecc71;
  box-shadow: 0 0 8px rgba(46, 204, 113, 0.4);
}

.status-text {
  font-size: 13px;
  color: #95a5a6;
}

.connection-info {
  flex: 1;
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #7f8c8d;
}

.info-item {
  display: flex;
  gap: 4px;
}

.connect-btn {
  padding: 8px 16px;
  background: #3498db;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}

.connect-btn:hover {
  background: #2980b9;
}

/* 连接表单 */
.connection-form {
  background: rgba(0,0,0,0.2);
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.connection-form h3 {
  margin: 0 0 12px;
  font-size: 14px;
  color: #7f8c8d;
}

/* 选项卡 */
.tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 12px;
  overflow-x: auto;
  flex-wrap: nowrap;
  padding-bottom: 4px;
  -webkit-overflow-scrolling: touch;
}
.tabs::-webkit-scrollbar {
  height: 4px;
}
.tabs::-webkit-scrollbar-thumb {
  background: #2c3e50;
  border-radius: 2px;
}

.tab-btn {
  flex-shrink: 0;
  padding: 8px 12px;
  background: rgba(0,0,0,0.2);
  color: #95a5a6;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  white-space: nowrap;
}

.tab-btn.active {
  background: #3498db;
  color: #fff;
}

.tab-btn:hover:not(.active) {
  background: rgba(52, 152, 219, 0.2);
}

/* 状态面板 */
.status-panel {
  flex: 1;
  overflow-y: auto;
}

.tab-content {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 信息卡片 */
.info-card {
  background: rgba(0,0,0,0.2);
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.info-card h4 {
  margin: 0 0 12px;
  font-size: 14px;
  color: #7f8c8d;
  font-weight: 500;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px 20px;
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.info-label {
  color: #95a5a6;
}

.info-value {
  color: #e0e0e0;
  font-family: monospace;
}

.info-value.highlight {
  color: #00d9ff;
  font-weight: bold;
}

.info-value.stop {
  color: #e74c3c;
}

/* 表单元素 */
.form-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.form-row label {
  color: #95a5a6;
  font-size: 13px;
  min-width: 80px;
}

.form-row input, .form-row select {
  flex: 1;
  padding: 8px 12px;
  background: #1a1a2e;
  border: 1px solid #2c3e50;
  border-radius: 4px;
  color: #fff;
  font-size: 13px;
}

.form-row input:focus, .form-row select:focus {
  outline: none;
  border-color: #3498db;
}

.form-row input[type="checkbox"] {
  flex: 0;
  width: auto;
}

/* 按钮 */
button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

button.primary { background: #3498db; color: #fff; }
button.primary:hover:not(:disabled) { background: #2980b9; }

button.secondary { background: #5a6c7d; color: #ecf0f1; }
button.secondary:hover:not(:disabled) { background: #4a5c6d; }

button.success { background: #2ecc71; color: #fff; }
button.success:hover:not(:disabled) { background: #27ae60; }

button.warning { background: #e67e22; color: #fff; }
button.warning:hover:not(:disabled) { background: #d35400; }

button.danger { background: #e74c3c; color: #fff; }
button.danger:hover:not(:disabled) { background: #c0392b; }

button.full { width: 100%; margin-bottom: 8px; }

.refresh-btn {
  padding: 6px 16px;
  background: rgba(0,0,0,0.3);
  color: #95a5a6;
  font-size: 12px;
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(0,0,0,0.5);
  color: #e0e0e0;
}

/* 控制按钮区域 */
.mode-switch-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 10px 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
  border: 1px solid #2c3e50;
}
.mode-switch-bar.mode-switch-top {
  margin-top: 0;
  background: rgba(52, 152, 219, 0.15);
  border-color: #3498db;
  flex-shrink: 0;
  flex-wrap: wrap;
}
.mode-hint {
  flex: 1;
  font-size: 11px;
  color: #95a5a6;
}
.nickname-label {
  font-size: 12px;
  color: #bdc3c7;
  white-space: nowrap;
}
.nickname-input {
  width: 120px;
  padding: 6px 8px;
  font-size: 12px;
  border: 1px solid #2c3e50;
  border-radius: 4px;
  background: rgba(0,0,0,0.3);
  color: #ecf0f1;
}
.nickname-input::placeholder {
  color: #7f8c8d;
}
.mode-btn.manual {
  padding: 8px 14px;
  background: #3498db;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  white-space: nowrap;
}
.mode-btn.manual:hover:not(:disabled) {
  background: #2980b9;
}
.mode-btn.manual:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.mode-btn.auto {
  padding: 8px 14px;
  background: #2ecc71;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  white-space: nowrap;
}
.mode-btn.auto:hover:not(:disabled) {
  background: #27ae60;
}
.mode-btn.auto:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.mode-btn.stop-dispatch {
  padding: 8px 12px;
  background: #e67e22;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  white-space: nowrap;
}
.mode-btn.stop-dispatch:hover:not(:disabled) {
  background: #d35400;
}
.mode-btn.stop-dispatch:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.mode-btn.release-ctrl {
  padding: 8px 12px;
  background: #95a5a6;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  white-space: nowrap;
}
.mode-btn.release-ctrl:hover:not(:disabled) {
  background: #7f8c8d;
}
.mode-btn.release-ctrl:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.control-buttons {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.button-group {
  border: 1px solid #2c3e50;
  border-radius: 8px;
  padding: 12px;
}

.button-group label {
  display: block;
  color: #95a5a6;
  font-size: 12px;
  margin-bottom: 8px;
}

.speed-inputs, .relocate-inputs {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}

.speed-inputs > div, .relocate-inputs > div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.speed-inputs span, .relocate-inputs span {
  font-size: 11px;
  color: #95a5a6;
}

.speed-inputs input, .relocate-inputs input {
  padding: 6px;
  background: #1a1a2e;
  border: 1px solid #2c3e50;
  border-radius: 4px;
  color: #fff;
  font-size: 12px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-buttons button {
  flex: 1;
}

/* 电池显示 */
.battery-display {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
}

.battery-icon {
  position: relative;
  width: 120px;
  height: 50px;
  border: 3px solid #7f8c8d;
  border-radius: 8px;
  padding: 4px;
}

.battery-level {
  height: 100%;
  background: linear-gradient(90deg, #2ecc71, #f1c40f);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.battery-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 16px;
  font-weight: bold;
  color: #fff;
  text-shadow: 0 0 4px rgba(0,0,0,0.5);
}

.battery-details {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.detail-item > span:last-child {
  font-family: monospace;
  color: #e0e0e0;
}

.detail-item > span:last-child.charging {
  color: #2ecc71;
}

/* 急停状态 */
.emergency-status {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}

.status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(46, 204, 113, 0.1);
  border-radius: 6px;
}

.status-row.active {
  background: rgba(231, 76, 60, 0.2);
}

.status-row .status-label {
  color: #95a5a6;
  font-size: 13px;
}

.status-row .status-value {
  font-weight: 500;
  color: #2ecc71;
}

.status-row.active .status-value {
  color: #e74c3c;
}

/* I/O状态 */
.io-section {
  margin-bottom: 16px;
}

.io-section h5 {
  font-size: 12px;
  color: #95a5a6;
  margin-bottom: 8px;
}

.io-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.io-item {
  display: flex;
  flex-direction: column;
  padding: 8px;
  background: rgba(0,0,0,0.2);
  border-radius: 4px;
  font-size: 12px;
}

.io-item.active {
  background: rgba(46, 204, 113, 0.2);
}

.io-item.invalid {
  opacity: 0.5;
}

.io-id {
  color: #7f8c8d;
  font-weight: 500;
}

.io-status {
  font-size: 11px;
  color: #95a5a6;
}

.io-item.active .io-status {
  color: #2ecc71;
  font-weight: bold;
}

.io-source {
  font-size: 10px;
  color: #5e6d7e;
}

/* 导航控制 */
.nav-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.nav-status {
  margin-bottom: 12px;
}

.nav-status h5 {
  font-size: 12px;
  color: #95a5a6;
  margin-bottom: 8px;
}

/* 日志 */
.log-section {
  margin-top: 12px;
}

.log-section h4 {
  font-size: 13px;
  color: #7f8c8d;
  margin-bottom: 8px;
}

.log-list {
  max-height: 150px;
  overflow-y: auto;
  background: rgba(0,0,0,0.2);
  border-radius: 6px;
  padding: 10px;
}

.log-entry {
  display: flex;
  gap: 12px;
  font-size: 12px;
  margin-bottom: 6px;
  font-family: 'Consolas', monospace;
}

.log-time {
  color: #5e6d7e;
  min-width: 80px;
}

.log-message {
  flex: 1;
  color: #8b949e;
}

.log-entry.error .log-message {
  color: #e74c3c;
}

.log-entry.success .log-message {
  color: #2ecc71;
}

/* 库位状态 */
.bins-info {
  margin-bottom: 12px;
}

.bins-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.bin-item {
  padding: 12px;
  background: rgba(0,0,0,0.2);
  border: 1px solid #2c3e50;
  border-radius: 6px;
  text-align: center;
  cursor: default;
  transition: all 0.2s;
}

.bin-item:hover {
  border-color: #3498db;
}

.bin-item.filled {
  background: rgba(231, 76, 60, 0.2);
  border-color: #e74c3c;
}

.bin-item.invalid {
  opacity: 0.5;
}

.bin-id {
  font-size: 12px;
  color: #e0e0e0;
  font-weight: 500;
  margin-bottom: 4px;
}

.bin-status {
  font-size: 10px;
  color: #95a5a6;
}

/* 电机状态 */
.motor-list {
  max-height: 250px;
  overflow-y: auto;
}

.motor-item {
  background: rgba(0,0,0,0.2);
  border: 1px solid #2c3e50;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
}

.motor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.motor-name {
  font-size: 13px;
  color: #e0e0e0;
  font-weight: 500;
}

.motor-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(231, 76, 60, 0.2);
  color: #e74c3c;
}

.motor-status.active {
  background: rgba(46, 204, 113, 0.2);
  color: #2ecc71;
}

.motor-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.motor-detail {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.motor-detail > span:first-child {
  color: #95a5a6;
}

.motor-detail > span:last-child {
  color: #e0e0e0;
  font-family: monospace;
}

.motor-detail .error-code {
  color: #e74c3c;
}

/* 激光数据 */
.laser-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.laser-preview {
  width: 200px;
  height: 200px;
  background: rgba(0,0,0,0.3);
  border: 1px solid #2c3e50;
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}

.laser-points {
  width: 100%;
  height: 100%;
  position: relative;
}

.laser-point {
  position: absolute;
  width: 3px;
  height: 3px;
  background: #00d9ff;
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

/* Modbus数据 */
.modbus-form {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.modbus-result {
  margin-top: 12px;
}

.modbus-result h5 {
  font-size: 12px;
  color: #95a5a6;
  margin-bottom: 8px;
}

.modbus-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 8px;
}

.modbus-item {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  background: rgba(0,0,0,0.2);
  border-radius: 4px;
  font-size: 12px;
}

.modbus-addr {
  color: #95a5a6;
}

.modbus-value {
  color: #00d9ff;
  font-family: monospace;
}

/* 编码器 */
.encoder-section {
  margin-bottom: 12px;
}

.encoder-section h5 {
  font-size: 12px;
  color: #95a5a6;
  margin-bottom: 8px;
}

.encoder-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 8px;
  max-height: 150px;
  overflow-y: auto;
}

.encoder-item {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  background: rgba(0,0,0,0.2);
  border-radius: 4px;
  font-size: 12px;
}

.encoder-id {
  color: #7f8c8d;
}

.encoder-value {
  color: #00d9ff;
  font-family: monospace;
}

/* 扫图状态 */
.slam-status-display {
  display: flex;
  justify-content: center;
  padding: 24px;
}

.slam-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px;
  background: rgba(0,0,0,0.2);
  border-radius: 12px;
  min-width: 150px;
}

.slam-indicator.active {
  background: rgba(46, 204, 113, 0.2);
}

.slam-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #2c3e50;
  position: relative;
}

.slam-indicator.active .slam-icon {
  background: #2ecc71;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.4); }
  50% { box-shadow: 0 0 0 12px rgba(46, 204, 113, 0); }
}

.slam-text {
  font-size: 14px;
  color: #e0e0e0;
}

.slam-indicator.active .slam-text {
  color: #2ecc71;
}

/* 空状态 */
.empty-state {
  padding: 24px;
  text-align: center;
  color: #5e6d7e;
  font-size: 12px;
}
</style>
