# Gamemode

> 高级版灵魂出窍（切旁观，切回生存传送回原位置）

感谢 [方块君](https://github.com/Squaregentleman) 的 [gamemode](https://github.com/Squaregentleman/MCDR-plugins) 插件

## 前置插件

- [MinecraftDataAPI](https://github.com/MCDReforged/MinecraftDataAPI)

## 使用

`!!spec` 切换旁观/生存

`!!spec <player>` 切换他人模式

`!!tp <player>` 传送至指定玩家

`!!tp <dimension>` 传送至指定维度（主世界与下界自动换算坐标）

`!!tp [dimension] <x> <y> <z>` 传送至（指定维度的）指定坐标

`!!back` 返回上个地点

若启用了 `short_commands`，可使用配置的短命令（如: `!s`）替代 `!!spec`

## 配置

默认配置如下:

```json
{
    "version": 2,
    "data_path": null,
    "short_commands": [
        "!s"
    ],
    "permissions": {
        "spec": 1,
        "spec_other": 2,
        "tp": 1,
        "back": 1
    },
    "range_limit": {
        "check_interval": 0,
        "x": 50,
        "y": 50,
        "z": 50
    }
}
```

### `version`

配置文件版本，请不要更改

### `data_path`

默认值: `null`

用于设置存储正处于旁观模式的玩家的信息（如: 他们生存切旁观时的位置）等数据的文件的位置，默认（`null`）存储于插件配置文件夹中。

如果你同时安装了其他备份插件（如 Prime Backup），则建议将此项设置为存档内的文件，防止回档后玩家的 "旁观" 没有回档，例如 `server/world/mcdr-plugin-config/gamemode/data.json`。

### `permissions`

各种操作所需的最低权限

#### `spec`

默认值: `1`

使用 `!!spec` 与 `short_command` (若启用) 的最低权限

#### `spec_other`

默认值: `2`

使用 `!!spec <player>` 的最低权限

#### `tp`

默认值: `1`

使用 `!!tp <player>`、`!!tp <dimension>`、`!!tp [dimension] <x> <y> <z>` 的最低权限

#### `back`

默认值: `1`

使用 `!!back` 的最低权限

### `short_commands`

默认值: `["!s"]`

短命令列表，`!!spec` 的别名，运行此命令的权限要求与 `!!spec` 相同。

### `range_limit`

活动范围限制（切旁观时限制活动范围在一个长方体内），超过限制范围将自动传回到最近的边界，仅对无 tp 权限的玩家生效。

#### `check_interval`

默认值: `0`

检查间隔（秒），`0` 表示禁用活动范围限制，推荐不大于 `5`

#### `x`

默认值: `50`

x 方向活动半径，`0` 代表不限制此方向上的活动范围

#### `y`

默认值: `50`

y 方向活动半径，`0` 代表不限制此方向上的活动范围

#### `z`

默认值: `50`

z 方向活动半径，`0` 代表不限制此方向上的活动范围
