import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as api from '../api'

export const groups = [
  { id: 'overview', name: '概览', icon: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="1" y="1" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.5"/><rect x="9" y="1" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.5"/><rect x="1" y="9" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.5"/><rect x="9" y="9" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.5"/></svg>' },
  { id: 'control', name: '控制', icon: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="3" stroke="currentColor" stroke-width="1.5"/><path d="M8 1v2M8 13v2M1 8h2M13 8h2M3 3l1.5 1.5M11.5 11.5L13 13M3 13l1.5-1.5M11.5 4.5L13 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>' },
  { id: 'monitor', name: '监控', icon: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="1" y="2" width="14" height="10" rx="2" stroke="currentColor" stroke-width="1.5"/><path d="M5 14h6M8 12v2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>' },
  { id: 'navigation', name: '导航', icon: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3 14l5-12 5 12-5-4-5 4z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>' },
]

export const activeGroup = ref('navigation')
export const connectionStatus = ref({ connected: false, host: '' })
export const loading = ref(false)
export const pollTimer = ref(null)
export const moveHeartbeatTimer = ref(null)

export const connectForm = ref({ host: '172.16.11.211', port: 19204 })

export const robotInfo = ref({})
export const locationInfo = ref({})
export const speedInfo = ref({})
export const batteryInfo = ref({})
export const emergencyInfo = ref({})
export const ioInfo = ref({ DI: [], DO: [] })
export const navStatusInfo = ref({})
export const binsInfo = ref({ header: {}, bins: [] })
export const motorInfo = ref({ motor_info: [] })
export const laserInfo = ref({ lasers: [] })
export const encoderInfo = ref({ encoder: [], motor_encoder: [] })
export const slamInfo = ref({ slam_status: 0 })
export const modbusResult = ref({})
export const modbusRegisters = ref('121,122')

export const moveForm = ref({ vx: 0.5, vy: 0, w: 0 })
export const controlNickname = ref('agv-web')
export const relocateForm = ref({ x: 0, y: 0, angleDeg: 0 })
export const translateForm = ref({ dist: 1, vx: null, vy: null, mode: 0 })
export const planPathForm = ref({
  sourceId: '',
  targetId: '',
  start_height: '',
  fork_mid_height: '',
  end_height: '',
  fork_dist: '',
})

export const oneKeyForm = ref({
  /** fork_in_3051：货叉随 3051（operation + 高度）；nav_6040：3051 仅站点导航，货叉只走 6040，不下发 operation */
  oneKeyScheme: 'fork_in_3051',
  pickId: '',
  dropId: '',
  timeoutSec: 120,
  pollMs: 500,
  pick_start_height: '',
  pick_fork_mid_height: '',
  pick_end_height: '',
  drop_start_height: '',
  drop_fork_mid_height: '',
  drop_operation: 'ForkUnload',
  drop_end_height: 0,
  /** nav_6040：取货段 3051 之前可选 6040 目标高度 (m) */
  pick6040Height: '',
  /** nav_6040：送货段 3051 之前可选 6040 目标高度 (m) */
  drop6040Height: '',
  /** 送货段 3051 完成后再发 6040（常用 0 降叉）；留空不执行 */
  afterDrop6040Height: '',
  /** 取货段 3051 请求体是否携带 recognize:true（见 API 文档路径导航/货叉 ForkLoad 等说明） */
  pickRecognize: false,
  showPreview: false,
})
export const oneKeyPreviewJson = ref('')

export const navForm = ref({
  target: '', type: 'point',
  sourceId: 'SELF_POSITION', targetId: 'LM1', taskId: '',
  pickDropPickId: '',
  pickDropDropId: '',
  pickDropTimeoutSec: 300,
  pickDropLoadStartHeight: '',
  pickDropLoadMidHeight: '',
  pickDropLoadEndHeight: '',
  pickDropLoadForkDist: '',
  forkDiId: '',
  forkWaitTimeoutSec: 120,
  forkPollMs: 500,
  pathNavOperation: '',
  pathNavUnloadAtEnd: false,
  pathNavForkStartHeight: '',
  pathNavForkMidHeight: '',
  pathNavForkEndHeight: 0,
  pathNavForkDist: '',
  
  pathNav6040Height: '',
  
  pathNavForkAfterMode: 'in_place',
  pathNavForkAfterDelaySec: 2,
  
  pathNavForkStatusPrefer: 'auto',
  planAutoUnloadLast: false,
  specifiedSegments: [
    { source_id: 'LM1', id: 'LM2', task_id: '12344321', operation: '', start_height: '', fork_mid_height: '', end_height: '', fork_dist: '' },
    { source_id: 'LM2', id: 'AP1', task_id: '12344322', operation: 'ForkHeight', start_height: '', fork_mid_height: '', end_height: 0.2, fork_dist: '' },
  ],
  moveAngle: 1.57, speedW: null, locMode: 0,
  spinAngle: 1.57, genericNavJson: '{}', clearTaskId: '', tasklistName: '',
})


export const planPathLastRoute = ref(null)

export const specPath3066PreviewJson = ref('')
export const specPath3066PreviewError = ref('')
export const specPath3066PreviewContinuityWarnings = ref([])

export const tasklistResult = ref(null)
export const tasklistStatusHint = ref('')
export const simpleBattery = ref(false)
export const logs = ref([])

export const locMethodText = computed(() => {
  const methods = { 0: '自然轮廓', 1: '反光柱', 2: '二维码', 3: '里程计', 4: '3D定位', 5: '天码', 6: '特征定位', 7: '3D特征', 8: '3D KF' }
  return methods[locationInfo.value.loc_method] || '-'
})

export const slamStatusText = computed(() => {
  const map = { 0: '未扫图', 1: '扫图中', 2: '扫图完成' }
  return map[slamInfo.value.slam_status] || '未知'
})

export function log(message, isError = false, isSuccess = false) {
  logs.value.unshift({ time: new Date().toLocaleTimeString(), message, error: isError, success: isSuccess })
  if (logs.value.length > 50) logs.value.pop()
}

export function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export function findDiEntry(diList, diId) {
  const raw = String(diId ?? '').trim()
  if (!raw) return null
  return (diList || []).find((d) => String(d.id) === raw || Number(d.id) === Number(diId))
}


export function parseForkDiIdList(input) {
  const s = String(input ?? '').trim()
  if (!s) return []
  return s.split(/[,，;\s]+/).map((x) => x.trim()).filter(Boolean)
}


export function forkDiSignalsAnyReady(diList, ids) {
  for (const id of ids) {
    const item = findDiEntry(diList, id)
    if (item && item.status === true) return true
  }
  return false
}


export function forkDiSignalsAllReady(diList, ids) {
  for (const id of ids) {
    const item = findDiEntry(diList, id)
    if (!item || item.status !== true) return false
  }
  return true
}


export function forkDiSignalsReady(diList, ids, mode) {
  return mode === 'any' ? forkDiSignalsAnyReady(diList, ids) : forkDiSignalsAllReady(diList, ids)
}

export function resolveDiCombineMode(options) {
  return options.diMode === 'any' ? 'any' : 'all'
}


export async function waitForForkDiReady(diInput, options = {}) {
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


export async function waitForForkDiReadyAtPickup(pickId, diInput, options = {}) {
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


export function normalizeLocationFromApi(raw) {
  if (!raw || typeof raw !== 'object') return {}
  return raw.data && typeof raw.data === 'object' ? raw.data : raw
}

/** 导航状态（1020）与位置等接口一致：task_status 等字段可能在 data 内 */
export function normalizeNavStatusFromApi(raw) {
  if (!raw || typeof raw !== 'object') return {}
  return raw.data && typeof raw.data === 'object' ? raw.data : raw
}

/** 状态口 1020 响应 task_status（与 API接口.docx 一致） */
export const NAV_TASK_STATUS = {
  NONE: 0,
  WAITING: 1,
  RUNNING: 2,
  SUSPENDED: 3,
  COMPLETED: 4,
  FAILED: 5,
  CANCELED: 6,
}


export async function isRobotAtStation(stationId) {
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


export async function waitForNavigationTaskCompleted(expectedTaskStatus = 4, options = {}) {
  const timeoutSec = Number(options.timeoutSec) || 120
  const pollMs = Number(options.pollMs) || 500
  const timeoutMs = Math.max(5000, timeoutSec * 1000)
  const intervalMs = Math.max(200, pollMs)
  const start = Date.now()
  while (Date.now() - start < timeoutMs) {
    const navData = await api.robokitGetNavStatus().catch(() => null)
    if (!navData) {
      await sleep(intervalMs)
      continue
    }
    const payload = normalizeNavStatusFromApi(navData)
    const raw =
      payload.task_status ??
      payload.taskStatus ??
      payload.status ??
      navData.task_status ??
      navData.taskStatus ??
      navData.status
    if (raw !== undefined && raw !== null) {
      const st = Number(raw)
      if (!Number.isFinite(st)) {
        await sleep(intervalMs)
        continue
      }
      if (st === NAV_TASK_STATUS.FAILED) {
        throw new Error('导航任务失败（1020 task_status=5 FAILED），未下发送货段')
      }
      if (st === NAV_TASK_STATUS.CANCELED) {
        throw new Error('导航任务已取消（1020 task_status=6 CANCELED），未下发送货段')
      }
      if (st === Number(expectedTaskStatus)) return { ...navData, ...payload }
    }
    await sleep(intervalMs)
  }
  const cond = `task_status=${expectedTaskStatus}`
  throw new Error(
    `等待导航任务完成（1020 期望 ${cond}，4=COMPLETED）超时（${timeoutMs / 1000}s）`,
  )
}

async function readNavTaskStatusNumber() {
  const navData = await api.robokitGetNavStatus().catch(() => null)
  if (!navData || typeof navData !== 'object') return null
  const payload = normalizeNavStatusFromApi(navData)
  const raw =
    payload.task_status ??
    payload.taskStatus ??
    payload.status ??
    navData.task_status ??
    navData.taskStatus ??
    navData.status
  if (raw === undefined || raw === null) return null
  const st = Number(raw)
  return Number.isFinite(st) ? st : null
}

/**
 * 刚下发自定义 3051 后：先尽量等到 task_status 离开 COMPLETED(4)（新任务接单/执行），再等到再次 COMPLETED。
 * 避免仍停留在上一段「已完成」时误判第二段已结束。
 */
export async function waitForNavigationTaskActiveThenCompleted(options = {}) {
  const timeoutSec = Number(options.timeoutSec) || 120
  const pollMs = Math.max(200, Number(options.pollMs) || 500)
  const totalDeadline = Date.now() + Math.max(5000, timeoutSec * 1000)
  const activePhaseMs = Math.min(20000, Math.max(5000, timeoutSec * 500))
  const activeDeadline = Date.now() + activePhaseMs
  let sawActive = false
  while (Date.now() < activeDeadline && Date.now() < totalDeadline) {
    const st = await readNavTaskStatusNumber()
    if (st == null) {
      await sleep(pollMs)
      continue
    }
    if (st === NAV_TASK_STATUS.FAILED) {
      throw new Error('导航任务失败（1020 task_status=5），送货段未完成')
    }
    if (st === NAV_TASK_STATUS.CANCELED) {
      throw new Error('导航任务已取消（1020 task_status=6），送货段未完成')
    }
    if (
      st === NAV_TASK_STATUS.WAITING ||
      st === NAV_TASK_STATUS.RUNNING ||
      st === NAV_TASK_STATUS.SUSPENDED
    ) {
      sawActive = true
      break
    }
    await sleep(pollMs)
  }
  if (!sawActive) {
    log(
      '未在限时内读到 task_status=1/2/3（新段执行中），将直接轮询 task_status=4（若车体状态刷新慢，请拉长超时）',
      false,
      false,
    )
  }
  await waitForNavigationTaskCompleted(NAV_TASK_STATUS.COMPLETED, options)
}


export function mergeForkNumericFromPickDropLoad(extra, form) {
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


export async function monitorPickLegForDiOrArrival(pickId, diInput, options = {}) {
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
  } catch (_) {  }
  throw new Error(`取货段监测超时（${timeoutMs / 1000}s），已尝试停止导航`)
}


export async function runPickDrop3051Flow() {
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
  } catch (_) {  }

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
  } catch (_) {  }
  await sleep(400)

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

export const FORK_NUMERIC_KEYS = ['start_height', 'fork_mid_height', 'end_height', 'fork_dist']


export function mergeForkNumericFromSeg(item, seg) {
  for (const key of FORK_NUMERIC_KEYS) {
    const v = seg[key]
    if (v != null && v !== '' && Number.isFinite(Number(v))) {
      item[key] = Number(v)
    }
  }
}


/**
 * 将「智能路径规划」里填写的货叉参数同步到多段列表。
 * 多段时：起步前举升(start_height)、前移(fork_dist)只作用首段，到点后(end_height)只作用末段，
 * 避免途经站每段都重复「起步/到点」举升；fork_mid_height 作用于每一段以保持行驶中的目标高度。
 * 仅一段时：四个参数都作用于该段（与整段 3051/3066 单段语义一致）。
 */
export function applyPlanPathForkDefaultsToSegments(segments, planForm) {
  const n = segments.length
  if (!n) return

  const applyKey = (seg, key) => {
    const raw = planForm[key]
    if (raw != null && raw !== '' && Number.isFinite(Number(raw))) {
      seg[key] = Number(raw)
    }
  }

  if (n === 1) {
    for (const key of FORK_NUMERIC_KEYS) {
      applyKey(segments[0], key)
    }
    return
  }

  const first = segments[0]
  const last = segments[n - 1]
  applyKey(first, 'start_height')
  applyKey(first, 'fork_dist')
  applyKey(last, 'end_height')

  for (const seg of segments) {
    applyKey(seg, 'fork_mid_height')
  }
}

export function mergeForkNumericFromForm(extra, form) {
  for (const key of FORK_NUMERIC_KEYS) {
    const raw = form[key]
    if (raw != null && raw !== '' && Number.isFinite(Number(raw))) {
      extra[key] = Number(raw)
    }
  }
}

export function mergeOneKeyForkNumeric(extra, form, part = 'pick') {
  const prefix = part === 'drop' ? 'drop' : 'pick'
  const map = [
    ['start_height', `${prefix}_start_height`],
    ['fork_mid_height', `${prefix}_fork_mid_height`],
    ['end_height', `${prefix}_end_height`],
  ]
  for (const [targetKey, formKey] of map) {
    const raw = form[formKey]
    if (raw != null && raw !== '' && Number.isFinite(Number(raw))) {
      extra[targetKey] = Number(raw)
    }
  }
}

/** 路径导航 3051 取货段：文档中可与 ForkLoad 等一并下发的 recognize（bool） */
export function applyPickRecognizeToPathNavBody(body, form) {
  if (!body || typeof body !== 'object' || !form || form.pickRecognize !== true) return
  body.recognize = true
}

function oneKeyOptional6040Height(raw) {
  if (raw == null || raw === '') return null
  const n = Number(raw)
  return Number.isFinite(n) ? n : null
}


export async function runPreDeliverySetForkHeight(heightM, logPrefix = '设置货叉高度') {
  if (heightM == null || !Number.isFinite(heightM)) {
    log(`${logPrefix}：未解析到目标高度(m)，跳过`, false, false)
    return true
  }
  const msg = api.ROBOKIT_MSG_SET_FORK_HEIGHT
  try {
    log(`${logPrefix}：API ${msg}，params { height: ${heightM} } …`, false, true)
    const cmdAt = Date.now()
    await api.robokitSetForkHeight({ height: heightM })
    await sleep(200)
    const prefer = pathNavForkStatusPreferToApi()
    log(
      `${logPrefix}：等待 fork_height_in_place（${prefer === 'auto' ? '先 1100 再 1028' : prefer}；避免误判上一周期已到位）…`,
      false,
      false,
    )
    const waitRes = await api.robokitWaitForkHeightInPlace({
      timeoutSec: 60,
      pollMs: 300,
      preferStatus: prefer === 'auto' ? undefined : prefer,
      commandIssuedAt: cmdAt,
      minMsBeforeAcceptTrue: 750,
      trySeeFalseFirst: true,
      falseFirstMaxMs: 4000,
    })
    if (waitRes.ok) {
      if (waitRes.sawFalseAfterCommand === false) {
        log(
          `${logPrefix}：未观察到 in_place 先变 false（目标高度可能与当前一致或车体不翻转该位），已用最短等待后再判到位`,
          false,
          false,
        )
      }
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


export async function sendMoveTaskListBy3051(list, sceneLabel = '3051分段') {
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


export async function sendTwoLegBy3051Self(pickId, dropId, firstTaskId = null, secondTaskId = null, pickExtra = {}, dropExtra = {}) {
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


export function mergeForkNumericFromPathNavForm(extra, form) {
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

export function getSegmentContinuityWarnings(list) {
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


export function buildMoveTaskListFromSegments(segments) {
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

export function updateSpecPath3066Preview() {
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

export async function copySpecPath3066Preview() {
  const text = specPath3066PreviewJson.value
  if (!text) return
  try {
    await navigator.clipboard.writeText(text)
    log('已复制 3066 请求 JSON', false, true)
  } catch (e) {
    log('复制失败（部分环境需 HTTPS，可手动全选文本框复制）', true)
  }
}


export async function refreshOneKeyPreview() {
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
    const nav6040 = oneKeyForm.value.oneKeyScheme === 'nav_6040'
    const pickH6040 = oneKeyOptional6040Height(oneKeyForm.value.pick6040Height)
    const dropH6040 = oneKeyOptional6040Height(oneKeyForm.value.drop6040Height)
    const afterDropH6040 = oneKeyOptional6040Height(oneKeyForm.value.afterDrop6040Height)

    if (nav6040) {
      if (pickId) {
        if (pickH6040 != null) {
          requests.push({
            api: 6040,
            description: '取货前设货叉高度',
            body: { height: pickH6040 },
          })
        }
        const pickNavBody = {
          source_id: 'SELF_POSITION',
          id: pickId,
          task_id: baseTaskId + '01',
        }
        applyPickRecognizeToPathNavBody(pickNavBody, oneKeyForm.value)
        requests.push({
          api: 3051,
          description: '取货段纯导航（无 operation / 无货叉高度字段）',
          body: pickNavBody,
        })
      }
      if (dropId) {
        if (dropH6040 != null) {
          requests.push({
            api: 6040,
            description: '送货前设货叉高度',
            body: { height: dropH6040 },
          })
        }
        requests.push({
          api: 3051,
          description: '送货段纯导航（无 operation / 无货叉高度字段）',
          body: { source_id: 'SELF_POSITION', id: dropId, task_id: baseTaskId + '02' },
        })
        if (afterDropH6040 != null) {
          requests.push({
            api: 6040,
            description: '送货完成后设货叉高度',
            body: { height: afterDropH6040 },
          })
        }
      }
    } else if (pickId) {
      const req1 = {
        source_id: 'SELF_POSITION',
        id: pickId,
        task_id: baseTaskId + '01',
        operation: 'ForkLoad',
      }
      mergeOneKeyForkNumeric(req1, oneKeyForm.value, 'pick')
      applyPickRecognizeToPathNavBody(req1, oneKeyForm.value)
      requests.push({ api: 3051, description: '取货段（仅取货 / 全程首段）', body: req1 })
    }
    if (!nav6040 && dropId) {
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
      if (afterDropH6040 != null) {
        requests.push({
          api: 6040,
          description: '送货完成后设货叉高度',
          body: { height: afterDropH6040 },
        })
      }
    }

    const hintParts = []
    if (!pickId) hintParts.push('未填取货点：全程/仅取货预览不含首段')
    if (!dropId) hintParts.push('未填放货点：预览不含次段')
    if (nav6040) {
      hintParts.push('模式：3051 仅导航；货叉高度仅 6040（未填高度则跳过对应 6040）')
    }
    oneKeyPreviewJson.value = JSON.stringify({
      scheme: nav6040 ? 'nav_6040' : 'fork_in_3051',
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


export async function handleOneKeyCarryPickOnly() {
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
    const taskId1 = `${baseTaskId}P1`
    const nav6040 = oneKeyForm.value.oneKeyScheme === 'nav_6040'
    const pickH6040 = oneKeyOptional6040Height(oneKeyForm.value.pick6040Height)

    const req1Nav = { source_id: 'SELF_POSITION', id: pickId, task_id: taskId1 }
    const req1Fork = {
      source_id: 'SELF_POSITION',
      id: pickId,
      task_id: taskId1,
      operation: 'ForkLoad',
    }
    mergeOneKeyForkNumeric(req1Fork, oneKeyForm.value, 'pick')
    applyPickRecognizeToPathNavBody(req1Nav, oneKeyForm.value)
    applyPickRecognizeToPathNavBody(req1Fork, oneKeyForm.value)

    oneKeyPreviewJson.value = JSON.stringify(
      {
        scheme: nav6040 ? 'nav_6040' : 'fork_in_3051',
        description: '仅取货段',
        requests: nav6040
          ? [
              ...(pickH6040 != null ? [{ api: 6040, body: { height: pickH6040 } }] : []),
              { api: 3051, description: '取货段', body: req1Nav },
            ]
          : [{ api: 3051, description: '取货段', body: req1Fork }],
      },
      null,
      2,
    )

    if (!skipLoadLeg) {
      if (nav6040 && pickH6040 != null) {
        const ok = await runPreDeliverySetForkHeight(pickH6040, '一键搬运·取货前 6040')
        if (!ok) return
      }
      let pickExtra = null
      if (nav6040 && oneKeyForm.value.pickRecognize === true) {
        pickExtra = { recognize: true }
      }
      if (!nav6040) {
        pickExtra = { operation: 'ForkLoad' }
        mergeOneKeyForkNumeric(pickExtra, oneKeyForm.value, 'pick')
        applyPickRecognizeToPathNavBody(pickExtra, oneKeyForm.value)
      }
      const r1 = await api.robokitPathNavigation('SELF_POSITION', pickId, taskId1, pickExtra)
      if (r1?.ret_code !== 0) {
        log('仅取货 3051 下发失败', true)
        return
      }
      log(
        nav6040
          ? `仅取货 已下发纯导航 SELF_POSITION→${pickId}（无 operation）`
          : `仅取货 已下发 SELF_POSITION→${pickId}`,
        false,
        true,
      )
    } else {
      log('仅取货：已在取货点，未下发导航；第二段请点「仅下发送货段」', false, false)
    }
  } catch (e) {
    log('仅取货错误: ' + (e.message || e), true)
  } finally {
    loading.value = false
  }
}


export async function handleOneKeyCarryDropOnly() {
  loading.value = true
  try {
    const dropId = String(oneKeyForm.value.dropId || '').trim()
    if (!dropId) {
      log('仅送货：请填写放货点', true)
      return
    }

    const baseTaskId = String(Date.now() % 100000000)
    const taskId2 = `${baseTaskId}D1`
    const nav6040 = oneKeyForm.value.oneKeyScheme === 'nav_6040'
    const dropH6040 = oneKeyOptional6040Height(oneKeyForm.value.drop6040Height)
    const afterDropH6040 = oneKeyOptional6040Height(oneKeyForm.value.afterDrop6040Height)

    const req2Nav = { source_id: 'SELF_POSITION', id: dropId, task_id: taskId2 }
    const op = String(oneKeyForm.value.drop_operation || 'ForkUnload')
    const req2Fork = {
      source_id: 'SELF_POSITION',
      id: dropId,
      task_id: taskId2,
      operation: op,
      end_height: 0,
    }
    mergeOneKeyForkNumeric(req2Fork, oneKeyForm.value, 'drop')
    if (req2Fork.operation === 'ForkUnload' && req2Fork.end_height === undefined) req2Fork.end_height = 0

    const previewRequests = nav6040
      ? [
          ...(dropH6040 != null ? [{ api: 6040, body: { height: dropH6040 } }] : []),
          { api: 3051, description: '放货段', body: req2Nav },
          ...(afterDropH6040 != null
            ? [{ api: 6040, description: '送货完成后', body: { height: afterDropH6040 } }]
            : []),
        ]
      : [
          { api: 3051, description: '放货段', body: req2Fork },
          ...(afterDropH6040 != null
            ? [{ api: 6040, description: '送货完成后', body: { height: afterDropH6040 } }]
            : []),
        ]
    oneKeyPreviewJson.value = JSON.stringify(
      { scheme: nav6040 ? 'nav_6040' : 'fork_in_3051', requests: previewRequests },
      null,
      2,
    )

    if (nav6040 && dropH6040 != null) {
      const ok = await runPreDeliverySetForkHeight(dropH6040, '一键搬运·送货前 6040')
      if (!ok) return
    }
    let dropExtra = null
    if (!nav6040) {
      dropExtra = { operation: req2Fork.operation, end_height: 0 }
      mergeOneKeyForkNumeric(dropExtra, oneKeyForm.value, 'drop')
      if (dropExtra.operation === 'ForkUnload' && dropExtra.end_height === undefined) dropExtra.end_height = 0
    }

    const r2 = await api.robokitPathNavigation('SELF_POSITION', dropId, taskId2, dropExtra)
    if (r2?.ret_code === 0) {
      log(
        nav6040
          ? `仅送货：已下发纯导航 SELF_POSITION→${dropId}（无 operation）`
          : `仅送货：已下发 SELF_POSITION→${dropId}`,
        false,
        true,
      )
      if (afterDropH6040 != null) {
        log('仅送货：等待送货段完成后再发 6040 降叉…', false, true)
        try {
          await waitForNavigationTaskActiveThenCompleted({
            timeoutSec: oneKeyForm.value.timeoutSec,
            pollMs: oneKeyForm.value.pollMs,
          })
        } catch (e) {
          log('仅送货：等待完成失败 — ' + (e.message || e), true)
          return
        }
        const okDown = await runPreDeliverySetForkHeight(
          afterDropH6040,
          '仅送货·送货完成后 6040',
        )
        if (!okDown) log('仅送货：送货后降叉未确认到位', true)
      }
    } else {
      log('仅送货：3051 下发失败', true)
    }
  } catch (e) {
    log('仅送货错误: ' + (e.message || e), true)
  } finally {
    loading.value = false
  }
}

export async function handleOneKeyCarry() {
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
    const taskId1 = `${baseTaskId}01`
    const taskId2 = `${baseTaskId}02`
    const nav6040 = oneKeyForm.value.oneKeyScheme === 'nav_6040'
    const pickH6040 = oneKeyOptional6040Height(oneKeyForm.value.pick6040Height)
    const dropH6040 = oneKeyOptional6040Height(oneKeyForm.value.drop6040Height)
    const afterDropH6040 = oneKeyOptional6040Height(oneKeyForm.value.afterDrop6040Height)

    const req1Nav = { source_id: 'SELF_POSITION', id: pickId, task_id: taskId1 }
    const req1Fork = {
      source_id: 'SELF_POSITION',
      id: pickId,
      task_id: taskId1,
      operation: 'ForkLoad',
    }
    mergeOneKeyForkNumeric(req1Fork, oneKeyForm.value, 'pick')
    applyPickRecognizeToPathNavBody(req1Nav, oneKeyForm.value)
    applyPickRecognizeToPathNavBody(req1Fork, oneKeyForm.value)

    const op2 = String(oneKeyForm.value.drop_operation || 'ForkUnload')
    const req2Nav = { source_id: 'SELF_POSITION', id: dropId, task_id: taskId2 }
    const req2Fork = {
      source_id: 'SELF_POSITION',
      id: dropId,
      task_id: taskId2,
      operation: op2,
      end_height: 0,
    }
    mergeOneKeyForkNumeric(req2Fork, oneKeyForm.value, 'drop')
    if (req2Fork.operation === 'ForkUnload' && req2Fork.end_height === undefined) req2Fork.end_height = 0

    let pickExtra = null
    let dropExtra = null
    let previewRequests = []
    if (nav6040 && oneKeyForm.value.pickRecognize === true) {
      pickExtra = { recognize: true }
    }
    if (nav6040) {
      if (pickH6040 != null) {
        previewRequests.push({ api: 6040, description: '取货前', body: { height: pickH6040 } })
      }
      previewRequests.push({ api: 3051, description: '取货段纯导航', body: req1Nav })
      if (dropH6040 != null) {
        previewRequests.push({ api: 6040, description: '送货前', body: { height: dropH6040 } })
      }
      previewRequests.push({ api: 3051, description: '送货段纯导航', body: req2Nav })
      if (afterDropH6040 != null) {
        previewRequests.push({
          api: 6040,
          description: '送货完成后货叉高度',
          body: { height: afterDropH6040 },
        })
      }
    } else {
      pickExtra = { operation: 'ForkLoad' }
      mergeOneKeyForkNumeric(pickExtra, oneKeyForm.value, 'pick')
      applyPickRecognizeToPathNavBody(pickExtra, oneKeyForm.value)
      dropExtra = { operation: req2Fork.operation, end_height: 0 }
      mergeOneKeyForkNumeric(dropExtra, oneKeyForm.value, 'drop')
      if (dropExtra.operation === 'ForkUnload' && dropExtra.end_height === undefined) dropExtra.end_height = 0
      previewRequests = [
        { api: 3051, description: '取货段', body: req1Fork },
        { api: 3051, description: '放货段', body: req2Fork },
      ]
      if (afterDropH6040 != null) {
        previewRequests.push({
          api: 6040,
          description: '送货完成后货叉高度',
          body: { height: afterDropH6040 },
        })
      }
    }

    oneKeyPreviewJson.value = JSON.stringify({
      scheme: nav6040 ? 'nav_6040' : 'fork_in_3051',
      requests: previewRequests,
    }, null, 2)

    if (!skipLoadLeg) {
      if (nav6040 && pickH6040 != null) {
        const ok = await runPreDeliverySetForkHeight(pickH6040, '一键搬运·取货前 6040')
        if (!ok) return
      }
      const r1 = await api.robokitPathNavigation('SELF_POSITION', pickId, taskId1, pickExtra)
      if (r1?.ret_code !== 0) { log('一键搬运 首段 3051 下发失败', true); return }
      log(
        nav6040
          ? `一键搬运 首段纯导航已下发: SELF_POSITION→${pickId}`
          : `一键搬运 首段已下发: SELF_POSITION→${pickId}`,
        false,
        true,
      )
    }
    log('一键搬运：轮询状态口 1020，首段完成后 task_status=4 即下发送货段 3051…', false, true)
    await waitForNavigationTaskCompleted(4, {
      timeoutSec: oneKeyForm.value.timeoutSec,
      pollMs: oneKeyForm.value.pollMs,
    })
    log('一键搬运：已检测到 task_status=4（首段完成），下发送货导航…', false, true)
    if (nav6040 && dropH6040 != null) {
      const ok = await runPreDeliverySetForkHeight(dropH6040, '一键搬运·送货前 6040')
      if (!ok) return
    }
    const r2 = await api.robokitPathNavigation('SELF_POSITION', dropId, taskId2, dropExtra)
    if (r2?.ret_code === 0) {
      log(
        nav6040
          ? `一键搬运 送货段纯导航已下发: SELF_POSITION→${dropId}`
          : `一键搬运 送货段已下发: SELF_POSITION→${dropId}`,
        false,
        true,
      )
      if (afterDropH6040 != null) {
        log('一键搬运：等待送货段完成（1020）后再发 6040 降叉…', false, true)
        try {
          await waitForNavigationTaskActiveThenCompleted({
            timeoutSec: oneKeyForm.value.timeoutSec,
            pollMs: oneKeyForm.value.pollMs,
          })
        } catch (e) {
          log('一键搬运：等待送货段完成失败 — ' + (e.message || e), true)
          return
        }
        const okDown = await runPreDeliverySetForkHeight(
          afterDropH6040,
          '一键搬运·送货完成后 6040',
        )
        if (!okDown) log('一键搬运：送货后降叉未确认到位，请现场确认', true)
      }
    } else {
      log('一键搬运 第二段下发失败', true)
    }
  } catch (e) {
    log('一键搬运错误: ' + (e.message || e), true)
  } finally {
    loading.value = false
  }
}

export function formatRobokitError(msg) {
  if (!msg || typeof msg !== 'string') return msg
  if (msg.includes('40009') || msg.includes('deprecated')) return msg + ' → 固件已弃用模式切换 API，抢占控制后可直接执行移动'
  if (msg.includes('40012')) return msg + ' → 调度中，请先「抢占控制」'
  if (msg.includes('40020')) return msg + ' → 控制权已被抢占'
  if (msg.includes('40101')) return msg + ' → 被其他设备锁定，需在该设备上释放'
  return msg
}

export async function handleConnect() {
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

export async function handleDisconnect() {
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

export async function handleToggleConnection() {
  connectionStatus.value.connected ? await handleDisconnect() : await handleConnect()
}

export async function loadAllStatus() {
  await Promise.all([loadRobotInfo(), loadLocation(), loadSpeed(), loadBattery(), loadEmergency()])
}

export async function loadRobotInfo() {
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

export async function loadLocation() {
  try {
    const data = await api.robokitGetLocation()
    if (data) locationInfo.value = data.data && typeof data.data === 'object' ? data.data : data
  } catch (e) { log('获取位置失败: ' + e.message, true) }
}

export async function loadSpeed() {
  try {
    const data = await api.robokitGetSpeed()
    if (data) speedInfo.value = data.data && typeof data.data === 'object' ? data.data : data
  } catch (e) { log('获取速度失败: ' + e.message, true) }
}

export async function loadBattery() {
  try {
    const data = await api.robokitGetBattery(simpleBattery.value)
    if (data) batteryInfo.value = data
  } catch (e) { log('获取电池状态失败: ' + e.message, true) }
}

export async function loadEmergency() {
  try {
    const data = await api.robokitGetEmergency()
    if (data) emergencyInfo.value = data
  } catch (e) { log('获取急停状态失败: ' + e.message, true) }
}

export async function loadIO() {
  loading.value = true
  try { const data = await api.robokitGetIO(); if (data) ioInfo.value = data }
  catch (e) { log('获取I/O状态失败: ' + e.message, true) }
  finally { loading.value = false }
}

export async function loadNavStatus() {
  loading.value = true
  try {
    const [navData, locData] = await Promise.all([api.robokitGetNavStatus(), api.robokitGetLocStatus()])
    if (navData) navStatusInfo.value.status = '运行中'
    if (locData) navStatusInfo.value.loc_status = '已定位'
  } catch (e) { log('获取导航状态失败: ' + e.message, true) }
  finally { loading.value = false }
}

export async function loadBins() {
  loading.value = true
  try { const data = await api.robokitGetBins(); if (data) binsInfo.value = data }
  catch (e) { log('获取库位状态失败: ' + e.message, true) }
  finally { loading.value = false }
}

export async function loadMotor() {
  loading.value = true
  try { const data = await api.robokitGetMotor(); if (data) motorInfo.value = data }
  catch (e) { log('获取电机状态失败: ' + e.message, true) }
  finally { loading.value = false }
}

export async function loadLaser() {
  loading.value = true
  try { const data = await api.robokitGetLaser(); if (data) laserInfo.value = data }
  catch (e) { log('获取激光数据失败: ' + e.message, true) }
  finally { loading.value = false }
}

export async function loadEncoder() {
  loading.value = true
  try { const data = await api.robokitGetEncoder(); if (data) encoderInfo.value = data }
  catch (e) { log('获取编码器数据失败: ' + e.message, true) }
  finally { loading.value = false }
}

export async function loadSlam() {
  loading.value = true
  try { const data = await api.robokitGetSlam(); if (data) slamInfo.value = data }
  catch (e) { log('获取扫图状态失败: ' + e.message, true) }
  finally { loading.value = false }
}

export async function handleQueryModbus() {
  loading.value = true
  try {
    const registers = modbusRegisters.value.split(',').map(r => parseInt(r.trim())).filter(r => !isNaN(r))
    if (!registers.length) { log('请输入有效的寄存器地址', true); return }
    const data = await api.robokitQueryModbus(registers)
    if (data) { modbusResult.value = data; log(`Modbus查询成功: ${registers.join(',')}`, false, true) }
  } catch (e) { log('Modbus查询失败: ' + e.message, true) }
  finally { loading.value = false }
}

export async function handleTakeControl() {
  loading.value = true
  try {
    try { await api.robokitTakeControl(controlNickname.value || 'agv-web'); log('抢占控制权成功', false, true); return } catch {}
    try { await api.robokitStopNavigation(); log('已停止导航', false, true); return } catch {}
    await api.robokitStop(); log('已发送停止指令', false, true)
  } catch (e) { log('抢占控制失败: ' + formatRobokitError(e.message), true) }
  finally { loading.value = false }
}

export async function handleReleaseControl() {
  loading.value = true
  try { await api.robokitReleaseControl(); log('已释放控制权', false, true) }
  catch (e) { log('释放控制失败: ' + formatRobokitError(e.message), true) }
  finally { loading.value = false }
}

export async function handleSetMode(mode) {
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

export async function handleMove() {
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

export async function handleStop() {
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

export function fillRelocateFromCurrent() {
  if (locationInfo.value.x != null && locationInfo.value.y != null) {
    relocateForm.value.x = Number(locationInfo.value.x.toFixed(3))
    relocateForm.value.y = Number(locationInfo.value.y.toFixed(3))
    relocateForm.value.angleDeg = Number(((locationInfo.value.angle ?? 0) * 180 / Math.PI).toFixed(1))
    log('已填入当前位置', false, true)
  }
}

export async function handleRelocate() {
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

export async function handleConfirmLocation() {
  loading.value = true
  try {
    const result = await api.robokitConfirmLocation()
    if (result?.ret_code === 0) { log('定位已确认', false, true); await loadLocation() }
    else { log('确认定位失败', true) }
  } catch (e) { log('确认定位错误: ' + formatRobokitError(e.message), true) }
  finally { loading.value = false }
}

export async function handleCancelRelocate() {
  loading.value = true
  try {
    const result = await api.robokitCancelRelocate()
    if (result?.ret_code === 0) log('已取消重定位', false, true)
    else log('取消重定位失败', true)
  } catch (e) { log('取消重定位错误: ' + formatRobokitError(e.message), true) }
  finally { loading.value = false }
}

export async function handleTranslate() {
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

export async function handleEmergencyStop() {
  loading.value = true
  try {
    const result = await api.robokitEmergencyStop()
    if (result?.ret_code === 0) log('紧急停车已执行', false, true)
    else log('紧急停车失败', true)
  } catch (e) { log('紧急停车错误: ' + formatRobokitError(e.message), true) }
  finally { loading.value = false }
}

export async function handleQuickRelocate() {
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

export async function handleMoveTo() {
  const target = navForm.value.target?.trim()
  if (!target) { log('请输入目标', true); return }
  loading.value = true
  try {

    try {
      await api.robokitSetMode(1)
    } catch (_) {  }
    const result = await api.robokitMoveTo(target, navForm.value.type)
    if (result?.ret_code === 0) log(`导航到 ${navForm.value.type}: ${target}`, false, true)
    else log(`导航指令失败: ${result?.err_msg || 'ret_code=' + (result?.ret_code ?? '?')}`, true)
  } catch (e) { log('导航错误: ' + e.message, true) }
  finally { loading.value = false }
}

export function pathNavForkStatusPreferToApi() {
  const v = navForm.value.pathNavForkStatusPrefer || 'auto'
  if (v === '1100' || v === '1028') return v
  return 'auto'
}


export async function applyNavFormForkStateWait(contextLabel) {
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


export async function handlePathNav6040SetHeight(overrideHeight) {
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

export async function handlePathNav6040Quick(v) {
  navForm.value.pathNav6040Height = v
  await handlePathNav6040SetHeight(v)
}


export async function handlePathNav6040DownZero() {
  navForm.value.pathNav6040Height = 0
  await handlePathNav6040SetHeight(0)
}

export async function handlePathNavigation() {
  loading.value = true
  try {
    const sourceId = (navForm.value.sourceId || '').trim()
    const targetId = (navForm.value.targetId || '').trim()
    if (!sourceId || !targetId) { log('请填写起点 source_id 与终点 id', true); return }
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

export async function handlePlanPath() {
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

export function addSpecifiedSegment() {
  const segments = navForm.value.specifiedSegments
  navForm.value.specifiedSegments = [
    ...segments,
    { source_id: '', id: '', task_id: '', operation: '', start_height: '', fork_mid_height: '', end_height: '', fork_dist: '' },
  ]
  updateSpecPath3066Preview()
}

export function removeSpecifiedSegment(idx) {
  if (navForm.value.specifiedSegments.length <= 1) return
  const segments = [...navForm.value.specifiedSegments]
  segments.splice(idx, 1)
  navForm.value.specifiedSegments = segments
  updateSpecPath3066Preview()
}

export async function handleSpecifiedPathNavigation() {
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
      } catch (_) {  }
      log('若小车未动: 请确认已抢占控制权，并确认站点间有直接线路', false, false)
    } else {
      log(`指定路径失败: ret_code=${result?.ret_code ?? '?'} ${result?.err_msg || ''}`, true)
      if (result) log('完整响应: ' + JSON.stringify(result), true, false)
    }
  } catch (e) { log('指定路径导航错误: ' + e.message, true) }
  finally { loading.value = false }
}

export async function handleStopNavigation() {
  loading.value = true
  try {
    const result = await api.robokitStopNavigation()
    if (result?.ret_code === 0) log('导航已停止', false, true)
    else log('停止导航失败', true)
  } catch (e) { log('停止导航错误: ' + e.message, true) }
  finally { loading.value = false }
}

export async function handlePauseNavigation() {
  loading.value = true
  try {
    const result = await api.robokitPauseNavigation()
    if (result?.ret_code === 0) log('已暂停当前导航(3001)', false, true)
    else log('暂停失败', true)
  } catch (e) { log('暂停导航错误: ' + e.message, true) }
  finally { loading.value = false }
}

export async function handleResumeNavigation() {
  loading.value = true
  try {
    const result = await api.robokitResumeNavigation()
    if (result?.ret_code === 0) log('已继续当前导航(3002)', false, true)
    else log('继续失败', true)
  } catch (e) { log('继续导航错误: ' + e.message, true) }
  finally { loading.value = false }
}

export async function handleCancelNavigation() {
  loading.value = true
  try {
    const result = await api.robokitCancelNavigation()
    if (result?.ret_code === 0) log('已取消当前导航(3003)', false, true)
    else log('取消失败', true)
  } catch (e) { log('取消导航错误: ' + e.message, true) }
  finally { loading.value = false }
}

export async function handleTurn() {
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

export async function handleSpin() {
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

export async function handleCircular() {
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

export async function handlePathEnable() {
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

export async function handleClearTargetList() {
  loading.value = true
  try {
    const result = await api.robokitClearTargetList()
    if (result?.ret_code === 0) log('已清除指定导航路径(3067)', false, true)
    else log('清除失败', true)
  } catch (e) { log('清除路径错误: ' + e.message, true) }
  finally { loading.value = false }
}

export async function handleClearByTaskId() {
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

export const TASKLIST_STATUS_MAP = {
  0: '无/空闲',
  1: '运行中',
  2: '完成',
  3: '失败',
  4: '取消',
  5: '暂停',
  6: '已结束/完成(以接口文档为准)',
}
export async function handleGetTasklistStatus() {
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

export async function handleGetTasklistList() {
  loading.value = true
  try {
    const data = await api.robokitGetTasklistList()
    tasklistResult.value = data != null ? JSON.stringify(data, null, 2) : null
    if (data != null) log('已查询所有任务链(3115)', false, true)
  } catch (e) { log('查询任务链列表错误: ' + e.message, true) }
  finally { loading.value = false }
}

export async function handleExecuteTasklist() {
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

export async function handleGetTargetPath() {
  loading.value = true
  try {
    const data = await api.robokitGetTargetPath()
    tasklistResult.value = data != null ? JSON.stringify(data, null, 2) : null
    if (data != null) log('已获取路径(3053)', false, true)
  } catch (e) { log('获取路径错误: ' + e.message, true) }
  finally { loading.value = false }
}

export function startPoll() {
  if (pollTimer.value) return
  pollTimer.value = setInterval(() => {
    if (connectionStatus.value.connected) {
      loadLocation(); loadSpeed(); loadEmergency()
    }
  }, 1000)
}

export function stopPoll() {
  if (pollTimer.value) { clearInterval(pollTimer.value); pollTimer.value = null }
}

export function stopMoveHeartbeat() {
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

export function useRobokit() {
  return {
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
    normalizeNavStatusFromApi,
    NAV_TASK_STATUS,
    isRobotAtStation,
    waitForNavigationTaskCompleted,
    waitForNavigationTaskActiveThenCompleted,
    mergeForkNumericFromPickDropLoad,
    monitorPickLegForDiOrArrival,
    FORK_NUMERIC_KEYS,
    mergeForkNumericFromSeg,
    applyPlanPathForkDefaultsToSegments,
    mergeForkNumericFromForm,
    mergeOneKeyForkNumeric,
    applyPickRecognizeToPathNavBody,
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
  }
}
