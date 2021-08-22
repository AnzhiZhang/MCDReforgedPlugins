# SinglePlayerSleep

允许在服务器中单人睡觉跳过夜晚

## 前置插件

- [MinecraftDataAPI](https://github.com/MCDReforged/MinecraftDataAPI)

- [ConfigAPI](https://github.com/hanbings/ConfigAPI)

## 配置

配置文件位于 `config\SinglePlayerSleep\SinglePlayerSleep.yml`

`skip_wait_time`

跳过夜晚所需要的时间

默认值: `10`

`wait_before_skip`

开始跳过夜晚前等待的时间

默认值: `5`

其余配置项为语言, 可自定义插件的语言显示

## 使用

`!!sleep` 声明我在睡觉, 开始跳过夜晚

`!!sleep cancel` 取消其他玩家的跳过夜晚声明
