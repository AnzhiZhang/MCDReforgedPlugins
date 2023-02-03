# QQBridge使用文档

运行 `QQBridge.py` 直接使用

## 指令

| 指令 | 功能 |
| - | - |
| stop | 关闭QQBridge |
| help | 获取帮助 |
| reload config | 重载配置文件 |
| debug thread | 查看线程列表 |

## 配置

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
  url: post
```

默认值: 上文的例子

`debug_mode`

调试模式

默认值: `flase`

> 你还需要修改 CoolQAPI 配置文件的 `post_host`, `post_port`, `post_url` 使其与 `server_list` 的内容对应
>
> 建议从 `5702` 向上增加，如第一个服为 `5702` 第二个服为 `5703`

## 开发

有关QQBridge的开发帮助位于开发文档的[QQBridge](plugin.md#QQBridge)章节
