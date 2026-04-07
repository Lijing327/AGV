<template>
<div v-if="activeGroup === 'navigation'" class="group-content nav-panel-root">
          <div class="nav-subtabs" role="tablist">
            <button
              v-for="t in navSubTabs"
              :key="t.id"
              type="button"
              role="tab"
              class="nav-subtab"
              :class="{ active: navSubTab === t.id }"
              :aria-selected="navSubTab === t.id"
              @click="navSubTab = t.id"
            >
              {{ t.label }}
            </button>
          </div>
          
          <div class="card priority-card" v-show="navSubTab === 'carry'">
            <div class="card-head"><h4>一键搬运</h4></div>
            <div class="form-field compact one-key-scheme-row">
              <label>模式</label>
              <select v-model="oneKeyForm.oneKeyScheme" class="fork-mode-select">
                <option value="fork_in_3051">货叉随 3051（ForkLoad / 送货 operation）</option>
                <option value="nav_6040">3051 纯导航 + 6040 设货叉高（无 operation）</option>
              </select>
            </div>
            <p v-if="oneKeyForm.oneKeyScheme === 'nav_6040'" class="card-hint one-key-scheme-hint">
              两段 3051 仅下发站点路径；货叉高度只用 6040。取货前/送货前可留空则跳过；「送货完成后」填高度（常用 0）则在第二段 3051 完成后再发 6040 降叉。
            </p>
            <div class="input-row-2">
              <div class="form-field compact">
                <label>取货点（站点）</label>
                <input v-model="oneKeyForm.pickId" placeholder="如 PP1" />
              </div>
              <div class="form-field compact">
                <label>放货点（站点）</label>
                <input v-model="oneKeyForm.dropId" placeholder="如 LM55" />
              </div>
            </div>
            <div class="input-row-2">
              <div class="form-field compact">
                <label>首段完成等待 · 超时 (秒)</label>
                <input v-model.number="oneKeyForm.timeoutSec" type="number" min="5" step="1" />
              </div>
              <div class="form-field compact">
                <label>轮询 (ms)</label>
                <input v-model.number="oneKeyForm.pollMs" type="number" min="200" step="100" />
              </div>
            </div>
            <div class="fork-nav-options one-key-pick-recognize">
              <label class="fork-check">
                <input type="checkbox" v-model="oneKeyForm.pickRecognize" />
                取货段携带 recognize（路径导航 3051，与 ForkLoad/纯导航等配合见《API接口》路径导航说明）
              </label>
            </div>
            <template v-if="oneKeyForm.oneKeyScheme === 'fork_in_3051'">
              <h5 class="nav-subcard-title">取货段 ForkLoad</h5>
              <div class="input-row-3 fork-height-row plan-fork-defaults">
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
              </div>
              <h5 class="nav-subcard-title">送货段</h5>
              <div class="input-row-3">
                <div class="form-field compact">
                  <label>送货段 operation</label>
                  <select v-model="oneKeyForm.drop_operation" class="fork-mode-select">
                    <option value="ForkUnload">ForkUnload</option>
                    <option value="ForkHeight">ForkHeight</option>
                    <option value="ForkForward">ForkForward</option>
                    <option value="Wait">Wait</option>
                  </select>
                </div>
              </div>
              <div class="input-row-3 fork-height-row plan-fork-defaults">
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
              </div>
            </template>
            <template v-else>
              <h5 class="nav-subcard-title">货叉高度（6040，分段可选）</h5>
              <div class="input-row-2 fork-height-row">
                <div class="form-field compact">
                  <label>取货前 height (m)</label>
                  <input v-model="oneKeyForm.pick6040Height" type="number" step="0.01" placeholder="可选" />
                </div>
                <div class="form-field compact">
                  <label>送货前 height (m)</label>
                  <input v-model="oneKeyForm.drop6040Height" type="number" step="0.01" placeholder="可选" />
                </div>
              </div>
            </template>
            <div class="input-row-2 fork-height-row one-key-after-drop">
              <div class="form-field compact">
                <label>送货完成后 height (m)</label>
                <input
                  v-model="oneKeyForm.afterDrop6040Height"
                  type="number"
                  step="0.01"
                  placeholder="常用 0 降叉，留空不执行"
                />
              </div>
            </div>
            <div class="fork-nav-options">
              <label class="fork-check">
                <input type="checkbox" v-model="oneKeyForm.showPreview" />
                显示 3051 预览
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
          </div>

          <div class="card" v-show="navSubTab === 'core'">
            <div class="card-head"><h4>智能路径规划</h4></div>
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
              多段路径时：「起步前 / 前移」仅写入<strong>第 1 段</strong>，「到点后」仅写入<strong>最后一段</strong>；「行走中」写入每一段。可在下方指定路径里单独改某段。
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
                末段自动 ForkUnload
              </label>
            </div>

            <div class="plan-3066-preview">
              <div class="plan-preview-toolbar">
                <h5 class="plan-preview-title">3066 请求体预览</h5>
                <div class="plan-preview-btns">
                  <button type="button" class="btn btn-ghost-sm" @click="updateSpecPath3066Preview" :disabled="loading">刷新预览</button>
                  <button type="button" class="btn btn-ghost-sm" @click="copySpecPath3066Preview" :disabled="!specPath3066PreviewJson">复制 JSON</button>
                </div>
              </div>
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

          <div class="card priority-card" v-show="navSubTab === 'core'">
            <div class="card-head"><h4>指定路径 (3066)</h4></div>
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
            <div class="btn-row-2">
              <button type="button" class="btn btn-ghost-sm" @click="addSpecifiedSegment" :disabled="loading">+ 添加一段</button>
              <button type="button" class="btn btn-blue full" @click="handleSpecifiedPathNavigation" :disabled="loading">指定路径(3066)</button>
            </div>
          </div>
          <div class="card" v-show="navSubTab === 'core'">
            <div class="card-head"><h4>路径导航 (3051)</h4></div>
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
            <div class="fork-nav-options">
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
            <div class="fork-nav-options path-nav-fork-state">
              <div class="input-row-3">
                <div class="form-field compact">
                  <label>货叉动作后</label>
                  <select v-model="navForm.pathNavForkAfterMode" class="fork-mode-select">
                    <option value="in_place">等 fork_height_in_place</option>
                    <option value="delay">固定延时</option>
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
                    <option value="auto">状态口 自动</option>
                    <option value="1100">优先 1100</option>
                    <option value="1028">优先 1028</option>
                  </select>
                </div>
              </div>
            </div>
            <div class="fork-nav-options path-nav-6040-block">
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
            <button class="btn btn-blue full" @click="handlePathNavigation" :disabled="loading">路径导航(3051)</button>
          </div>
          <div class="card nav-card-tight" v-show="navSubTab === 'core'">
            <div class="card-head"><h4>导航控制</h4></div>
            <div class="btn-row-2">
              <button class="btn btn-red" @click="handleStopNavigation" :disabled="loading">停止导航(3052)</button>
              <button class="btn btn-ghost-sm" @click="handlePauseNavigation" :disabled="loading">暂停(3001)</button>
              <button class="btn btn-ghost-sm" @click="handleResumeNavigation" :disabled="loading">继续(3002)</button>
              <button class="btn btn-ghost-sm" @click="handleCancelNavigation" :disabled="loading">取消(3003)</button>
            </div>
          </div>
          <div class="card" v-show="navSubTab === 'motion'">
            <div class="card-head"><h4>转动 (3056)</h4></div>
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
          <div class="card" v-show="navSubTab === 'motion'">
            <div class="card-head"><h4>托盘旋转 (3057)</h4></div>
            <div class="input-row-2">
              <div class="form-field compact">
                <label>角度 (rad)</label>
                <input v-model.number="navForm.spinAngle" type="number" step="0.01" placeholder="如 1.57" />
              </div>
              <button class="btn btn-blue-outline" style="align-self:flex-end" @click="handleSpin" :disabled="loading">执行</button>
            </div>
          </div>
          <div class="card" v-show="navSubTab === 'motion'">
            <div class="card-head"><h4>圆弧(3058) / 线路(3059)</h4></div>
            <div class="form-field">
              <label>请求体 JSON</label>
              <textarea v-model="navForm.genericNavJson" rows="3" placeholder='{"key": "value"}' class="json-textarea"></textarea>
            </div>
            <div class="btn-row-2">
              <button class="btn btn-ghost-sm" @click="handleCircular" :disabled="loading">圆弧运动(3058)</button>
              <button class="btn btn-ghost-sm" @click="handlePathEnable" :disabled="loading">启用禁用线路(3059)</button>
            </div>
          </div>
          <div class="card" v-show="navSubTab === 'motion'">
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
          <div class="card" v-show="navSubTab === 'diag'">
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
          <div class="card" v-show="navSubTab === 'diag'">
            <div class="card-head"><h4>获取路径导航的路径 (3053)</h4></div>
            <button class="btn btn-ghost full" @click="handleGetTargetPath" :disabled="loading">获取当前路径</button>
          </div>
          <div class="card" v-show="navSubTab === 'diag'">
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
          <div class="card" v-show="navSubTab === 'diag'">
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
          <div class="card" v-show="navSubTab === 'diag'">
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
          <div class="card" v-show="navSubTab === 'diag'">
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
</template>

<script setup>
import { ref } from 'vue'
import { useRobokit } from "../../composables/useRobokit.js"

const navSubTab = ref('core')
const navSubTabs = [
  { id: 'core', label: '算路与下发' },
  { id: 'carry', label: '一键搬运' },
  { id: 'motion', label: '动作 / 清除' },
  { id: 'diag', label: '任务链 / 状态' },
]

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

<style scoped>
.nav-panel-root {
  gap: 8px;
}
.nav-subcard-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary, #aaa);
  margin: 10px 0 6px;
}
.nav-subtabs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 2px 0 10px;
  margin-bottom: 2px;
  border-bottom: 1px solid var(--border, rgba(255, 255, 255, 0.08));
  position: sticky;
  top: 0;
  z-index: 2;
  background: var(--bg-card, rgba(15, 18, 28, 0.92));
  backdrop-filter: blur(8px);
}
.nav-subtab {
  border: 1px solid var(--border, rgba(255, 255, 255, 0.1));
  background: transparent;
  color: var(--text-muted, #888);
  font-size: 12px;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.nav-subtab:hover {
  color: var(--text-secondary, #ccc);
  border-color: rgba(59, 130, 246, 0.35);
}
.nav-subtab.active {
  color: var(--blue, #3b82f6);
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(59, 130, 246, 0.1);
}
.nav-panel-root :deep(.card) {
  padding: 12px;
}
.nav-panel-root :deep(.card-head) {
  margin-bottom: 8px;
}
.nav-panel-root :deep(.card-hint) {
  font-size: 11px;
  line-height: 1.45;
  margin-bottom: 8px;
}
.nav-card-tight :deep(.btn-row-2) {
  flex-wrap: wrap;
}
.card-warn-inline {
  display: inline;
  color: var(--yellow, #eab308);
  margin-left: 4px;
}
.one-key-scheme-row {
  margin-bottom: 6px;
}
.one-key-scheme-hint {
  margin-top: 0 !important;
}
</style>
