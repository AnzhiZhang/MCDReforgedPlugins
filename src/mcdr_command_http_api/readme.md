# MCDR Command HTTP API

> 提供 HTTP 调用 MCDR 命令的接口

## 依赖

| 插件 | 版本 |
| - | - |
| [fastapi_mcdr](https://github.com/AnzhiZhang/MCDReforgedPlugins/tree/master/src/fastapi_mcdr) | \>=2.0.0 |

## 配置

配置文件路径：`config/mcdr_command_http_api/config.json`

| 配置项 | 默认值 | 说明 |
| - | - | - |
| `token` | 随机生成 | 接口鉴权 Token，首次加载时自动生成 |

## 接口

所有接口均挂载在 `/mcdr_command_http_api` 路径下。

### 鉴权

请求时需在 HTTP Header 中携带 Bearer Token：

```http
Authorization: Bearer <token>
```

### POST /mcdr_command_http_api/execute

在 MCDR 命令系统中执行一条命令。

#### 请求体

```json
{
  "command": "!!MCDR status",
  "timeout": 10000
}
```

| 字段 | 类型 | 说明 |
| - | - | - |
| `command` | `string` | 要执行的 MCDR 命令 |
| `timeout` | `int` | 等待回复的最长时间（ms） |

#### 响应

```json
{
    "status": "ok",
    "command": "!!MCDR status",
    "reply": {
        "id": 2178126035648,
        "is_finished": false,
        "messages": [
            "MCDReforged version: 2.15.7",
            "MCDR state: Running",
            "Server state: Running",
            "Server startup: True",
            "Exit after server stops: True",
            "Rcon: Offline",
            "Plugin count: 5",
            "Server PID: 26804",
            "  cmd.exe: 26804",
            "  └── java.exe: 53608",
            "Info queue load: 0/2048",
            "Task queue load: 0/1048576",
            "Thread count: 13"
        ]
    }
}
```
##### reply 获取逻辑
- 大部分插件的命令均能正常响应：即命令回调函数正常释放了 `CommandSource`;
- 若命令回调函数执行结束后 `CommandSource` 未被释放，则不保证能收到全部消息，且在 `timeout`毫秒后的消息会被丢弃，以下为可能的技术细节：
  - 命令回调函数将 `CommandSource` 放到了新的线程，命令回调函数返回后仍然通过 `CommandSource.reply` 回复消息；
  - 命令回调函数创建了 `CommandSource` 的作用域外部的应用，如将 `CommandSource` 放到了全局列表，且后续有其他方法通过 `CommandSource.reply` 回复消息。

##### reply 结构
| 字段 | 类型 | 说明 |
| - | - | - |
| `id` | int | 回复 ID |
| `is_finished` | bool | 是否返回了命令的全部回复，true: 一定得收集了全部回复，false: 不保证回复完整性 |
| `messages` | list[str] | 回复消息 |

#### 错误码

| 状态码 | 说明 |
| - | - |
| `401` | Token 无效 |

## 在线调试

启动 MCDR 后访问 `http://<服务器IP>:8080/mcdr_command_http_api/docs` 可使用 Swagger UI 在线测试接口。
