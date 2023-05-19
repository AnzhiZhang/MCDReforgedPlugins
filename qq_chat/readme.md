<!-- markdownlint-disable MD033 -->
# QQChat

> 用于连接 `Minecraft` 和 `QQ` 的插件

## 功能说明

### 名词定义

| 名词 | 含义 | 备注 |
| ---------- | :--------------------: | ------------------------------------------------------------ |
| **群友** | QQ群聊中的玩家 | |
| **玩家** | MC服务器中的玩家 | |
| **管理** | 对于qq_chat的管理员（admin） | `admins` |
| **主群** | 服务器的主要交流群 | `main_group` 一般指服务器最大的群，包括所有人，有且只有一个，如配置多个群将取第一个 |
| **管理群** | 服务器管理群 | `manage_groups` 此群群友无论是否配置为管理，在此群中都具有管理的权限 |
| **同步群** | 服务器聊天板同步群 | `message_sync_groups` 同步所有玩家的发言，在此群中发送非命令的消息也会同步到服务器 |

### 场景说明

1. 管理可以在任何场景下（包括群聊和私聊）都具有对应权限（包括 `mc`、`list`、`command`、`whitelist`、`mcdr`）
2. 管理群中，所有人均获得管理权限，即使有的人没有在 `admins` 中
3. MCDR指令的执行没有返回信息，不太适用于需要交互的场景（除非你知道MCDR会输出什么），请自行判断与使用

## 迁移说明

由于功能升级改动了配置文件，如需将 `v1.0.1` 的配置文件迁移至 `v1.1.0`，并维持原有功能，请参考如下步骤

1. 将 `groups` 属性配置的群组，填入 `message_sync_groups` 中
2. 删除 `groups` 属性

## 配置说明

| 配置项 | 含义 | 默认值 | 注意事项 |
| ----------------------------- | -------------------------- | -------------------- | ------------------------------------------------------------ |
| `main_group` | 主群 | `[123456]` | 最多填一个，多填取首个 |
| `manage_groups` | 管理群 | `[1234563, 1234564]` | 非必填 |
| `message_sync_groups` | 同步群 | `[1234567, 1234568]` | 非必填 |
| `server_name` | 服务器名 | `'survival'` | 发送到qq时会加上server_name的前缀 |
| `admins` | 管理列表 | `[1234565, 1234566]` | 理论上非必填（ |
| `sync_group_only_admin:` | 同步群是否只包含管理 | `true` | 如果关闭，成员权限同主群<br />如果打开。成员权限同管理群 |
| `whitelist_add_with_bound` | 群友绑定id时自动添加白名单 | `false` | 离线服使用大概率有问题 |
| `whitelist_remove_with_leave` | 玩家退群自动移除白名单 | `true` | 须防止冒名绑定id |
| `mc_to_qq` | mc发言同步qq群 | `false` | 主群只同步使用`!!qq`指令的信息<br />同步群全部同步 |
| `qq_to_mc` | qq群发言同步mc | `false` | 主群只同步使用`/mc`指令的信息<br />同步群全部同步 |
| `list` | 开启`/list`指令 | `true` | Whynot? |
| `mc` | 开启`/mc`指令 | `true` | Whynot? |
| `qq` | 开启`/qq`指令 | `true` | Whynot? |
| `mcdr` | 开启`/mcdr`指令 | `false` | **仅仅建议紧急运维时使用，没有返回信息，没有返回信息，没有返回信息** |
| `command_prefix` | 触发机器人指令的前缀 | `['/']` | 配置单字符如 `'/'` 或 `'#'` 时，指令格式为 `/list` 等<br />配置多字符如 `'mc'` 或 `'bot'` 时，指令格式为 `mc list`，需在前缀与指令之间添加空格 |

## 命令帮助

**注：以前缀为`'/'`为例，实际指令请参考配置文件**

> 普通玩家命令帮助如下

`/list` 获取在线玩家列表

`/bound <ID>` 绑定你的游戏ID

`/mc <msg>` 向游戏内发送消息

`!!qq <msg>` 游戏内向主群发送消息

> 管理员命令帮助如下

`/bound` 查看绑定相关帮助

`/whitelist` 查看白名单相关帮助

`/command <command>` 执行任意指令

`/mc <msg>` 向游戏内发送消息

`/mcdr <mcdr command>` 执行mcdr指令（可不添加 `!!` 前缀，无回显，谨慎使用）

> bound指令帮助

`/bound list` 查看绑定列表

`/bound check <qq number>` 查询绑定ID

`/bound unbound <qq number>` 解除绑定

`/bound <qq number> <ID>` 绑定新ID

> whitelist指令帮助

`/whitelist add <target>` 添加白名单成员

`/whitelist list` 列出白名单成员

`/whitelist off` 关闭白名单

`/whitelist on` 开启白名单

`/whitelist reload` 重载白名单

`/whitelist remove <target>` 删除白名单成员

注: `<target>` 可以是玩家名/目标选择器/UUID
