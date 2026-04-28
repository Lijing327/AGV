# RBK Tcp Java 客户端

demo 在 test 文件夹下的 `com.seer.sdk.demo` 的 `RbkClientDemo`

备注：Rbk 多数 API 的请求和响应正文都是 JSON。

```java
public class Main {
    public static void main(String[] args) {
    RbkClient rbkClient = new RbkClient("192.168.8.114");
    RbkResult request = rbkClient.request(1000, "", 10000);
    rbkClient.dispose(); // 释放连接资源
}
```

## AGV Java 后端（最小对接版）

项目内新增了一个轻量 HTTP 服务：`com.seer.sdk.agvserver.AgvJavaServer`，用于在 AGV 项目中作为 Java 后端对接前端接口。

### 启动方式

- 默认端口 8001
- 可传启动参数指定端口（例如 `8002`）

示例：

```bash
mvn exec:java -Dexec.mainClass="com.seer.sdk.agvserver.AgvJavaServer"
```

或指定端口：

```bash
mvn exec:java -Dexec.mainClass="com.seer.sdk.agvserver.AgvJavaServer" -Dexec.args="8002"
```

### 已对接接口（与前端路径保持一致）

- `POST /api/robokit/connect`
- `POST /api/robokit/disconnect`
- `GET /api/robokit/status`
- `POST /api/robokit/call`
- `GET /api/robokit/robot/location`
- `GET /api/robokit/robot/speed`
- `GET /api/robokit/robot/battery`
- `GET /api/robokit/robot/emergency`
- `GET /api/robokit/robot/io`
- `POST /api/robokit/control/move`
- `POST /api/robokit/control/stop`
- `POST /api/robokit/control/take`
- `POST /api/robokit/control/release`
- `POST /api/robokit/navigation/path`
- `POST /api/robokit/navigation/specified-path`
- `POST /api/robokit/navigation/stop`
- `GET /api/robokit/navigation/status`

### 前端切换到 Java 后端

将前端环境变量 `VITE_API_BASE` 指向 Java 服务，例如：

```env
VITE_API_BASE=http://<java服务IP>:8001/api
```
