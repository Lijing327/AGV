package com.seer.sdk.demo;

import com.seer.sdk.rbk.RbkClient;
import com.seer.sdk.rbk.RbkResult;
import com.seer.sdk.rbk.RbkResultKind;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.Scanner;

public class DEMO {

    public static void main(String[] args) {
        // 0. 配置参数
        String robotIp = "172.16.11.211";

        // 创建 Scanner 对象，用于读取 System.in (控制台输入)
        Scanner scanner = new Scanner(System.in);

        // 提示用户输入目标点
        System.out.print("请输入导航目标点 (例如 AP0): ");
        String targetPoint = scanner.nextLine();

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
            // 路径导航 (API 3051) - 倒走模式
            // ---------------------------------------------------------

            System.out.println("正在规划路径: 从当前位置 到 " + targetPoint + " (倒走模式)...");

            // 构建请求对象
            JSONObject navReqJson = new JSONObject();

            // 设置路径参数
            navReqJson.put("id", targetPoint);            // 目标点：用户输入
            navReqJson.put("source_id", "SELF_POSITION"); // 起点：当前位置

            // 添加运动参数：倒走模式
//            navReqJson.put("method", "backward");
//            navReqJson.put("max_speed", 0.6);
//            navReqJson.put("max_acc", 0.5);
            navReqJson.put("operation","ForkLoad");
            navReqJson.put("start_height", 0.14);
            navReqJson.put("end_height", 0.25);
            navReqJson.put("recognize", true);
            navReqJson.put("recfile", "plt/p0001.plt");
//            navReqJson.put("recfile", "pallet/p0001.pallet");


            // 生成任务 ID
            String currentTaskId = "TASK_" + System.currentTimeMillis();
            navReqJson.put("task_id", currentTaskId);

            String navReqStr = navReqJson.toString();
            System.out.println("发送导航请求: " + navReqStr);

            // 使用 API 3051 发送请求
            RbkResult navResult = rbkClient.request(3051, navReqStr, 5000);

            if (!RbkResultKind.Ok.equals(navResult.getKind())) {
                System.err.println("导航指令发送失败: " + navResult.getErrMsg());
                return;
            }
            System.out.println("导航指令发送成功，任务 ID: " + currentTaskId);



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
}
