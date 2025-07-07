# UUID API

> 玩家 UUID API

## 依赖的 Python 模块

- requests

## 使用方法

```python
get_uuid(name: str) -> UUID | None
```

未查到时返回 `None`。

示例：

```python
uuid_api = server.get_plugin_instance('uuid_api')
uuid = uuid_api.get_uuid('Steve')
server.logger.warning(uuid)
```

## 配置

### use_usercache

默认值: `true`

是否使用 `usercache.json` 文件中的数据做为缓存来获取玩家 UUID。

### override_online_mode

默认值: `false`

是否覆盖 `server.properties` 中的 `online-mode` 设置。

如果设置为 `true`，则插件将忽略 `server.properties` 中的在线模式设置，并使用插件配置中的 `override_online_mode_value`。

如果使用了 BungeeCord 或 Velocity 等代理服务器，并开启了正版验证, 或实际的 UUID 与 `server.properties` 中的 `online-mode` 并不匹配，设置该值确保插件正确处理在线模式。

### override_online_mode_value

默认值: `true`

如果 `override_online_mode` 设置为 `true`，则此值将决定插件是否认为服务器处于在线模式。
