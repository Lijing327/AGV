package com.seer.sdk.demo;

import com.seer.sdk.rbk.RbkClient;
import com.seer.sdk.rbk.RbkResult;
import com.seer.sdk.rbk.RbkResultKind;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.Scanner;

public class TransportGoodsDemo {

    public static void main(String[] args) {
        // 0. 配置参数
        String robotIp = "172.16.11.211";

        // 创建 Scanner 对象，用于读取 System.in (控制台输入)
        Scanner scanner = new Scanner(System.in);

        // 提示用户输入取货点
        System.out.print("请输入取货点 (例如 AP0): ");
        String target1Point = scanner.nextLine();

        // 提示用户输入送货点
        System.out.print("请输入送货点 (例如 AP1): ");
        String target2Point = scanner.nextLine();

        // 提示用户输入货叉目标高度
        System.out.println("请输入货叉目标高度 (例如 1.0,默认为 0.25): ");
        // 读取用户输入的字符串
        String inputStr = scanner.nextLine();
        // 判断输入是否为空，如果为空则使用默认值 0.25，否则进行解析
        double targetHeight = inputStr.trim().isEmpty() ? 0.25 : Double.parseDouble(inputStr);


        RbkClient rbkClient = new RbkClient(robotIp);

        try {
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
            // 2. 第一次路径导航 (API 3051) -> 去取货点
            // ---------------------------------------------------------
            System.out.println("正在规划路径(1): 从当前位置 到 " + target1Point + "...");

            JSONObject navReqJson1 = new JSONObject();
            navReqJson1.put("id", target1Point);           // 目标点：取货点
            navReqJson1.put("source_id", "SELF_POSITION"); // 起点：当前位置

            // 生成任务 ID
            String currentTaskId1 = "TASK_" + System.currentTimeMillis();
            navReqJson1.put("task_id", currentTaskId1);

            // 货叉加载货物，会将叉车状态变成载货中
//            navReqJson1.put("operation", "ForkLoad");

            String navReqStr1 = navReqJson1.toString();
            System.out.println("发送导航请求(1): " + navReqStr1);

            // 使用 API 3051
            RbkResult navResult1 = rbkClient.request(3051, navReqStr1, 5000);

            if (!RbkResultKind.Ok.equals(navResult1.getKind())) {
                System.err.println("导航指令(1)发送失败: " + navResult1.getErrMsg());
                return;
            }
            System.out.println("导航指令(1)发送成功，任务 ID: " + currentTaskId1);


            // ---------------------------------------------------------
            // 3. 轮询 I/O 状态 (API 1013)
            // ---------------------------------------------------------
            System.out.println("开始轮询 I/O 状态，等待 ID=1 或 ID=9 为高电平...");

            boolean isConditionMet = false; // 标记是否满足停止条件
//            long startTime = System.currentTimeMillis();
//            long timeoutMillis = 60000; // 超时时间 60秒

            while (!isConditionMet) {
                // 检查超时
//                if (System.currentTimeMillis() - startTime > timeoutMillis) {
//                    System.err.println("错误：等待 I/O 信号超时！");
//                    return;
//                }

                // 构建查询请求 JSON (API 1013 通常不需要参数，或者为空对象)
                JSONObject queryReqJson = new JSONObject();

                // 发送查询请求 (API 1013)
                // 注意：这里假设 1013 是查询 I/O 的接口 ID
                RbkResult queryResult = rbkClient.request(1013, queryReqJson.toString(), 1000);

                if (RbkResultKind.Ok.equals(queryResult.getKind())) {
                    try {
                        String rawResponse = queryResult.getResStr();
                        // System.out.println("收到原始 I/O 响应: " + rawResponse); // 调试时可取消注释

                        JSONObject resJson = new JSONObject(rawResponse);

                        // 检查是否存在 DI 字段
                        if (!resJson.has("DI")) {
                            System.err.println("响应中未找到 'DI' 字段。完整响应: " + rawResponse);
                            Thread.sleep(1000);
                            continue; // 继续下一次循环
                        }

                        // 获取 DI 数组
                        JSONArray diList = resJson.getJSONArray("DI");
                        boolean foundSignal = false;

                        if (diList.length() > 0) {
                            // 遍历 DI 数组查找 id=1 或 id=9 且 status=true 的项
                            for (int i = 0; i < diList.length(); i++) {
                                JSONObject diObj = diList.getJSONObject(i);
                                int id = diObj.getInt("id");
                                boolean status = diObj.getBoolean("status");
                                boolean valid = diObj.optBoolean("valid", true); // 默认为 true

                                // 检查 ID 是否匹配，状态是否为高电平，且 DI 是否启用
                                if ((id == 1 || id == 9) && status && valid) {
                                    System.out.println("检测到触发信号: ID=" + id + ", Status=" + status);
                                    foundSignal = true;
                                    break; // 找到一个即可停止
                                }
                            }
                        }

                        if (foundSignal) {
                            System.out.println("满足停止条件，当前任务停止，准备执行下一个任务。");
                            isConditionMet = true; // 跳出 while 循环
                        } else {
                            // 未满足条件，继续等待
                            // System.out.println("当前未检测到触发信号 (ID=1/9 High)，继续轮询...");
                            Thread.sleep(500); // 休眠 500ms 避免频繁请求
                        }

                    } catch (Exception e) {
                        System.err.println("解析 I/O 状态 JSON 失败: " + e.getMessage());
                        e.printStackTrace(); // 打印堆栈以便调试
                    }
                } else {
                    System.err.println("查询 I/O 状态请求失败: " + queryResult.getErrMsg());
                    Thread.sleep(1000); // 请求失败稍作等待再试
                }
            }

            // ---------------------------------------------------------
            // 循环结束，说明检测到信号或超时（超时在循环内return了）
            // 此处可以继续执行后续逻辑，例如下发下一个任务
            // ---------------------------------------------------------
            System.out.println("I/O 监测结束，继续执行后续流程...");


            // ---------------------------------------------------------
            // 4. 控制货叉高度 (API 6040)
            // ---------------------------------------------------------
            System.out.println("正在发送货叉高度控制指令，目标高度: " + targetHeight + "米...");

            JSONObject forkReqJson = new JSONObject();
            forkReqJson.put("height", targetHeight);
            String forkReqStr = forkReqJson.toString();

            RbkResult forkResult = rbkClient.request(6040, forkReqStr, 10000);

            // ---------------------------------------------------------
            // 5. 处理货叉响应结果
            // ---------------------------------------------------------
            if (RbkResultKind.Ok.equals(forkResult.getKind())) {
                String resStr = forkResult.getResStr();
                JSONObject resJson = new JSONObject(resStr);
                int retCode = resJson.optInt("ret_code", -1);

                if (retCode == 0) {
                    System.out.println("货叉指令执行成功！正在移动到 " + targetHeight + " 米。");
                } else {
                    String errMsg = resJson.optString("err_msg", "未知错误");
                    System.err.println("货叉指令执行失败，错误码: " + retCode + ", 错误信息: " + errMsg);
                }
            } else {
                System.err.println("SDK 请求失败: " + forkResult.getErrMsg());
            }

            // ---------------------------------------------------------
            // 6 等待第一个任务完成 (使用 API 1020)
            // ---------------------------------------------------------
            System.out.println("等待到达取货点...");
            waitForTaskCompletion(rbkClient);
            System.out.println("已到达取货点，准备执行下一步。");


            // ---------------------------------------------------------
            // 7. 第二次路径导航 (API 3051) -> 去送货点
            // ---------------------------------------------------------
            System.out.println("正在规划路径(2): 从当前位置 到 " + target2Point + "...");

            JSONObject navReqJson2 = new JSONObject();
            navReqJson2.put("id", target2Point);           // 目标点：送货点
            navReqJson2.put("source_id", "SELF_POSITION"); // 起点：当前位置

            // 生成任务 ID
            String currentTaskId2 = "TASK_" + System.currentTimeMillis();
            navReqJson2.put("task_id", currentTaskId2);
            // 货叉卸载货物，会将叉车的状态变成非载货中
//            navReqJson2.put("operation", "ForkUnload");

            String navReqStr2 = navReqJson2.toString();
            System.out.println("发送导航请求(2): " + navReqStr2);

            // 使用 API 3051
            RbkResult navResult2 = rbkClient.request(3051, navReqStr2, 5000);

            if (!RbkResultKind.Ok.equals(navResult2.getKind())) {
                System.err.println("导航指令(2)发送失败: " + navResult2.getErrMsg());
                return;
            }
            System.out.println("导航指令(2)发送成功，任务 ID: " + currentTaskId2);


            // ---------------------------------------------------------
            // 8 等待第二个任务完成 (可选)
            // ---------------------------------------------------------
            System.out.println("等待到达送货点...");
            waitForTaskCompletion(rbkClient);
            System.out.println("已到达送货点，任务结束。");

            // ---------------------------------------------------------
            // 9. 控制货叉高度 (API 6040) - 第二次
            // ---------------------------------------------------------
            double fixedHeight = 0.14;
            System.out.println("正在发送货叉高度控制指令，目标高度: " + fixedHeight + "米...");

            JSONObject forkReqJson2 = new JSONObject(); // 使用 forkReqJson2
            forkReqJson2.put("height", fixedHeight);
            String forkReqStr2 = forkReqJson2.toString();

            RbkResult forkResult2 = rbkClient.request(6040, forkReqStr2, 10000); // 使用 forkResult2

            // ---------------------------------------------------------
            // 10. 处理货叉响应结果
            // ---------------------------------------------------------
            // 修正：这里必须判断 forkResult2，而不是 forkResult
            if (RbkResultKind.Ok.equals(forkResult2.getKind())) {
                String resStr = forkResult2.getResStr();
                JSONObject resJson = new JSONObject(resStr);
                int retCode = resJson.optInt("ret_code", -1);

                if (retCode == 0) {
                    System.out.println("货叉指令执行成功！正在移动到 " + fixedHeight + " 米。");
                } else {
                    String errMsg = resJson.optString("err_msg", "未知错误");
                    System.err.println("货叉指令执行失败，错误码: " + retCode + ", 错误信息: " + errMsg);
                }
            } else {
                System.err.println("SDK 请求失败: " + forkResult2.getErrMsg());
            }



        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            // ---------------------------------------------------------
            // 4. 释放连接
            // ---------------------------------------------------------
            rbkClient.dispose();
            System.out.println("连接已释放。");
        }
    }

    /**
     * 辅助方法：轮询等待任务完成
     * 使用 API 1020 查询导航状态
     * 返回字段: {"task_status": 4} 表示完成
     */
    private static void waitForTaskCompletion(RbkClient client) throws InterruptedException {
        // 超时时间设置，例如 5分钟 (300000ms)
        long timeoutMillis = 300000;
        long startTime = System.currentTimeMillis();
        boolean isFinished = false;

        while (!isFinished) {
            // 检查超时
            if (System.currentTimeMillis() - startTime > timeoutMillis) {
                System.err.println("错误：等待导航任务超时！");
                return;
            }

            try {
                // 构建查询请求 (API 1020)
                JSONObject queryReq = new JSONObject();
                queryReq.put("simple", true); // 只返回简单数据

                // 发送查询
                RbkResult result = client.request(1020, queryReq.toString(), 1000);

                if (RbkResultKind.Ok.equals(result.getKind())) {
                    String rawResponse = result.getResStr();
                    // 解析 JSON
                    JSONObject resJson = new JSONObject(rawResponse);

                    // 获取 task_status 字段
                    if (resJson.has("task_status")) {
                        int status = resJson.getInt("task_status");

                        // 状态码 4 代表 Completed (完成)
                        if (status == 4) {
                            System.out.println("导航任务已完成 (Status: 4)。");
                            isFinished = true;
                        } else if (status >= 5) { // Failed, Canceled, OverTime 等
                            System.err.println("导航任务异常结束，状态码: " + status);
                            return; // 任务失败，停止等待
                        } else {
                            // 任务仍在进行中 (Waiting, Running 等)，继续轮询
                            // System.out.println("当前导航状态: " + status); // 调试用
                            Thread.sleep(500); // 休眠 0.5 秒
                        }
                    } else {
                        System.err.println("响应中未找到 'task_status' 字段。");
                        Thread.sleep(1000);
                    }
                } else {
                    System.err.println("查询导航状态请求失败: " + result.getErrMsg());
                    Thread.sleep(1000);
                }
            } catch (Exception e) {
                System.err.println("解析状态 JSON 失败: " + e.getMessage());
                e.printStackTrace();
                Thread.sleep(1000);
            }
        }
    }
}
