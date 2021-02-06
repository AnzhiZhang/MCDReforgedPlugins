# ColoredChat

支持原版显示 [Minecraft样式代码](https://minecraft-zh.gamepedia.com/%E6%A0%B7%E5%BC%8F%E4%BB%A3%E7%A0%81) 的插件

## 配置

`force_refresh`

是否刷新聊天栏的所有内容, 某些无法被记录的信息可能会被覆盖

默认值: `True`

## 使用

正常聊天就好, 使用 `&` 替换 `§` 产生具有样式的文本

## API

插件若担心自己的信息被淹没, 可以使用 `append_msg(msg)` 方法来添加信息
