package com.seer.sdk.demo;

import com.seer.sdk.rbk.RbkClient;
import com.seer.sdk.rbk.RbkResult;
import com.seer.sdk.rbk.RbkResultKind;
import org.json.JSONObject;
import java.util.Scanner;

public class FangShangload {

    public static void main(String[] args) {
        // 0. 配置参数
        String robotIp = "192.168.0.211";

        // 创建 Scanner 对象，用于读取 System.in (控制台输入)
        Scanner scanner = new Scanner(System.in);

        // 提示用户输入取货点
        System.out.print("请输入取货点 (例如 AP0): ");
        String target1Point = scanner.nextLine();
        target1Point = target1Point.toUpperCase();

        // 提示用户输入货叉目标高度
//        System.out.println("请输入货叉目标高度 (例如 1.0,默认为 0.25): ");
        // 读取用户输入的字符串
//        String inputStr = scanner.nextLine();
        // 判断输入是否为空，如果为空则使用默认值 0.25，否则进行解析
//        double targetHeight = inputStr.trim().isEmpty() ? 0.25 : Double.parseDouble(inputStr);


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
            navReqJson1.put("operation", "ForkLoad");
//            navReqJson1.put("start_height", 0.1);
            navReqJson1.put("end_height", 0.25);
            navReqJson1.put("recognize", true);
            navReqJson1.put("recfile", "plt/p2.plt");
            navReqJson1.put("max_speed", 0.15);
            navReqJson1.put("max_wspeed", 0.2);

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
            // 3 等待第一个任务完成 (使用 API 1020)
            // ---------------------------------------------------------
            System.out.println("等待到达取货点...");
            waitForTaskCompletion(rbkClient);
            System.out.println("已到达取货点，准备执行下一步。");


            // ---------------------------------------------------------
            // 7. 第二次路径导航 (API 3051) -> 去链条机前置点
            // ---------------------------------------------------------
//            System.out.println("正在规划路径(2): 从当前位置 到 " + target2Point + "...");

            JSONObject navReqJson2 = new JSONObject();
            navReqJson2.put("id", "LM2");           // 目标点：送货点
            navReqJson2.put("source_id", "SELF_POSITION"); // 起点：当前位置

            // 生成任务 ID
            String currentTaskId2 = "TASK_" + System.currentTimeMillis();
            navReqJson2.put("task_id", currentTaskId2);
            // 货叉卸载货物，会将叉车的状态变成非载货中
            navReqJson2.put("operation", "ForkHeight");
            navReqJson2.put("max_speed", 0.25);
//            navReqJson2.put("start_height", 0.25);
            navReqJson2.put("end_height", 1.1);
            navReqJson2.put("max_wspeed", 0.2);

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
            // 8 等待第一个任务完成 (使用 API 1020)
            // ---------------------------------------------------------
            System.out.println("等待到达立库前置点...");
            waitForTaskCompletion(rbkClient);
            System.out.println("已到达立库前置点，准备执行下一步。");

            // ---------------------------------------------------------
            // 9. 第三次路径导航 (API 3051) -> 去链条机放货
            // ---------------------------------------------------------
            JSONObject navReqJson3 = new JSONObject();
            navReqJson3.put("id", "AP1");           // 目标点：送货点
            navReqJson3.put("source_id", "SELF_POSITION"); // 起点：当前位置

            // 生成任务 ID
            String currentTaskId3 = "TASK_" + System.currentTimeMillis();
            navReqJson3.put("task_id", currentTaskId3);
            // 货叉卸载货物，会将叉车的状态变成非载货中
            navReqJson3.put("operation", "ForkUnload");
            navReqJson3.put("max_speed", 0.15);
            navReqJson3.put("start_height", 1.1);
            navReqJson3.put("end_height", 0.94);

            String navReqStr3 = navReqJson3.toString();
            System.out.println("发送导航请求(3): " + navReqStr3);

            // 使用 API 3051
            RbkResult navResult3 = rbkClient.request(3051, navReqStr3, 5000);

            if (!RbkResultKind.Ok.equals(navResult3.getKind())) {
                System.err.println("导航指令(3)发送失败: " + navResult3.getErrMsg());
                return;
            }
            System.out.println("导航指令(3)发送成功，任务 ID: " + currentTaskId3);

            // ---------------------------------------------------------
            // 10 等待第一个任务完成 (使用 API 1020)
            // ---------------------------------------------------------
            System.out.println("等待叉车放货...");
            waitForTaskCompletion(rbkClient);
            System.out.println("叉车放货完成，准备执行下一步。");

            // ---------------------------------------------------------
            // 11. 第四次路径导航 (API 3051) -> 回到前置点待命
            // ---------------------------------------------------------
            JSONObject navReqJson4 = new JSONObject();
            navReqJson4.put("id", "LM2");           // 目标点：送货点
            navReqJson4.put("source_id", "SELF_POSITION"); // 起点：当前位置

            // 生成任务 ID
            String currentTaskId4 = "TASK_" + System.currentTimeMillis();
            navReqJson4.put("task_id", currentTaskId4);
            // 货叉卸载货物，会将叉车的状态变成非载货中
            navReqJson4.put("operation", "ForkHeight");
            navReqJson4.put("max_speed", 0.25);
            navReqJson4.put("start_height", 0.94);
            navReqJson4.put("end_height", 0.09);

            String navReqStr4 = navReqJson4.toString();
            System.out.println("发送导航请求(4): " + navReqStr4);

            // 使用 API 3051
            RbkResult navResult4 = rbkClient.request(3051, navReqStr4, 5000);

            if (!RbkResultKind.Ok.equals(navResult4.getKind())) {
                System.err.println("导航指令(4)发送失败: " + navResult4.getErrMsg());
                return;
            }
            System.out.println("导航指令(4)发送成功，任务 ID: " + currentTaskId4);


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
