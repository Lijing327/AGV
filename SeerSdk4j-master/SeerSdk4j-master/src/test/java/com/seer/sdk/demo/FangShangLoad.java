package com.seer.sdk.demo;

import com.seer.sdk.rbk.RbkClient;
import com.seer.sdk.rbk.RbkResult;
import com.seer.sdk.rbk.RbkResultKind;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.Scanner;
import java.util.function.Supplier;


public class FangShangLoad {

    public static void main(String[] args) {
        // 0. 配置参数
        String robotIp = "192.168.25.211";

        // 初始化变量
        RbkClient rbkClient = null;
        Scanner scanner = null;
        String activeTaskId = null;

        try {
            // 创建 Scanner 对象
            scanner = new Scanner(System.in);

            // 创建 RbkClient 对象
            rbkClient = new RbkClient(robotIp);

            // ---------------------------------------------------------
            // 1. 抢占控制权
            // ---------------------------------------------------------
            System.out.println("正在尝试抢占控制权...");
            String loginReq = "{\"nick_name\":\"operator\"}";
            RbkResult loginResult = rbkClient.request(4005, loginReq, 5000);

            if (!RbkResultKind.Ok.equals(loginResult.getKind())) {
                System.err.println("抢占控制权失败: " + loginResult.getErrMsg());
                return;
            }
            System.out.println("抢占控制权成功");

            // ---------------------------------------------------------
            // 2. 获取并验证用户输入的取货点
            // ---------------------------------------------------------
            String target1Point = "";
            boolean isValidStation = false;

            while (!isValidStation) {
                System.out.print("请输入取货点 (例如 AP0): ");
                target1Point = scanner.nextLine();
                target1Point = target1Point.toUpperCase();

                // 验证站点ID是否有效
                isValidStation = validateStationId(rbkClient, target1Point);
                if (!isValidStation) {
                    System.err.println("错误：输入的站点ID '" + target1Point + "' 在当前地图中不存在！请重新输入。");
                }
            }
            System.out.println("站点验证通过，开始执行任务...");

            // ---------------------------------------------------------
            // 3. 第一次路径导航 (API 3051) -> 去取货点
            // ---------------------------------------------------------
            System.out.println("正在规划路径(1): 从当前位置 到 " + target1Point + "...");

            // 生成任务 ID 并记录
            activeTaskId = "TASK_" + System.currentTimeMillis();

            // 使用抽取的方法发送导航请求
            boolean navResult1 = sendNavigationWithRetry(
                    rbkClient,
                    target1Point,
                    "ForkLoad",
                    null, // startHeight 不需要
                    0.25, // endHeight
                    0.15, // maxSpeed
                    0.2,  // maxWspeed
                    true, // recognize
                    "plt/p2.plt", // recfile
                    activeTaskId
            );

            if (!navResult1) {
                System.err.println("导航指令(1)发送失败");
                return;
            }
            System.out.println("导航指令(1)发送成功，任务 ID: " + activeTaskId);

            // ---------------------------------------------------------
            // 4. 等待第一个任务完成 (使用 API 1020)
            // ---------------------------------------------------------
            System.out.println("等待到达取货点...");
            boolean task1Success = waitForTaskCompletion(rbkClient, activeTaskId, 300000);

            // 任务结束（无论成功失败），清空 ID，防止 finally 块误取消
            activeTaskId = null;

            if (!task1Success) {
                System.err.println("任务1执行失败或超时");
                return;
            }
            System.out.println("已到达取货点，准备执行下一步。");

            // ---------------------------------------------------------
            // 5. 第二次路径导航 (API 3051) -> 去链条机前置点
            // ---------------------------------------------------------
            System.out.println("正在规划路径(2): 从当前位置 到 LM2...");

            // 生成任务 ID 并记录
            activeTaskId = "TASK_" + System.currentTimeMillis();

            // 使用抽取的方法发送导航请求
            boolean navResult2 = sendNavigationWithRetry(
                    rbkClient,
                    "LM2",
                    "ForkHeight",
                    null, // startHeight 不需要
                    1.1, // endHeight
                    0.25, // maxSpeed
                    0.2,  // maxWspeed
                    false, // recognize
                    null, // recfile
                    activeTaskId
            );

            if (!navResult2) {
                System.err.println("导航指令(2)发送失败");
                return;
            }
            System.out.println("导航指令(2)发送成功，任务 ID: " + activeTaskId);

            // ---------------------------------------------------------
            // 6. 等待第二个任务完成 (使用 API 1020)
            // ---------------------------------------------------------
            System.out.println("等待到达立库前置点...");
            boolean task2Success = waitForTaskCompletion(rbkClient, activeTaskId, 300000);

            // 任务结束，清空 ID
            activeTaskId = null;

            if (!task2Success) {
                System.err.println("任务2执行失败或超时");
                return;
            }
            System.out.println("已到达立库前置点，准备执行下一步。");

            // ---------------------------------------------------------
            // 7. 第三次路径导航 (API 3051) -> 去链条机放货
            // ---------------------------------------------------------
            System.out.println("正在规划路径(3): 从当前位置 到 AP1...");

            // 生成任务 ID 并记录
            activeTaskId = "TASK_" + System.currentTimeMillis();

            // 使用抽取的方法发送导航请求
            boolean navResult3 = sendNavigationWithRetry(
                    rbkClient,
                    "AP1",
                    "ForkUnload",
                    1.1, // startHeight
                    0.94, // endHeight
                    0.15, // maxSpeed
                    0.2,  // maxWspeed
                    false, // recognize
                    null, // recfile
                    activeTaskId
            );

            if (!navResult3) {
                System.err.println("导航指令(3)发送失败");
                return;
            }
            System.out.println("导航指令(3)发送成功，任务 ID: " + activeTaskId);

            // ---------------------------------------------------------
            // 8. 等待第三个任务完成 (使用 API 1020)
            // ---------------------------------------------------------
            System.out.println("等待叉车放货...");
            boolean task3Success = waitForTaskCompletion(rbkClient, activeTaskId, 300000);

            // 任务结束，清空 ID
            activeTaskId = null;

            if (!task3Success) {
                System.err.println("任务3执行失败或超时");
                return;
            }
            System.out.println("叉车放货完成，准备执行下一步。");

            // ---------------------------------------------------------
            // 9. 第四次路径导航 (API 3051) -> 回到前置点待命
            // ---------------------------------------------------------
            System.out.println("正在规划路径(4): 从当前位置 到 LM2...");

            // 生成任务 ID 并记录
            activeTaskId = "TASK_" + System.currentTimeMillis();

            // 使用抽取的方法发送导航请求
            boolean navResult4 = sendNavigationWithRetry(
                    rbkClient,
                    "LM2",
                    "ForkHeight",
                    0.94, // startHeight
                    0.09, // endHeight
                    0.25, // maxSpeed
                    0.2,  // maxWspeed
                    false, // recognize
                    null, // recfile
                    activeTaskId
            );

            if (!navResult4) {
                System.err.println("导航指令(4)发送失败");
                return;
            }
            System.out.println("导航指令(4)发送成功，任务 ID: " + activeTaskId);

            // ---------------------------------------------------------
            // 10. 等待第四个任务完成 (使用 API 1020)
            // ---------------------------------------------------------
            System.out.println("等待回到前置点...");
            boolean task4Success = waitForTaskCompletion(rbkClient, activeTaskId, 300000);

            // 任务结束，清空 ID
            activeTaskId = null;

            if (!task4Success) {
                System.err.println("任务4执行失败或超时");
                return;
            }
            System.out.println("已回到前置点，所有任务完成。");

        } catch (Exception e) {
            System.err.println("程序运行发生异常: " + e.getMessage());
            e.printStackTrace();
        } finally {
            // ---------------------------------------------------------
            // 11. 清理工作
            // ---------------------------------------------------------

            // 逻辑判断：如果当前有正在执行的任务，先尝试取消
            if (activeTaskId != null) {
                System.err.println("检测到程序异常退出，正在尝试取消当前任务: " + activeTaskId);
                cancelTask(rbkClient, activeTaskId);
                // 等待一小段时间，让取消指令生效
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                }
            }

            // 释放连接 (增加非空判断和 try-catch)
            if (rbkClient != null) {
                try {
                    rbkClient.dispose();
                    System.out.println("连接已释放。");
                } catch (Exception e) {
                    System.err.println("释放连接时发生异常: " + e.getMessage());
                }
            }

            // 关闭 Scanner
            // 注意：关闭 Scanner 会关闭底层的 System.in。
            // 如果此代码后续还需要从控制台读取输入，请移除下面的 close() 调用。
            // 对于独立运行的 Demo 程序，关闭它是良好的习惯。
            if (scanner != null) {
                try {
                    scanner.close();
                } catch (Exception e) {
                    System.err.println("关闭 Scanner 时发生异常: " + e.getMessage());
                }
            }
        }
    }

    /**
     * 验证站点ID是否在当前地图中存在
     *
     * @param client RbkClient 客户端
     * @param stationId 要验证的站点ID
     * @return 如果站点存在返回true，否则返回false
     */
    private static boolean validateStationId(RbkClient client, String stationId) {
        try {
            // 构建查询请求 (API 1301)
            JSONObject queryReq = new JSONObject();

            // 发送查询
            RbkResult result = client.request(1301, queryReq.toString(), 5000);

            if (RbkResultKind.Ok.equals(result.getKind())) {
                String rawResponse = result.getResStr();
                // 解析 JSON
                JSONObject resJson = new JSONObject(rawResponse);

                // 检查返回码
                if (resJson.has("ret_code") && resJson.getInt("ret_code") == 0) {
                    // 获取站点列表
                    if (resJson.has("stations")) {
                        JSONArray stations = resJson.getJSONArray("stations");

                        // 遍历站点列表，查找匹配的站点ID
                        for (int i = 0; i < stations.length(); i++) {
                            JSONObject station = stations.getJSONObject(i);
                            if (station.has("id") && stationId.equals(station.getString("id"))) {
                                System.out.println("找到匹配站点: " + stationId);
                                return true;
                            }
                        }

                        // 遍历完所有站点未找到匹配
                        System.out.println("地图中未找到站点: " + stationId);
                        return false;
                    } else {
                        System.err.println("响应中未找到 'stations' 字段");
                        return false;
                    }
                } else {
                    System.err.println("查询站点信息失败，返回码: " + resJson.optInt("ret_code", -1));
                    return false;
                }
            } else {
                System.err.println("查询站点信息请求失败: " + result.getErrMsg());
                return false;
            }
        } catch (Exception e) {
            System.err.println("验证站点ID时发生异常: " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }

    /**
     * 发送导航请求（带重试机制）
     *
     * @param client RbkClient 客户端
     * @param targetId 目标点ID
     * @param operation 操作类型 (ForkLoad, ForkUnload, ForkHeight 等)
     * @param startHeight 起始高度 (可为 null)
     * @param endHeight 结束高度
     * @param maxSpeed 最大速度
     * @param maxWspeed 最大角速度
     * @param recognize 是否识别
     * @param recfile 识别文件路径 (可为 null)
     * @param taskId 任务ID
     * @return 是否发送成功
     */
    private static boolean sendNavigationWithRetry(
            RbkClient client,
            String targetId,
            String operation,
            Double startHeight,
            double endHeight,
            double maxSpeed,
            double maxWspeed,
            boolean recognize,
            String recfile,
            String taskId) {

        // 构建导航请求
        JSONObject navReqJson = new JSONObject();
        navReqJson.put("id", targetId);
        navReqJson.put("source_id", "SELF_POSITION");
        navReqJson.put("task_id", taskId);
        navReqJson.put("operation", operation);
        navReqJson.put("end_height", endHeight);
        navReqJson.put("max_speed", maxSpeed);
        navReqJson.put("max_wspeed", maxWspeed);

        // 可选参数
        if (startHeight != null) {
            navReqJson.put("start_height", startHeight);
        }

        if (recognize) {
            navReqJson.put("recognize", recognize);
            navReqJson.put("recfile", recfile);
        }

        String navReqStr = navReqJson.toString();
        String operationName = "导航到 " + targetId;

        // 使用重试机制发送导航请求
        return executeWithRetry(
                () -> client.request(3051, navReqStr, 5000),
                3, // 最大重试次数
                500, // 初始延迟500毫秒
                operationName
        );
    }


    /**
     * 辅助方法：轮询等待任务完成
     * 使用 API 1020 查询导航状态
     *
     * @param client RbkClient 客户端
     * @param taskId 要等待的任务ID
     * @param timeoutMillis 超时时间(毫秒)
     * @return 任务是否成功完成
     * @throws InterruptedException
     */
    private static boolean waitForTaskCompletion(RbkClient client, String taskId, long timeoutMillis) throws InterruptedException {
        long startTime = System.currentTimeMillis();
        boolean isFinished = false;
        boolean isSuccess = false;
        int consecutiveTimeouts = 0;
        final int MAX_CONSECUTIVE_TIMEOUTS = 5;

        while (!isFinished) {
            // 检查超时
            if (System.currentTimeMillis() - startTime > timeoutMillis) {
                System.err.println("错误：等待导航任务超时！TaskID: " + taskId);
                cancelTask(client, taskId);
                return false;
            }

            try {
                JSONObject queryReq = new JSONObject();
                queryReq.put("simple", true);
                queryReq.put("task_id", taskId);

                RbkResult result = client.request(1020, queryReq.toString(), 3000);

                if (RbkResultKind.Ok.equals(result.getKind())) {
                    consecutiveTimeouts = 0;
                    String rawResponse = result.getResStr();
                    JSONObject resJson = new JSONObject(rawResponse);

                    if (resJson.has("task_status")) {
                        int status = resJson.getInt("task_status");

                        if (status == 4) {
                            System.out.println("导航任务已完成 (Status: 4)。TaskID: " + taskId);
                            isFinished = true;
                            isSuccess = true;
                        } else if (status >= 5) {
                            System.err.println("导航任务异常结束，状态码: " + status + "，TaskID: " + taskId);
                            isFinished = true;
                            isSuccess = false;
                        } else {
                            Thread.sleep(500);
                        }
                    } else {
                        System.err.println("响应中未找到 'task_status' 字段。TaskID: " + taskId);
                        Thread.sleep(1000);
                    }
                } else {
                    System.err.println("查询导航状态请求失败: " + result.getErrMsg() + "，TaskID: " + taskId);
                    Thread.sleep(1000);
                }
            } catch (Exception e) {
                consecutiveTimeouts++;
                System.err.println("查询导航状态异常 (" + consecutiveTimeouts + "/" + MAX_CONSECUTIVE_TIMEOUTS + "): " + e.getMessage() + "，TaskID: " + taskId);

                if (consecutiveTimeouts >= MAX_CONSECUTIVE_TIMEOUTS) {
                    System.err.println("连续超时次数过多，认为任务失败。TaskID: " + taskId);
                    cancelTask(client, taskId);
                    return false;
                }

                Thread.sleep(2000);
            }
        }

        return isSuccess;
    }

    /**
     * 取消任务
     * 使用 API 3052 取消指定任务
     *
     * @param client RbkClient 客户端
     * @param taskId 要取消的任务ID
     */
    private static void cancelTask(RbkClient client, String taskId) {
        try {
            JSONObject cancelReq = new JSONObject();
            cancelReq.put("task_id", taskId);

            RbkResult result = client.request(3052, cancelReq.toString(), 5000);

            if (RbkResultKind.Ok.equals(result.getKind())) {
                System.out.println("任务取消请求已发送。TaskID: " + taskId);
            } else {
                System.err.println("任务取消请求失败: " + result.getErrMsg() + "，TaskID: " + taskId);
            }
        } catch (Exception e) {
            System.err.println("取消任务时发生异常: " + e.getMessage() + "，TaskID: " + taskId);
            e.printStackTrace();
        }
    }

    /**
     * 通用重试工具方法
     * 使用指数退避策略进行重试
     *
     * @param operation      要执行的操作，返回 RbkResult
     * @param maxRetries     最大重试次数
     * @param initialDelayMs 初始延迟时间（毫秒）
     * @param operationName  操作名称（用于日志打印）
     * @return 操作成功返回 true，否则返回 false
     */
    private static boolean executeWithRetry(Supplier<RbkResult> operation, int maxRetries, long initialDelayMs, String operationName) {
        int retryCount = 0;
        long currentDelay = initialDelayMs;

        while (retryCount <= maxRetries) {
            try {
                RbkResult result = operation.get();

                if (RbkResultKind.Ok.equals(result.getKind())) {
                    if (retryCount > 0) {
                        System.out.println(operationName + " 重试成功 (第 " + retryCount + " 次重试)");
                    }
                    return true;
                } else {
                    System.err.println(operationName + " 失败: " + result.getErrMsg());
                }
            } catch (Exception e) {
                System.err.println(operationName + " 发生异常: " + e.getMessage());
            }

            // 如果这是最后一次尝试，不再等待
            if (retryCount == maxRetries) {
                break;
            }

            retryCount++;
            System.err.println(operationName + " 失败，" + currentDelay + "ms 后进行第 " + retryCount + " 次重试...");

            try {
                Thread.sleep(currentDelay);
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
                System.err.println("重试等待被中断");
                return false;
            }

            // 指数退避：每次延迟时间翻倍，最大不超过 5 秒
            currentDelay = Math.min(currentDelay * 2, 5000);
        }

        System.err.println(operationName + " 达到最大重试次数 (" + maxRetries + ")，操作失败。");
        return false;
    }
}
