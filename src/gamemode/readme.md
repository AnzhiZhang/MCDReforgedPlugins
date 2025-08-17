# Gamemode

> 高级版灵魂出窍 (切旁观, 切回生存传送回原位置)

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

若启用了 `short_command`, 可使用配置的短命令 (如: `!s`) 实现与 `!!spec` 相同的效果

## 配置

默认配置如下:

```json
{
    "config_version": 2,
    "permissions": {
        "spec": 1,
        "spec_other": 2,
        "tp": 1,
        "back": 1
    },
    "short_command": {
        "enabled": false,
        "command": "!s"
    },
    "data_save_path": ""
}
```

### `config_version`

配置文件版本, 请不要更改

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

### `short_command`

短命令相关

#### `enabled`

默认值: `false`

是否启用短命令

#### `command`

默认值: `!s`

`!!spec` 命令的别名. 运行此命令的权限要求与 `!!spec` 相同

### `data_save_path`

默认值: (空)

用于设置存储正处于旁观模式的玩家的信息 (如: 他们生存切旁观时的位置) 等数据的文件的位置.

为空 (默认) 时存储于 `config/gamemode/config.json`

如果你同时安装了其他备份插件 (如 Prime Backup), 则建议将此文件放置于存档内而不是默认的存档外, 防止回档后玩家的 "旁观" 没有回档. 例如: `server/world/mcdr-plugin-config/gamemode/data.json`.