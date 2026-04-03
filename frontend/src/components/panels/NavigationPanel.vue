<template>
<div v-if="activeGroup === 'navigation'" class="group-content">
          
          <div class="card priority-card">
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

          
          <div class="card">
            <div class="card-head"><h4>导航控制</h4></div>
            <div class="btn-row-2">
              <button class="btn btn-red" @click="handleStopNavigation" :disabled="loading">停止导航(3052)</button>
              <button class="btn btn-ghost-sm" @click="handlePauseNavigation" :disabled="loading">暂停(3001)</button>
              <button class="btn btn-ghost-sm" @click="handleResumeNavigation" :disabled="loading">继续(3002)</button>
              <button class="btn btn-ghost-sm" @click="handleCancelNavigation" :disabled="loading">取消(3003)</button>
            </div>
          </div>

          
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

          
          <div class="card">
            <div class="card-head"><h4>获取路径导航的路径 (3053)</h4></div>
            <button class="btn btn-ghost full" @click="handleGetTargetPath" :disabled="loading">获取当前路径</button>
          </div>

          
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
