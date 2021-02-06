# Bot

> 地毯端机器人管理与放置

## 前置插件

[ConfigAPI](https://github.com/zhang-anzhi/MCDReforgedPlugins/tree/master/ConfigAPI)
[JsonDataAPI](https://github.com/zhang-anzhi/MCDReforgedPlugins/tree/master/JsonDataAPI)

## 使用方法

`!!bot` 显示机器人列表

`!!bot help` 显示帮助

`!!bot spawn <name>` 生成机器人

`!!bot kill <name>` 移除机器人

`!!bot add <name> <dim> <pos> <facing>` 添加机器人到机器人列表

`!!bot remove <name>` 从机器人列表移除机器人

## 配置

### gamemode

默认值: `survival`

生成机器人的游戏模式

### permissions

`list`

默认值: 1

使用 `!!bot` 的最低权限

`spawn`

默认值: 2

使用 `!!bot spwan` 的最低权限

`kill`

默认值: 2

使用 `!!bot kill` 的最低权限

`add`

默认值: 3

使用 `!!bot add` 的最低权限

`remove`

默认值: 3

使用 `!!bot remove` 的最低权限
