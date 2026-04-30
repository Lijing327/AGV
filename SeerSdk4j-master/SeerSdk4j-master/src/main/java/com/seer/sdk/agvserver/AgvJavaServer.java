package com.seer.sdk.agvserver;

import com.seer.sdk.rbk.RbkClient;
import com.seer.sdk.rbk.RbkResult;
import com.seer.sdk.rbk.RbkResultKind;
import com.sun.net.httpserver.Headers;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.ByteArrayOutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;

public class AgvJavaServer {
    private static final int DEFAULT_HTTP_PORT = 8001;
    private static final long DEFAULT_TIMEOUT_MS = 10_000L;

    private static volatile RbkClient rbkClient;
    private static volatile String currentHost = "";
    private static volatile boolean connected = false;
    private static final int NAV_COMPLETED_STATUS = 4;

    public static void main(String[] args) throws IOException {
        int port = DEFAULT_HTTP_PORT;
        if (args.length > 0) {
            try {
                port = Integer.parseInt(args[0]);
            } catch (NumberFormatException ignored) {
                port = DEFAULT_HTTP_PORT;
            }
        }
        HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);
        server.createContext("/", new RouterHandler());
        server.setExecutor(Executors.newFixedThreadPool(8));
        Runtime.getRuntime().addShutdownHook(new Thread(AgvJavaServer::disposeClient));
        server.start();
        System.out.println("AGV Java backend started on http://0.0.0.0:" + port);
    }

    private static class RouterHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            addCorsHeaders(exchange.getResponseHeaders());
            if ("OPTIONS".equalsIgnoreCase(exchange.getRequestMethod())) {
                sendJson(exchange, 200, new JSONObject().put("ok", true));
                return;
            }
            String path = exchange.getRequestURI().getPath();
            String method = exchange.getRequestMethod().toUpperCase();
            try {
                if ("/".equals(path) && "GET".equals(method)) {
                    sendJson(exchange, 200, new JSONObject()
                            .put("message", "AGV Java Backend API")
                            .put("api_prefix", "/api")
                            .put("robokit_prefix", "/api/robokit"));
                    return;
                }
                if ("/api/robokit/connect".equals(path) && "POST".equals(method)) {
                    handleConnect(exchange);
                    return;
                }
                if ("/api/robokit/disconnect".equals(path) && "POST".equals(method)) {
                    handleDisconnect(exchange);
                    return;
                }
                if ("/api/robokit/status".equals(path) && "GET".equals(method)) {
                    sendJson(exchange, 200, new JSONObject()
                            .put("connected", connected)
                            .put("host", currentHost));
                    return;
                }
                if ("/api/robokit/call".equals(path) && "POST".equals(method)) {
                    handleGenericCall(exchange);
                    return;
                }

                // 常用状态接口
                if ("/api/robokit/robot/location".equals(path) && "GET".equals(method)) {
                    handleSimpleApi(exchange, 1004, null);
                    return;
                }
                if ("/api/robokit/robot/speed".equals(path) && "GET".equals(method)) {
                    handleSimpleApi(exchange, 1005, null);
                    return;
                }
                if ("/api/robokit/robot/battery".equals(path) && "GET".equals(method)) {
                    JSONObject params = parseQuerySimple(exchange.getRequestURI().getQuery());
                    handleSimpleApi(exchange, 1007, params);
                    return;
                }
                if ("/api/robokit/robot/emergency".equals(path) && "GET".equals(method)) {
                    handleSimpleApi(exchange, 1012, null);
                    return;
                }
                if ("/api/robokit/robot/io".equals(path) && "GET".equals(method)) {
                    handleSimpleApi(exchange, 1013, null);
                    return;
                }

                // 常用控制与导航接口
                if ("/api/robokit/control/move".equals(path) && "POST".equals(method)) {
                    handleControlMove(exchange);
                    return;
                }
                if ("/api/robokit/control/stop".equals(path) && "POST".equals(method)) {
                    handleSimpleApi(exchange, 2000, null);
                    return;
                }
                if ("/api/robokit/control/take".equals(path) && "POST".equals(method)) {
                    JSONObject req = readJsonBody(exchange);
                    JSONObject params = new JSONObject();
                    params.put("nick_name", req.optString("nick_name", "agv-java"));
                    handleSimpleApi(exchange, 4005, params);
                    return;
                }
                if ("/api/robokit/control/release".equals(path) && "POST".equals(method)) {
                    handleSimpleApi(exchange, 4006, new JSONObject());
                    return;
                }
                if ("/api/robokit/navigation/path".equals(path) && "POST".equals(method)) {
                    handlePath3051(exchange);
                    return;
                }
                if ("/api/robokit/navigation/specified-path".equals(path) && "POST".equals(method)) {
                    handleSpecifiedPath3066(exchange);
                    return;
                }
                if ("/api/robokit/navigation/stop".equals(path) && "POST".equals(method)) {
                    handleSimpleApi(exchange, 3052, null);
                    return;
                }
                if ("/api/robokit/navigation/status".equals(path) && "GET".equals(method)) {
                    handleSimpleApi(exchange, 1020, null);
                    return;
                }
                if ("/api/robokit/workflow/fangshang/load".equals(path) && "POST".equals(method)) {
                    handleFangShangLoadWorkflow(exchange);
                    return;
                }
                if ("/api/robokit/workflow/fangshang/unload".equals(path) && "POST".equals(method)) {
                    handleFangShangUnloadWorkflow(exchange);
                    return;
                }
                if ("/api/robokit/workflow/fangshang/java/load".equals(path) && "POST".equals(method)) {
                    handleFangShangLoadWorkflow(exchange);
                    return;
                }
                if ("/api/robokit/workflow/fangshang/java/unload".equals(path) && "POST".equals(method)) {
                    handleFangShangUnloadWorkflow(exchange);
                    return;
                }

                sendJson(exchange, 404, new JSONObject().put("detail", "Not Found: " + path));
            } catch (Exception e) {
                sendJson(exchange, 500, new JSONObject().put("detail", e.getMessage()));
            }
        }
    }

    // ----------------------------------------------------------------------
    // 基础连接与通用接口
    // ----------------------------------------------------------------------
    private static void handleConnect(HttpExchange exchange) throws IOException {
        JSONObject req = readJsonBody(exchange);
        String host = req.optString("host", "").trim();
        if (host.isEmpty()) {
            sendJson(exchange, 400, new JSONObject().put("detail", "host 不能为空"));
            return;
        }
        disposeClient();
        rbkClient = new RbkClient(host);
        currentHost = host;
        connected = true;
        sendJson(exchange, 200, new JSONObject().put("success", true).put("message", "连接成功"));
    }

    private static void handleDisconnect(HttpExchange exchange) throws IOException {
        disposeClient();
        sendJson(exchange, 200, new JSONObject().put("success", true));
    }

    private static void handleGenericCall(HttpExchange exchange) throws IOException {
        if (!ensureConnected(exchange)) {
            return;
        }
        JSONObject req = readJsonBody(exchange);
        int msgType = req.optInt("msg_type", -1);
        if (msgType < 0) {
            sendJson(exchange, 400, new JSONObject().put("detail", "msg_type 无效"));
            return;
        }
        JSONObject params = req.optJSONObject("params");
        String requestBody = params == null ? "" : params.toString();
        RbkResult rbkResult = rbkClient.request(msgType, requestBody, DEFAULT_TIMEOUT_MS);
        sendRbkResult(exchange, rbkResult);
    }

    private static void handleSimpleApi(HttpExchange exchange, int apiNo, JSONObject params) throws IOException {
        if (!ensureConnected(exchange)) {
            return;
        }
        String requestBody = params == null ? "" : params.toString();
        RbkResult rbkResult = rbkClient.request(apiNo, requestBody, DEFAULT_TIMEOUT_MS);
        sendRbkResult(exchange, rbkResult);
    }

    private static void handleControlMove(HttpExchange exchange) throws IOException {
        JSONObject req = readJsonBody(exchange);
        JSONObject params = new JSONObject();
        params.put("vx", req.optDouble("vx", 0));
        params.put("vy", req.optDouble("vy", 0));
        params.put("w", req.optDouble("w", 0));
        handleSimpleApi(exchange, 2010, params);
    }

    private static void handlePath3051(HttpExchange exchange) throws IOException {
        JSONObject req = readJsonBody(exchange);
        String sourceId = req.optString("source_id", "").trim();
        String targetId = req.has("target_id") ? req.optString("target_id", "").trim() : req.optString("id", "").trim();
        if (sourceId.isEmpty() || targetId.isEmpty()) {
            sendJson(exchange, 400, new JSONObject().put("detail", "缺少 source_id 与 target_id（或 id）"));
            return;
        }
        JSONObject payload = new JSONObject(req.toString());
        payload.remove("target_id");
        payload.put("source_id", sourceId);
        payload.put("id", targetId);
        handleSimpleApi(exchange, 3051, payload);
    }

    private static void handleSpecifiedPath3066(HttpExchange exchange) throws IOException {
        JSONObject req = readJsonBody(exchange);
        JSONArray list = req.optJSONArray("move_task_list");
        if (list == null || list.isEmpty()) {
            sendJson(exchange, 400, new JSONObject().put("detail", "move_task_list 不能为空"));
            return;
        }
        JSONObject payload = new JSONObject();
        payload.put("move_task_list", list);
        handleSimpleApi(exchange, 3066, payload);
    }

    // ----------------------------------------------------------------------
    // 方上取货流程（四段导航，带日志收集）
    // ----------------------------------------------------------------------
    private static void handleFangShangLoadWorkflow(HttpExchange exchange) throws IOException {
        if (!ensureConnected(exchange)) return;

        List<String> logs = new ArrayList<>();
        logs.add("========== 方上取货流程开始 ==========");

        try {
            JSONObject req = readJsonBody(exchange);
            String pickupPoint = req.optString("pickup_point", "").trim().toUpperCase();
            if (pickupPoint.isEmpty()) {
                logs.add("[错误] 请求参数缺少 pickup_point");
                sendJsonWithLogs(exchange, 400, false, "缺少取货点参数", logs);
                return;
            }
            logs.add("[参数] 取货点: " + pickupPoint);

            String nickName = req.optString("nick_name", "operator").trim();
            if (nickName.isEmpty()) nickName = "operator";
            int timeoutSec = Math.max(5, req.optInt("timeout_sec", 300));
            int pollMs = Math.max(200, req.optInt("poll_ms", 500));
            double targetHeight = req.has("target_height") ? req.optDouble("target_height", 0.25) : 0.25;
            boolean recognize = !req.has("recognize") || req.optBoolean("recognize", true);
            String recfile = req.optString("recfile", "plt/p2.plt");

            // 1. 验证站点
            logs.add("[步骤1] 验证取货点站点ID...");
            if (!validateStationId(rbkClient, pickupPoint, logs)) {
                sendJsonWithLogs(exchange, 400, false, "站点验证失败：" + pickupPoint + " 不存在", logs);
                return;
            }

            // 2. 抢占控制权
            logs.add("[步骤2] 抢占控制权...");
            JSONObject takeBody = new JSONObject().put("nick_name", nickName);
            RbkResult login = rbkClient.request(4005, takeBody.toString(), DEFAULT_TIMEOUT_MS);
            if (!isOk(login)) {
                logs.add("[错误] 抢占控制权失败: " + (login.getErrMsg() == null ? "未知错误" : login.getErrMsg()));
                sendJsonWithLogs(exchange, 502, false, "抢占控制权失败", logs);
                return;
            }
            logs.add("[步骤2] 抢占控制权成功");

            JSONArray tasks = new JSONArray();

            // 第一段：去取货点
            logs.add("\n[步骤3] 执行第一段导航：去取货点 " + pickupPoint);
            String taskId1 = buildTaskId("L1");
            JSONObject req1 = new JSONObject()
                    .put("source_id", "SELF_POSITION")
                    .put("id", pickupPoint)
                    .put("task_id", taskId1)
                    .put("operation", "ForkLoad")
                    .put("end_height", targetHeight)
                    .put("recognize", recognize)
                    .put("recfile", recfile)
                    .put("max_speed", 0.15)
                    .put("max_wspeed", 0.2);
            logs.add("[请求] " + req1.toString());
            RbkResult r1 = rbkClient.request(3051, req1.toString(), DEFAULT_TIMEOUT_MS);
            if (!isOk(r1)) {
                logs.add("[错误] 导航指令发送失败: " + (r1.getErrMsg() == null ? "" : r1.getErrMsg()));
                sendJsonWithLogs(exchange, 502, false, "第一段导航下发失败", logs);
                return;
            }
            logs.add("[成功] 导航指令已发送，任务ID: " + taskId1);
            logs.add("[等待] 等待机器人到达取货点...");
            boolean ok1 = waitForTaskCompletion(rbkClient, taskId1, timeoutSec, pollMs, logs);
            if (!ok1) {
                sendJsonWithLogs(exchange, 504, false, "第一段导航执行失败", logs);
                return;
            }
            tasks.put(new JSONObject().put("task_id", taskId1).put("request", req1).put("response", parseSafeObject(r1.getResStr())));

            // 第二段：去LM2
            logs.add("\n[步骤4] 执行第二段导航：去立库前置点 LM2");
            String taskId2 = buildTaskId("L2");
            JSONObject req2 = new JSONObject()
                    .put("source_id", "SELF_POSITION")
                    .put("id", "LM2")
                    .put("task_id", taskId2)
                    .put("operation", "ForkHeight")
                    .put("max_speed", 0.25)
                    .put("end_height", 1.1)
                    .put("max_wspeed", 0.2);
            logs.add("[请求] " + req2.toString());
            RbkResult r2 = rbkClient.request(3051, req2.toString(), DEFAULT_TIMEOUT_MS);
            if (!isOk(r2)) {
                logs.add("[错误] 导航指令发送失败: " + (r2.getErrMsg() == null ? "" : r2.getErrMsg()));
                sendJsonWithLogs(exchange, 502, false, "第二段导航下发失败", logs);
                return;
            }
            logs.add("[成功] 导航指令已发送，任务ID: " + taskId2);
            logs.add("[等待] 等待机器人到达立库前置点...");
            boolean ok2 = waitForTaskCompletion(rbkClient, taskId2, timeoutSec, pollMs, logs);
            if (!ok2) {
                sendJsonWithLogs(exchange, 504, false, "第二段导航执行失败", logs);
                return;
            }
            tasks.put(new JSONObject().put("task_id", taskId2).put("request", req2).put("response", parseSafeObject(r2.getResStr())));

            // 第三段：去AP1放货
            logs.add("\n[步骤5] 执行第三段导航：去放货点 AP1");
            String taskId3 = buildTaskId("L3");
            JSONObject req3 = new JSONObject()
                    .put("source_id", "SELF_POSITION")
                    .put("id", "AP1")
                    .put("task_id", taskId3)
                    .put("operation", "ForkUnload")
                    .put("max_speed", 0.15)
                    .put("start_height", 1.1)
                    .put("end_height", 0.94);
            logs.add("[请求] " + req3.toString());
            RbkResult r3 = rbkClient.request(3051, req3.toString(), DEFAULT_TIMEOUT_MS);
            if (!isOk(r3)) {
                logs.add("[错误] 导航指令发送失败: " + (r3.getErrMsg() == null ? "" : r3.getErrMsg()));
                sendJsonWithLogs(exchange, 502, false, "第三段导航下发失败", logs);
                return;
            }
            logs.add("[成功] 导航指令已发送，任务ID: " + taskId3);
            logs.add("[等待] 等待叉车放货...");
            boolean ok3 = waitForTaskCompletion(rbkClient, taskId3, timeoutSec, pollMs, logs);
            if (!ok3) {
                sendJsonWithLogs(exchange, 504, false, "第三段导航执行失败", logs);
                return;
            }
            tasks.put(new JSONObject().put("task_id", taskId3).put("request", req3).put("response", parseSafeObject(r3.getResStr())));

            // 第四段：回LM2
            logs.add("\n[步骤6] 执行第四段导航：回到前置点 LM2");
            String taskId4 = buildTaskId("L4");
            JSONObject req4 = new JSONObject()
                    .put("source_id", "SELF_POSITION")
                    .put("id", "LM2")
                    .put("task_id", taskId4)
                    .put("operation", "ForkHeight")
                    .put("max_speed", 0.25)
                    .put("start_height", 0.94)
                    .put("end_height", 0.09);
            logs.add("[请求] " + req4.toString());
            RbkResult r4 = rbkClient.request(3051, req4.toString(), DEFAULT_TIMEOUT_MS);
            if (!isOk(r4)) {
                logs.add("[错误] 导航指令发送失败: " + (r4.getErrMsg() == null ? "" : r4.getErrMsg()));
                sendJsonWithLogs(exchange, 502, false, "第四段导航下发失败", logs);
                return;
            }
            logs.add("[成功] 导航指令已发送，任务ID: " + taskId4);
            logs.add("[等待] 等待机器人回到前置点...");
            boolean ok4 = waitForTaskCompletion(rbkClient, taskId4, timeoutSec, pollMs, logs);
            if (!ok4) {
                sendJsonWithLogs(exchange, 504, false, "第四段导航执行失败", logs);
                return;
            }
            tasks.put(new JSONObject().put("task_id", taskId4).put("request", req4).put("response", parseSafeObject(r4.getResStr())));

            logs.add("\n========== 流程全部完成 ==========");
            JSONObject response = new JSONObject()
                    .put("success", true)
                    .put("message", "方上取货流程执行成功")
                    .put("tasks", tasks)
                    .put("logs", new JSONArray(logs));
            sendJson(exchange, 200, response);

        } catch (Exception e) {
            logs.add("[系统异常] " + e.getMessage());
            e.printStackTrace();
            sendJsonWithLogs(exchange, 500, false, "服务器内部错误", logs);
        }
    }

    // ----------------------------------------------------------------------
    // 方上卸货流程（同样带日志）
    // ----------------------------------------------------------------------
    private static void handleFangShangUnloadWorkflow(HttpExchange exchange) throws IOException {
        if (!ensureConnected(exchange)) return;

        List<String> logs = new ArrayList<>();
        logs.add("========== 方上卸货流程开始 ==========");

        try {
            JSONObject req = readJsonBody(exchange);
            String deliveryPoint = req.optString("delivery_point", "").trim().toUpperCase();
            if (deliveryPoint.isEmpty()) {
                logs.add("[错误] 请求参数缺少 delivery_point");
                sendJsonWithLogs(exchange, 400, false, "缺少卸货点参数", logs);
                return;
            }
            logs.add("[参数] 卸货点: " + deliveryPoint);

            String nickName = req.optString("nick_name", "operator").trim();
            if (nickName.isEmpty()) nickName = "operator";
            int timeoutSec = Math.max(5, req.optInt("timeout_sec", 300));
            int pollMs = Math.max(200, req.optInt("poll_ms", 500));

            // 抢占控制权
            logs.add("[步骤1] 抢占控制权...");
            JSONObject takeBody = new JSONObject().put("nick_name", nickName);
            RbkResult login = rbkClient.request(4005, takeBody.toString(), DEFAULT_TIMEOUT_MS);
            if (!isOk(login)) {
                logs.add("[错误] 抢占控制权失败: " + (login.getErrMsg() == null ? "未知错误" : login.getErrMsg()));
                sendJsonWithLogs(exchange, 502, false, "抢占控制权失败", logs);
                return;
            }
            logs.add("[步骤1] 抢占控制权成功");

            JSONArray tasks = new JSONArray();

            // 第一段：LM2升叉
            logs.add("\n[步骤2] 执行第一段导航：起始升叉 LM2");
            String taskId1 = buildTaskId("U1");
            JSONObject req1 = new JSONObject()
                    .put("source_id", "SELF_POSITION")
                    .put("id", "LM2")
                    .put("task_id", taskId1)
                    .put("operation", "ForkHeight")
                    .put("start_height", 0.09)
                    .put("end_height", 0.94)
                    .put("max_speed", 0.4)
                    .put("max_wspeed", 0.2);
            logs.add("[请求] " + req1.toString());
            RbkResult r1 = rbkClient.request(3051, req1.toString(), DEFAULT_TIMEOUT_MS);
            if (!isOk(r1)) {
                logs.add("[错误] 导航指令发送失败: " + (r1.getErrMsg() == null ? "" : r1.getErrMsg()));
                sendJsonWithLogs(exchange, 502, false, "第一段导航下发失败", logs);
                return;
            }
            logs.add("[成功] 导航指令已发送，任务ID: " + taskId1);
            logs.add("[等待] 等待叉臂升至0.94...");
            boolean ok1 = waitForTaskCompletion(rbkClient, taskId1, timeoutSec, pollMs, logs);
            if (!ok1) {
                sendJsonWithLogs(exchange, 504, false, "第一段导航执行失败", logs);
                return;
            }
            tasks.put(new JSONObject().put("task_id", taskId1).put("request", req1).put("response", parseSafeObject(r1.getResStr())));

            // 第二段：去AP1取货
            logs.add("\n[步骤3] 执行第二段导航：去AP1取货");
            String taskId2 = buildTaskId("U2");
            JSONObject req2 = new JSONObject()
                    .put("source_id", "SELF_POSITION")
                    .put("id", "AP1")
                    .put("task_id", taskId2)
                    .put("operation", "ForkLoad")
                    .put("max_speed", 0.15)
                    .put("start_height", 0.94)
                    .put("end_height", 1.1);
            logs.add("[请求] " + req2.toString());
            RbkResult r2 = rbkClient.request(3051, req2.toString(), DEFAULT_TIMEOUT_MS);
            if (!isOk(r2)) {
                logs.add("[错误] 导航指令发送失败: " + (r2.getErrMsg() == null ? "" : r2.getErrMsg()));
                sendJsonWithLogs(exchange, 502, false, "第二段导航下发失败", logs);
                return;
            }
            logs.add("[成功] 导航指令已发送，任务ID: " + taskId2);
            logs.add("[等待] 等待取货完成...");
            boolean ok2 = waitForTaskCompletion(rbkClient, taskId2, timeoutSec, pollMs, logs);
            if (!ok2) {
                sendJsonWithLogs(exchange, 504, false, "第二段导航执行失败", logs);
                return;
            }
            tasks.put(new JSONObject().put("task_id", taskId2).put("request", req2).put("response", parseSafeObject(r2.getResStr())));

            // 第三段：回LM2降叉
            logs.add("\n[步骤4] 执行第三段导航：回LM2降叉");
            String taskId3 = buildTaskId("U3");
            JSONObject req3 = new JSONObject()
                    .put("source_id", "SELF_POSITION")
                    .put("id", "LM2")
                    .put("task_id", taskId3)
                    .put("operation", "ForkHeight")
                    .put("max_speed", 0.15)
                    .put("start_height", 1.1)
                    .put("end_height", 0.25);
            logs.add("[请求] " + req3.toString());
            RbkResult r3 = rbkClient.request(3051, req3.toString(), DEFAULT_TIMEOUT_MS);
            if (!isOk(r3)) {
                logs.add("[错误] 导航指令发送失败: " + (r3.getErrMsg() == null ? "" : r3.getErrMsg()));
                sendJsonWithLogs(exchange, 502, false, "第三段导航下发失败", logs);
                return;
            }
            logs.add("[成功] 导航指令已发送，任务ID: " + taskId3);
            logs.add("[等待] 等待叉臂降至0.25...");
            boolean ok3 = waitForTaskCompletion(rbkClient, taskId3, timeoutSec, pollMs, logs);
            if (!ok3) {
                sendJsonWithLogs(exchange, 504, false, "第三段导航执行失败", logs);
                return;
            }
            tasks.put(new JSONObject().put("task_id", taskId3).put("request", req3).put("response", parseSafeObject(r3.getResStr())));

            // 第四段：去卸货点卸货
            logs.add("\n[步骤5] 执行第四段导航：去卸货点 " + deliveryPoint);
            String taskId4 = buildTaskId("U4");
            JSONObject req4 = new JSONObject()
                    .put("source_id", "SELF_POSITION")
                    .put("id", deliveryPoint)
                    .put("task_id", taskId4)
                    .put("operation", "ForkUnload")
                    .put("max_speed", 0.25)
                    .put("start_height", 0.25)
                    .put("end_height", 0.09)
                    .put("max_wspeed", 0.2);
            logs.add("[请求] " + req4.toString());
            RbkResult r4 = rbkClient.request(3051, req4.toString(), DEFAULT_TIMEOUT_MS);
            if (!isOk(r4)) {
                logs.add("[错误] 导航指令发送失败: " + (r4.getErrMsg() == null ? "" : r4.getErrMsg()));
                sendJsonWithLogs(exchange, 502, false, "第四段导航下发失败", logs);
                return;
            }
            logs.add("[成功] 导航指令已发送，任务ID: " + taskId4);
            logs.add("[等待] 等待卸货完成...");
            boolean ok4 = waitForTaskCompletion(rbkClient, taskId4, timeoutSec, pollMs, logs);
            if (!ok4) {
                sendJsonWithLogs(exchange, 504, false, "第四段导航执行失败", logs);
                return;
            }
            tasks.put(new JSONObject().put("task_id", taskId4).put("request", req4).put("response", parseSafeObject(r4.getResStr())));

            logs.add("\n========== 卸货流程全部完成 ==========");
            JSONObject response = new JSONObject()
                    .put("success", true)
                    .put("message", "方上卸货流程执行成功")
                    .put("tasks", tasks)
                    .put("logs", new JSONArray(logs));
            sendJson(exchange, 200, response);

        } catch (Exception e) {
            logs.add("[系统异常] " + e.getMessage());
            e.printStackTrace();
            sendJsonWithLogs(exchange, 500, false, "服务器内部错误", logs);
        }
    }

    // ----------------------------------------------------------------------
    // 辅助方法：站点验证、任务等待、取消任务、日志响应等
    // ----------------------------------------------------------------------
    private static boolean validateStationId(RbkClient client, String stationId, List<String> logs) {
        logs.add("[验证] 正在查询地图站点列表...");
        try {
            JSONObject queryReq = new JSONObject();
            RbkResult result = client.request(1301, queryReq.toString(), 5000);
            if (RbkResultKind.Ok.equals(result.getKind())) {
                String rawResponse = result.getResStr();
                JSONObject resJson = new JSONObject(rawResponse);
                if (resJson.has("ret_code") && resJson.getInt("ret_code") == 0) {
                    if (resJson.has("stations")) {
                        JSONArray stations = resJson.getJSONArray("stations");
                        for (int i = 0; i < stations.length(); i++) {
                            JSONObject station = stations.getJSONObject(i);
                            if (station.has("id") && stationId.equals(station.getString("id"))) {
                                logs.add("[验证] 站点 " + stationId + " 存在，验证通过。");
                                return true;
                            }
                        }
                        logs.add("[验证] 错误：地图中未找到站点 " + stationId);
                        return false;
                    } else {
                        logs.add("[验证] 错误：响应中无 stations 字段");
                        return false;
                    }
                } else {
                    logs.add("[验证] 错误：查询站点接口返回码异常");
                    return false;
                }
            } else {
                logs.add("[验证] 错误：请求站点列表失败 - " + result.getErrMsg());
                return false;
            }
        } catch (Exception e) {
            logs.add("[验证] 异常：" + e.getMessage());
            return false;
        }
    }

    private static boolean waitForTaskCompletion(RbkClient client, String taskId, long timeoutSec, int pollMs, List<String> logs) throws InterruptedException {
        long startTime = System.currentTimeMillis();
        long timeoutMillis = timeoutSec * 1000L;
        int consecutiveTimeouts = 0;
        final int MAX_CONSECUTIVE_TIMEOUTS = 5;

        while (true) {
            if (System.currentTimeMillis() - startTime > timeoutMillis) {
                logs.add("[等待] 错误：任务 " + taskId + " 执行超时 (" + timeoutSec + "s)");
                cancelTask(client, taskId, logs);
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
                        if (status == NAV_COMPLETED_STATUS) {
                            logs.add("[等待] 任务 " + taskId + " 已完成 (status=4)");
                            return true;
                        } else if (status >= 5) {
                            logs.add("[等待] 错误：任务 " + taskId + " 异常结束，状态码 " + status);
                            cancelTask(client, taskId, logs);
                            return false;
                        } else {
                            Thread.sleep(pollMs);
                        }
                    } else {
                        logs.add("[等待] 警告：响应无 task_status 字段，继续等待...");
                        Thread.sleep(pollMs);
                    }
                } else {
                    logs.add("[等待] 警告：查询状态失败 - " + result.getErrMsg());
                    Thread.sleep(pollMs);
                }
            } catch (Exception e) {
                consecutiveTimeouts++;
                logs.add("[等待] 异常 (" + consecutiveTimeouts + "/" + MAX_CONSECUTIVE_TIMEOUTS + "): " + e.getMessage());
                if (consecutiveTimeouts >= MAX_CONSECUTIVE_TIMEOUTS) {
                    logs.add("[等待] 错误：连续失败次数过多，任务 " + taskId + " 视为失败");
                    cancelTask(client, taskId, logs);
                    return false;
                }
                Thread.sleep(2000);
            }
        }
    }

    private static void cancelTask(RbkClient client, String taskId, List<String> logs) {
        try {
            JSONObject cancelReq = new JSONObject();
            cancelReq.put("task_id", taskId);
            RbkResult result = client.request(3052, cancelReq.toString(), 5000);
            if (RbkResultKind.Ok.equals(result.getKind())) {
                logs.add("[取消] 已发送取消任务请求: " + taskId);
            } else {
                logs.add("[取消] 取消任务失败: " + result.getErrMsg());
            }
        } catch (Exception e) {
            logs.add("[取消] 异常: " + e.getMessage());
        }
    }

    private static void sendJsonWithLogs(HttpExchange exchange, int statusCode, boolean success, String message, List<String> logs) throws IOException {
        JSONObject response = new JSONObject()
                .put("success", success)
                .put("message", message)
                .put("logs", new JSONArray(logs));
        sendJson(exchange, statusCode, response);
    }

    private static String buildTaskId(String suffix) {
        return "TASK_" + System.currentTimeMillis() + "_" + suffix;
    }

    private static boolean isOk(RbkResult rbkResult) {
        return rbkResult != null && rbkResult.getKind() == RbkResultKind.Ok;
    }

    private static JSONObject parseSafeObject(String raw) {
        if (raw == null || raw.trim().isEmpty()) return new JSONObject();
        try {
            return new JSONObject(raw);
        } catch (JSONException e) {
            return new JSONObject().put("raw", raw);
        }
    }

    private static void sleepQuietly(int millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException ignored) {
            Thread.currentThread().interrupt();
        }
    }

    private static JSONObject parseQuerySimple(String query) {
        JSONObject params = new JSONObject();
        if (query == null || query.isEmpty()) return params;
        String[] pairs = query.split("&");
        for (String pair : pairs) {
            String[] kv = pair.split("=", 2);
            if (kv.length == 2 && "simple".equalsIgnoreCase(kv[0])) {
                String value = kv[1].toLowerCase();
                if ("1".equals(value) || "true".equals(value) || "yes".equals(value)) {
                    params.put("simple", true);
                }
            }
        }
        return params;
    }

    private static boolean ensureConnected(HttpExchange exchange) throws IOException {
        if (!connected || rbkClient == null) {
            sendJson(exchange, 503, new JSONObject().put("detail", "未连接机器人，请先调用 /api/robokit/connect"));
            return false;
        }
        return true;
    }

    private static void sendRbkResult(HttpExchange exchange, RbkResult rbkResult) throws IOException {
        if (rbkResult.getKind() != RbkResultKind.Ok) {
            JSONObject body = new JSONObject()
                    .put("detail", rbkResult.getKind().name())
                    .put("err_msg", rbkResult.getErrMsg() == null ? "" : rbkResult.getErrMsg())
                    .put("api_no", rbkResult.getApiNo());
            sendJson(exchange, 502, body);
            return;
        }
        String res = rbkResult.getResStr();
        if (res == null || res.isEmpty()) {
            sendJson(exchange, 200, new JSONObject().put("ret_code", 0));
            return;
        }
        try {
            sendJsonRaw(exchange, 200, new JSONObject(res).toString());
        } catch (JSONException objErr) {
            try {
                JSONArray array = new JSONArray(res);
                sendJsonRaw(exchange, 200, array.toString());
            } catch (JSONException arrErr) {
                sendJson(exchange, 200, new JSONObject().put("ret_code", 0).put("raw", res));
            }
        }
    }

    private static JSONObject readJsonBody(HttpExchange exchange) throws IOException {
        String body = readBodyText(exchange);
        if (body == null || body.trim().isEmpty()) return new JSONObject();
        return new JSONObject(body);
    }

    private static String readBodyText(HttpExchange exchange) throws IOException {
        InputStream inputStream = exchange.getRequestBody();
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        byte[] buffer = new byte[4096];
        int length;
        while ((length = inputStream.read(buffer)) != -1) {
            outputStream.write(buffer, 0, length);
        }
        byte[] bytes = outputStream.toByteArray();
        return new String(bytes, StandardCharsets.UTF_8);
    }

    private static void sendJson(HttpExchange exchange, int code, JSONObject body) throws IOException {
        sendJsonRaw(exchange, code, body.toString());
    }

    private static void sendJsonRaw(HttpExchange exchange, int code, String json) throws IOException {
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        exchange.sendResponseHeaders(code, bytes.length);
        OutputStream outputStream = exchange.getResponseBody();
        outputStream.write(bytes);
        outputStream.close();
    }

    private static void addCorsHeaders(Headers headers) {
        headers.set("Access-Control-Allow-Origin", "*");
        headers.set("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
        headers.set("Access-Control-Allow-Headers", "Content-Type, Authorization");
    }

    private static synchronized void disposeClient() {
        if (rbkClient != null) {
            rbkClient.dispose();
        }
        rbkClient = null;
        currentHost = "";
        connected = false;
    }
}