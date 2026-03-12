# 机器人端报警码参考

> 来源：`机器人端错误码.docx`。为机器人本机/HMI 显示的报警码，与 API 返回的 `ret_code` 不同。

## 报警格式

- **级别**：Fatal / Error / Warning  
- **示例 JSON**：
```json
{
  "52101": 1712458103,
  "code": 52101,
  "dataTime": "2024-04-07T10:48:23.691+0800",
  "desc": "laser data invalid",
  "describe": "laser data invalid",
  "method": "",
  "reason": "",
  "times": 1,
  "timestamp": 1712458103
}
```

| 字段 | 类型 | 描述 |
|------|------|------|
| code | number | 报警码编号 |
| desc / describe | string | 报警描述 |
| method | string | 报警处理方法 |
| reason | string | 报警原因 |
| times | number | 报警次数 |
| dataTime / timestamp | string/number | 报警发生时间 |

---

## 5xxxx 报警码一览（按段）

### 50xxx 内部/地图/加载

| 报警码 | 报警内容 | 含义 | 处理办法 |
|--------|----------|------|----------|
| 50000 | cannot load plugin:xxx internal error | 内部插件加载错误 | 重新获取更新包/安装包；联系售后 |
| 50001 | resource exhaustion | 机器人内部资源耗尽 | 联系售后 |
| 50002 | lua error | 内部 lua 调用出错 | 重新获取更新包；联系售后 |
| 50101 | map load error | 地图加载错误 | 使用 Roboshop 重新编辑推送地图 |
| 50102 | map is too large | 地图面积过大 | 确保小于 200000㎡ |
| 50103 | map is empty | 地图数据为空 | 使用 Roboshop 重新编辑推送地图 |
| 50104 | map meta error | 地图元数据错误 | 使用 Roboshop 重新编辑上传地图 |
| 50105 | map resolution is illegal | 地图分辨率非法 | Roboshop 打开保存后重新上传 |
| 50106 | map format invalid | 地图格式非法 | Roboshop 打开保存后重新上传 |
| 50200/50201/50202 | mobilerobots 相关 | 加载/初始化/注册错误 | 更新包或安装包问题；确认底盘/模型 |
| 50203 | unsupported robot motion model | 不支持的机器人运动模型 | Roboshop 确认模型并重新上传 |
| 50204 | can not find mobilerobots | 找不到相应运动模型 | 确认底盘配置；更新包 |
| 50301 | dsp firmware model can not get | 固件未获取到底层模型 | 底板未连接/断连，尝试重启 |
| 50304 | firmware version too low | 固件版本过低 | 升级固件 |
| 50305 | firmware model unreachable | 固件获取模型失败 | 重新拉取模型；检查网络 |
| 50401 | battery too low and shutdown | 电量过低自动关机 | 及时充电；修改电池 error 阈值 |
| 50402 | temperature of battery is too high | 电池温度过高 | 联系电池供应商；修改温度阈值 |

### 52xxx 模式/任务/机构/传感器

| 报警码 | 报警内容 | 含义 | 处理办法 |
|--------|----------|------|----------|
| 52000 | mode is not activated | 高级运动模型未激活 | 激活后消除；或确认模型 chassis 与下发指令 |
| 52001 | Failed to initialize mobilerobots / robot model uninitialized | 机器人初始化失败 | 激活；确认 chassis 类型；检查安装包 |
| 52002 | src800 activation has problem | 控制器激活问题 | 联系售后 |
| 52003 | steerOffsetFile's path doesn't exist | 标定文件不存在 | 重新标定 |
| 52004 | tasklist name is illegal or tasklist file not exists | 任务链不合法或不存在 | 检查任务链命名和路径 |
| 52005 | Task timeout error! | 任务执行超时 | 延长任务执行超时时间 |
| 52007 | Open/set/save {1} error | 文件打开失败 | 检查文件存在及格式，清除异常后重新上传 |
| 52010 | robot model uninitialized | 机器人模型未初始化 | 报错后稍等(30s)再观察；检查底板通信 |
| 52015 | stations/points with the same id number in the map | 地图站点中有相同 id | Roboshop 检查地图，上传正确地图 |
| 52019 | Detect less than 3 reflectors | 检测到少于三个反光板 | 保证反光板数量及覆盖 |
| 52030 | roller error | Modbus 辊筒错误 | 急停/新指令清除；检查上料下料超时等 |
| 52031 | roller or jack or hook disconnected | 外设连接断开 | 检查模型外设配置、供电、接线 |
| 52032 | roller operation error | 辊筒操作错误 | 下发正确操作指令(RollerLoad/RollerUnload 等) |
| 52034 | ModbusJack/ModbusTractor/jack error | Modbus 顶升/牵引错误 | 查 Modbus 手册；联系售后 |
| 52039 | hook error | 牵引错误 | 发送合理牵引指令；急停恢复 |
| 52044 | GoodsId isn't same | 货物 id 与检测不匹配 | 按实际货物 id 下发任务 |
| 52050 | arm disconnected | 机械手连接错误 | 检查机械手 Modbus TCP |
| 52051 | Arm GraspLoad/GraspUnload/Reset 相关 | 机械手内部错误 | 检查寄存器、操作、Modbus |
| 52094 | laser lost laser data | 雷达数据丢失 | 检查雷达配置、硬件、网络 |
| 52096 | internal laser error | 激光内部错误 | 根据激光说明书或联系售后 |
| 52097 | please restart laser, get internal Error with Nanosick | Nanosick 内部错误 | 重启激光 |
| 52098 | cannot connect sick nano laser with same port | 两个 sick nano 配置了相同端口 | 激光上位机将两激光端口设成不同 |
| 52099 | laser config param error/wrong | sick 激光配置出错 | 用 sopas 恢复原始激光输出范围 |
| 52100 | can't connect with laser | 激光通讯连接不上 | 配置激光类型/IP/端口；检查网口与通讯线 |
| 52101 | laser data invalid | 当前帧激光点均为无效点 | 检查 ShadowMinAngle 等滤波参数，改为默认 |
| 52102 | localization module cannot get laser data | 定位插件未收到定位激光数据 | 配置激光；检查通讯线 |
| 52103 | cannot receive laser data from udp | 主控 UDP 收不到激光数据 | 配置激光；检查通讯线 |
| 52106 | odo data lost | 定位插件收不到里程数据 | 检查电机通讯、电机类型、陀螺仪 |
| 52107 | Switch map error in current station point | 切换的地图中不存在对应 SM 点 | 检查发送的 SM 点与地图配置 |
| 52110 | Error in Gyro / imu error | 陀螺仪未收到数据 | 联系售后 |
| 52111 | motor driver connection error | 驱动器连接故障/通信超时 | 检查驱动器、接线、CAN、模型配置 |
| 52112 | ultrasonic error | 超声波雷达故障 | 检查超声接线与模型配置 |
| 52113 | RFID reader error | RFID 读写器故障 | 检查 RFID 接线与配置 |
| 52116 | controller net down | 控制器网络断开 | 检查网络、拖链；联系售后 |
| 52117 | dioboard net down | DIO 连接断开 | 固件重启中，等待 |
| 52118 | seer dio heart beat loss | 底板心跳包丢失 | 网络/固件问题；联系售后 |
| 52119 | low task frequency | 控制器任务频率过低 | 联系售后 |
| 52120 | Don't setDO when movetask unreleased DO | setDO 冲突 | 取消任务或脚本 |
| 52122 | robot fall down | 存在倾覆风险 | 调整位姿倾角；或调高 FallDownAngle |
| 52123 | DSPChassis modbus IO error | Modbus IO 错误 | 检查 Modbus IO 扩展板与模型配置 |
| 52200 | robot is blocked | 机器人被阻挡 | 移开障碍物；检查碰撞 DI、膨胀宽度 |
| 52201 | robot out of path | 机器人在线路外 | 手动导航回线路；或修改 OutPathDist/OutPathError |
| 52202 | charge failed / charge timeout 等 | 充电过程错误 | 检查 chargerspot、充电片、充电桩、识别文件 |
| 52203 | Charge device is not enable! / charge path direction error | 充电机构未配置 | 检查模型 charger 是否启用 |
| 52204 | chargerspot status error | 充电桩状态异常 | 状态 -1 查网络/IP；-2 查充电桩硬件 |
| 52250 | 3D camera disconnected | 3D 相机通讯不上 | 配置相机类型/IP/端口；检查通讯线 |
| 52251 | camera : cannot receive trigger data | 收不到相机数据 | 配置相机；检查线；测试拍照功能 |
| 52253 | cannot connect with locCamera | 二维码相机通讯不上 | 配置相机类型/IP/端口；检查通讯线 |
| 52300 | too low confidence of localization | 定位置信度过低 | 手动控制到变化小处重定位；移除动态障碍 |
| 52301 | Cannot detect tag after some distance | 一段距离看不到二维码 | 调整 WarningDistance；或手动到可见二维码处 |
| 52302 | Cannot navigation before confirming localization | **导航前需要确认定位** | 通过 Roboshop 或 API 确认定位后报错消失 |
| 52309 | hook has an error | 牵引机构错误 | 检查 clampReachDI/releaseReachDI、Hook 类型、释放超时 |
| 52313 | slip.vx.t/vx.v / slip.vw... | 机器人打滑 | 检查地面污渍 |
| 52400 | battery connect error during charging | 充电过程中电池报警 | 先处理 54001 等电池报警 |
| 52500 | disconnect from dispatching system / RoboRoute | 与调度系统连接断开 | 检查网络；重试释放/抢占控制权 |
| 52501 | button timeout | 按钮超时 | - |
| 52502 | Dispatching system / RoboRoute command error | 调度系统指令错误 | 检查调度指令 |
| 52503 | battery is too low to move | 电量过低 | 及时充电；修改模型电池 low 阈值 |
| 52600 | low reach accuracy | 到点精度太低/货架偏离 | 栈板位置与角度；到点 xy/角度误差；标定与定位 |
| 52700 | can not find a feasible path | 找不到可通行路径 | 检查指令与地图线路、前置点、ForbiddenDirectGo |
| 52701 | can not find target id | 找不到目标点 | 检查下发指令与地图是否包含目标点；大小写 |
| 52702 | path plan failed | 路径规划失败 | 障碍物、起点终点、3066 格式、path percentage、超时等 |
| 527022 | path plan failed (子码) | 路径规划失败 | 同 52702：检查 3066 站点是否直连、起点是否在站点、地图线路与障碍物 |
| 52703 | unsupported navigation method | 不支持的导航方式 | 单舵轮不支持自由导航/绕障，改发其他任务 |
| 52705 | motion planning failed | 运动规划失败 | 半径、随动绕行、无定位、识别充电顺序等 |
| 52706 | can not find magstripe | 找不到磁条 | 检查磁条铺设；Roboshop 手动控制到磁条上 |
| 52708 | destination has obstacles | 终点处有障碍物 | 检查终点处点、禁行线、禁行区、障碍物 |
| 52713 | DO or DI area overlap | DO/DI 区域重叠 | 检查地图 DIArea/DOArea |
| 52715 | current pos has obstacles | 当前位置有障碍物 | 检查当前位点、禁行线、禁行区、障碍物 |
| 52716 | charger hardware problem | 充电设备硬件问题 | 检查充电桩状态 |
| 52717 | charger tcp connection problem | 充电 TCP 连接异常 | 检查识别文件 chargerspot ip/port、网段 |
| 52718 | Detect Skid and stop | 打滑紧急停止 | 检查轮子运动 |
| 52719 | The tag pos in map is not right | 二维码在地图中位置不对 | 检查二维码位置、重复张贴、定位 |
| 52800 | jack or fork config error / gowithfork failed | 顶升/货叉电机配置错误 | 检查 jack/fork 机构中 Linear Motor 配置 |
| **52801** | **module or motor control error** | **任务指令/机构配置错误** | **见 [API_ERROR_CODES.md#52801](API_ERROR_CODES.md#52801module-or-motor-control-error)** |
| 52802 | upLimit or downLimit error | 上下限位报错 | 检查模型与上下限位 DI |
| 52803 | AGV cannot support rotate | 不支持自旋转 | 确认模型与硬件；重绘路径或关闭 CheckSelfRotateError |
| 52804 | BinTask not in | 库位不包含下发任务 | 重新下发任务 |
| 52805 | pgv adjust reaches max times | 二次调整达到最大次数 | 检查 PGV 标定或调整最大次数 |
| 52806 | Charger error | 充电器错误 | 将充电器设为自动控制模式 |
| 52900 | third-party error | 第三方错误 | API 4800 设置；4801 清除 |
| 52952 | jack, rec, pgv adjust config file error | 顶升/识别/PGV 调整配置错误 | PGV 参数、blinkDO、Recfile、Modbus jack |
| 52954 | motor calibrate timeout | 电机标零超时 | 检查零位开关、限位、驱动器使能 |
| 52955 | src can not switch mode while moving | 移动时不能切换模式 | 静止时再切换 |
| 53000 | 脚本内自定义 | 脚本自定义错误 | script_args error / no script name 等 |
| 53002 | Script model not init | 脚本模型未初始化 | 检查脚本模型 |
| 53003 | unknow error | 未知错误(脚本) | 检查脚本逻辑 |

### 54xxx 硬件/电池/传感器/警告

| 报警码 | 报警内容 | 含义 | 处理办法 |
|--------|----------|------|----------|
| 54001 | battery error | 电池通讯出错 | 检查电池、接线、模型配置 |
| 54004 | controller emergency stop | 控制器急停触发 | 检查急停按钮接线 |
| 54013 | driver emergency stop | 驱动器失能 | 排查使能接线、驱动器报错、动力线 |
| 54018 | reflectors in map not enough | 反光板数量太少 | 添加反光板后重新扫图 |
| 54019 | Detect less than 3 reflectors | 检测到少于三个反光板 | 保证反光板数量 |
| 54020 | reflectors match failed | 反光板匹配不正确 | 重定位使反光板对应正确 |
| 54023 | abnormal sonic data | 超声数据异常 | 排查超声配置与电气 |
| 54025 | which driver emergency stop | 电机去使能 | 拔起急停或检查使能接线 |
| 54027 | no jack motor in model file | 收到顶升指令但未配置 byDO 顶升 | 检查模型 jack 机构 |
| 54028 | checkDi is false / DI status is wrong | 对位 DI 未触发 | 检查对位 DI、货物、模型 counterPointDI/contactDi |
| 54208 | The robot is charging... | 机器人充电中 | 等待脱离充电桩 |
| 54211 | low battery | 电量低 | 充电；修改电池报警阈值 |
| 54231 | Caution: robot is blocked / outside path | 注意被阻挡/在线路外 | 检查障碍物、传感器、停障参数 |
| 54232 | Ignoring Task caused by DISensor | 因 DI 忽略任务 | 检查 DISensor 类型 ignoreTask |
| 52302 | Cannot navigation before confirming localization | 导航前需确认定位 | 确认定位后报错消失 |

### 55xxx 调度/授权/功能

| 报警码 | 报警内容 | 含义 | 处理办法 |
|--------|----------|------|----------|
| 55001 | The robot is in the dispatching state... | 小车在调度模式 | 获取控制权后再控制 |
| 55502 | rbk_pallet is not activated | 栈板识别未激活 | 检查任务与 rbk_pallet 授权 |
| 55503 | rbk_pgv_loc is not activated | PGV 二次定位未激活 | 检查任务与 rbk_pgv_loc 授权 |
| 55504 | rbk_tag_nav is not activated | 二维码定位未激活 | 检查区域与 rbk_tag_nav 授权 |
| 55506 | rbk_spin is not activated | 随动未激活 | 检查任务与 rbk_spin 授权 |
| 55507 | rbk_reflector is not activated | 反光板定位未激活 | 检查地图与 rbk_reflector 授权 |
| 55511 | rbk_script is not activated | 脚本未激活 | 检查任务与 rbk_script 授权 |

---

## 与 API 错误码的区别

- **API 错误码**（如 40012、40020、52801）：机器人**响应**中的 `ret_code`，在调用 API 时返回。  
- **机器人端报警码**（本文档）：机器**本机/HMI** 上显示的报警，格式见上文，包含 code、desc、method、reason 等。

52801 在两端都会出现：API 返回 52801 时，机器人屏幕通常也会显示对应子提示（如 parse error、Action Over Time、label not in the map 等），具体排查见 [API_ERROR_CODES.md#52801](API_ERROR_CODES.md#52801module-or-motor-control-error)。

完整列表与更新以 `机器人端错误码.docx` 为准。
