# MapcrafterRender

通过服务器指令进行 `Mapcrafter` 渲染

自动复制最新存档, 自带扫地功能

## 使用

使用 `!!map` 进行渲染

## 配置

所有路径相对于MCDR根目录, 也就是 `MCDReforged.py` 所在的目录, 也可以填写绝对路径

`mapcrafter_path`

默认值: `mapcrafter`

Mapcrafter文件夹

`output_path`

默认值: ``

输出路径, 用于渲染前进行清理

`thread_num`

默认值: `4`

Mapcrafter渲染的线程数量, 请根据自己CPU实际情况填写

## 提示

- 请给你的配置文件起名为 `config.conf`, 放入 `mapcrafter_path`

参考配置:

```text
output_dir = D:\nginx\html

[global:map]
world = overworld

[world:overworld]
input_dir = world
dimension = overworld

[map:isometric]
name = Overworld_isometric
rotations = top-left
render_view = isometric
```

- Mapcrafter的配置问题可以百度或者发Issue

- 服务器不知道用什么的可以考虑[nginx](https://nginx.org/en/)
