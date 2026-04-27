package com.seer.sdk.demo;

import com.seer.sdk.rbk.RbkClient;
import com.seer.sdk.rbk.RbkResult;
import com.seer.sdk.rbk.RbkResultKind;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.Scanner;

public class LiftGoodsDemo {

    public static void main(String[] args) {
        // 0. 配置参数
        String robotIp = "172.16.11.211";

        // 创建 Scanner 对象，用于读取 System.in (控制台输入)
        Scanner scanner = new Scanner(System.in);

        // 导航起点和终点
//        String sourcePoint = "PP86";
//        String targetPoint = "LM0";

        // 提示用户输入起点
        System.out.print("请输入取货起点 (例如 AP0): ");
        // 读取用户输入的字符串
        String sourcePoint = scanner.nextLine();

        // 提示用户输入终点
//        System.out.print("请输入送货终点 (例如 AP1): ");
        // 读取用户输入的字符串
//        String targetPoint = scanner.nextLine();

        // 提示用户输入货叉目标高度
        System.out.println("请输入货叉目标高度 (例如 1.0): ");
        // 读取用户输入的字符串
        double targetHeight = Double.parseDouble(scanner.nextLine());

        // 货叉目标高度
//        double targetHeight = 1.0;

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
            // 2. 路径导航 (API 3051) 并获取 Task ID
            // ---------------------------------------------------------
            System.out.println("正在规划路径: 从当前位置 到 " + sourcePoint + "...");

            // 直接构建请求对象，不需要 move_task_list 数组
            JSONObject navReqJson = new JSONObject();

            // 设置路径参数
            navReqJson.put("id", sourcePoint);           // 目标点
            navReqJson.put("source_id", "SELF_POSITION"); // 固定起点为当前位置

            // --- 修改点：配置运动参数 ---
            // 注意：API 3051 的参数直接放在根对象下
            // task.put("method", "backward");        // 如果需要倒走，取消注释
            // task.put("max_speed", 0.6);           // 如果需要限速，取消注释

            // 生成任务 ID
            String currentTaskId = "TASK_" + System.currentTimeMillis();
            navReqJson.put("task_id", currentTaskId);

            String navReqStr = navReqJson.toString();
            System.out.println("发送导航请求: " + navReqStr);

            // 使用 API 3051
            RbkResult navResult = rbkClient.request(3051, navReqStr, 5000);

            if (!RbkResultKind.Ok.equals(navResult.getKind())) {
                System.err.println("导航指令发送失败: " + navResult.getErrMsg());
                return;
            }
            System.out.println("导航指令发送成功，任务 ID: " + currentTaskId);

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




        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            // ---------------------------------------------------------
            // 6. 释放连接
            // ---------------------------------------------------------
            rbkClient.dispose();
            System.out.println("连接已释放。");
        }
    }

    // 辅助方法：根据状态码返回描述
    private static String getStatusDesc(int status) {
        switch (status) {
            case 0: return "StatusNone";
            case 1: return "Waiting";
            case 2: return "Running";
            case 3: return "Suspended";
            case 4: return "Completed";
            case 5: return "Failed";
            case 6: return "Canceled";
            case 7: return "OverTime";
            case 404: return "NotFound";
            default: return "Unknown";
        }
    }
}

