<template>
  <div class="robokit-panel">
    <!-- 连接状态头部 -->
    <div class="conn-header">
      <div class="conn-status-row">
        <span class="conn-dot" :class="{ online: connectionStatus.connected }"></span>
        <span class="conn-text">{{ connectionStatus.connected ? '已连接' : '未连接' }}</span>
        <span class="conn-host" v-if="connectionStatus.connected">{{ connectionStatus.host }}</span>
        <button class="conn-btn" :class="{ disconnect: connectionStatus.connected }" @click="handleToggleConnection">
          {{ connectionStatus.connected ? '断开' : '连接' }}
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
        <button class="btn btn-blue full" @click="handleConnect">连接机器人</button>
      </div>
    </div>

    <!-- 已连接状态 -->
    <template v-if="connectionStatus.connected">
      <!-- 分组导航 -->
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

      <!-- 内容区 -->
      <div class="panel-content">

        <!-- ===== 概览 ===== -->
        <div v-if="activeGroup === 'overview'" class="group-content">
          <!-- 机器人信息卡 -->
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

          <!-- 位置卡 -->
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

          <!-- 速度卡 -->
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

        <!-- ===== 控制 ===== -->
        <div v-if="activeGroup === 'control'" class="group-content">
          <!-- 控制权 -->
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

          <!-- 移动控制 -->
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

          <!-- 定位控制 -->
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

          <!-- 平动 -->
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

        <!-- ===== 监控 ===== -->
        <div v-if="activeGroup === 'monitor'" class="group-content">
          <!-- 电池 -->
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

          <!-- 急停 -->
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

          <!-- I/O -->
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

          <!-- 电机 -->
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

          <!-- 编码器 -->
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

          <!-- 激光 -->
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

        <!-- ===== 导航 ===== -->
        <div v-if="activeGroup === 'navigation'" class="group-content">
          <!-- 指定路径导航：最终使用接口（置顶，多段编辑） -->
          <div class="card priority-card">
            <div class="card-head"><h4>指定路径 (3066) — 最终使用接口</h4></div>
            <p class="card-hint">向机器人发送站点序列，按序列依次经过不停留；每段必填 source_id、id、task_id（不可重复）；可带 operation（如 JackHeight）、jack_height。<strong>source_id 与 id 之间必须有直接相连的线路，不可跳点。</strong></p>
            <p class="card-hint card-warn">下发前请先在「控制」里点击<strong>「抢占控制」</strong>，抢占控制权后即可直接调用本接口。若小车未动：① 第一段 source_id 填站点名表示小车须<strong>已在该站点</strong>，否则第一段可填 <code>SELF_POSITION</code> 表示从当前位置出发；② 确认地图上站点之间有直接线路。</p>
            <p class="card-hint card-error">若报 <strong>52702 路径规划失败</strong>：① 确认地图上 <code>source_id</code> 与 <code>id</code> 两站点之间有<strong>直接连线</strong>（不可跳点）；② <code>jack_height</code> 单位为<strong>米</strong>，如 0.2 表示 0.2m，勿填 8.2 等过大数值；③ 确认地图已加载、站点 ID 与地图一致。</p>
            <div class="multi-segment-label">多段编辑</div>
            <div v-for="(seg, idx) in navForm.specifiedSegments" :key="idx" class="specified-segment">
              <div class="segment-head">第 {{ idx + 1 }} 段</div>
              <div class="input-row-3">
                <div class="form-field compact">
                  <label>source_id</label>
                  <input v-model="seg.source_id" placeholder="如 LM1" />
                </div>
                <div class="form-field compact">
                  <label>id</label>
                  <input v-model="seg.id" placeholder="如 LM2" />
                </div>
                <div class="form-field compact">
                  <label>task_id</label>
                  <input v-model="seg.task_id" placeholder="必填，唯一" />
                </div>
              </div>
              <div class="input-row-3">
                <div class="form-field compact">
                  <label>operation (可选)</label>
                  <select v-model="seg.operation">
                    <option value="">无</option>
                    <option value="JackHeight">JackHeight</option>
                    <option value="JackLoad">JackLoad</option>
                    <option value="JackUnload">JackUnload</option>
                    <option value="Wait">Wait</option>
                  </select>
                </div>
                <div class="form-field compact">
                  <label>jack_height (可选)</label>
                  <input v-model.number="seg.jack_height" type="number" step="0.01" placeholder="单位 m，如 0.2" title="单位：米，如 0.2 表示 0.2m" />
                </div>
                <div class="form-field compact segment-actions">
                  <label>&nbsp;</label>
                  <button type="button" class="btn btn-ghost-sm small" @click="removeSpecifiedSegment(idx)" :disabled="navForm.specifiedSegments.length <= 1">删除</button>
                </div>
              </div>
            </div>
            <div class="btn-row-2">
              <button type="button" class="btn btn-ghost-sm" @click="addSpecifiedSegment" :disabled="loading">+ 添加一段</button>
              <button type="button" class="btn btn-blue full" @click="handleSpecifiedPathNavigation" :disabled="loading">指定路径(3066)</button>
            </div>
          </div>

          <!-- 路径导航 (仅单车测试) -->
          <div class="card">
            <div class="card-head"><h4>路径导航 (3051)</h4></div>
            <p class="card-hint"><strong>仅用于单车/任务链测试</strong>，不能用于调度场景（否则速度不连续、不跟随路径等危险）。给定起点、终点站点名，机器人沿固定路径运行；起点可为 SELF_POSITION。</p>
            <p class="card-hint card-error">若<strong>路径导航失败</strong>或报 52702：① 确认地图上起点与终点<strong>有直接连线</strong>；② 若小车不在起点，起点填 <code>SELF_POSITION</code>；③ task_id 可选，若填须唯一。</p>
            <div class="input-row-3">
              <div class="form-field compact">
                <label>起点 source_id</label>
                <input v-model="navForm.sourceId" placeholder="如 LM2 或 SELF_POSITION" />
              </div>
              <div class="form-field compact">
                <label>终点 id</label>
                <input v-model="navForm.targetId" placeholder="如 LM1" />
              </div>
              <div class="form-field compact">
                <label>task_id (可选)</label>
                <input v-model="navForm.taskId" placeholder="可选" />
              </div>
            </div>
            <button class="btn btn-blue full" @click="handlePathNavigation" :disabled="loading">路径导航(3051)</button>
          </div>

          <!-- 导航控制：停止/暂停/继续/取消 -->
          <div class="card">
            <div class="card-head"><h4>导航控制</h4></div>
            <div class="btn-row-2">
              <button class="btn btn-red" @click="handleStopNavigation" :disabled="loading">停止导航(3052)</button>
              <button class="btn btn-ghost-sm" @click="handlePauseNavigation" :disabled="loading">暂停(3001)</button>
              <button class="btn btn-ghost-sm" @click="handleResumeNavigation" :disabled="loading">继续(3002)</button>
              <button class="btn btn-ghost-sm" @click="handleCancelNavigation" :disabled="loading">取消(3003)</button>
            </div>
          </div>

          <!-- 转动 (3056) -->
          <div class="card">
            <div class="card-head"><h4>转动 (3056)</h4></div>
            <p class="card-hint">固定角速度旋转固定角度，角度单位 rad</p>
            <div class="input-row-3">
              <div class="form-field compact">
                <label>角度 (rad)</label>
                <input v-model.number="navForm.moveAngle" type="number" step="0.01" placeholder="如 1.57" />
              </div>
              <div class="form-field compact">
                <label>角速度 (rad/s)</label>
                <input v-model.number="navForm.speedW" type="number" step="0.1" placeholder="可选" />
              </div>
              <div class="form-field compact">
                <label>定位模式</label>
                <select v-model.number="navForm.locMode">
                  <option :value="0">里程</option>
                  <option :value="1">激光</option>
                </select>
              </div>
            </div>
            <button class="btn btn-blue-outline full" @click="handleTurn" :disabled="loading">执行转动</button>
          </div>

          <!-- 托盘旋转 (3057) -->
          <div class="card">
            <div class="card-head"><h4>托盘旋转 (3057)</h4></div>
            <div class="input-row-2">
              <div class="form-field compact">
                <label>角度 (rad)</label>
                <input v-model.number="navForm.spinAngle" type="number" step="0.01" placeholder="如 1.57" />
              </div>
              <button class="btn btn-blue-outline" style="align-self:flex-end" @click="handleSpin" :disabled="loading">执行</button>
            </div>
          </div>

          <!-- 圆弧运动 (3058) / 启用禁用线路 (3059) -->
          <div class="card">
            <div class="card-head"><h4>圆弧(3058) / 线路(3059)</h4></div>
            <p class="card-hint">JSON 格式，见接口文档。圆弧示例: {"radius": 1, "angle": 1.57}</p>
            <div class="form-field">
              <label>请求体 JSON</label>
              <textarea v-model="navForm.genericNavJson" rows="3" placeholder='{"key": "value"}' class="json-textarea"></textarea>
            </div>
            <div class="btn-row-2">
              <button class="btn btn-ghost-sm" @click="handleCircular" :disabled="loading">圆弧运动(3058)</button>
              <button class="btn btn-ghost-sm" @click="handlePathEnable" :disabled="loading">启用禁用线路(3059)</button>
            </div>
          </div>

          <!-- 清除路径 -->
          <div class="card">
            <div class="card-head"><h4>清除导航路径</h4></div>
            <div class="input-row-2">
              <div class="form-field compact">
                <label>task_id (3068)</label>
                <input v-model="navForm.clearTaskId" placeholder="按任务id清除时填写" />
              </div>
              <div class="btn-row-2">
                <button class="btn btn-ghost-sm" @click="handleClearTargetList" :disabled="loading">清除指定路径(3067)</button>
                <button class="btn btn-ghost-sm" @click="handleClearByTaskId" :disabled="loading">按 task_id 清除(3068)</button>
              </div>
            </div>
          </div>

          <!-- 任务链 -->
          <div class="card">
            <div class="card-head"><h4>任务链 (3101/3115/3106)</h4></div>
            <div class="btn-row-2" style="margin-bottom:8px">
              <button class="btn btn-ghost-sm" @click="handleGetTasklistStatus" :disabled="loading">查询任务链状态(3101)</button>
              <button class="btn btn-ghost-sm" @click="handleGetTasklistList" :disabled="loading">查询所有任务链(3115)</button>
            </div>
            <div class="input-row-2">
              <div class="form-field compact">
                <label>预存任务链名称</label>
                <input v-model="navForm.tasklistName" placeholder="执行(3106)时填写" />
              </div>
              <button class="btn btn-blue-outline" @click="handleExecuteTasklist" :disabled="loading">执行预存任务链(3106)</button>
            </div>
            <div v-if="tasklistResult" class="tasklist-result">
              <div v-if="tasklistStatusHint" class="tasklist-hint">{{ tasklistStatusHint }}</div>
              <pre>{{ tasklistResult }}</pre>
            </div>
          </div>

          <!-- 获取路径 (3053) -->
          <div class="card">
            <div class="card-head"><h4>获取路径导航的路径 (3053)</h4></div>
            <button class="btn btn-ghost full" @click="handleGetTargetPath" :disabled="loading">获取当前路径</button>
          </div>

          <!-- 导航状态 -->
          <div class="card">
            <div class="card-head">
              <h4>导航状态</h4>
              <button class="icon-btn" @click="loadNavStatus" :disabled="loading" title="刷新">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M12 7a5 5 0 11-1.5-3.5M12 2v3h-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>
            </div>
            <div class="kv-grid compact">
              <div class="kv-item"><span class="kv-key">状态</span><span class="kv-val">{{ navStatusInfo.status || '-' }}</span></div>
              <div class="kv-item"><span class="kv-key">定位状态</span><span class="kv-val">{{ navStatusInfo.loc_status || '-' }}</span></div>
            </div>
          </div>

          <!-- 库位 -->
          <div class="card">
            <div class="card-head">
              <h4>库位状态</h4>
              <span class="kv-val" v-if="binsInfo.bins?.length">{{ binsInfo.bins.length }} 个</span>
              <button class="icon-btn" @click="loadBins" :disabled="loading" title="刷新">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M12 7a5 5 0 11-1.5-3.5M12 2v3h-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>
            </div>
            <div class="bins-grid" v-if="binsInfo.bins?.length">
              <div v-for="bin in binsInfo.bins" :key="bin.binId" class="bin-chip" :class="{ filled: bin.filled }">
                <span class="bin-id">{{ bin.binId }}</span>
                <span class="bin-st">{{ bin.filled ? '占用' : '空闲' }}</span>
              </div>
            </div>
            <div class="empty-hint" v-else>点击刷新获取库位数据</div>
          </div>

          <!-- Modbus -->
          <div class="card">
            <div class="card-head"><h4>Modbus 查询</h4></div>
            <div class="input-row-2">
              <div class="form-field compact" style="flex:2">
                <label>寄存器</label>
                <input v-model="modbusRegisters" placeholder="121,122,123" />
              </div>
              <button class="btn btn-blue" style="align-self:flex-end" @click="handleQueryModbus" :disabled="loading">查询</button>
            </div>
            <div class="modbus-result" v-if="Object.keys(modbusResult).length">
              <h5>4x 寄存器</h5>
              <div class="kv-grid compact">
                <div class="kv-item" v-for="(val, key) in modbusResult['4x'] || {}" :key="key">
                  <span class="kv-key">{{ key }}</span>
                  <span class="kv-val accent">{{ val }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- SLAM -->
          <div class="card">
            <div class="card-head">
              <h4>SLAM 扫图</h4>
              <button class="icon-btn" @click="loadSlam" :disabled="loading" title="刷新">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M12 7a5 5 0 11-1.5-3.5M12 2v3h-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>
            </div>
            <div class="slam-display">
              <span class="slam-dot" :class="{ scanning: slamInfo.slam_status === 1 }"></span>
              <span class="slam-text">{{ slamStatusText }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 日志 -->
    <div class="log-section">
      <div class="log-head">
        <h4>操作日志</h4>
        <span class="log-count">{{ logs.length }}</span>
      </div>
      <div class="log-list">
        <div v-for="(entry, i) in logs" :key="i" class="log-entry" :class="{ error: entry.error, success: entry.success }">
          <span class="log-time">{{ entry.time }}</span>
          <span class="log-msg">{{ entry.message }}</span>
        </div>
        <div class="empty-hint" v-if="!logs.length">暂无日志</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as api from '../api'

const groups = [
  { id: 'overview', name: '概览', icon: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="1" y="1" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.5"/><rect x="9" y="1" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.5"/><rect x="1" y="9" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.5"/><rect x="9" y="9" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.5"/></svg>' },
  { id: 'control', name: '控制', icon: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="3" stroke="currentColor" stroke-width="1.5"/><path d="M8 1v2M8 13v2M1 8h2M13 8h2M3 3l1.5 1.5M11.5 11.5L13 13M3 13l1.5-1.5M11.5 4.5L13 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>' },
  { id: 'monitor', name: '监控', icon: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="1" y="2" width="14" height="10" rx="2" stroke="currentColor" stroke-width="1.5"/><path d="M5 14h6M8 12v2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>' },
  { id: 'navigation', name: '导航', icon: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3 14l5-12 5 12-5-4-5 4z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>' },
]

const activeGroup = ref('overview')
const connectionStatus = ref({ connected: false, host: '' })
const loading = ref(false)
const pollTimer = ref(null)
const moveHeartbeatTimer = ref(null)

const connectForm = ref({ host: '172.16.11.211', port: 19204 })

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

const moveForm = ref({ vx: 0.5, vy: 0, w: 0 })
const controlNickname = ref('agv-web')
const relocateForm = ref({ x: 0, y: 0, angleDeg: 0 })
const translateForm = ref({ dist: 1, vx: null, vy: null, mode: 0 })
const navForm = ref({
  target: '', type: 'point',
  sourceId: 'SELF_POSITION', targetId: 'LM1', taskId: '',
  specifiedSegments: [
    { source_id: 'LM1', id: 'LM2', task_id: '12344321', operation: '', jack_height: '' },
    { source_id: 'LM2', id: 'AP1', task_id: '12344322', operation: 'JackHeight', jack_height: 0.2 },
  ],
  moveAngle: 1.57, speedW: null, locMode: 0,
  spinAngle: 1.57, genericNavJson: '{}', clearTaskId: '', tasklistName: '',
})
const tasklistResult = ref(null)
const tasklistStatusHint = ref('')
const simpleBattery = ref(false)
const logs = ref([])

const locMethodText = computed(() => {
  const methods = { 0: '自然轮廓', 1: '反光柱', 2: '二维码', 3: '里程计', 4: '3D定位', 5: '天码', 6: '特征定位', 7: '3D特征', 8: '3D KF' }
  return methods[locationInfo.value.loc_method] || '-'
})

const slamStatusText = computed(() => {
  const map = { 0: '未扫图', 1: '扫图中', 2: '扫图完成' }
  return map[slamInfo.value.slam_status] || '未知'
})

function log(message, isError = false, isSuccess = false) {
  logs.value.unshift({ time: new Date().toLocaleTimeString(), message, error: isError, success: isSuccess })
  if (logs.value.length > 50) logs.value.pop()
}

function formatRobokitError(msg) {
  if (!msg || typeof msg !== 'string') return msg
  if (msg.includes('40009') || msg.includes('deprecated')) return msg + ' → 固件已弃用模式切换 API，抢占控制后可直接执行移动'
  if (msg.includes('40012')) return msg + ' → 调度中，请先「抢占控制」'
  if (msg.includes('40020')) return msg + ' → 控制权已被抢占'
  if (msg.includes('40101')) return msg + ' → 被其他设备锁定，需在该设备上释放'
  return msg
}

async function handleConnect() {
  loading.value = true
  try {
    const result = await api.robokitConnect(connectForm.value.host, connectForm.value.port)
    if (result?.success) {
      connectionStatus.value = { connected: true, host: connectForm.value.host }
      log('连接成功', false, true)
      await loadAllStatus()
      startPoll()
    } else {
      log('连接失败', true)
    }
  } catch (e) { log('连接错误: ' + e.message, true) }
  finally { loading.value = false }
}

async function handleDisconnect() {
  loading.value = true
  try {
    stopMoveHeartbeat()
    try { await api.robokitStop() } catch {}
    await api.robokitDisconnect()
    connectionStatus.value = { connected: false, host: '' }
    log('已断开连接', false, true)
    stopPoll()
  } catch (e) { log('断开错误: ' + e.message, true) }
  finally { loading.value = false }
}

async function handleToggleConnection() {
  connectionStatus.value.connected ? await handleDisconnect() : await handleConnect()
}

async function loadAllStatus() {
  await Promise.all([loadRobotInfo(), loadLocation(), loadSpeed(), loadBattery(), loadEmergency()])
}

async function loadRobotInfo() {
  loading.value = true
  try {
    const data = await api.robokitGetInfo()
    if (data) {
      robotInfo.value = {
        '机器人ID': data.id || '-', '型号': data.model || '-', '版本': data.version || '-',
        '固件版本': data.dsp_version || '-', '地图版本': data.map_version || '-', '当前地图': data.current_map || '-',
      }
    }
  } catch (e) { log('获取机器人信息失败: ' + e.message, true) }
  finally { loading.value = false }
}

async function loadLocation() {
  try {
    const data = await api.robokitGetLocation()
    if (data) locationInfo.value = data.data && typeof data.data === 'object' ? data.data : data
  } catch (e) { log('获取位置失败: ' + e.message, true) }
}

async function loadSpeed() {
  try {
    const data = await api.robokitGetSpeed()
    if (data) speedInfo.value = data.data && typeof data.data === 'object' ? data.data : data
  } catch (e) { log('获取速度失败: ' + e.message, true) }
}

async function loadBattery() {
  try {
    const data = await api.robokitGetBattery(simpleBattery.value)
    if (data) batteryInfo.value = data
  } catch (e) { log('获取电池状态失败: ' + e.message, true) }
}

async function loadEmergency() {
  try {
    const data = await api.robokitGetEmergency()
    if (data) emergencyInfo.value = data
  } catch (e) { log('获取急停状态失败: ' + e.message, true) }
}

async function loadIO() {
  loading.value = true
  try { const data = await api.robokitGetIO(); if (data) ioInfo.value = data }
  catch (e) { log('获取I/O状态失败: ' + e.message, true) }
  finally { loading.value = false }
}

async function loadNavStatus() {
  loading.value = true
  try {
    const [navData, locData] = await Promise.all([api.robokitGetNavStatus(), api.robokitGetLocStatus()])
    if (navData) navStatusInfo.value.status = '运行中'
    if (locData) navStatusInfo.value.loc_status = '已定位'
  } catch (e) { log('获取导航状态失败: ' + e.message, true) }
  finally { loading.value = false }
}

async function loadBins() {
  loading.value = true
  try { const data = await api.robokitGetBins(); if (data) binsInfo.value = data }
  catch (e) { log('获取库位状态失败: ' + e.message, true) }
  finally { loading.value = false }
}

async function loadMotor() {
  loading.value = true
  try { const data = await api.robokitGetMotor(); if (data) motorInfo.value = data }
  catch (e) { log('获取电机状态失败: ' + e.message, true) }
  finally { loading.value = false }
}

async function loadLaser() {
  loading.value = true
  try { const data = await api.robokitGetLaser(); if (data) laserInfo.value = data }
  catch (e) { log('获取激光数据失败: ' + e.message, true) }
  finally { loading.value = false }
}

async function loadEncoder() {
  loading.value = true
  try { const data = await api.robokitGetEncoder(); if (data) encoderInfo.value = data }
  catch (e) { log('获取编码器数据失败: ' + e.message, true) }
  finally { loading.value = false }
}

async function loadSlam() {
  loading.value = true
  try { const data = await api.robokitGetSlam(); if (data) slamInfo.value = data }
  catch (e) { log('获取扫图状态失败: ' + e.message, true) }
  finally { loading.value = false }
}

async function handleQueryModbus() {
  loading.value = true
  try {
    const registers = modbusRegisters.value.split(',').map(r => parseInt(r.trim())).filter(r => !isNaN(r))
    if (!registers.length) { log('请输入有效的寄存器地址', true); return }
    const data = await api.robokitQueryModbus(registers)
    if (data) { modbusResult.value = data; log(`Modbus查询成功: ${registers.join(',')}`, false, true) }
  } catch (e) { log('Modbus查询失败: ' + e.message, true) }
  finally { loading.value = false }
}

async function handleTakeControl() {
  loading.value = true
  try {
    try { await api.robokitTakeControl(controlNickname.value || 'agv-web'); log('抢占控制权成功', false, true); return } catch {}
    try { await api.robokitStopNavigation(); log('已停止导航', false, true); return } catch {}
    await api.robokitStop(); log('已发送停止指令', false, true)
  } catch (e) { log('抢占控制失败: ' + formatRobokitError(e.message), true) }
  finally { loading.value = false }
}

async function handleReleaseControl() {
  loading.value = true
  try { await api.robokitReleaseControl(); log('已释放控制权', false, true) }
  catch (e) { log('释放控制失败: ' + formatRobokitError(e.message), true) }
  finally { loading.value = false }
}

async function handleSetMode(mode) {
  loading.value = true
  try {
    await api.robokitSetMode(mode)
    log(mode === 0 ? '已切换到手动模式' : '已切换到自动模式', false, true)
  } catch (e) {
    const msg = e.message || ''
    if (msg.includes('40009') || msg.includes('deprecated')) {
      log('当前固件已弃用模式切换，抢占控制后可直接执行移动', false, true)
    } else { log('切换模式失败: ' + formatRobokitError(msg), true) }
  } finally { loading.value = false }
}

async function handleMove() {
  if (moveHeartbeatTimer.value) { log('速度指令发送中，点击「停止」结束', false, true); return }
  loading.value = true
  try {
    try { await api.robokitTakeControl(controlNickname.value || 'agv-web') } catch {}
    try { await api.robokitSetMode(0) } catch {}
    const result = await api.robokitMove(moveForm.value.vx, moveForm.value.vy, moveForm.value.w)
    if (result?.ret_code === 0) {
      log(`开始移动: Vx=${moveForm.value.vx} Vy=${moveForm.value.vy} W=${moveForm.value.w}`, false, true)
      moveHeartbeatTimer.value = setInterval(async () => {
        if (!connectionStatus.value.connected) { stopMoveHeartbeat(); return }
        try { await api.robokitMove(moveForm.value.vx, moveForm.value.vy, moveForm.value.w) } catch {}
      }, 150)
      await Promise.all([loadSpeed(), loadLocation()])
    } else { log('移动指令失败', true) }
  } catch (e) { log('移动错误: ' + formatRobokitError(e.message), true) }
  finally { loading.value = false }
}

async function handleStop() {
  stopMoveHeartbeat()
  loading.value = true
  try {
    try { await api.robokitTakeControl(controlNickname.value || 'agv-web') } catch {}
    try { await api.robokitSetMode(0) } catch {}
    const result = await api.robokitStop()
    if (result?.ret_code === 0) { log('停止指令已发送', false, true); await Promise.all([loadSpeed(), loadLocation()]) }
    else { log('停止指令失败', true) }
  } catch (e) { log('停止错误: ' + formatRobokitError(e.message), true) }
  finally { loading.value = false }
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
    if (result?.ret_code === 0) {
      log(`重定位: X=${relocateForm.value.x} Y=${relocateForm.value.y} 角度=${relocateForm.value.angleDeg}°`, false, true)
      await loadLocation()
      try { const cr = await api.robokitConfirmLocation(); if (cr?.ret_code === 0) log('已确认定位', false, true) } catch {}
      await loadLocation()
    } else { log('重定位失败', true) }
  } catch (e) { log('重定位错误: ' + formatRobokitError(e.message), true) }
  finally { loading.value = false }
}

async function handleConfirmLocation() {
  loading.value = true
  try {
    const result = await api.robokitConfirmLocation()
    if (result?.ret_code === 0) { log('定位已确认', false, true); await loadLocation() }
    else { log('确认定位失败', true) }
  } catch (e) { log('确认定位错误: ' + formatRobokitError(e.message), true) }
  finally { loading.value = false }
}

async function handleCancelRelocate() {
  loading.value = true
  try {
    const result = await api.robokitCancelRelocate()
    if (result?.ret_code === 0) log('已取消重定位', false, true)
    else log('取消重定位失败', true)
  } catch (e) { log('取消重定位错误: ' + formatRobokitError(e.message), true) }
  finally { loading.value = false }
}

async function handleTranslate() {
  loading.value = true
  try {
    const dist = Number(translateForm.value.dist)
    if (!Number.isFinite(dist) || dist <= 0) { log('请填写有效距离', true); return }
    const vx = translateForm.value.vx != null && translateForm.value.vx !== '' ? translateForm.value.vx : null
    const vy = translateForm.value.vy != null && translateForm.value.vy !== '' ? translateForm.value.vy : null
    const result = await api.robokitTranslate(dist, vx, vy, translateForm.value.mode ?? 0)
    if (result?.ret_code === 0) {
      log(`平动: 距离=${dist}m${vx != null ? ` Vx=${vx}` : ''}${vy != null ? ` Vy=${vy}` : ''}`, false, true)
      await loadLocation()
    } else { log('平动指令失败', true) }
  } catch (e) { log('平动错误: ' + (e.message || e), true) }
  finally { loading.value = false }
}

async function handleEmergencyStop() {
  loading.value = true
  try {
    const result = await api.robokitEmergencyStop()
    if (result?.ret_code === 0) log('紧急停车已执行', false, true)
    else log('紧急停车失败', true)
  } catch (e) { log('紧急停车错误: ' + formatRobokitError(e.message), true) }
  finally { loading.value = false }
}

async function handleQuickRelocate() {
  loading.value = true
  try {
    await loadLocation()
    const x = locationInfo.value.x ?? 0
    const y = locationInfo.value.y ?? 0
    const angleRad = (locationInfo.value.angle ?? 0) * 1
    const result = await api.robokitRelocate(x, y, angleRad)
    if (result?.ret_code === 0) {
      log(`已发起重定位 (${x.toFixed(2)}, ${y.toFixed(2)})，请等待约10-30秒定位完成后再执行导航`, false, true)
      try { await api.robokitConfirmLocation() } catch (_) {}
    } else { log('重定位失败', true) }
  } catch (e) { log('重定位错误: ' + formatRobokitError(e.message), true) }
  finally { loading.value = false }
}

async function handleMoveTo() {
  const target = navForm.value.target?.trim()
  if (!target) { log('请输入目标', true); return }
  loading.value = true
  try {
    // 导航需在自动模式下执行，先尝试切换（部分固件已弃用 4000 则忽略失败）
    try {
      await api.robokitSetMode(1)
    } catch (_) { /* 40009 等忽略 */ }
    const result = await api.robokitMoveTo(target, navForm.value.type)
    if (result?.ret_code === 0) log(`导航到 ${navForm.value.type}: ${target}`, false, true)
    else log(`导航指令失败: ${result?.err_msg || 'ret_code=' + (result?.ret_code ?? '?')}`, true)
  } catch (e) { log('导航错误: ' + e.message, true) }
  finally { loading.value = false }
}

async function handlePathNavigation() {
  loading.value = true
  try {
    const sourceId = (navForm.value.sourceId || '').trim()
    const targetId = (navForm.value.targetId || '').trim()
    if (!sourceId || !targetId) { log('请填写起点 source_id 与终点 id', true); return }
    const taskId = (navForm.value.taskId || '').trim() || null
    const result = await api.robokitPathNavigation(sourceId, targetId, taskId)
    if (result?.ret_code === 0) log(`路径导航(3051) ${sourceId} → ${targetId}`, false, true)
    else log('路径导航失败', true)
  } catch (e) { log('路径导航错误: ' + e.message, true) }
  finally { loading.value = false }
}

function addSpecifiedSegment() {
  const segments = navForm.value.specifiedSegments
  navForm.value.specifiedSegments = [
    ...segments,
    { source_id: '', id: '', task_id: '', operation: '', jack_height: '' },
  ]
}

function removeSpecifiedSegment(idx) {
  if (navForm.value.specifiedSegments.length <= 1) return
  const segments = [...navForm.value.specifiedSegments]
  segments.splice(idx, 1)
  navForm.value.specifiedSegments = segments
}

async function handleSpecifiedPathNavigation() {
  loading.value = true
  try {
    const list = []
    for (const seg of navForm.value.specifiedSegments) {
      const source_id = (seg.source_id || '').trim()
      const id = (seg.id || '').trim()
      const task_id = (seg.task_id || '').trim()
      if (!source_id || !id || !task_id) {
        log('指定路径(3066) 每段须填写 source_id、id、task_id', true)
        return
      }
      const item = { source_id, id, task_id }
      if (seg.operation && seg.operation !== '') item.operation = seg.operation
      if (seg.jack_height != null && seg.jack_height !== '' && Number.isFinite(Number(seg.jack_height))) {
        item.jack_height = Number(seg.jack_height)
      }
      list.push(item)
    }
    for (let i = 0; i < list.length - 1; i++) {
      const currEnd = list[i].id
      const nextStart = list[i + 1].source_id
      if (currEnd !== nextStart) {
        log(`第 ${i + 1} 段终点「${currEnd}」与第 ${i + 2} 段起点「${nextStart}」不一致，线路不连续，小车可能不执行后续段或报错`, true)
        log('请将下一段的 source_id 改为上一段的 id，保证首尾相连', true)
      }
    }
    const requestBody = { move_task_list: list }
    const requestStr = JSON.stringify(requestBody, null, 2)
    log('指定路径(3066) 请求体:', false, false)
    log(requestStr, false, false)
    const result = await api.robokitSpecifiedPathNavigation(list)
    if (result?.ret_code === 0) {
      log(`指定路径(3066) 已下发 ${list.length} 段`, false, true)
      log('机器人响应: ' + JSON.stringify(result), false, false)
      try {
        const status = await api.robokitGetTasklistStatus()
        if (status && (status.task_status !== undefined || status.task_type !== undefined)) {
          const st = status.task_status ?? status.status ?? '-'
          const type = status.task_type ?? '-'
          log(`任务状态: task_type=${type} task_status=${st}`, false, false)
        }
      } catch (_) { /* 仅辅助，忽略 */ }
      log('若小车未动: 请确认已抢占控制权，并确认站点间有直接线路', false, false)
    } else {
      log(`指定路径失败: ret_code=${result?.ret_code ?? '?'} ${result?.err_msg || ''}`, true)
      if (result) log('完整响应: ' + JSON.stringify(result), true, false)
    }
  } catch (e) { log('指定路径导航错误: ' + e.message, true) }
  finally { loading.value = false }
}

async function handleStopNavigation() {
  loading.value = true
  try {
    const result = await api.robokitStopNavigation()
    if (result?.ret_code === 0) log('导航已停止', false, true)
    else log('停止导航失败', true)
  } catch (e) { log('停止导航错误: ' + e.message, true) }
  finally { loading.value = false }
}

async function handlePauseNavigation() {
  loading.value = true
  try {
    const result = await api.robokitPauseNavigation()
    if (result?.ret_code === 0) log('已暂停当前导航(3001)', false, true)
    else log('暂停失败', true)
  } catch (e) { log('暂停导航错误: ' + e.message, true) }
  finally { loading.value = false }
}

async function handleResumeNavigation() {
  loading.value = true
  try {
    const result = await api.robokitResumeNavigation()
    if (result?.ret_code === 0) log('已继续当前导航(3002)', false, true)
    else log('继续失败', true)
  } catch (e) { log('继续导航错误: ' + e.message, true) }
  finally { loading.value = false }
}

async function handleCancelNavigation() {
  loading.value = true
  try {
    const result = await api.robokitCancelNavigation()
    if (result?.ret_code === 0) log('已取消当前导航(3003)', false, true)
    else log('取消失败', true)
  } catch (e) { log('取消导航错误: ' + e.message, true) }
  finally { loading.value = false }
}

async function handleTurn() {
  loading.value = true
  try {
    const angle = Number(navForm.value.moveAngle)
    if (!Number.isFinite(angle)) { log('请填写有效角度', true); return }
    const speedW = navForm.value.speedW != null && navForm.value.speedW !== '' ? Number(navForm.value.speedW) : null
    const result = await api.robokitTurn(angle, speedW, navForm.value.locMode ?? 0)
    if (result?.ret_code === 0) log(`转动 ${angle} rad`, false, true)
    else log('转动失败', true)
  } catch (e) { log('转动错误: ' + e.message, true) }
  finally { loading.value = false }
}

async function handleSpin() {
  loading.value = true
  try {
    const angle = Number(navForm.value.spinAngle)
    if (!Number.isFinite(angle)) { log('请填写有效角度', true); return }
    const result = await api.robokitSpin({ angle })
    if (result?.ret_code === 0) log(`托盘旋转 ${angle} rad`, false, true)
    else log('托盘旋转失败', true)
  } catch (e) { log('托盘旋转错误: ' + e.message, true) }
  finally { loading.value = false }
}

async function handleCircular() {
  loading.value = true
  try {
    const body = JSON.parse(navForm.value.genericNavJson || '{}')
    const result = await api.robokitCircular(body)
    if (result?.ret_code === 0) log('圆弧运动已下发(3058)', false, true)
    else log('圆弧运动失败', true)
  } catch (e) {
    if (e instanceof SyntaxError) log('JSON 格式错误', true)
    else log('圆弧运动错误: ' + e.message, true)
  }
  finally { loading.value = false }
}

async function handlePathEnable() {
  loading.value = true
  try {
    const body = JSON.parse(navForm.value.genericNavJson || '{}')
    const result = await api.robokitPathEnable(body)
    if (result?.ret_code === 0) log('启用/禁用线路已下发(3059)', false, true)
    else log('启用/禁用线路失败', true)
  } catch (e) {
    if (e instanceof SyntaxError) log('JSON 格式错误', true)
    else log('启用/禁用线路错误: ' + e.message, true)
  }
  finally { loading.value = false }
}

async function handleClearTargetList() {
  loading.value = true
  try {
    const result = await api.robokitClearTargetList()
    if (result?.ret_code === 0) log('已清除指定导航路径(3067)', false, true)
    else log('清除失败', true)
  } catch (e) { log('清除路径错误: ' + e.message, true) }
  finally { loading.value = false }
}

async function handleClearByTaskId() {
  const taskId = (navForm.value.clearTaskId || '').trim()
  if (!taskId) { log('请填写 task_id', true); return }
  loading.value = true
  try {
    const result = await api.robokitClearByTaskId(taskId)
    if (result?.ret_code === 0) log(`已按 task_id 清除(3068): ${taskId}`, false, true)
    else log('清除失败', true)
  } catch (e) { log('按 task_id 清除错误: ' + e.message, true) }
  finally { loading.value = false }
}

const TASKLIST_STATUS_MAP = {
  0: '无/空闲',
  1: '运行中',
  2: '完成',
  3: '失败',
  4: '取消',
  5: '暂停',
  6: '已结束/完成(以接口文档为准)',
}
async function handleGetTasklistStatus() {
  loading.value = true
  tasklistStatusHint.value = ''
  try {
    const data = await api.robokitGetTasklistStatus()
    tasklistResult.value = data != null ? JSON.stringify(data, null, 2) : null
    if (data != null) {
      log('已查询任务链状态(3101)', false, true)
      const ts = data?.tasklist_status
      if (ts && typeof ts.taskListStatus === 'number') {
        const s = ts.taskListStatus
        tasklistStatusHint.value = `taskListStatus=${s} (${TASKLIST_STATUS_MAP[s] ?? '见接口文档'})`
      }
    }
  } catch (e) { log('查询任务链状态错误: ' + e.message, true) }
  finally { loading.value = false }
}

async function handleGetTasklistList() {
  loading.value = true
  try {
    const data = await api.robokitGetTasklistList()
    tasklistResult.value = data != null ? JSON.stringify(data, null, 2) : null
    if (data != null) log('已查询所有任务链(3115)', false, true)
  } catch (e) { log('查询任务链列表错误: ' + e.message, true) }
  finally { loading.value = false }
}

async function handleExecuteTasklist() {
  const name = (navForm.value.tasklistName || '').trim()
  if (!name) { log('请填写预存任务链名称', true); return }
  loading.value = true
  try {
    const result = await api.robokitExecuteTasklist(name)
    if (result?.ret_code === 0) log(`已执行预存任务链(3106): ${name}`, false, true)
    else log('执行任务链失败', true)
  } catch (e) { log('执行任务链错误: ' + e.message, true) }
  finally { loading.value = false }
}

async function handleGetTargetPath() {
  loading.value = true
  try {
    const data = await api.robokitGetTargetPath()
    tasklistResult.value = data != null ? JSON.stringify(data, null, 2) : null
    if (data != null) log('已获取路径(3053)', false, true)
  } catch (e) { log('获取路径错误: ' + e.message, true) }
  finally { loading.value = false }
}

function startPoll() {
  if (pollTimer.value) return
  pollTimer.value = setInterval(() => {
    if (connectionStatus.value.connected) {
      loadLocation(); loadSpeed(); loadEmergency()
    }
  }, 1000)
}

function stopPoll() {
  if (pollTimer.value) { clearInterval(pollTimer.value); pollTimer.value = null }
}

function stopMoveHeartbeat() {
  if (moveHeartbeatTimer.value) { clearInterval(moveHeartbeatTimer.value); moveHeartbeatTimer.value = null }
}

onMounted(() => { log('Robokit面板已初始化'); startPoll() })
onUnmounted(() => {
  stopMoveHeartbeat()
  api.robokitStop().catch(() => {})
  stopPoll()
})
</script>

<style scoped>
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

/* 内容区 */
.panel-content {
  flex: 1;
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

.ctrl-form-row { margin-bottom: 10px; }
.ctrl-btns { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }

.btn-row-2 { display: flex; gap: 8px; }
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
  max-height: 120px; overflow-y: auto; padding: 0 12px 10px;
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
