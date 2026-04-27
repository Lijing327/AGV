package com.seer.sdk.demo;

import com.seer.sdk.rbk.RbkClient;
import com.seer.sdk.rbk.RbkResult;
import com.seer.sdk.rbk.RbkResultKind;
import org.json.JSONObject;

public class DIControlDemo {

    public static void main(String[] args) {
        // 0. 配置参数
        String robotIp = "172.16.11.211";

        // 要配置的 DI ID 列表
        int[] diIds = {1, 9};

        RbkClient rbkClient = new RbkClient(robotIp);

        try {
            // ---------------------------------------------------------
            // 1. 抢占控制权 (API 4005)
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
            // 2. 配置 DI 状态 (API 4140)
            // ---------------------------------------------------------
            for (int id : diIds) {
                System.out.println("正在配置 DI ID: " + id + " 启用...");

                // 构建请求 JSON: {"id": 1, "valid": true}
                JSONObject diReqJson = new JSONObject();
                diReqJson.put("id", id);
                diReqJson.put("valid", true);
                String diReqStr = diReqJson.toString();

                // 发送配置请求
                RbkResult diResult = rbkClient.request(4140, diReqStr, 5000);

                // 处理响应结果
                if (RbkResultKind.Ok.equals(diResult.getKind())) {
                    System.out.println("DI ID " + id + " 配置请求发送成功。");

                    // 可选：解析返回值确认是否真的配置成功
                    try {
                        JSONObject resJson = new JSONObject(diResult.getResStr());
                        int retCode = resJson.optInt("ret_code", -1);
                        if (retCode == 0) {
                            System.out.println("DI ID " + id + " 启用成功。");
                        } else {
                            String errMsg = resJson.optString("err_msg", "未知错误");
                            System.err.println("DI ID " + id + " 配置失败 (业务层面): " + errMsg);
                        }
                    } catch (Exception e) {
                        System.err.println("解析 DI 响应失败: " + e.getMessage());
                    }

                } else {
                    System.err.println("DI ID " + id + " 配置请求发送失败 (SDK层面): " + diResult.getErrMsg());
                }
            }

        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            // ---------------------------------------------------------
            // 3. 释放连接
            // ---------------------------------------------------------
            rbkClient.dispose();
            System.out.println("连接已释放。");
        }
    }
}
