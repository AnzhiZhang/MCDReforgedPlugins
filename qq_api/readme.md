# QQAPI

> QQ bot development API.

## Usage

### QQ Bot Configuration

It is recommended to use [go-cqhttp](https://github.com/Mrs4s/go-cqhttp).

Set qq account and password in `account` field:

```yaml
account:
  uin: 1233456
  password: ''
```

Add http server in `servers` field:

```yaml
servers:
  - http:
      address: 0.0.0.0:5700
      post:
      - url: http://127.0.0.1:5701/
```

## 配置文件

`post_host`

默认值: `127.0.0.1`

接收转发消息的ip地址

`post_port`

默认值: `5701`

接收转发消息的端口

`api_host`

默认值: `127.0.0.1`

api的ip地址

`api_port`

默认值: `5700`

api的端口

### 关于多服使用

`QQBridge` 是一个可以将机器人上报消息分发给多个服务器进行处理的应用。

直接运行 `QQBridge.py` 即可。

#### 指令

| 指令 | 功能 |
| - | - |
| stop | 关闭QQBridge |
| help | 获取帮助 |
| reload config | 重载配置文件 |
| debug thread | 查看线程列表 |

#### 配置

`post_host`

接收上报信息的地址

默认值: `127.0.0.1`

`post_port`

接收上报信息的端口

默认值: `5701`

`post_utl`

接收上报信息的url

默认值: `/post`

以上接收上报消息的配置与 [readme.md](../readme.md) 对应

`server_list`

需要转发的服务器列表, 参照以下格式填写

```yaml
example:
  host: 127.0.0.1
  port: 5702
  url: ''
```

默认值: 上文的例子

`debug_mode`

调试模式

默认值: `flase`

> 你还需要修改 QQAPI 配置文件的 `post_host`, `post_port` 使其与 `server_list` 的内容对应
>
> 建议从 `5702` 向上增加，如第一个服为 `5702` 第二个服为 `5703`

## 开发

[示例模范插件 QQChat](https://github.com/AnzhiZhang/MCDReforgedPlugins/tree/master/qq_chat)

### 事件

当从QQ接收到消息, 会触发以下各类事件

每个事件监听器需要使用 `register_event_listener` API 注册, 事件ID为 `qq_api.事件名`

- `server`：[PluginServerInterface](https://mcdreforged.readthedocs.io/zh_CN/latest/code_references/PluginServerInterface.html)
- `bot`：[CQHttp](https://aiocqhttp.nonebot.dev/module/aiocqhttp/index.html#aiocqhttp.CQHttp)。
- `event`：[Event](https://aiocqhttp.nonebot.dev/module/aiocqhttp/index.html#aiocqhttp.Event)

| 事件 | 参考 |
| - | - |
| on_message(server, bot, event) | [on_message](https://aiocqhttp.nonebot.dev/module/aiocqhttp/index.html#aiocqhttp.CQHttp.on_message) |
| on_notice(server, bot, event) | [on_notice](https://aiocqhttp.nonebot.dev/module/aiocqhttp/index.html#aiocqhttp.CQHttp.on_notice) |
| on_request(server, bot, event) | [on_request](https://aiocqhttp.nonebot.dev/module/aiocqhttp/index.html#aiocqhttp.CQHttp.on_request) |
| on_meta_event(server, bot, event) | [on_meta_event](https://aiocqhttp.nonebot.dev/module/aiocqhttp/index.html#aiocqhttp.CQHttp.on_meta_event) |

### API

#### get_bot()

用于获取 `bot` 对象
