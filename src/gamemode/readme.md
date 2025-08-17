# Gamemode

> 高级版灵魂出窍(切旁观, 切回生存传送回原位置)

感谢 [方块君](https://github.com/Squaregentleman) 的 [gamemode](https://github.com/Squaregentleman/MCDR-plugins) 插件

## 前置插件

- [MinecraftDataAPI](https://github.com/MCDReforged/MinecraftDataAPI)

## 使用

`!!spec` / `!s` 旁观/生存切换

`!!tp <dimension> [position]` 传送至指定地点

`!!back` 返回上个地点

## 配置

### short_command

默认值: `True`

是否启用短命令

### range_limit

活动范围限制（切旁观时限制活动范围在一个长方体内），超过限制范围将自动传回到最近的边界，仅对无 tp 权限的玩家生效。

`check_interval` 默认值: `0`

检查间隔（秒），`0` 表示禁用活动范围限制，推荐不大于 `5`

`x` 默认值: `50`

x 方向活动半径，`0` 代表不限制此方向上的活动范围

`y` 默认值: `50`

y 方向活动半径，`0` 代表不限制此方向上的活动范围

`z` 默认值: `50`

z 方向活动半径，`0` 代表不限制此方向上的活动范围

### 其他数字配置是权限

`spec`

默认值: `1`

使用 `!!spec` 的最低权限

`spec_other`

默认值: `2`

使用 `!!spec <player` 的最低权限

`tp`

默认值: `1`

使用 `!!tp <dimension> [position]` 的最低权限

`back`

默认值: `1`

使用 `!!back` 的最低权限
