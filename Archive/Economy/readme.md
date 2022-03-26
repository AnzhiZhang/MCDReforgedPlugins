<!-- markdownlint-disable-file MD033 -->
# Economy

> 经济插件

## 环境要求

### 前置插件

- [Vault](https://github.com/zhang-anzhi/MCDReforgedPlugins/tree/master/Vault)
- [ConfigAPI](https://github.com/hanbings/ConfigAPI)

## 使用方法

| 命令 | 功能 |
|---|---|
| !!money | 查询你的余额 |
| !!money help | 查看帮助 |
| !!money top | 查看财富榜 |
| !!money check \<player> | 查询他人余额 |
| !!money pay \<player> \<amount> | 将你的钱支付给他人 |
| !!money give \<player> \<amount> | 给予他人钱 |
| !!money take \<player> \<amount> | 拿取他人钱 |
| !!money set \<player> \<amount> | 设置他人余额 |

## 配置文件

配置文件为`config/economy.yml`

### MAXIMAL_TOPS

默认值: `10`

使用 `!!money top` 时显示的数量

### DEFAULT_BALANCE

默认值: `10.00`

新玩家的默认余额

### REMINDER

默认值: `False`

余额被 `take`/`give`/`set` 时是否提醒玩家

### PERMISSIONS

默认值:

```yaml
top: 2
check: 2
give: 3
take: 3
set: 3
```

最低可以使用这些指令的权限等级
