# QQChat

> 用于连接 `Minecraft` 和 `QQ` 的插件

## 配置

`groups`

默认值: `[1234561, 1234562]`

交互的群组列表

`admins`

默认值: `[1234563, 1234564]`

可以私聊执行管理员指令的qq号

`whitelist_add_with_bound`

默认值: `False`

玩家绑定游戏ID时添加白名单

`whitelist_remove_with_leave`

默认值: `True`

玩家退群时移除白名单

`forwards`

默认值: `{'mc_to_qq': False, 'qq_to_mc': False}`

设置是否自动在 Minecraft 和 QQ 之间转发消息

`commands`

默认值: `{'list': True, 'mc': True, 'qq': True,}`

设置是否启用命令

## 功能

### 普通玩家命令

`/help` 查看帮助

`/list` 获取在线玩家列表

`/bound <ID>` 绑定你的游戏ID

`/mc <msg>` 向游戏内发送消息

`!!qq <msg>` 向qq群发送消息

需要注意普通玩家只能在群里执行指令，而管理可以私聊执行 `/list` 和 `/mc`

### 管理员命令

管理员命令只能私聊机器人执行, 管理员QQ号需要添加到配置文件中

#### 基础帮助

`/help` 查看帮助

`/bound` 查看绑定相关帮助

`/whitelist` 查看白名单相关帮助

`/command <command>` 执行任意指令

#### 绑定相关

`/bound list` 查看绑定列表

`/bound check <qq number>` 查询绑定ID

`/bound unbound <qq number>` 解除绑定

`/bound <qq number> <ID>` 绑定新ID

#### 白名单相关

`/whitelist add <target>` 添加白名单成员

`/whitelist list` 列出白名单成员

`/whitelist off` 关闭白名单

`/whitelist on` 开启白名单

`/whitelist reload` 重载白名单

`/whitelist remove <target>` 删除白名单成员

`<target>` 可以是玩家名/目标选择器/UUID
