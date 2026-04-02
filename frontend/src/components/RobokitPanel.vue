<template>
  <div class="robokit-panel">
    <!-- 连接状态头部 -->
    <div class="conn-header">
      <div class="conn-status-row">
        <span class="conn-dot" :class="{ online: connectionStatus.connected }"></span>
        <span class="conn-text">{{ connectionStatus.connected ? '已连接' : '未连接' }}</span>
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
          <!-- 智能路径规划：输入起点终点自动生成 move_task_list -->
          <div class="card">
            <div class="card-head"><h4>智能路径规划</h4></div>
            <p class="card-hint">
              本功能相当于<strong>指定路径 (3066) 的自动填表</strong>：根据已加载地图用 BFS 求最短站点序列，自动生成每段的
              <code>source_id</code>、<code>id</code>、<code>task_id</code> 并写入下方多段表单；你仍可改货叉参数后再下发。
              无需再手工逐段添加中间点。
            </p>
            <p class="card-hint card-warn">
              <strong>「规划路径」不会让机器人动：</strong>只请求本机后端 <code>/map/plan-path</code> 算路并更新下方表单。真正下发导航必须再点「指定路径（3066）」或「一键搬运」等按钮。
            </p>
            <div class="input-row-3">
              <div class="form-field compact">
                <label>起点</label>
                <input v-model="planPathForm.sourceId" placeholder="如 LM1" />
              </div>
              <div class="form-field compact">
                <label>终点</label>
                <input v-model="planPathForm.targetId" placeholder="如 AP1" />
              </div>
              <div class="form-field compact segment-actions">
                <label>&nbsp;</label>
                <button type="button" class="btn btn-blue" @click="handlePlanPath" :disabled="loading">规划路径</button>
              </div>
            </div>
            <p class="card-hint plan-fork-hint">
              货叉参数（可选，单位 m）：规划成功后会自动写入<strong>下方每一段</strong>；留空的项不下发。若勾选末段 <code>ForkUnload</code>，最后一段仍会强制 <code>end_height=0</code>。
            </p>
            <div class="input-row-4 fork-height-row plan-fork-defaults">
              <div class="form-field compact">
                <label>start_height (m) 起步前举升</label>
                <input v-model.number="planPathForm.start_height" type="number" step="0.01" placeholder="可选" />
              </div>
              <div class="form-field compact">
                <label>fork_mid_height (m) 行走中举升</label>
                <input v-model.number="planPathForm.fork_mid_height" type="number" step="0.01" placeholder="可选" />
              </div>
              <div class="form-field compact">
                <label>end_height (m) 到点后举升</label>
                <input v-model.number="planPathForm.end_height" type="number" step="0.01" placeholder="可选" />
              </div>
              <div class="form-field compact">
                <label>fork_dist (m) 前移距离</label>
                <input v-model.number="planPathForm.fork_dist" type="number" step="0.01" placeholder="可选" />
              </div>
            </div>
            <div class="fork-nav-options">
              <label class="fork-check">
                <input type="checkbox" v-model="navForm.planAutoUnloadLast" />
                规划后末段自动 <code>ForkUnload</code>（到终点卸货，<code>end_height=0</code>）
              </label>
              <p class="card-hint fork-nav-hint">载货任务：先叉货，再点「指定路径(3066)」；勾选后最后一段会带货叉卸载。可与下方「下发前先等 DI」配合使用。</p>
            </div>

            <div class="plan-3066-preview">
              <div class="plan-preview-toolbar">
                <h5 class="plan-preview-title">3066 请求体预览</h5>
                <div class="plan-preview-btns">
                  <button type="button" class="btn btn-ghost-sm" @click="updateSpecPath3066Preview" :disabled="loading">刷新预览</button>
                  <button type="button" class="btn btn-ghost-sm" @click="copySpecPath3066Preview" :disabled="!specPath3066PreviewJson">复制 JSON</button>
                </div>
              </div>
              <p class="card-hint plan-preview-desc">
                以下为当前下方「多段编辑」表单对应的 <code>POST</code> 体（与真正下发 3066 时一致）。规划成功后会自动更新；改表单后请点「刷新预览」核对。
              </p>
              <p class="card-hint plan-preview-desc">
                若某段未选 <code>operation</code> 但填写了货叉高度/前移参数，系统会自动补为 <code>ForkHeight</code>（已体现在下方 JSON）。
              </p>
              <p v-if="planPathLastRoute?.length" class="plan-route-line">
                <strong>站点序列：</strong><code>{{ planPathLastRoute.join(' → ') }}</code>
              </p>
              <p v-if="specPath3066PreviewError" class="card-hint card-error">{{ specPath3066PreviewError }}</p>
              <ul v-else-if="specPath3066PreviewContinuityWarnings.length" class="plan-preview-warns">
                <li v-for="(w, wi) in specPath3066PreviewContinuityWarnings" :key="wi">{{ w }}</li>
              </ul>
              <textarea
                class="json-textarea plan-preview-ta"
                readonly
                rows="14"
                :value="specPath3066PreviewJson"
                placeholder="填写起点/终点后点击「规划路径」，或编辑下方多段后点「刷新预览」"
              />
            </div>
          </div>

          <!-- 一键搬运：ForkLoad → 导航 → ForkUnload（不影响现有逻辑，独立按钮） -->
          <div class="card">
            <div class="card-head"><h4>一键搬运（新功能）</h4></div>
            <p class="card-hint">
              用于验证流程：可到取货点执行 <code>ForkLoad</code>，再导航到目标点执行 <code>ForkUnload</code>。
              可<strong>仅下发取货段</strong>或<strong>仅下发送货段</strong>分步试验；全程按钮仍走完整 A/B 流程。
              <strong>不会改变</strong>现有 3051 / 3066 的使用方式。
            </p>
            <div class="input-row-3">
              <div class="form-field compact">
                <label>取货点（站点）</label>
                <input v-model="oneKeyForm.pickId" placeholder="如 PP1" />
              </div>
              <div class="form-field compact">
                <label>放货点（站点）</label>
                <input v-model="oneKeyForm.dropId" placeholder="如 LM55" />
              </div>
              <div class="form-field compact">
                <label>模式</label>
                <select v-model="oneKeyForm.mode" class="fork-mode-select">
                  <option value="A">A：两次3051连续下发（不等待DI）</option>
                  <option value="B">B：先到取货点 → 等DI确认 → 再到放货点</option>
                </select>
              </div>
            </div>
            <div class="input-row-3">
              <div class="form-field compact">
                <label>叉好信号 DI (id)（用于 B）</label>
                <input v-model="oneKeyForm.diId" placeholder="多个用英文逗号分隔，如 1,9" />
              </div>
              <div class="form-field compact">
                <label>超时 (秒)</label>
                <input v-model.number="oneKeyForm.timeoutSec" type="number" min="5" step="1" />
              </div>
              <div class="form-field compact">
                <label>轮询 (ms)</label>
                <input v-model.number="oneKeyForm.pollMs" type="number" min="200" step="100" />
              </div>
            </div>
            <div v-if="oneKeyForm.mode === 'B'" class="input-row-3">
              <div class="form-field compact">
                <label>多路 DI 条件（模式 B）</label>
                <select v-model="oneKeyForm.diCombineMode" class="fork-mode-select">
                  <option value="all">全部满足（与）— 推荐，可降低途中误触发（如 52166）</option>
                  <option value="any">任意一路（或）— 两路先后到位也可</option>
                </select>
              </div>
            </div>
            <p class="card-hint plan-fork-hint">货叉参数（可选，单位 m）：取货段与送货段分别独立设置，互不影响。</p>
            <div class="card-hint"><strong>取货段（ForkLoad）</strong></div>
            <div class="input-row-4 fork-height-row plan-fork-defaults">
              <div class="form-field compact">
                <label>start_height (m)</label>
                <input v-model.number="oneKeyForm.pick_start_height" type="number" step="0.01" placeholder="可选" />
              </div>
              <div class="form-field compact">
                <label>fork_mid_height (m)</label>
                <input v-model.number="oneKeyForm.pick_fork_mid_height" type="number" step="0.01" placeholder="可选" />
              </div>
              <div class="form-field compact">
                <label>end_height (m)</label>
                <input v-model.number="oneKeyForm.pick_end_height" type="number" step="0.01" placeholder="可选" />
              </div>
              <div class="form-field compact">
                <label>fork_dist (m)</label>
                <input v-model.number="oneKeyForm.pick_fork_dist" type="number" step="0.01" placeholder="可选" />
              </div>
            </div>
            <div class="card-hint"><strong>送货段（ForkUnload）</strong></div>
            <div class="input-row-3">
              <div class="form-field compact">
                <label>送货段 operation</label>
                <select v-model="oneKeyForm.drop_operation" class="fork-mode-select">
                  <option value="ForkUnload">ForkUnload（到点卸货）</option>
                  <option value="ForkHeight">ForkHeight（行进中抬升）</option>
                  <option value="ForkForward">ForkForward（前移）</option>
                  <option value="Wait">Wait（不做动作）</option>
                </select>
              </div>
            </div>
            <div class="input-row-4 fork-height-row plan-fork-defaults">
              <div class="form-field compact">
                <label>start_height (m)</label>
                <input v-model.number="oneKeyForm.drop_start_height" type="number" step="0.01" placeholder="可选" />
              </div>
              <div class="form-field compact">
                <label>fork_mid_height (m)</label>
                <input v-model.number="oneKeyForm.drop_fork_mid_height" type="number" step="0.01" placeholder="可选" />
              </div>
              <div class="form-field compact">
                <label>end_height (m)</label>
                <input v-model.number="oneKeyForm.drop_end_height" type="number" step="0.01" placeholder="默认 0" />
              </div>
              <div class="form-field compact">
                <label>fork_dist (m)</label>
                <input v-model.number="oneKeyForm.drop_fork_dist" type="number" step="0.01" placeholder="可选" />
              </div>
            </div>
            <div class="fork-nav-options one-key-pre6073">
              <label class="fork-check">
                <input type="checkbox" v-model="oneKeyForm.preDelivery6073" />
                下发送货(3051)前先执行<strong>设置货叉高度</strong>（API <code>{{ api.ROBOKIT_MSG_SET_FORK_HEIGHT }}</code>）
              </label>
              <div v-if="oneKeyForm.preDelivery6073" class="input-row-3">
                <div class="form-field compact">
                  <label>目标高度 (m)</label>
                  <input v-model.number="oneKeyForm.preDelivery6073Height" type="number" step="0.01" placeholder="留空则用送货段 start_height" />
                </div>
              </div>
              <p v-if="oneKeyForm.preDelivery6073" class="card-hint fork-6073-hint">通过 <code>/robokit/call</code> 发 <strong>6040</strong> 后，页面会<strong>自动轮询</strong>状态口 <strong>1100 / 1028</strong>（<code>port=19204</code>）直至 <code>fork_height_in_place===true</code> 再下发送货 3051；若固件未返回该字段则延时约 2s 兜底。</p>
            </div>
            <div class="fork-nav-options">
              <label class="fork-check">
                <input type="checkbox" v-model="oneKeyForm.showPreview" />
                显示本次一键搬运将下发的 3051 请求（用于核对）
              </label>
              <textarea v-if="oneKeyForm.showPreview" class="json-textarea plan-preview-ta" readonly rows="12" :value="oneKeyPreviewJson" />
            </div>
            <div class="btn-row-2 one-key-split-btns">
              <button type="button" class="btn btn-ghost-sm" @click="handleOneKeyCarryPickOnly" :disabled="loading">仅下发取货段</button>
              <button type="button" class="btn btn-ghost-sm" @click="handleOneKeyCarryDropOnly" :disabled="loading">仅下发送货段</button>
            </div>
            <div class="btn-row-2">
              <button type="button" class="btn btn-ghost-sm" @click="refreshOneKeyPreview" :disabled="loading">刷新预览</button>
              <button type="button" class="btn btn-blue full" @click="handleOneKeyCarry" :disabled="loading">执行一键搬运（全程）</button>
            </div>
            <p class="card-hint card-warn">
              说明：<strong>全程</strong>为两次 <code>3051</code>（<code>SELF_POSITION</code>）。模式 B + DI：取货后<strong>不中断</strong>导航再接送货；无 DI 时两段间仍会取消/停止再接第二段。<strong>仅取货</strong>只发 ForkLoad→取货点；模式 B 且填了 DI 时会在取货点等 DI 后结束（需自行再点送货）。<strong>仅送货</strong>只发放货段（可选先 6040）。若报 <code>52166</code> 可试 DI「全部满足」。送货段 operation 可用 <code>ForkHeight</code> 等。
            </p>
          </div>

          <!-- 指定路径导航：最终使用接口（置顶，多段编辑） -->
          <div class="card priority-card">
            <div class="card-head"><h4>指定路径 (3066) — 最终使用接口</h4></div>
            <p class="card-hint">每段必填 source_id、id、task_id；货叉路径可带 <code>operation</code>：<code>ForkLoad</code> / <code>ForkUnload</code> / <code>ForkHeight</code> / <code>ForkForward</code> / <code>Wait</code>，以及可选 <code>start_height</code>、<code>fork_mid_height</code>、<code>end_height</code>（单位 m）、<code>fork_dist</code>（前移距离）。<strong>相邻段须首尾相连。</strong></p>
            <p class="card-hint card-warn">下发前请先在「控制」里点击<strong>「抢占控制」</strong>，抢占控制权后即可直接调用本接口。若小车未动：① 第一段 source_id 填站点名表示小车须<strong>已在该站点</strong>，否则第一段可填 <code>SELF_POSITION</code> 表示从当前位置出发；② 确认地图上站点之间有直接线路。</p>
            <p class="card-hint card-error">若报 <strong>52702 路径规划失败</strong>：① 确认 <code>source_id</code> 与 <code>id</code> 两站点间有<strong>直接连线</strong>；② 货叉高度类参数单位为<strong>米</strong>，勿填过大；③ 地图站点 ID 与地图一致。</p>
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
                    <option value="Wait">Wait</option>
                    <option value="ForkLoad">ForkLoad</option>
                    <option value="ForkUnload">ForkUnload</option>
                    <option value="ForkHeight">ForkHeight</option>
                    <option value="ForkForward">ForkForward</option>
                  </select>
                </div>
                <div class="form-field compact segment-actions">
                  <label>&nbsp;</label>
                  <button type="button" class="btn btn-ghost-sm small" @click="removeSpecifiedSegment(idx)" :disabled="navForm.specifiedSegments.length <= 1">删除</button>
                </div>
              </div>
              <div class="input-row-4 fork-height-row">
                <div class="form-field compact">
                  <label>start_height (m)</label>
                  <input v-model.number="seg.start_height" type="number" step="0.01" placeholder="起步前举升" />
                </div>
                <div class="form-field compact">
                  <label>fork_mid_height (m)</label>
                  <input v-model.number="seg.fork_mid_height" type="number" step="0.01" placeholder="行走中举升" />
                </div>
                <div class="form-field compact">
                  <label>end_height (m)</label>
                  <input v-model.number="seg.end_height" type="number" step="0.01" placeholder="到点后举升" />
                </div>
                <div class="form-field compact">
                  <label>fork_dist (m)</label>
                  <input v-model.number="seg.fork_dist" type="number" step="0.01" placeholder="前移距离" />
                </div>
              </div>
            </div>
            <div class="fork-nav-options">
              <label class="fork-check">
                <input type="checkbox" v-model="navForm.specPathWaitFork" />
                下发前先等待 DI 叉好（可多路，<code>status</code> 须<strong>全部为 true</strong>）
              </label>
              <div v-if="navForm.specPathWaitFork" class="input-row-3 fork-di-row">
                <div class="form-field compact">
                  <label>叉好信号 DI (id)</label>
                  <input v-model="navForm.forkDiId" placeholder="如 1,9 与监控区 id 一致" />
                </div>
                <div class="form-field compact">
                  <label>超时 (秒)</label>
                  <input v-model.number="navForm.forkWaitTimeoutSec" type="number" min="5" step="1" />
                </div>
                <div class="form-field compact">
                  <label>轮询 (ms)</label>
                  <input v-model.number="navForm.forkPollMs" type="number" min="200" step="100" />
                </div>
              </div>
            </div>
            <div class="fork-nav-options">
              <label class="fork-check">
                <input type="checkbox" v-model="navForm.specPathPre6073" />
                分段送货第二段 3051 前先执行<strong>设置货叉高度</strong>（API <code>{{ api.ROBOKIT_MSG_SET_FORK_HEIGHT }}</code>）
              </label>
              <div v-if="navForm.specPathPre6073" class="input-row-3">
                <div class="form-field compact">
                  <label>目标高度 (m)</label>
                  <input v-model.number="navForm.specPathPre6073Height" type="number" step="0.01" placeholder="留空则用末段 start_height" />
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
            <div v-if="navForm.pathNavMode !== 'pick_drop_3051'" class="input-row-3">
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
            <div v-else class="input-row-3">
              <div class="form-field compact">
                <label>取货点 id</label>
                <input v-model="navForm.pickDropPickId" placeholder="站点名，与地图一致" />
              </div>
              <div class="form-field compact">
                <label>放货点 id</label>
                <input v-model="navForm.pickDropDropId" placeholder="站点名，与地图一致" />
              </div>
              <div class="form-field compact">
                <label class="muted-label">起点</label>
                <input value="SELF_POSITION（固定）" readonly class="readonly-input" />
              </div>
            </div>
            <div class="form-field compact">
              <label>出发模式</label>
              <select v-model="navForm.pathNavMode" class="fork-mode-select">
                <option value="direct">直接出发（不等待叉货信号）</option>
                <option value="wait_fork">等待 DI 叉好后再出发</option>
                <option value="pick_drop_3051">取放货：途中 DI 全 true 则去放货点；到取货点未装货则停止</option>
              </select>
            </div>
            <div v-if="navForm.pathNavMode === 'wait_fork'" class="input-row-3">
              <div class="form-field compact">
                <label>叉好信号 DI (id)</label>
                <input v-model="navForm.forkDiId" placeholder="如 1,9，多个英文逗号分隔" />
              </div>
              <div class="form-field compact">
                <label>超时 (秒)</label>
                <input v-model.number="navForm.forkWaitTimeoutSec" type="number" min="5" step="1" />
              </div>
              <div class="form-field compact">
                <label>轮询 (ms)</label>
                <input v-model.number="navForm.forkPollMs" type="number" min="200" step="100" />
              </div>
            </div>
            <div v-if="navForm.pathNavMode === 'pick_drop_3051'" class="input-row-3">
              <div class="form-field compact">
                <label>装货就绪 DI (id)</label>
                <input v-model="navForm.forkDiId" placeholder="可选；如 1,9（都为 true 才算就绪）" />
              </div>
              <div class="form-field compact">
                <label>首段监测超时 (秒)</label>
                <input v-model.number="navForm.pickDropTimeoutSec" type="number" min="10" step="1" />
              </div>
              <div class="form-field compact">
                <label>轮询 (ms)</label>
                <input v-model.number="navForm.forkPollMs" type="number" min="200" step="100" />
              </div>
            </div>
            <div v-if="navForm.pathNavMode === 'pick_drop_3051'" class="input-row-4 fork-3051-heights">
              <div class="form-field compact">
                <label>取货段 start_height (m)</label>
                <input v-model.number="navForm.pickDropLoadStartHeight" type="number" step="0.01" placeholder="ForkLoad 可选" />
              </div>
              <div class="form-field compact">
                <label>fork_mid_height (m)</label>
                <input v-model.number="navForm.pickDropLoadMidHeight" type="number" step="0.01" placeholder="可选" />
              </div>
              <div class="form-field compact">
                <label>end_height (m)</label>
                <input v-model.number="navForm.pickDropLoadEndHeight" type="number" step="0.01" placeholder="可选" />
              </div>
              <div class="form-field compact">
                <label>fork_dist (m)</label>
                <input v-model.number="navForm.pickDropLoadForkDist" type="number" step="0.01" placeholder="可选" />
              </div>
            </div>
            <div v-if="navForm.pathNavMode === 'pick_drop_3051'" class="fork-nav-options">
              <label class="fork-check">
                <input type="checkbox" v-model="navForm.pickDropPre6073" />
                第二段送货(3051)前先执行<strong>设置货叉高度</strong>（API <code>{{ api.ROBOKIT_MSG_SET_FORK_HEIGHT }}</code>）
              </label>
              <div v-if="navForm.pickDropPre6073" class="input-row-3">
                <div class="form-field compact">
                  <label>目标高度 (m)</label>
                  <input v-model.number="navForm.pickDropPre6073Height" type="number" step="0.01" placeholder="留空则用下方 ForkUnload 高度参数" />
                </div>
              </div>
            </div>
            <p v-if="navForm.pathNavMode === 'pick_drop_3051'" class="card-hint">
              连续两次 <strong>3051</strong>：① <code>SELF_POSITION</code>→取货点（<code>ForkLoad</code>），轮询 I/O 与站点；② 多路 DI 须<strong>同一时刻</strong>全部为 <code>true</code> 后视为装货完成，再<strong>停止当前导航</strong>并发 <code>SELF_POSITION</code>→放货点；若超时仍未齐套则停止并报错。下方「本段附带货叉 ForkUnload」作用于<strong>第二段</strong>放货点。
            </p>
            <div v-if="navForm.pathNavMode !== 'pick_drop_3051'" class="fork-nav-options">
              <div class="form-field compact">
                <label>本段货叉操作 (可选)</label>
                <select v-model="navForm.pathNavOperation" class="fork-mode-select">
                  <option value="">无</option>
                  <option value="ForkLoad">ForkLoad</option>
                  <option value="ForkUnload">ForkUnload</option>
                  <option value="ForkHeight">ForkHeight</option>
                  <option value="ForkForward">ForkForward</option>
                  <option value="Wait">Wait</option>
                </select>
              </div>
              <div v-if="navForm.pathNavOperation" class="input-row-4 fork-3051-heights">
                <div class="form-field compact">
                  <label>start_height (m)</label>
                  <input v-model.number="navForm.pathNavForkStartHeight" type="number" step="0.01" placeholder="可选" />
                </div>
                <div class="form-field compact">
                  <label>fork_mid_height (m)</label>
                  <input v-model.number="navForm.pathNavForkMidHeight" type="number" step="0.01" placeholder="可选" />
                </div>
                <div class="form-field compact">
                  <label>end_height (m)</label>
                  <input v-model.number="navForm.pathNavForkEndHeight" type="number" step="0.01" placeholder="可选（ForkUnload 常用 0）" />
                </div>
                <div class="form-field compact">
                  <label>fork_dist (m)</label>
                  <input v-model.number="navForm.pathNavForkDist" type="number" step="0.01" placeholder="可选" />
                </div>
              </div>
            </div>
            <div v-else class="fork-nav-options">
              <label class="fork-check">
                <input type="checkbox" v-model="navForm.pathNavUnloadAtEnd" />
                本段附带货叉 <code>ForkUnload</code>（到终点卸货，非载货状态）
              </label>
              <div v-if="navForm.pathNavUnloadAtEnd" class="input-row-4 fork-3051-heights">
                <div class="form-field compact">
                  <label>start_height (m)</label>
                  <input v-model.number="navForm.pathNavForkStartHeight" type="number" step="0.01" placeholder="可选" />
                </div>
                <div class="form-field compact">
                  <label>fork_mid_height (m)</label>
                  <input v-model.number="navForm.pathNavForkMidHeight" type="number" step="0.01" placeholder="可选" />
                </div>
                <div class="form-field compact">
                  <label>end_height (m)</label>
                  <input v-model.number="navForm.pathNavForkEndHeight" type="number" step="0.01" title="卸货常用 0" />
                </div>
                <div class="form-field compact">
                  <label>fork_dist (m)</label>
                  <input v-model.number="navForm.pathNavForkDist" type="number" step="0.01" placeholder="可选" />
                </div>
              </div>
            </div>
            <div class="fork-nav-options path-nav-fork-state">
              <div class="input-row-3">
                <div class="form-field compact">
                  <label>货叉动作后</label>
                  <select v-model="navForm.pathNavForkAfterMode" class="fork-mode-select">
                    <option value="in_place">等待 fork_height_in_place（轮询状态口）</option>
                    <option value="delay">仅固定延时</option>
                    <option value="none">不等待</option>
                  </select>
                </div>
                <div v-if="navForm.pathNavForkAfterMode === 'delay'" class="form-field compact">
                  <label>延时 (秒)</label>
                  <input v-model.number="navForm.pathNavForkAfterDelaySec" type="number" min="0" step="0.5" />
                </div>
                <div v-else class="form-field compact">
                  <label class="muted-label">&nbsp;</label>
                  <span class="readonly-input path-nav-fork-state-spacer">—</span>
                </div>
                <div class="form-field compact">
                  <label>状态口顺序</label>
                  <select v-model="navForm.pathNavForkStatusPrefer" class="fork-mode-select">
                    <option value="auto">自动（先 1100 再 1028）</option>
                    <option value="1100">优先 1100</option>
                    <option value="1028">优先 1028</option>
                  </select>
                </div>
              </div>
              <p class="card-hint compact-hint">适用于本卡「发送 6040」及本段货叉为 ForkLoad / ForkHeight / ForkUnload / ForkForward 的 <strong>3051</strong> 下发成功后（<code>Wait</code> 与「无」不跟状态）。</p>
            </div>
            <div class="fork-nav-options path-nav-6040-block">
              <div class="card-hint compact-hint">可与 3051 分开测试：<strong>设置货叉高度</strong>（<code>{{ api.ROBOKIT_MSG_SET_FORK_HEIGHT }}</code>，立即返回；是否再轮询 <code>fork_height_in_place</code> 由上方「货叉动作后」决定。</div>
              <div class="input-row-3 path-nav-6040-row">
                <div class="form-field compact">
                  <label>height (m)</label>
                  <input v-model.number="navForm.pathNav6040Height" type="number" step="0.01" placeholder="如 0.15、1.2" />
                </div>
                <div class="form-field compact path-nav-6040-actions">
                  <label class="muted-label">&nbsp;</label>
                  <button type="button" class="btn btn-ghost-sm" @click="handlePathNav6040SetHeight()" :disabled="loading">发送 {{ api.ROBOKIT_MSG_SET_FORK_HEIGHT }}</button>
                </div>
              </div>
              <div class="path-nav-6040-quick">
                <span class="quick-label">快捷高度 (m)</span>
                <button type="button" class="btn btn-ghost-sm small" @click="handlePathNav6040Quick(0)" :disabled="loading">0</button>
                <button type="button" class="btn btn-ghost-sm small" @click="handlePathNav6040Quick(0.1)" :disabled="loading">0.1</button>
                <button type="button" class="btn btn-ghost-sm small" @click="handlePathNav6040Quick(0.15)" :disabled="loading">0.15</button>
                <button type="button" class="btn btn-ghost-sm small" @click="handlePathNav6040Quick(0.5)" :disabled="loading">0.5</button>
                <button type="button" class="btn btn-ghost-sm small" @click="handlePathNav6040Quick(1)" :disabled="loading">1</button>
                <button type="button" class="btn btn-ghost-sm small" @click="handlePathNav6040Quick(1.2)" :disabled="loading">1.2</button>
              </div>
              <div class="path-nav-6040-quick">
                <span class="quick-label" title="部分地牛文档">地牛</span>
                <button type="button" class="btn btn-ghost-sm small" @click="handlePathNav6040Quick(1)" :disabled="loading">1 上升</button>
                <button type="button" class="btn btn-ghost-sm small" @click="handlePathNav6040DownZero" :disabled="loading">0 下降</button>
              </div>
            </div>
            <p v-if="navForm.pathNavMode === 'wait_fork'" class="card-hint">将反复查询机器人 I/O（与「监控」中刷新同源），直到所填<strong>每个</strong> DI 的 <code>status</code> 均为 <code>true</code> 再下发 3051。</p>
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
const planPathForm = ref({
  sourceId: '',
  targetId: '',
  start_height: '',
  fork_mid_height: '',
  end_height: '',
  fork_dist: '',
})

const oneKeyForm = ref({
  pickId: '',
  dropId: '',
  mode: 'B', // A:一次下发  B:分段下发并等待DI（推荐）
  diId: '',
  timeoutSec: 120,
  pollMs: 500,
  pick_start_height: '',
  pick_fork_mid_height: '',
  pick_end_height: '',
  pick_fork_dist: '',
  drop_start_height: '',
  drop_fork_mid_height: '',
  drop_operation: 'ForkUnload',
  drop_end_height: 0,
  drop_fork_dist: '',
  preDelivery6073: true,
  preDelivery6073Height: '',
  showPreview: false,
  /** 模式 B 多路 DI：'all' 全部 true（与） | 'any' 任一路 true（或） */
  diCombineMode: 'all',
})
const oneKeyPreviewJson = ref('')

const navForm = ref({
  target: '', type: 'point',
  sourceId: 'SELF_POSITION', targetId: 'LM1', taskId: '',
  pathNavMode: 'direct',
  pickDropPickId: '',
  pickDropDropId: '',
  pickDropTimeoutSec: 300,
  pickDropLoadStartHeight: '',
  pickDropLoadMidHeight: '',
  pickDropLoadEndHeight: '',
  pickDropLoadForkDist: '',
  pickDropPre6073: true,
  pickDropPre6073Height: '',
  forkDiId: '',
  forkWaitTimeoutSec: 120,
  forkPollMs: 500,
  pathNavOperation: '',
  pathNavUnloadAtEnd: false,
  pathNavForkStartHeight: '',
  pathNavForkMidHeight: '',
  pathNavForkEndHeight: 0,
  pathNavForkDist: '',
  /** 路径导航(3051)卡片内独立试 6040 */
  pathNav6040Height: '',
  /** 3051/6040 货叉动作后：in_place | delay | none */
  pathNavForkAfterMode: 'in_place',
  pathNavForkAfterDelaySec: 2,
  /** auto | 1100 | 1028 — 查询 fork_height_in_place 时状态 API 顺序 */
  pathNavForkStatusPrefer: 'auto',
  planAutoUnloadLast: false,
  specPathWaitFork: false,
  specPathPre6073: true,
  specPathPre6073Height: '',
  specifiedSegments: [
    { source_id: 'LM1', id: 'LM2', task_id: '12344321', operation: '', start_height: '', fork_mid_height: '', end_height: '', fork_dist: '' },
    { source_id: 'LM2', id: 'AP1', task_id: '12344322', operation: 'ForkHeight', start_height: '', fork_mid_height: '', end_height: 0.2, fork_dist: '' },
  ],
  moveAngle: 1.57, speedW: null, locMode: 0,
  spinAngle: 1.57, genericNavJson: '{}', clearTaskId: '', tasklistName: '',
})

/** 最近一次「智能路径规划」返回的站点序列（仅用于预览展示） */
const planPathLastRoute = ref(null)
/** 与当前多段表单一致的 3066 POST 体 JSON 字符串 */
const specPath3066PreviewJson = ref('')
const specPath3066PreviewError = ref('')
const specPath3066PreviewContinuityWarnings = ref([])

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

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function findDiEntry(diList, diId) {
  const raw = String(diId ?? '').trim()
  if (!raw) return null
  return (diList || []).find((d) => String(d.id) === raw || Number(d.id) === Number(diId))
}

/** 从输入解析多个 DI 编号，支持英文/中文逗号、分号、空格 */
function parseForkDiIdList(input) {
  const s = String(input ?? '').trim()
  if (!s) return []
  return s.split(/[,，;\s]+/).map((x) => x.trim()).filter(Boolean)
}

/** 所列 DI 中任一路在列表中存在且本轮 status 为 true（多路为「或」） */
function forkDiSignalsAnyReady(diList, ids) {
  for (const id of ids) {
    const item = findDiEntry(diList, id)
    if (item && item.status === true) return true
  }
  return false
}

/** 所列 DI 均存在且本轮 status 均为 true（多路为「与」） */
function forkDiSignalsAllReady(diList, ids) {
  for (const id of ids) {
    const item = findDiEntry(diList, id)
    if (!item || item.status !== true) return false
  }
  return true
}

/** @param {'any'|'all'} mode */
function forkDiSignalsReady(diList, ids, mode) {
  return mode === 'any' ? forkDiSignalsAnyReady(diList, ids) : forkDiSignalsAllReady(diList, ids)
}

function resolveDiCombineMode(options) {
  return options.diMode === 'any' ? 'any' : 'all'
}

/** 轮询 I/O，直到 DI 满足条件（默认：多路全部为 true） */
async function waitForForkDiReady(diInput, options = {}) {
  const ids = parseForkDiIdList(diInput)
  if (!ids.length) {
    throw new Error('请填写至少一个 DI 编号（多个用英文逗号分隔，如 1,9）')
  }
  const mode = resolveDiCombineMode(options)
  const idLabel = ids.join('、')
  const timeoutMs = Math.max(5000, (Number(options.timeoutSec) || 120) * 1000)
  const intervalMs = Math.max(200, Number(options.pollMs) || 500)
  const start = Date.now()
  while (Date.now() - start < timeoutMs) {
    const io = await api.robokitGetIO()
    if (!io) {
      throw new Error('查询 I/O 无响应，请检查后端与机器人连接')
    }
    if (io.ret_code != null && io.ret_code !== 0) {
      throw new Error('查询 I/O 失败: ' + (io.err_msg || 'ret_code=' + io.ret_code))
    }
    if (forkDiSignalsReady(io?.DI, ids, mode)) return
    await sleep(intervalMs)
  }
  const cond = mode === 'any' ? '任一为 true' : '全部为 true'
  throw new Error(`等待 DI「${idLabel}」${cond} 超时（${timeoutMs / 1000}s），请确认已叉货且 I/O 配置正确`)
}

/** 等待“到取货点且 DI 满足条件”（默认：多路全部为 true），用于避免 DI 提前误触发（52166） */
async function waitForForkDiReadyAtPickup(pickId, diInput, options = {}) {
  const ids = parseForkDiIdList(diInput)
  const pickNorm = String(pickId || '').trim()
  if (!pickNorm) throw new Error('缺少取货点站点 id')
  if (!ids.length) throw new Error('请填写至少一个 DI 编号（多个用英文逗号分隔，如 1,9）')
  const mode = resolveDiCombineMode(options)
  const timeoutMs = Math.max(5000, (Number(options.timeoutSec) || 120) * 1000)
  const intervalMs = Math.max(200, Number(options.pollMs) || 500)
  const start = Date.now()
  while (Date.now() - start < timeoutMs) {
    const [io, locRaw] = await Promise.all([api.robokitGetIO(), api.robokitGetLocation()])
    if (io?.ret_code != null && io.ret_code !== 0) {
      throw new Error('查询 I/O 失败: ' + (io.err_msg || 'ret_code=' + io.ret_code))
    }
    const loc = normalizeLocationFromApi(locRaw)
    const station = String(loc?.current_station ?? '').trim()
    const diReady = forkDiSignalsReady(io?.DI, ids, mode)
    if (station === pickNorm && diReady) return
    await sleep(intervalMs)
  }
  const cond = mode === 'any' ? '任一路就绪' : '全部就绪'
  throw new Error(`等待“到取货点且DI${cond}”超时（${timeoutMs / 1000}s），请检查 cargoContactDI / ForkDiDist / 定位站点`)
}

/** 与 loadLocation 一致，解析定位接口中的 data 嵌套 */
function normalizeLocationFromApi(raw) {
  if (!raw || typeof raw !== 'object') return {}
  return raw.data && typeof raw.data === 'object' ? raw.data : raw
}

/** 实时查询当前位置站点，判断是否已在指定站点 */
async function isRobotAtStation(stationId) {
  const target = String(stationId || '').trim()
  if (!target) return false
  try {
    const locRaw = await api.robokitGetLocation()
    const loc = normalizeLocationFromApi(locRaw)
    const current = String(loc?.current_station || '').trim()
    return current !== '' && current === target
  } catch (_) {
    return false
  }
}

/** 取货段 ForkLoad 货叉数值并入 extra */
function mergeForkNumericFromPickDropLoad(extra, form) {
  const fields = [
    ['start_height', form.pickDropLoadStartHeight],
    ['fork_mid_height', form.pickDropLoadMidHeight],
    ['end_height', form.pickDropLoadEndHeight],
    ['fork_dist', form.pickDropLoadForkDist],
  ]
  for (const [key, raw] of fields) {
    if (raw != null && raw !== '' && Number.isFinite(Number(raw))) {
      extra[key] = Number(raw)
    }
  }
}

/**
 * 首段 3051（去取货点）已下发后：轮询 DI 与 current_station。
 * 默认多路 DI 为「与」；到取货点后继续轮询直至满足或超时。
 * @returns {'di_ready'}
 */
async function monitorPickLegForDiOrArrival(pickId, diInput, options = {}) {
  const ids = parseForkDiIdList(diInput)
  const pickNorm = String(pickId || '').trim()
  const mode = resolveDiCombineMode(options)
  const timeoutMs = Math.max(10000, (Number(options.timeoutSec) || 300) * 1000)
  const intervalMs = Math.max(200, Number(options.pollMs) || 500)
  const start = Date.now()
  while (Date.now() - start < timeoutMs) {
    const [io, locRaw] = await Promise.all([api.robokitGetIO(), api.robokitGetLocation()])
    if (io?.ret_code != null && io.ret_code !== 0) {
      throw new Error('查询 I/O 失败: ' + (io.err_msg || 'ret_code=' + io.ret_code))
    }
    const loc = normalizeLocationFromApi(locRaw)
    const station = String(loc?.current_station ?? '').trim()
    const diReady = forkDiSignalsReady(io?.DI, ids, mode)
    if (station === pickNorm && diReady) {
      return 'di_ready'
    }
    await sleep(intervalMs)
  }
  try {
    await api.robokitStopNavigation()
  } catch (_) { /* ignore */ }
  throw new Error(`取货段监测超时（${timeoutMs / 1000}s），已尝试停止导航`)
}

/** 3051 取放货：SELF_POSITION→取货(ForkLoad)+监测 → SELF_POSITION→放货 */
async function runPickDrop3051Flow() {
  const pickId = String(navForm.value.pickDropPickId || '').trim()
  const dropId = String(navForm.value.pickDropDropId || '').trim()
  const di = String(navForm.value.forkDiId ?? '').trim()
  if (!pickId || !dropId) {
    log('取放货模式请填写取货点与放货点站点 id', true)
    return
  }
  const hasDi = parseForkDiIdList(di).length > 0
  try {
    await api.robokitSetMode(1)
  } catch (_) { /* 40009 等忽略 */ }

  const extraLoad = { operation: 'ForkLoad' }
  mergeForkNumericFromPickDropLoad(extraLoad, navForm.value)
  const baseId = String(Date.now() % 100000000)
  const taskId1 = `${baseId}P`
  const taskId2 = `${baseId}D`

  log(`取放货(3051)：下发首段 SELF_POSITION → ${pickId}（ForkLoad）…`, false, false)
  const r1 = await api.robokitPathNavigation('SELF_POSITION', pickId, taskId1, extraLoad)
  if (r1?.ret_code !== 0) {
    log(`首段 3051 下发失败: ${r1?.err_msg || 'ret_code=' + (r1?.ret_code ?? '?')}`, true)
    return
  }

  if (hasDi) {
    await monitorPickLegForDiOrArrival(pickId, di, {
      timeoutSec: navForm.value.pickDropTimeoutSec,
      pollMs: navForm.value.forkPollMs,
    })
  } else {
    log('未填写 DI，按“DI可选”策略：首段下发后直接进入第二段', false, false)
  }

  log(`装货 DI 已就绪，停止当前导航并下发第二段 SELF_POSITION → ${dropId}…`, false, true)
  try {
    await api.robokitStopNavigation()
  } catch (_) { /* ignore */ }
  await sleep(400)

  if (navForm.value.pickDropPre6073) {
    const h6073 = resolvePickDrop6073Height(navForm.value)
    const ok6073 = await runPreDeliverySetForkHeight(h6073, '取放货(3051)')
    if (!ok6073) return
  }

  const extraDrop = {}
  if (navForm.value.pathNavUnloadAtEnd) {
    extraDrop.operation = 'ForkUnload'
    mergeForkNumericFromPathNavForm(extraDrop, navForm.value)
    if (extraDrop.end_height === undefined) {
      extraDrop.end_height = 0
    }
  }
  const r2 = await api.robokitPathNavigation(
    'SELF_POSITION',
    dropId,
    taskId2,
    Object.keys(extraDrop).length ? extraDrop : null,
  )
  if (r2?.ret_code === 0) {
    log(`取放货(3051) 第二段已下发: SELF_POSITION → ${dropId}`, false, true)
  } else {
    log(`第二段 3051 下发失败: ${r2?.err_msg || 'ret_code=' + (r2?.ret_code ?? '?')}`, true)
  }
}

const FORK_NUMERIC_KEYS = ['start_height', 'fork_mid_height', 'end_height', 'fork_dist']

/** 从段对象提取货叉数值字段，写入 item（仅发送有限数字） */
function mergeForkNumericFromSeg(item, seg) {
  for (const key of FORK_NUMERIC_KEYS) {
    const v = seg[key]
    if (v != null && v !== '' && Number.isFinite(Number(v))) {
      item[key] = Number(v)
    }
  }
}

/** 将智能规划表单中的货叉默认值写入每一段（仅覆盖表单里填了有效数字的项） */
function applyPlanPathForkDefaultsToSegments(segments, planForm) {
  for (const seg of segments) {
    for (const key of FORK_NUMERIC_KEYS) {
      const raw = planForm[key]
      if (raw != null && raw !== '' && Number.isFinite(Number(raw))) {
        seg[key] = Number(raw)
      }
    }
  }
}

function mergeForkNumericFromForm(extra, form) {
  for (const key of FORK_NUMERIC_KEYS) {
    const raw = form[key]
    if (raw != null && raw !== '' && Number.isFinite(Number(raw))) {
      extra[key] = Number(raw)
    }
  }
}

function mergeOneKeyForkNumeric(extra, form, part = 'pick') {
  const prefix = part === 'drop' ? 'drop' : 'pick'
  const map = [
    ['start_height', `${prefix}_start_height`],
    ['fork_mid_height', `${prefix}_fork_mid_height`],
    ['end_height', `${prefix}_end_height`],
    ['fork_dist', `${prefix}_fork_dist`],
  ]
  for (const [targetKey, formKey] of map) {
    const raw = form[formKey]
    if (raw != null && raw !== '' && Number.isFinite(Number(raw))) {
      extra[targetKey] = Number(raw)
    }
  }
}

/** 一键搬运：设置货叉高度 — 目标高度：专用输入 > 送货段 start > 送货段 fork_mid */
function resolveOneKey6073Height(form) {
  const raw = form.preDelivery6073Height
  if (raw != null && raw !== '' && Number.isFinite(Number(raw))) return Number(raw)
  if (form.drop_start_height != null && form.drop_start_height !== '' && Number.isFinite(Number(form.drop_start_height))) {
    return Number(form.drop_start_height)
  }
  if (form.drop_fork_mid_height != null && form.drop_fork_mid_height !== '' && Number.isFinite(Number(form.drop_fork_mid_height))) {
    return Number(form.drop_fork_mid_height)
  }
  return null
}

/** 取放货模式：设置货叉高度 */
function resolvePickDrop6073Height(form) {
  const raw = form.pickDropPre6073Height
  if (raw != null && raw !== '' && Number.isFinite(Number(raw))) return Number(raw)
  if (form.pathNavForkStartHeight != null && form.pathNavForkStartHeight !== '' && Number.isFinite(Number(form.pathNavForkStartHeight))) {
    return Number(form.pathNavForkStartHeight)
  }
  if (form.pathNavForkMidHeight != null && form.pathNavForkMidHeight !== '' && Number.isFinite(Number(form.pathNavForkMidHeight))) {
    return Number(form.pathNavForkMidHeight)
  }
  return null
}

/** 指定路径分段：设置货叉高度 */
function resolveSpecPath6073Height(form, segList) {
  const raw = form.specPathPre6073Height
  if (raw != null && raw !== '' && Number.isFinite(Number(raw))) return Number(raw)
  if (!segList?.length) return null
  const last = segList[segList.length - 1]
  if (last.start_height != null && last.start_height !== '' && Number.isFinite(Number(last.start_height))) return Number(last.start_height)
  if (last.fork_mid_height != null && last.fork_mid_height !== '' && Number.isFinite(Number(last.fork_mid_height))) return Number(last.fork_mid_height)
  return null
}

/** 设置货叉高度：6040 后轮询 fork_height_in_place，再允许后续 3051（避免未抬升就发车） */
async function runPreDeliverySetForkHeight(heightM, logPrefix = '设置货叉高度') {
  if (heightM == null || !Number.isFinite(heightM)) {
    log(`${logPrefix}：未解析到目标高度(m)，跳过`, false, false)
    return true
  }
  const msg = api.ROBOKIT_MSG_SET_FORK_HEIGHT
  try {
    log(`${logPrefix}：API ${msg}，params { height: ${heightM} } …`, false, true)
    await api.robokitSetForkHeight({ height: heightM })
    await sleep(200)
    log(`${logPrefix}：等待 fork_height_in_place（1100/1028）…`, false, false)
    const waitRes = await api.robokitWaitForkHeightInPlace({
      timeoutSec: 60,
      pollMs: 300,
    })
    if (waitRes.ok) {
      log(`${logPrefix}：货叉高度已到位`, false, true)
    } else if (waitRes.reason === 'no_field') {
      log(`${logPrefix}：状态接口未返回 fork_height_in_place，延时 2s 后继续（请核对文档端口/编号）`, false, false)
      await sleep(2000)
    } else {
      log(`${logPrefix}：等待 fork_height_in_place 超时，货叉可能未到位`, true)
      return false
    }
    await sleep(200)
    return true
  } catch (e) {
    log(`${logPrefix} API ${msg} 失败: ` + (e.message || e), true)
    return false
  }
}

/** 将 move_task_list 的各段按 3051 逐段下发（兼容不支持 3066 的现场） */
async function sendMoveTaskListBy3051(list, sceneLabel = '3051分段') {
  for (let i = 0; i < list.length; i++) {
    const seg = list[i]
    const sourceId = String(seg.source_id || '').trim()
    const targetId = String(seg.id || '').trim()
    const taskId = String(seg.task_id || '').trim() || null
    const extra = {}
    for (const [k, v] of Object.entries(seg)) {
      if (k === 'source_id' || k === 'id' || k === 'task_id') continue
      if (v === undefined || v === null || v === '') continue
      extra[k] = v
    }
    const r = await api.robokitPathNavigation(
      sourceId,
      targetId,
      taskId,
      Object.keys(extra).length ? extra : null,
    )
    if (r?.ret_code !== 0) {
      log(`${sceneLabel} 第 ${i + 1} 段下发失败: ${sourceId}→${targetId}`, true)
      if (r) log('完整响应: ' + JSON.stringify(r), true, false)
      return false
    }
    log(`${sceneLabel} 第 ${i + 1}/${list.length} 段已下发: ${sourceId}→${targetId}`, false, true)
    await sleep(180)
  }
  return true
}

/** 两次 3051：均以 SELF_POSITION 为起点，分别到取货点/送货点 */
async function sendTwoLegBy3051Self(pickId, dropId, firstTaskId = null, secondTaskId = null, pickExtra = {}, dropExtra = {}) {
  const r1 = await api.robokitPathNavigation(
    'SELF_POSITION',
    String(pickId || '').trim(),
    firstTaskId,
    Object.keys(pickExtra || {}).length ? pickExtra : null,
  )
  if (r1?.ret_code !== 0) {
    log(`首段 3051 下发失败: SELF_POSITION→${pickId}`, true)
    if (r1) log('完整响应: ' + JSON.stringify(r1), true, false)
    return false
  }
  log(`首段 3051 已下发: SELF_POSITION→${pickId}`, false, true)
  return true
}

/** 从导航表单提取 3051 货叉可选高度（用于 ForkUnload 勾选时） */
function mergeForkNumericFromPathNavForm(extra, form) {
  const fields = [
    ['start_height', form.pathNavForkStartHeight],
    ['fork_mid_height', form.pathNavForkMidHeight],
    ['end_height', form.pathNavForkEndHeight],
    ['fork_dist', form.pathNavForkDist],
  ]
  for (const [key, raw] of fields) {
    if (raw != null && raw !== '' && Number.isFinite(Number(raw))) {
      extra[key] = Number(raw)
    }
  }
}

function getSegmentContinuityWarnings(list) {
  const messages = []
  for (let i = 0; i < list.length - 1; i++) {
    const currEnd = list[i].id
    const nextStart = list[i + 1].source_id
    if (currEnd !== nextStart) {
      messages.push(
        `第 ${i + 1} 段终点「${currEnd}」与第 ${i + 2} 段起点「${nextStart}」不一致，线路不连续`,
      )
    }
  }
  return messages
}

/** 与下发 3066 相同规则，从多段表单构建 move_task_list */
function buildMoveTaskListFromSegments(segments) {
  const list = []
  let autoOperationCount = 0
  for (let i = 0; i < segments.length; i++) {
    const seg = segments[i]
    const source_id = (seg.source_id || '').trim()
    const id = (seg.id || '').trim()
    const task_id = (seg.task_id || '').trim()
    if (!source_id || !id || !task_id) {
      return {
        ok: false,
        list,
        error: `第 ${i + 1} 段须填写 source_id、id、task_id`,
      }
    }
    const item = { source_id, id, task_id }
    if (seg.operation && seg.operation !== '') item.operation = seg.operation
    mergeForkNumericFromSeg(item, seg)
    // 兼容部分固件：仅填高度但 operation 为空时会按 Wait 忽略中途/到点动作
    if (!item.operation) {
      const hasForkNumeric = FORK_NUMERIC_KEYS.some((k) => item[k] !== undefined)
      if (hasForkNumeric) {
        item.operation = 'ForkHeight'
        autoOperationCount += 1
      }
    }
    list.push(item)
  }
  return { ok: true, list, error: '', autoOperationCount }
}

function updateSpecPath3066Preview() {
  const built = buildMoveTaskListFromSegments(navForm.value.specifiedSegments)
  specPath3066PreviewJson.value = JSON.stringify({ move_task_list: built.list }, null, 2)
  if (!built.ok) {
    specPath3066PreviewError.value = built.error
    specPath3066PreviewContinuityWarnings.value = []
    return
  }
  specPath3066PreviewError.value = ''
  specPath3066PreviewContinuityWarnings.value = getSegmentContinuityWarnings(built.list)
}

async function copySpecPath3066Preview() {
  const text = specPath3066PreviewJson.value
  if (!text) return
  try {
    await navigator.clipboard.writeText(text)
    log('已复制 3066 请求 JSON', false, true)
  } catch (e) {
    log('复制失败（部分环境需 HTTPS，可手动全选文本框复制）', true)
  }
}

/**
 * 一键搬运 JSON 预览（与 handleOneKeyCarry 的路径构建规则一致，需路径规划接口）
 * 未填写取货/放货点时仅生成占位说明，不请求后端。
 */
async function refreshOneKeyPreview() {
  const pickId = String(oneKeyForm.value.pickId || '').trim()
  const dropId = String(oneKeyForm.value.dropId || '').trim()
  if (!pickId && !dropId) {
    oneKeyPreviewJson.value = JSON.stringify(
      { requests: [], hint: '请至少填写取货点或放货点后点「刷新预览」' },
      null,
      2,
    )
    return
  }
  try {
    const baseTaskId = String(Date.now() % 100000000)
    const requests = []
    if (pickId) {
      const req1 = {
        source_id: 'SELF_POSITION',
        id: pickId,
        task_id: baseTaskId + '01',
        operation: 'ForkLoad',
      }
      mergeOneKeyForkNumeric(req1, oneKeyForm.value, 'pick')
      requests.push({ api: 3051, description: '取货段（仅取货 / 全程首段）', body: req1 })
    }
    if (dropId) {
      if (oneKeyForm.value.preDelivery6073) {
        const h6073 = resolveOneKey6073Height(oneKeyForm.value)
        const fh = api.ROBOKIT_MSG_SET_FORK_HEIGHT
        requests.push({
          api: fh,
          description: '送货前设置货叉高度（仅送货 / 全程）',
          call: { port: 19210, msg_type: fh, params: h6073 != null ? { height: h6073 } : {} },
        })
      }
      const req2 = {
        source_id: 'SELF_POSITION',
        id: dropId,
        task_id: baseTaskId + '02',
        operation: String(oneKeyForm.value.drop_operation || 'ForkUnload'),
        end_height: 0,
      }
      mergeOneKeyForkNumeric(req2, oneKeyForm.value, 'drop')
      if (req2.operation === 'ForkUnload' && req2.end_height === undefined) req2.end_height = 0
      requests.push({ api: 3051, description: '放货段（仅送货 / 全程次段）', body: req2 })
    }
    const hintParts = []
    if (!pickId) hintParts.push('未填取货点：全程/仅取货预览不含首段')
    if (!dropId) hintParts.push('未填放货点：全程/仅送货预览不含次段与 6040')
    oneKeyPreviewJson.value = JSON.stringify({
      mode: oneKeyForm.value.mode,
      diCombineMode: oneKeyForm.value.mode === 'B' ? oneKeyForm.value.diCombineMode : undefined,
      hint: hintParts.length ? hintParts.join('；') : undefined,
      requests,
    }, null, 2)
  } catch (e) {
    oneKeyPreviewJson.value = JSON.stringify(
      { error: String(e?.message || e) },
      null,
      2,
    )
  }
}

/** 仅下发取货段（ForkLoad→取货点）；模式 B 且配置 DI 时在取货点等到条件满足后结束，不下发送货段 */
async function handleOneKeyCarryPickOnly() {
  loading.value = true
  try {
    const pickId = String(oneKeyForm.value.pickId || '').trim()
    if (!pickId) {
      log('仅取货：请填写取货点', true)
      return
    }

    const skipLoadLeg = await isRobotAtStation(pickId)
    if (skipLoadLeg) {
      log(`仅取货：当前已在取货点「${pickId}」，跳过首段导航`, false, true)
    }

    const baseTaskId = String(Date.now() % 100000000)
    const req1 = {
      source_id: 'SELF_POSITION',
      id: pickId,
      task_id: baseTaskId + 'P1',
      operation: 'ForkLoad',
    }
    mergeOneKeyForkNumeric(req1, oneKeyForm.value, 'pick')
    const pickExtra = { operation: req1.operation }
    mergeOneKeyForkNumeric(pickExtra, oneKeyForm.value, 'pick')

    oneKeyPreviewJson.value = JSON.stringify(
      {
        mode: oneKeyForm.value.mode,
        description: '仅取货段',
        diCombineMode: oneKeyForm.value.mode === 'B' ? oneKeyForm.value.diCombineMode : undefined,
        requests: [{ api: 3051, description: '取货段', body: req1 }],
      },
      null,
      2,
    )

    const di = String(oneKeyForm.value.diId ?? '').trim()
    const hasDi = parseForkDiIdList(di).length > 0
    const diMode = oneKeyForm.value.diCombineMode === 'any' ? 'any' : 'all'
    const diCondShort = diMode === 'any' ? '任一为 true' : '全部为 true'

    if (oneKeyForm.value.mode === 'A') {
      if (!skipLoadLeg) {
        const r1 = await api.robokitPathNavigation('SELF_POSITION', pickId, req1.task_id, pickExtra)
        if (r1?.ret_code !== 0) {
          log('仅取货(A) 3051 下发失败', true)
          return
        }
        log(`仅取货(A) 已下发 SELF_POSITION→${pickId}（未下发送货段）`, false, true)
      } else {
        log('仅取货(A)：已在取货点，未下发导航；测第二段请点「仅下发送货段」', false, false)
      }
      return
    }

    if (!skipLoadLeg) {
      const r1 = await api.robokitPathNavigation('SELF_POSITION', pickId, req1.task_id, pickExtra)
      if (r1?.ret_code !== 0) {
        log('仅取货(B) ForkLoad 段下发失败', true)
        return
      }
      if (hasDi) {
        log(
          `仅取货(B) 已下发 ForkLoad，等待到取货点且 DI「${parseForkDiIdList(di).join('、')}」${diCondShort}…`,
          false,
          true,
        )
      } else {
        log('仅取货(B) 已下发 ForkLoad，结束（未下发送货段）', false, true)
      }
    } else if (hasDi) {
      log(`仅取货(B) 已在取货点，等待 DI「${parseForkDiIdList(di).join('、')}」${diCondShort}…`, false, true)
    } else {
      log('仅取货(B)：已在取货点且未配置 DI，无需下发', false, false)
      return
    }

    if (hasDi) {
      await waitForForkDiReadyAtPickup(pickId, di, {
        timeoutSec: oneKeyForm.value.timeoutSec,
        pollMs: oneKeyForm.value.pollMs,
        diMode,
      })
      log('仅取货(B)：DI 条件已满足，本段结束（测送货请点「仅下发送货段」）', false, true)
    }
  } catch (e) {
    log('仅取货错误: ' + (e.message || e), true)
  } finally {
    loading.value = false
  }
}

/** 仅下发放货段（可选先 6040），不执行取货段 */
async function handleOneKeyCarryDropOnly() {
  loading.value = true
  try {
    const dropId = String(oneKeyForm.value.dropId || '').trim()
    if (!dropId) {
      log('仅送货：请填写放货点', true)
      return
    }

    const baseTaskId = String(Date.now() % 100000000)
    const req2 = {
      source_id: 'SELF_POSITION',
      id: dropId,
      task_id: baseTaskId + 'D1',
      operation: String(oneKeyForm.value.drop_operation || 'ForkUnload'),
      end_height: 0,
    }
    mergeOneKeyForkNumeric(req2, oneKeyForm.value, 'drop')
    if (req2.operation === 'ForkUnload' && req2.end_height === undefined) req2.end_height = 0
    const dropExtra = { operation: req2.operation, end_height: 0 }
    mergeOneKeyForkNumeric(dropExtra, oneKeyForm.value, 'drop')
    if (dropExtra.operation === 'ForkUnload' && dropExtra.end_height === undefined) dropExtra.end_height = 0

    const previewRequests = []
    if (oneKeyForm.value.preDelivery6073) {
      const hPrev = resolveOneKey6073Height(oneKeyForm.value)
      const fh = api.ROBOKIT_MSG_SET_FORK_HEIGHT
      previewRequests.push({
        api: fh,
        description: '送货前设置货叉高度',
        call: { port: 19210, msg_type: fh, params: hPrev != null ? { height: hPrev } : {} },
      })
    }
    previewRequests.push({ api: 3051, description: '放货段', body: req2 })
    oneKeyPreviewJson.value = JSON.stringify(
      { mode: oneKeyForm.value.mode, requests: previewRequests },
      null,
      2,
    )

    if (oneKeyForm.value.preDelivery6073) {
      const h6073 = resolveOneKey6073Height(oneKeyForm.value)
      const ok6073 = await runPreDeliverySetForkHeight(h6073, '仅送货')
      if (!ok6073) return
    }
    const r2 = await api.robokitPathNavigation('SELF_POSITION', dropId, req2.task_id, dropExtra)
    if (r2?.ret_code === 0) {
      log(`仅送货：已下发 SELF_POSITION→${dropId}`, false, true)
    } else {
      log('仅送货：3051 下发失败', true)
    }
  } catch (e) {
    log('仅送货错误: ' + (e.message || e), true)
  } finally {
    loading.value = false
  }
}

async function handleOneKeyCarry() {
  loading.value = true
  try {
    const pickId = String(oneKeyForm.value.pickId || '').trim()
    const dropId = String(oneKeyForm.value.dropId || '').trim()
    if (!pickId || !dropId) { log('请填写取货点与放货点', true); return }

    const skipLoadLeg = await isRobotAtStation(pickId)
    if (skipLoadLeg) {
      log(`检测到当前站点已是取货点「${pickId}」，自动跳过首段 SELF_POSITION→${pickId}`, false, true)
    }

    const baseTaskId = String(Date.now() % 100000000)

    const req1 = { source_id: 'SELF_POSITION', id: pickId, task_id: baseTaskId + '01', operation: 'ForkLoad' }
    mergeOneKeyForkNumeric(req1, oneKeyForm.value, 'pick')
    const req2 = {
      source_id: 'SELF_POSITION',
      id: dropId,
      task_id: baseTaskId + '02',
      operation: String(oneKeyForm.value.drop_operation || 'ForkUnload'),
      end_height: 0,
    }
    mergeOneKeyForkNumeric(req2, oneKeyForm.value, 'drop')
    if (req2.operation === 'ForkUnload' && req2.end_height === undefined) req2.end_height = 0
    const pickExtra = { operation: req1.operation }
    mergeOneKeyForkNumeric(pickExtra, oneKeyForm.value, 'pick')
    const dropExtra = { operation: req2.operation, end_height: 0 }
    mergeOneKeyForkNumeric(dropExtra, oneKeyForm.value, 'drop')
    if (dropExtra.operation === 'ForkUnload' && dropExtra.end_height === undefined) dropExtra.end_height = 0
    const previewRequests = [{ api: 3051, description: '取货段', body: req1 }]
    if (oneKeyForm.value.preDelivery6073) {
      const hPrev = resolveOneKey6073Height(oneKeyForm.value)
      const fh = api.ROBOKIT_MSG_SET_FORK_HEIGHT
      previewRequests.push({
        api: fh,
        description: '送货前设置货叉高度',
        call: { port: 19210, msg_type: fh, params: hPrev != null ? { height: hPrev } : {} },
      })
    }
    previewRequests.push({ api: 3051, description: '放货段', body: req2 })
    oneKeyPreviewJson.value = JSON.stringify({
      mode: oneKeyForm.value.mode,
      diCombineMode: oneKeyForm.value.mode === 'B' ? oneKeyForm.value.diCombineMode : undefined,
      requests: previewRequests,
    }, null, 2)

    if (oneKeyForm.value.mode === 'A') {
      if (!skipLoadLeg) {
        const r1 = await api.robokitPathNavigation('SELF_POSITION', pickId, req1.task_id, pickExtra)
        if (r1?.ret_code !== 0) { log('一键搬运(A) 首段 3051 下发失败', true); return }
        log(`一键搬运(A) 首段已下发: SELF_POSITION→${pickId}`, false, true)
      }
      if (oneKeyForm.value.preDelivery6073) {
        const h6073 = resolveOneKey6073Height(oneKeyForm.value)
        const ok6073 = await runPreDeliverySetForkHeight(h6073, '一键搬运(A)')
        if (!ok6073) return
      }
      const r2 = await api.robokitPathNavigation('SELF_POSITION', dropId, req2.task_id, dropExtra)
      if (r2?.ret_code === 0) log(`一键搬运(A) 第二段已下发: SELF_POSITION→${dropId}`, false, true)
      else log('一键搬运(A) 第二段下发失败', true)
      return
    }

    // 模式 B：先下发 ForkLoad 段，等 DI（可选「全部/任意」），再下发剩余段（含 ForkUnload）
    const di = String(oneKeyForm.value.diId ?? '').trim()
    const hasDi = parseForkDiIdList(di).length > 0
    const diMode = oneKeyForm.value.diCombineMode === 'any' ? 'any' : 'all'
    const diCondShort = diMode === 'any' ? '任一为 true' : '全部为 true'

    if (!skipLoadLeg) {
      const r1 = await api.robokitPathNavigation('SELF_POSITION', pickId, req1.task_id, pickExtra)
      if (r1?.ret_code !== 0) { log('一键搬运(B) ForkLoad 段下发失败', true); return }
      if (hasDi) {
        log(`一键搬运(B) 已下发 ForkLoad 段，等待“到取货点且 DI「${parseForkDiIdList(di).join('、')}」${diCondShort}”…`, false, true)
      } else {
        log('一键搬运(B) 未填写 DI，首段下发后直接进入第二段', false, false)
      }
    } else {
      if (hasDi) {
        log(`一键搬运(B) 已在取货点，跳过 ForkLoad 导航段，等待 DI「${parseForkDiIdList(di).join('、')}」${diCondShort}…`, false, true)
      } else {
        log('一键搬运(B) 已在取货点且未填写 DI，直接进入第二段', false, false)
      }
    }
    if (hasDi) {
      await waitForForkDiReadyAtPickup(pickId, di, {
        timeoutSec: oneKeyForm.value.timeoutSec,
        pollMs: oneKeyForm.value.pollMs,
        diMode,
      })
      log(`DI「${parseForkDiIdList(di).join('、')}」已满足（${diCondShort}），连续下发送货段 3051（不取消当前导航）`, false, true)
    } else {
      // 未配置 DI：两段之间仍先取消/停止，减少任务链重叠类异常
      try {
        await api.robokitCancelNavigation()
      } catch (_) { /* ignore */ }
      try {
        await api.robokitStopNavigation()
      } catch (_) { /* ignore */ }
      await sleep(300)
    }

    if (oneKeyForm.value.preDelivery6073) {
      const h6073 = resolveOneKey6073Height(oneKeyForm.value)
      const ok6073 = await runPreDeliverySetForkHeight(h6073, '一键搬运(B)')
      if (!ok6073) return
    }
    const r2 = await api.robokitPathNavigation('SELF_POSITION', dropId, req2.task_id, dropExtra)
    if (r2?.ret_code === 0) log(`一键搬运(B) 第二段已下发: SELF_POSITION→${dropId}`, false, true)
    else log('一键搬运(B) 第二段下发失败', true)
  } catch (e) {
    log('一键搬运错误: ' + (e.message || e), true)
  } finally {
    loading.value = false
  }
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
  log('正在连接机器人…', false, false)
  try {
    const host = String(connectForm.value.host || '').trim()
    const portRaw = connectForm.value.port
    const port =
      portRaw === '' || portRaw == null ? null : Number(portRaw)
    const result = await api.robokitConnect(
      host,
      Number.isFinite(port) ? port : null
    )
    if (result?.success) {
      connectionStatus.value = { connected: true, host }
      log(result.message || '连接成功', false, true)
      if (result.push_listener === false) {
        log(result.message || '推送端口未连通', false, false)
      }
      startPoll()
      // 不在此处 await loadAllStatus：任一子接口挂起会导致整页一直停在「连接中」
      loadAllStatus().catch((err) => {
        log('连接后刷新状态失败: ' + (err.message || err), true)
      })
    } else {
      log(result?.message || '连接失败（success=false）', true)
    }
  } catch (e) {
    log('连接错误: ' + (e?.message || e), true)
  } finally {
    loading.value = false
  }
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

function pathNavForkStatusPreferToApi() {
  const v = navForm.value.pathNavForkStatusPrefer || 'auto'
  if (v === '1100' || v === '1028') return v
  return 'auto'
}

/** 路径导航卡：按「货叉动作后」执行等待 fork_height_in_place / 固定延时 / 不等待 */
async function applyNavFormForkStateWait(contextLabel) {
  const mode = navForm.value.pathNavForkAfterMode || 'in_place'
  if (mode === 'none') {
    log(`${contextLabel}：货叉动作后选择「不等待」`, false, false)
    return true
  }
  if (mode === 'delay') {
    const sec = Math.max(0, Number(navForm.value.pathNavForkAfterDelaySec) || 2)
    log(`${contextLabel}：固定延时 ${sec}s …`, false, false)
    await sleep(Math.round(sec * 1000))
    return true
  }
  const preferApi = pathNavForkStatusPreferToApi()
  log(
    `${contextLabel}：等待 fork_height_in_place（${preferApi === 'auto' ? '先 1100 再 1028' : preferApi}）…`,
    false,
    false,
  )
  const waitRes = await api.robokitWaitForkHeightInPlace({
    timeoutSec: 60,
    pollMs: 300,
    preferStatus: preferApi,
  })
  if (waitRes.ok) {
    log(`${contextLabel}：fork_height_in_place 已就绪`, false, true)
    return true
  }
  if (waitRes.reason === 'no_field') {
    log(`${contextLabel}：状态口未返回 fork_height_in_place，延时 2s 后继续`, false, false)
    await sleep(2000)
    return true
  }
  log(`${contextLabel}：等待 fork_height_in_place 超时`, true)
  return false
}

/** 路径导航卡片：单独发送 6040 设置货叉高度 */
async function handlePathNav6040SetHeight(overrideHeight) {
  let num
  if (overrideHeight !== undefined && overrideHeight !== null && overrideHeight !== '') {
    num = Number(overrideHeight)
  } else {
    num = Number(navForm.value.pathNav6040Height)
  }
  if (!Number.isFinite(num)) {
    log('6040：请填写有效 height (m) 或点击快捷数值', true)
    return
  }
  loading.value = true
  try {
    await api.robokitSetForkHeight({ height: num })
    log(`6040 已发送 height=${num}`, false, true)
    navForm.value.pathNav6040Height = num
    await applyNavFormForkStateWait('6040')
  } catch (e) {
    log('6040 失败: ' + (e.message || e), true)
  } finally {
    loading.value = false
  }
}

async function handlePathNav6040Quick(v) {
  navForm.value.pathNav6040Height = v
  await handlePathNav6040SetHeight(v)
}

/** 与「1 上升」区分：明确为地牛下降 0 */
async function handlePathNav6040DownZero() {
  navForm.value.pathNav6040Height = 0
  await handlePathNav6040SetHeight(0)
}

async function handlePathNavigation() {
  loading.value = true
  try {
    if (navForm.value.pathNavMode === 'pick_drop_3051') {
      await runPickDrop3051Flow()
      return
    }
    const sourceId = (navForm.value.sourceId || '').trim()
    const targetId = (navForm.value.targetId || '').trim()
    if (!sourceId || !targetId) { log('请填写起点 source_id 与终点 id', true); return }
    if (navForm.value.pathNavMode === 'wait_fork') {
      const di = String(navForm.value.forkDiId ?? '').trim()
      if (!parseForkDiIdList(di).length) {
        log('「等待 DI 叉好」请填写 DI 编号，多个用英文逗号分隔（如 1,9，须全部为 true）', true)
        return
      }
      log(`等待 DI「${parseForkDiIdList(di).join('、')}」全部为 true（叉好）…`, false, false)
      await waitForForkDiReady(di, {
        timeoutSec: navForm.value.forkWaitTimeoutSec,
        pollMs: navForm.value.forkPollMs,
      })
      log(`DI「${parseForkDiIdList(di).join('、')}」已满足，下发 3051`, false, true)
    }
    const taskId = (navForm.value.taskId || '').trim() || null
    const extra = {}
    const pathOp = String(navForm.value.pathNavOperation || '').trim()
    if (pathOp) {
      extra.operation = pathOp
      mergeForkNumericFromPathNavForm(extra, navForm.value)
      if (pathOp === 'ForkUnload' && extra.end_height === undefined) {
        extra.end_height = 0
      }
    }
    const result = await api.robokitPathNavigation(
      sourceId,
      targetId,
      taskId,
      Object.keys(extra).length ? extra : null,
    )
    if (result?.ret_code === 0) {
      log(`路径导航(3051) ${sourceId} → ${targetId}`, false, true)
      const forkMotionOps = new Set(['ForkLoad', 'ForkUnload', 'ForkHeight', 'ForkForward'])
      if (pathOp && forkMotionOps.has(pathOp)) {
        const okWait = await applyNavFormForkStateWait(`3051·${pathOp}`)
        if (!okWait) {
          log('3051：货叉状态等待未成功，请自行确认后再操作', true)
        }
      }
    } else {
      log('路径导航失败', true)
    }
  } catch (e) { log('路径导航错误: ' + e.message, true) }
  finally { loading.value = false }
}

async function handlePlanPath() {
  const sourceId = (planPathForm.value.sourceId || '').trim()
  const targetId = (planPathForm.value.targetId || '').trim()
  if (!sourceId || !targetId) {
    log('请填写起点和终点', true)
    return
  }
  loading.value = true
  try {
    const result = await api.planPath(sourceId, targetId)
    const list = result.move_task_list || []
    if (!list.length) {
      log('未找到可行路径', true)
      return
    }
    navForm.value.specifiedSegments = list.map((seg) => ({
      source_id: seg.source_id,
      id: seg.id,
      task_id: seg.task_id,
      operation: seg.operation || '',
      start_height: seg.start_height != null ? seg.start_height : '',
      fork_mid_height: seg.fork_mid_height != null ? seg.fork_mid_height : '',
      end_height: seg.end_height != null ? seg.end_height : '',
      fork_dist: seg.fork_dist != null ? seg.fork_dist : '',
    }))
    applyPlanPathForkDefaultsToSegments(navForm.value.specifiedSegments, planPathForm.value)
    if (navForm.value.planAutoUnloadLast && navForm.value.specifiedSegments.length) {
      const last = navForm.value.specifiedSegments[navForm.value.specifiedSegments.length - 1]
      last.operation = 'ForkUnload'
      last.end_height = 0
    }
    planPathLastRoute.value = result.path || null
    updateSpecPath3066Preview()
    log(`路径规划成功: ${result.path?.join(' → ') || sourceId + ' → ' + targetId}，共 ${list.length} 段`, false, true)
  } catch (e) {
    log('路径规划失败: ' + (e.message || e), true)
  } finally {
    loading.value = false
  }
}

function addSpecifiedSegment() {
  const segments = navForm.value.specifiedSegments
  navForm.value.specifiedSegments = [
    ...segments,
    { source_id: '', id: '', task_id: '', operation: '', start_height: '', fork_mid_height: '', end_height: '', fork_dist: '' },
  ]
  updateSpecPath3066Preview()
}

function removeSpecifiedSegment(idx) {
  if (navForm.value.specifiedSegments.length <= 1) return
  const segments = [...navForm.value.specifiedSegments]
  segments.splice(idx, 1)
  navForm.value.specifiedSegments = segments
  updateSpecPath3066Preview()
}

async function handleSpecifiedPathNavigation() {
  loading.value = true
  try {
    const built = buildMoveTaskListFromSegments(navForm.value.specifiedSegments)
    if (!built.ok) {
      log('指定路径(3066) ' + built.error, true)
      return
    }
    const list = built.list
    if (built.autoOperationCount > 0) {
      log(`检测到 ${built.autoOperationCount} 段仅填了货叉数值参数，已自动补 operation=ForkHeight`, false, false)
    }
    updateSpecPath3066Preview()
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
    // 勾选等待 DI 时：若首段为 ForkLoad，按“取货段 + 等DI + 送货段”两次下发
    const splitByForkLoad = navForm.value.specPathWaitFork
      && list.length > 1
      && String(list[0]?.operation || '').trim() === 'ForkLoad'
    if (splitByForkLoad) {
      const di = String(navForm.value.forkDiId ?? '').trim()
      if (!parseForkDiIdList(di).length) {
        log('已勾选「下发前先等待 DI」请填写 DI 编号，多个用英文逗号分隔（如 1,9）', true)
        return
      }
      const pickId = String(list[0]?.id || '').trim()
      const dropSeg = list[list.length - 1]
      const dropId = String(dropSeg?.id || '').trim()
      const pickTaskId = String(list[0]?.task_id || '').trim() || null
      const dropTaskId = String(dropSeg?.task_id || '').trim() || null
      const pickExtra = {}
      for (const [k, v] of Object.entries(list[0] || {})) {
        if (k === 'source_id' || k === 'id' || k === 'task_id') continue
        if (v === undefined || v === null || v === '') continue
        pickExtra[k] = v
      }
      const dropExtra = {}
      for (const [k, v] of Object.entries(dropSeg || {})) {
        if (k === 'source_id' || k === 'id' || k === 'task_id') continue
        if (v === undefined || v === null || v === '') continue
        dropExtra[k] = v
      }
      log(`指定路径改用 3051 两次下发：SELF_POSITION→${pickId}，DI就绪后 SELF_POSITION→${dropId}`, false, true)
      const ok1 = await sendTwoLegBy3051Self(pickId, dropId, pickTaskId, dropTaskId, pickExtra, dropExtra)
      if (!ok1) return
      log(`首段已下发，等待“到取货点且 DI「${parseForkDiIdList(di).join('、')}」全部为 true”…`, false, true)
      await waitForForkDiReadyAtPickup(pickId, di, {
        timeoutSec: navForm.value.forkWaitTimeoutSec,
        pollMs: navForm.value.forkPollMs,
      })
      log(`DI 已就绪，先结束当前导航，再下发送货段`, false, true)
      try { await api.robokitCancelNavigation() } catch (_) { /* ignore */ }
      try { await api.robokitStopNavigation() } catch (_) { /* ignore */ }
      await sleep(300)
      if (navForm.value.specPathPre6073) {
        const h6073 = resolveSpecPath6073Height(navForm.value, list)
        const ok6073 = await runPreDeliverySetForkHeight(h6073, '指定路径-送货前')
        if (!ok6073) return
      }
      const r2 = await api.robokitPathNavigation(
        'SELF_POSITION',
        dropId,
        dropTaskId,
        Object.keys(dropExtra).length ? dropExtra : null,
      )
      if (r2?.ret_code === 0) {
        log(`第二段 3051 已下发: SELF_POSITION→${dropId}`, false, true)
      } else {
        log(`第二段 3051 下发失败: SELF_POSITION→${dropId}`, true)
        if (r2) log('完整响应: ' + JSON.stringify(r2), true, false)
      }
      return
    }

    if (navForm.value.specPathWaitFork) {
      const di = String(navForm.value.forkDiId ?? '').trim()
      if (!parseForkDiIdList(di).length) {
        log('已勾选「下发前先等待 DI」请填写 DI 编号，多个用英文逗号分隔（如 1,9）', true)
        return
      }
      log(`等待 DI「${parseForkDiIdList(di).join('、')}」全部为 true 后再下发 3066…`, false, false)
      await waitForForkDiReady(di, {
        timeoutSec: navForm.value.forkWaitTimeoutSec,
        pollMs: navForm.value.forkPollMs,
      })
      log(`DI「${parseForkDiIdList(di).join('、')}」已满足`, false, true)
    }
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

onMounted(() => {
  log('Robokit面板已初始化')
  startPoll()
  updateSpecPath3066Preview()
  void refreshOneKeyPreview()
})
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
