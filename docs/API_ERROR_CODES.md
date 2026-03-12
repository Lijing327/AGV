# API 错误码参考 (来自 API错误码.docx)

错误码为机器人**响应**中的 `ret_code`，0 表示成功。  
机器人**本机/HMI 显示的报警码**（5xxxx 等）见 [机器人端报警码](ROBOT_ALARM_CODES.md)。

## 常见错误

| 错误码 | 名称 | 说明 |
|-------|------|------|
| 40012 | dispatching | 调度系统控制中，不能执行独立操作，需先抢占控制 |
| 40020 | preempted | 控制权被抢占，不能执行独立操作；抢占控制也可能失败，需等待对方释放 |
| 40101 | locked | 机器人被其他设备锁定（如 172.16.15.75），需在该设备上释放锁定 |
| 40400 | src_require_error | 获取控制权错误 |
| 40401 | src_release_error | 释放控制权错误 |
| 52801 | module_or_motor | 任务指令报错，或机构/模型配置错误（详见下方） |
| 60000 | robot_error_wtype_res | **错误的报文类型**，端口与 API 编号不匹配 |

## 52801：module or motor control error

任务指令报错，或者机构配置错误。**具体原因以机器人屏幕/日志中报错后面的提示为准**。

### 常见子提示与含义

| 提示 | 含义 |
|------|------|
| parse error | 任务指令格式错误 |
| The *** module is not available in the robot model! | 某机构/设备未在模型文件中配置，但下发了相关任务 |
| The Skill name is wrong | 任务指令中技能名错误 |
| No Jack Module | 执行了顶升任务但机器人无顶升机构 |
| init model is null | 机构初始化失败 |
| Action Over Time | 机构执行超时 |
| Fork module's Motors are empty | 货叉机构下电机配置为空 |
| operation name error / no operation!!! / operation should be string!!! | 货叉 operation 配置错误或类型错误 |
| all Motors are empty / All Motors are empty! | 模型文件中没有可控电机 |
| no motor or wrong command / no motor param / motor param is none | 下发电机指令或参数错误 |
| is not in the robot model | 某机构/设备不在模型文件中 |
| pushMotor is empty! | 推正机构下未配置 pushMotor |
| value is missing or wrong! | 下发指令的值类型错误 |
| label: is not in the map | 下发的 label 不在当前地图中 |

### 排查方向

1. **parse error、module is not available、Skill name is wrong、operation 相关、no motor/param、value is wrong、label not in map** → 检查**下发指令**（参数、类型、地图中的站点/标签）。
2. **init model is null** → 检查对应机构在**模型文件**中是否已启用。
3. **all Motors are empty** → 检查**模型文件**中电机 motor 设备配置。
4. **is not in the robot model** → 检查**模型文件**是否包含该机构/设备。
5. **pushMotor is empty!** → 检查模型文件**推正机构**的 pushPositiveMotor 与 mtoor 机构中的电机类型是否合理。
6. **Action Over Time** → 机构执行超时，检查配置的**执行时间**是否合理，以及报错时机构/电机是否已到位。
7. 无法判断时联系售后。

---

## 60000 说明

> 若用户将某类型的报文发错了端口将得到这个响应

- 19204 期望 1xxx
- 19205 期望 2xxx  
- 19206 期望 3xxx
- 19207 期望 4xxx

## 抢占/释放控制权 API (端口 19207)

| 功能 | API 编号 | 必填参数 |
|------|----------|----------|
| 抢占控制权 | 4005 | `nick_name` 控制权抢占者名称 |
| 释放控制权 | 4006 | - |
