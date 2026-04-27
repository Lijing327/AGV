package com.seer.sdk.demo;

import com.seer.sdk.rbk.RbkClient;
import com.seer.sdk.rbk.RbkResult;
import com.seer.sdk.rbk.RbkResultKind;
import org.json.JSONArray;
import org.json.JSONObject;

public class API3066Demo {

    public static void main(String[] args) {
        // 0. 配置参数
        String robotIp = "172.16.11.211";

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
            // 2. 构建多段路径导航请求 (API 3066)
            // ---------------------------------------------------------
            System.out.println("正在构建多段导航任务...");

            JSONObject navReqJson = new JSONObject();
            JSONArray moveTaskList = new JSONArray();

            // --- 任务 1: PP86 -> LM0 (倒走, 0.6m/s) ---
            JSONObject task1 = new JSONObject();
            task1.put("id", "LM0");
            task1.put("source_id", "PP86");
            task1.put("method", "backward");
            task1.put("max_speed", 0.6);
            task1.put("task_id", "TASK_1_" + System.currentTimeMillis());
            moveTaskList.put(task1);

            // --- 任务 2: LM0 -> LM1 (正走, 0.8m/s) ---
            JSONObject task2 = new JSONObject();
            task2.put("id", "LM1");
            task2.put("source_id", "LM0");
            task2.put("method", "forward"); // 正走，或者不填(默认)
            task2.put("max_speed", 0.8);
            task2.put("task_id", "TASK_2_" + System.currentTimeMillis());
            moveTaskList.put(task2);

            // --- 任务 3: LM1 -> LM2 (倒走, 0.5m/s) ---
            JSONObject task3 = new JSONObject();
            task3.put("id", "LM2");
            task3.put("source_id", "LM1");
            task3.put("method", "backward");
            task3.put("max_speed", 0.5);
            task3.put("task_id", "TASK_3_" + System.currentTimeMillis());
            moveTaskList.put(task3);

            // 将列表放入外层 JSON
            navReqJson.put("move_task_list", moveTaskList);

            String navReqStr = navReqJson.toString();
            System.out.println("发送多段导航请求: " + navReqStr);

            // 发送请求
            RbkResult navResult = rbkClient.request(3066, navReqStr, 5000);

            if (!RbkResultKind.Ok.equals(navResult.getKind())) {
                System.err.println("导航指令发送失败: " + navResult.getErrMsg());
                return;
            }
            System.out.println("多段导航指令发送成功。");

            // ---------------------------------------------------------
            // 3. 轮询任务状态 (API 1110)
            // ---------------------------------------------------------
            // 注意：由于我们发送了多个任务，通常我们只需要关注最后一个任务的状态，
            // 或者我们可以轮询整个任务列表的状态。

            // 这里为了演示，我们只追踪最后一个任务 (task3) 的 ID
            String finalTaskId = task3.getString("task_id");

            System.out.println("开始轮询最终任务状态 (ID: " + finalTaskId + ")...");

            boolean isTaskFinished = false;
            long startTime = System.currentTimeMillis();
            long timeoutMillis = 120000; // 增加超时时间，因为任务变多了

            while (!isTaskFinished) {
                if (System.currentTimeMillis() - startTime > timeoutMillis) {
                    System.err.println("错误：等待导航任务超时！");
                    return;
                }

                // 构建查询请求
                JSONObject queryReqJson = new JSONObject();
                JSONArray taskIds = new JSONArray();
                taskIds.put(finalTaskId); // 只查询最后一个任务
                queryReqJson.put("task_ids", taskIds);

                RbkResult queryResult = rbkClient.request(1110, queryReqJson.toString(), 1000);

                if (RbkResultKind.Ok.equals(queryResult.getKind())) {
                    try {
                        JSONObject resJson = new JSONObject(queryResult.getResStr());
                        JSONArray statusList = resJson.getJSONArray("task_status_list");

                        if (statusList.length() > 0) {
                            JSONObject statusObj = statusList.getJSONObject(0);
                            int status = statusObj.getInt("status");

                            System.out.println("当前任务状态: " + getStatusDesc(status));

                            if (status == 4) { // Completed
                                System.out.println("所有导航任务完成！");
                                isTaskFinished = true;
                            } else if (status >= 5) {
                                System.err.println("任务异常结束，状态码: " + status);
                                return;
                            } else {
                                Thread.sleep(500);
                            }
                        }
                    } catch (Exception e) {
                        System.err.println("解析状态 JSON 失败: " + e.getMessage());
                    }
                }
            }

            // ---------------------------------------------------------
            // 4. 后续操作 (如控制货叉)
            // ---------------------------------------------------------
            System.out.println("导航序列结束，准备执行后续操作...");
            // ... 此处可以添加货叉控制代码 ...

        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            rbkClient.dispose();
            System.out.println("连接已释放。");
        }
    }

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
