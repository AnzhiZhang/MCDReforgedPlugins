# StartStopHelperR

> 开关服助手

## 使用

| 指令 | 用途 |
| - | - |
| !!server | 显示帮助信息 |
| !!server start | 启动服务器 |
| !!server stop | 关闭服务器 |
| !!server stop_exit | 关闭服务器并退出 MCDR |
| !!server restart | 重启服务器 |
| !!server exit | 退出 MCDR |

## 配置

### permissions

各指令所需的最低权限等级

默认值:

```json
{
    "help": 3,
    "start": 3,
    "stop": 3,
    "stop_exit": 4,
    "restart": 3,
    "exit": 4
}
```
