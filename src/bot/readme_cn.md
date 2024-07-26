# Bot

[English](readme.md)

> 最好用的地毯模组假人管理器！

## 依赖

- [MinecraftDataAPI](https://github.com/MCDReforged/MinecraftDataAPI)
- [MoreCommandNodes](../more_command_nodes)

## 使用方法

`!!bot` 查看帮助

`!!bot list [index] [filter]` 显示假人列表

`!!bot spawn <name>` 上线假人

`!!bot kill <name>` 下线假人

`!!bot action <name> [index]` 执行假人动作

`!!bot tags` 查看可用标签

`!!bot tags <tag> spawn/kill` 上线/下线带有标签的假人

`!!bot info <name>` 查看假人信息

`!!bot save <name> [position] [facing] [dimension]` 保存假人

`!!bot del <name>` 删除保存的假人

`!!bot config <name> <option> <value>` 配置假人

### 工作流

```mermaid
sequenceDiagram
    participant Player/Console
    participant Online Bots
    participant Saved Bots

    Player/Console-->>Online Bots: !!bot spawn (player)
    Saved Bots-->>Online Bots: !!bot spawn
    Online Bots-->>Online Bots: !!bot kill
    Online Bots-->>Saved Bots: !!bot save
    Player/Console-->>Saved Bots: !!bot save [location]
    Saved Bots-->>Saved Bots: !!bot del
```

### list

**index**：列表的页码

**filter**：可用选项为：`--all`、`--online` 或 `--saved`，过滤假人

### spawn

上线假人

```mermaid
flowchart TD
    start([list])
    is_saved{Saved?}
    is_player{Running by Player?}

    start --> is_saved
    is_saved -->|Yes| spawn1(Spawn at Saved Location)
    is_saved -->|No| is_player
    is_player -->|Yes| spawn2(Spawn at player's Location)
    is_player -->|No| error1([Not Saved Error])
```

### kill

下线假人

### action

执行假人动作

当指定 `index` 时，执行特定动作而不是全部动作

### tags

查看可用标签和上线/下线带有标签的假人

`!!bot tags` 查看可用标签

`!!bot tags <tag> spawn` 上线带有标签的假人

`!!bot tags <tag> kill` 下线带有标签的假人

### info

查看假人信息

### save

保存假人

```mermaid
flowchart TD
    start([save])
    with_location{Has Location?}
    online{Online or Saved?}
    is_player{Running by Player?}

    start --> with_location
    with_location -->|Yes| save3(Save at Input Location)
    with_location -->|No| online

    online -->|Yes| save1(Save at Bot's Location)
    online -->|No| is_player
    is_player -->|Yes| save2(Save at player's location)
    is_player -->|No| error1([Bot Not Exists])
```

### del

删除保存的假人

### config

配置假人

### 完整指令树

```mermaid
flowchart LR
    start(!!bot)

    start --> list(list)
    list --> list_index["&lt;index&gt;"]
    list_index --> list_index_arg["
        --all
        --online
        --saved
    "]

    start --> spawn(spawn)
    spawn --> spawn_name("&lt;name&gt;")

    start --> kill(kill)
    kill --> kill_name("&lt;name&gt;")

    start --> action(action)
    action --> action_name("&lt;name&gt;")
    action_name --> action_name_index["&lt;index&gt;"]

    start --> tags(tags)
    tags --> tags_tag["&lt;tag&gt;"]
    tags_tag --> tags_tag_spawn(spawn)
    tags_tag --> tags_tag_kill(kill)

    start --> info(info)
    info --> info_name("&lt;name&gt;")

    start --> save(save)
    save --> save_name("&lt;name&gt;")
    save_name --> save_name_position["&lt;position&gt;"]
    save_name_position --> save_name_position_facing["&lt;facing&gt;"]
    save_name_position_facing --> save_name_position_facing_dimension["&lt;dimension&gt;"]

    start --> del(del)
    del --> del_name("&lt;name&gt;")

    start --> config(config)
    config --> config_name("&lt;name&gt;")
    config_name --> config_name_name("name &lt;newName&gt;")
    config_name --> config_name_position("position &lt;position&gt;")
    config_name --> config_name_facing("facing &lt;facing&gt;")
    config_name --> config_name_dimension("dimension &lt;dimension&gt;")
    config_name --> config_name_comment("comment &lt;comment&gt;")
    config_name --> config_name_actions(actions)
    config_name --> config_name_tags(tags)
    config_name --> config_name_autoLogin("autoLogin &lt;autoLogin&gt;")
    config_name --> config_name_autoRunActions("autoRunActions &lt;autoRunActions&gt;")
    config_name --> config_name_autoUpdate("autoUpdate &lt;autoUpdate&gt;")

    config_name_actions --> config_name_actions_append("append &lt;action&gt;")
    config_name_actions --> config_name_actions_insert("insert &lt;index&gt; &lt;action&gt;")
    config_name_actions --> config_name_actions_delete("delete &lt;index&gt")
    config_name_actions --> config_name_actions_edit("edit &lt;index&gt; &lt;action&gt;")
    config_name_actions --> config_name_actions_clear(clear)

    config_name_tags --> config_name_tags_append["append &lt;tag&gt;"]
    config_name_tags --> config_name_tags_insert["insert &lt;index&gt; &lt;tag&gt;"]
    config_name_tags --> config_name_tags_delete["delete &lt;index&gt"]
    config_name_tags --> config_name_tags_edit["edit &lt;index&gt; &lt;tag&gt;"]
    config_name_tags --> config_name_tags_clear[clear]
```

## 配置

### gamemode

默认值: `survival`

生成假人的游戏模式

### force_gamemode

默认值: `false`

是否强制所有假人使用 `gamemode` 配置的游戏模式，如果为 `false`，只有已保存的假人会使用 `gamemode` 配置的游戏模式。

### name_prefix

默认值: `bot_`

假人名称前缀

### name_suffix

默认值: 无

假人名称后缀

### permissions

使用对应指令的最低权限

## FastAPI MCDR

该插件支持 [FastAPI MCDR](../fastapi_mcdr) 插件，详细接口请查阅源码，或运行后通过 `http://127.0.0.1:8080/docs` 查看 FastAPI 文档。

Python 包要求：

```text
pydantic>=2.0
```
