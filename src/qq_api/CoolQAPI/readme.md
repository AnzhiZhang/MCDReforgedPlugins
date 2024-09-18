# CoolQAPI

> [!NOTE]  
> 这是 CoolQAPI （qq_api 0.x) 的归档

---

> [MCDReforged](https://github.com/Fallen-Breath/MCDReforged) 的QQ开发API
>
> 事件功能参考了 [MCDReforged](https://github.com/Fallen-Breath/MCDReforged) 的插件加载

## 环境要求

### 依赖的Python模块

已存储在 [requirements.txt](requirements.txt) 中, 可以使用 `pip install -r requirements.txt` 安装

## 使用

前往 [release](https://github.com/zhang-anzhi/CoolQAPI/releases) 页面下载最新的release并解压

### 配置QQ机器人

机器人建议使用 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)

如有问题可以在 MCDR 群内讨论或发 Issue

示例配置(请修改QQ号和密码)：

```yaml
{
    uin: 123123123
    password: "password"
    encrypt_password: false
    password_encrypted: ""
    enable_db: true
    access_token: ""
    relogin: {
        enabled: true
        relogin_delay: 3
        max_relogin_times: 0
    }
    _rate_limit: {
        enabled: false
        frequency: 1
        bucket_size: 1
    }
    ignore_invalid_cqcode: false
    force_fragmented: false
    heartbeat_interval: 0
    http_config: {
        enabled: true
        host: 127.0.0.1
        port: 5700
        timeout: 0
        post_urls: {
            "127.0.0.1:5701/post": ""
        }
    }
    ws_config: {
        enabled: false
        host: 0.0.0.0
        port: 6700
    }
    ws_reverse_servers: []
    post_message_format: array
    use_sso_address: false
    debug: false
    log_level: "info"
    web_ui: {
        enabled: false
        host: 127.0.0.1
        web_ui_port: 9999
        web_input: false
    }
}
```

### 配置MCDR

将 `CoolQAPI-MCDR.py` 和 `CoolQAPI` 文件夹放入MCDR的plugins文件夹

重载MCDR

### 关于多服使用

`QQBridge` 可以将一个机器人接受的信息分发给多个服务器进行处理

这里是进行多个服务器配置的方法 [QQBridge使用文档](docs/QQBridge.md)

## 配置文件

配置文件位于 `CoolQAPI\config.yml`

`post_host`

默认值: `127.0.0.1`

接收转发消息的ip地址

`post_port`

默认值: `5701`

接收转发消息的端口

`post_path`

默认值: `post`

接收转发消息的路径

`api_host`

默认值: `127.0.0.1`

api的ip地址

`api_port`

默认值: `5700`

api的端口

`command_prefix`

默认值: `/`

触发命令事件的消息前缀

## 指令

| Command | Function |
| -| -|
| !!cq update | 检查并自动更新 |

## 开发

请阅读 [开发文档](docs/plugin.md) 了解开发相关内容
