# OnlinePlayerAPI

> 在线玩家 API

## API

### is_online(player: str, case_sensitive: bool = True)

如果玩家在线, 返回 `True`。

如果玩家不在线, 返回 `False`。

`case_sensitive` 是否忽略大小写。

### check_online(player: str, case_sensitive: bool = True)

与 `is_online(player)` 相同。

### get_player_list()

返回所有在线玩家的列表。

### normalize_player_name(player: str)

返回给定玩家名称的正确大小写形式。

如果玩家不在线，则引发 ValueError。
